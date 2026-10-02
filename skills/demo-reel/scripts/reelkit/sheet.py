"""Contact sheets for review: evenly spaced frames, or the frame either side of every detected cut."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from . import specs
from .ffmpeg import ToolError, media_path, probe, ratio, run, tool
from .media_qa import frame_series

MAX_TILES = 48


def contact_sheet(video: Path, out: Path, *, cuts: bool = False, n: int = 12, cols: int = 4,
                  width: int = 360) -> dict[str, Any]:
    src = media_path(video)
    v = next((s for s in probe(src).get("streams", []) if s.get("codec_type") == "video"), {})
    fps = ratio(v.get("avg_frame_rate")) or 30.0
    if cuts:
        # Same detector as visual.shot_length, so the sheet shows exactly the cuts the gate counts.
        frames = frame_series(src)
        at = [round(f["t"] * fps) for f in frames[2:] if f.get("score", 0) >= specs.CUT_SCORE]
        picks = sorted({i for c in at for i in (c - 1, c) if i >= 0})
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
    return {"out": str(out), "mode": "cuts" if cuts else "even", "cols": cols, "rows": rows,
            "times": [round(i / fps, 3) for i in picks]}
