"""Contact sheets for review: evenly spaced frames, or the frame either side of every detected cut."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from . import specs
from .ffmpeg import ToolError, media_path, probe, ratio, run, tool
from .media_qa import frame_series

MAX_TILES = 48


def _risk_picks(frames: list[dict[str, float]], n: int) -> tuple[list[int], dict[int, list[str]]]:
    """Pick review candidates for darkness, weak contrast, abrupt change, and static runs."""
    if not frames:
        return [], {}
    reasons: dict[int, list[str]] = {}

    def add(index: int, reason: str) -> None:
        reasons.setdefault(index, []).append(reason)

    quota = max(1, math.ceil(n / 4))
    for index in sorted(range(len(frames)), key=lambda i: frames[i].get("YAVG", 255))[:quota]:
        add(index, "dark")
    for index in sorted(range(len(frames)),
                        key=lambda i: frames[i].get("YHIGH", 0) - frames[i].get("YLOW", 0))[:quota]:
        add(index, "low-contrast")
    abrupt = [i for i in range(2, len(frames)) if frames[i].get("score", 0) < specs.CUT_SCORE]
    for index in sorted(abrupt, key=lambda i: frames[i].get("YDIF", 0), reverse=True)[:quota]:
        add(index, "abrupt-change")

    runs: list[tuple[int, int]] = []
    start = None
    for index in range(2, len(frames)):
        still = frames[index].get("YDIF", 0) < specs.MOTION_YDIF
        if still and start is None:
            start = index
        elif not still and start is not None:
            runs.append((start, index - 1))
            start = None
    if start is not None:
        runs.append((start, len(frames) - 1))
    for lo, hi in sorted(runs, key=lambda run: run[1] - run[0], reverse=True)[:quota]:
        add((lo + hi) // 2, "static-run")

    if len(reasons) < n:
        # Rank remaining frames by combined percentile risk so the sheet still fills without clustering one metric.
        ranks = {i: 0 for i in range(len(frames))}
        metrics = [
            sorted(range(len(frames)), key=lambda i: frames[i].get("YAVG", 255)),
            sorted(range(len(frames)), key=lambda i: frames[i].get("YHIGH", 0) - frames[i].get("YLOW", 0)),
            sorted(range(len(frames)), key=lambda i: frames[i].get("YDIF", 0), reverse=True),
        ]
        for order in metrics:
            for rank, index in enumerate(order):
                ranks[index] += rank
        for index in sorted(ranks, key=ranks.get):
            if index not in reasons:
                add(index, "combined-risk")
            if len(reasons) >= n:
                break
    picks = sorted(reasons, key=lambda i: (-len(reasons[i]), i))[:n]
    return sorted(picks), reasons


def contact_sheet(video: Path, out: Path, *, cuts: bool = False, weakest: bool = False,
                  n: int = 12, cols: int = 4, width: int = 360) -> dict[str, Any]:
    if cuts and weakest:
        raise ToolError("choose either --cuts or --weakest")
    src = media_path(video)
    v = next((s for s in probe(src).get("streams", []) if s.get("codec_type") == "video"), {})
    fps = ratio(v.get("avg_frame_rate")) or 30.0
    reasons: dict[int, list[str]] = {}
    if cuts:
        # Same detector as visual.shot_length, so the sheet shows exactly the cuts the gate counts.
        frames = frame_series(src)
        at = [round(f["t"] * fps) for f in frames[2:] if f.get("score", 0) >= specs.CUT_SCORE]
        picks = sorted({i for c in at for i in (c - 1, c) if i >= 0})
    elif weakest:
        frames = frame_series(src)
        picks, reasons = _risk_picks(frames, n)
    else:
        total = int(v.get("nb_frames") or 0) or round(float(v.get("duration") or 0) * fps)
        picks = sorted({min(total - 1, round((k + 0.5) * total / n)) for k in range(n)}) if total > 0 else []
    if not picks:
        raise ToolError("no frames to sheet" + (" (no cuts detected)" if cuts else ""))
    picks = picks[:MAX_TILES]
    cols = max(1, min(cols, len(picks)))
    rows = math.ceil(len(picks) / cols)
    select = "+".join(f"eq(n\\,{i})" for i in picks)
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    run([tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-an",
         "-vf", f"select='{select}',scale={width}:-2,tile={cols}x{rows}:padding=6:margin=6:color=0x202020",
         "-fps_mode", "passthrough", "-frames:v", "1", str(out)])
    mode = "cuts" if cuts else "weakest" if weakest else "even"
    result = {"out": str(out), "mode": mode, "cols": cols, "rows": rows,
              "times": [round(i / fps, 3) for i in picks]}
    if weakest:
        result["risks"] = [{"time": round(i / fps, 3), "reasons": reasons[i]} for i in picks]
    return result
