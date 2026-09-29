"""Finishing pass: platform framing, two-pass loudness normalization, poster-as-frame-0, faststart."""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path

from . import specs
from .ffmpeg import ToolError, media_path, probe, run, tool

LOUDNORM_TP = -1.5  # headroom so AAC encoding stays under the -1 dBTP gate
# loudnorm's linear mode cannot cap peaks when it adds gain; this limiter (-2.5 dBFS) does.
PEAK_LIMITER = "alimiter=limit=0.75:attack=1:release=50:level=disabled"
# Sub-30 Hz energy is inaudible on phones but makes AAC overshoot true peak by up to 4 dB after limiting.
SUBSONIC_CUT = "highpass=f=30:poles=2"
# Browser/PNG/JPEG sources arrive full-range; platforms expect limited-range yuv420p.
TV_RANGE = "scale=out_range=tv,format=yuv420p"


def _video_graph(fmt: str, fit: str, fps: int, focus: tuple[float, float]) -> str:
    w, h = specs.FORMATS[fmt]
    tail = f"setsar=1,fps={fps},{TV_RANGE}[v]"
    if fit == "crop":
        fx, fy = (min(1.0, max(0.0, f)) for f in focus)
        return (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h}:(iw-{w})*{fx}:(ih-{h})*{fy},{tail}")
    return (f"[0:v]split=2[bg][fg];"
            f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=24:2,"
            f"eq=brightness=-0.08[bgb];"
            f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2[fgs];"
            f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,{tail}")


def _measure_loudness(src: str) -> dict[str, str]:
    err = run([tool("ffmpeg"), "-hide_banner", "-nostats", "-i", src, "-vn", "-af",
               f"{SUBSONIC_CUT},loudnorm=I={specs.LOUDNESS_TARGET_LUFS}:TP={LOUDNORM_TP}:LRA=11:print_format=json",
               "-f", "null", "-"]).stderr
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S)
    if not m:
        raise ToolError("loudnorm did not report measurements")
    return json.loads(m.group(0))


def finish(src_path: Path, out_path: Path, fmt: str, *, poster_t: float | None = None, fit: str = "blur",
           focus: tuple[float, float] = (0.5, 0.5), fps: int = 30, duration: float | None = None) -> Path:
    if fmt not in specs.FORMATS:
        raise ToolError(f"unknown format {fmt!r}; choose from {sorted(specs.FORMATS)}")
    src = media_path(src_path)
    has_audio = any(s.get("codec_type") == "audio" for s in probe(src).get("streams", []))
    out_path = out_path.resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        staged = Path(tmp) / "staged.mp4"
        args = [tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", src]
        if not has_audio:
            args += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        args += ["-filter_complex", _video_graph(fmt, fit, fps, focus), "-map", "[v]"]
        if has_audio:
            ln = _measure_loudness(src)
            args += ["-map", "0:a:0", "-af",
                     f"{SUBSONIC_CUT},loudnorm=I={specs.LOUDNESS_TARGET_LUFS}:TP={LOUDNORM_TP}:LRA=11:"
                     f"measured_I={ln['input_i']}:measured_TP={ln['input_tp']}:measured_LRA={ln['input_lra']}:"
                     f"measured_thresh={ln['input_thresh']}:offset={ln['target_offset']}:linear=true,"
                     f"aresample=48000,{PEAK_LIMITER}"]
        else:
            args += ["-map", "1:a:0", "-shortest"]
        if duration:
            args += ["-t", f"{duration:.3f}"]
        args += ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-color_range", "tv",
                 "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                 "-movflags", "+faststart", str(staged)]
        run(args)

        if poster_t is None:
            shutil.move(staged, out_path)
            return out_path

        poster = out_path.with_suffix(".jpg")
        run([tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{poster_t:.3f}",
             "-i", str(staged), "-frames:v", "1", "-q:v", "2", str(poster)])
        # Replace only frame 0 so duration, frame count, and audio sync are untouched.
        run([tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", str(staged), "-i", str(poster),
             "-filter_complex", f"[0:v][1:v]overlay=0:0:enable='eq(n,0)',{TV_RANGE}[v]",
             "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
             "-profile:v", "high", "-color_range", "tv", "-c:a", "copy", "-movflags", "+faststart", str(out_path)])
    return out_path
