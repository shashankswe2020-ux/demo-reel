"""Pixel- and sample-level measurements of a rendered reel. Nothing here trusts the plan."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any

from . import captions, specs
from .checks import Check, make
from .ffmpeg import (ToolError, frame_metadata, loudness, media_path, parse_metadata, probe, ratio, run,
                     silences, tool, top_level_atoms)


def infer_format(width: int, height: int) -> str | None:
    return next((name for name, dims in specs.FORMATS.items() if dims == (width, height)), None)


def frame_series(path: str | Path) -> list[dict[str, float]]:
    vf = (f"scale={specs.ANALYSIS_WIDTH}:-2,signalstats,scdet=threshold={specs.CUT_SCORE},"
          "metadata=print:file=-")
    return frame_metadata(path, vf)


def _edge_density(path: str | Path) -> dict[str, float]:
    zones = {
        "bottom": f"crop=iw:ih*{specs.SAFE_ZONE['bottom']}:0:ih*{1 - specs.SAFE_ZONE['bottom']}",
        "right": f"crop=iw*{specs.SAFE_ZONE['right']}:ih:iw*{1 - specs.SAFE_ZONE['right']}:0",
        "center": "crop=iw*0.6:ih*0.4:iw*0.2:ih*0.3",
    }
    labels = list(zones)
    graph = [f"[0:v]fps=4,scale=270:480,edgedetect=low=0.1:high=0.3,split={len(labels)}"
             + "".join(f"[s{i}]" for i in range(len(labels)))]
    graph += [f"[s{i}]{zones[z]},signalstats,metadata=print:file={z}.txt[o{i}]" for i, z in enumerate(labels)]
    src = media_path(path)
    with tempfile.TemporaryDirectory() as tmp:
        args = [tool("ffmpeg"), "-hide_banner", "-nostats", "-i", src, "-an", "-filter_complex", ";".join(graph)]
        for i in range(len(labels)):
            args += ["-map", f"[o{i}]", "-f", "null", "-"]
        run(args, cwd=Path(tmp))
        out = {}
        for z in labels:
            frames = parse_metadata((Path(tmp) / f"{z}.txt").read_text())
            vals = [f["YAVG"] for f in frames if "YAVG" in f]
            out[z] = sum(vals) / len(vals) if vals else 0.0
    return out


def _loop_ssim(path: str | Path, fps: float) -> float | None:
    src = media_path(path)
    with tempfile.TemporaryDirectory() as tmp:
        first, last = Path(tmp) / "first.png", Path(tmp) / "last.png"
        run([tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-ss", f"{1.5 / fps:.4f}", "-i", src,
             "-frames:v", "1", str(first)])
        run([tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-sseof", "-0.3", "-i", src,
             "-update", "1", str(last)])
        err = run([tool("ffmpeg"), "-hide_banner", "-i", str(first), "-i", str(last),
                   "-lavfi", "[1:v][0:v]scale2ref[b][a];[a][b]ssim", "-f", "null", "-"]).stderr
    m = re.search(r"All:([\d.]+)", err)
    return float(m.group(1)) if m else None


def analyze(path: Path, fmt: str | None = None, expected_duration: float | None = None,
            srt: Path | None = None, loop_strategy: str | None = None,
            scope: str = "", check_captions: bool = True) -> tuple[list[Check], dict[str, Any]]:
    meta = probe(path)
    streams = meta.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), {})
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    fmt_info = meta.get("format", {})
    width, height = int(v.get("width", 0)), int(v.get("height", 0))
    duration = float(fmt_info.get("duration") or v.get("duration") or 0)
    fps = ratio(v.get("avg_frame_rate"))
    m: dict[str, Any] = {"width": width, "height": height, "duration": round(duration, 3), "fps": round(fps, 3)}
    fmt = fmt or infer_format(width, height)
    m["format"] = fmt
    c: list[Check] = []

    container_ok = (path.suffix.lower() == ".mp4" and "mp4" in fmt_info.get("format_name", "")
                    and v.get("codec_name") == "h264" and v.get("pix_fmt") == "yuv420p"
                    and a is not None and a.get("codec_name") == "aac")
    c.append(make("media.container", container_ok,
                  f"{fmt_info.get('format_name')} / {v.get('codec_name')} {v.get('pix_fmt')} / "
                  f"{a.get('codec_name') if a else 'no audio'}", scope=scope))
    expected_dims = specs.FORMATS.get(fmt or "")
    c.append(make("media.resolution", expected_dims == (width, height), f"{width}x{height} for {fmt}",
                  [width, height], expected_dims, scope))
    r_fps = ratio(v.get("r_frame_rate"))
    cfr = fps > 0 and abs(r_fps - fps) / fps < 0.005
    lo, hi = specs.FPS_RANGE
    c.append(make("media.fps", cfr and lo <= fps <= hi, f"avg={fps:.3f} r={r_fps:.3f}", round(fps, 3),
                  [lo, hi], scope))
    band_lo, band_hi = specs.DURATION_BAND_S
    dur_ok = band_lo - specs.DURATION_TOLERANCE_S <= duration <= band_hi + specs.DURATION_TOLERANCE_S
    if expected_duration is not None:
        dur_ok = dur_ok and abs(duration - expected_duration) <= specs.DURATION_TOLERANCE_S
    c.append(make("media.duration", dur_ok, f"{duration:.2f}s (plan {expected_duration})", round(duration, 2),
                  expected_duration or [band_lo, band_hi], scope))
    atoms = top_level_atoms(path)
    faststart = "moov" in atoms and "mdat" in atoms and atoms.index("moov") < atoms.index("mdat")
    c.append(make("media.faststart", faststart, f"atoms={atoms[:6]}", scope=scope))
    size_mb = path.stat().st_size / 1e6
    m["size_mb"] = round(size_mb, 2)
    c.append(make("media.file_size", size_mb <= specs.MAX_FILE_MB, f"{size_mb:.1f} MB", round(size_mb, 1),
                  specs.MAX_FILE_MB, scope))

    if a is None:
        c.append(make("media.audio_stream", False, "no audio stream", scope=scope))
        for cid in ("audio.loudness", "audio.true_peak", "audio.lra", "audio.leading_silence", "audio.dead_air"):
            c.append(make(cid, False, "no audio stream", scope=scope))
    else:
        rate, ch = int(a.get("sample_rate", 0)), int(a.get("channels", 0))
        c.append(make("media.audio_stream", ch == 2 and rate in specs.AUDIO_RATES, f"{ch}ch @ {rate} Hz",
                      scope=scope))
        loud = loudness(path)
        m["loudness"] = loud
        i_lufs = loud.get("integrated", float("-inf"))
        c.append(make("audio.loudness", abs(i_lufs - specs.LOUDNESS_TARGET_LUFS) <= specs.LOUDNESS_TOLERANCE_LU,
                      f"{i_lufs} LUFS", i_lufs, specs.LOUDNESS_TARGET_LUFS, scope))
        tp = loud.get("true_peak", 0.0)
        c.append(make("audio.true_peak", tp <= specs.TRUE_PEAK_MAX_DBTP, f"{tp} dBTP", tp,
                      specs.TRUE_PEAK_MAX_DBTP, scope))
        lra = loud.get("lra", 0.0)
        c.append(make("audio.lra", lra <= specs.LRA_MAX_LU, f"{lra} LU", lra, specs.LRA_MAX_LU, scope))
        spans = [(s, min(e, duration)) for s, e in silences(path, specs.SILENCE_NOISE_DB, 0.1)]
        lead = next((e - s for s, e in spans if s <= 0.01), 0.0)
        m["leading_silence_s"] = round(lead, 3)
        c.append(make("audio.leading_silence", lead <= specs.LEADING_SILENCE_MAX_S, f"{lead:.2f}s",
                      round(lead, 2), specs.LEADING_SILENCE_MAX_S, scope))
        longest = max((e - s for s, e in spans), default=0.0)
        m["longest_silence_s"] = round(longest, 3)
        c.append(make("audio.dead_air", longest <= specs.DEAD_AIR_MAX_S, f"longest silence {longest:.2f}s",
                      round(longest, 2), specs.DEAD_AIR_MAX_S, scope))

    frames = frame_series(path)
    m.update(_visual(frames, fps or 30.0, duration, c, scope))

    if fmt == "vertical":
        dens = _edge_density(path)
        m["edge_density"] = {k: round(val, 2) for k, val in dens.items()}
        if dens["center"] > 0.5:
            ratio_ui = max(dens["bottom"], dens["right"]) / dens["center"]
            c.append(make("visual.ui_clutter", ratio_ui <= specs.UI_CLUTTER_MAX_RATIO, f"ratio {ratio_ui:.2f}",
                          round(ratio_ui, 2), specs.UI_CLUTTER_MAX_RATIO, scope))
        else:
            c.append(make("visual.ui_clutter", None, "center has no detail to compare", scope=scope))
    else:
        c.append(make("visual.ui_clutter", None, "not vertical", scope=scope))

    if loop_strategy == "seamless":
        try:
            ssim = _loop_ssim(path, fps or 30.0)
        except ToolError as exc:
            ssim, note = None, str(exc)
        else:
            note = f"SSIM {ssim}"
        m["loop_ssim"] = ssim
        c.append(make("visual.loop_seam", ssim is not None and ssim >= specs.LOOP_SEAM_MIN_SSIM, note,
                      ssim, specs.LOOP_SEAM_MIN_SSIM, scope))
    else:
        c.append(make("visual.loop_seam", None, f"loop strategy {loop_strategy}", scope=scope))

    if check_captions:
        c.extend(captions.validate(srt, duration, scope))
    return c, m


def _visual(frames: list[dict[str, float]], fps: float, duration: float, c: list[Check],
            scope: str) -> dict[str, Any]:
    out: dict[str, Any] = {"frames_analyzed": len(frames)}
    if not frames:
        for cid in ("visual.poster", "visual.first_motion", "visual.black_frames", "visual.static_stretch",
                    "visual.shot_length"):
            c.append(make(cid, False, "no decodable frames", scope=scope))
        return out
    f0 = frames[0]
    contrast = f0.get("YHIGH", 0) - f0.get("YLOW", 0)
    out["poster"] = {"yavg": f0.get("YAVG"), "contrast": contrast}
    c.append(make("visual.poster",
                  f0.get("YAVG", 0) >= specs.POSTER_MIN_YAVG and contrast >= specs.POSTER_MIN_CONTRAST,
                  f"frame0 YAVG={f0.get('YAVG', 0):.0f} contrast={contrast:.0f}",
                  [round(f0.get("YAVG", 0)), round(contrast)],
                  [specs.POSTER_MIN_YAVG, specs.POSTER_MIN_CONTRAST], scope))

    # Frame 1 differs from a baked poster by construction, so real motion is measured from frame 2.
    motion_t = next((f["t"] for f in frames[2:] if f.get("YDIF", 0) >= specs.MOTION_YDIF), None)
    out["first_motion_s"] = motion_t
    limit = specs.FIRST_EVENT_MAX_S + 2 / fps
    c.append(make("visual.first_motion", motion_t is not None and motion_t <= limit,
                  f"first motion at {motion_t}s", motion_t, round(limit, 3), scope))

    black = [f for f in frames if f.get("YAVG", 255) < specs.BLACK_YAVG]
    in_hook = sum(1 for f in black if f["t"] < specs.HOOK_WINDOW_S)
    frac = len(black) / len(frames)
    out["black_fraction"] = round(frac, 4)
    c.append(make("visual.black_frames", in_hook == 0 and frac <= specs.BLACK_MAX_FRACTION,
                  f"{len(black)} black frames ({frac:.1%}), {in_hook} in hook", round(frac, 4),
                  specs.BLACK_MAX_FRACTION, scope))

    longest = run_len = 0
    for f in frames[1:]:
        run_len = run_len + 1 if f.get("YDIF", 0) < specs.MOTION_YDIF else 0
        longest = max(longest, run_len)
    stretch = longest / fps
    out["longest_static_s"] = round(stretch, 2)
    c.append(make("visual.static_stretch", stretch <= specs.STATIC_MAX_STRETCH_S, f"{stretch:.2f}s frozen",
                  round(stretch, 2), specs.STATIC_MAX_STRETCH_S, scope))

    cuts = [f["t"] for f in frames[2:] if f.get("score", 0) >= specs.CUT_SCORE]
    avg_shot = duration / (len(cuts) + 1) if duration else 0
    out["cuts"] = len(cuts)
    out["avg_shot_s"] = round(avg_shot, 2)
    lo, hi = specs.SHOT_LENGTH_RANGE_S
    c.append(make("visual.shot_length", lo <= avg_shot <= hi, f"{len(cuts)} cuts, avg shot {avg_shot:.2f}s",
                  round(avg_shot, 2), [lo, hi], scope))
    return out
