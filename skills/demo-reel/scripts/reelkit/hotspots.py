"""Mine the strongest windows of a long screen recording (yt-clipper's weighted-ensemble idea, local signals only)."""

from __future__ import annotations

from bisect import bisect_left
from pathlib import Path
from typing import Any

from . import specs
from .ffmpeg import momentary_loudness, probe
from .media_qa import frame_series

WEIGHTS = {"motion": 0.35, "cuts": 0.20, "loudness": 0.30, "hook": 0.15}


def _normalize(values: list[float]) -> list[float]:
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return [0.5] * len(values)
    return [(v - lo) / (hi - lo) for v in values]


class _Series:
    """Prefix sums so each window mean is O(log n) on long recordings."""

    def __init__(self, points: list[tuple[float, float]]):
        points = sorted(points)
        self.times = [t for t, _ in points]
        self.prefix = [0.0]
        for _, v in points:
            self.prefix.append(self.prefix[-1] + v)

    def mean(self, a: float, b: float) -> float:
        i, j = bisect_left(self.times, a), bisect_left(self.times, b)
        return (self.prefix[j] - self.prefix[i]) / (j - i) if j > i else 0.0


def hotspots(path: Path, window: float = 20.0, top: int = 3, min_gap: float = 5.0,
             step: float = 0.5) -> list[dict[str, Any]]:
    meta = probe(path)
    duration = float(meta.get("format", {}).get("duration") or 0)
    if duration <= window:
        return [{"start": 0.0, "end": round(duration, 2), "score": 1.0, "signals": {}}]
    frames = frame_series(path)
    motion = _Series([(f["t"], f.get("YDIF", 0.0)) for f in frames])
    cuts = _Series([(f["t"], 1.0 if f.get("score", 0) >= specs.CUT_SCORE else 0.0) for f in frames])
    has_audio = any(s.get("codec_type") == "audio" for s in meta.get("streams", []))
    loud = _Series([(t, max(-70.0, v)) for t, v in momentary_loudness(path)] if has_audio else [])

    starts = [i * step for i in range(int((duration - window) / step) + 1)]
    raw = {
        "motion": [motion.mean(s, s + window) for s in starts],
        "cuts": [cuts.mean(s, s + window) for s in starts],
        "loudness": [loud.mean(s, s + window) for s in starts],
        "hook": [motion.mean(s, s + specs.HOOK_WINDOW_S) for s in starts],
    }
    norm = {k: _normalize(v) for k, v in raw.items()}
    scored = [(sum(WEIGHTS[k] * norm[k][i] for k in WEIGHTS), i) for i in range(len(starts))]
    scored.sort(reverse=True)

    picked: list[dict[str, Any]] = []
    for score, i in scored:
        s = starts[i]
        if all(s + window + min_gap <= p["start"] or s >= p["end"] + min_gap for p in picked):
            picked.append({"start": round(s, 2), "end": round(s + window, 2), "score": round(score, 3),
                           "signals": {k: round(norm[k][i], 3) for k in WEIGHTS}})
            if len(picked) == top:
                break
    return picked
