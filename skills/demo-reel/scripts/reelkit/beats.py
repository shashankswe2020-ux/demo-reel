"""Beat grid, downbeats, per-band onsets, and loudness envelopes for any soundtrack (stdlib + FFmpeg)."""

from __future__ import annotations

import math
import statistics
from array import array
from pathlib import Path
from typing import Any

from .ffmpeg import ToolError, media_path, run, tool

SR = 11025
HOP = 64  # ~5.8 ms per analysis frame
WIN = 256
BANDS = {"low": "lowpass=f=150", "mid": "highpass=f=200,lowpass=f=2500", "high": "highpass=f=5000"}
BPM_RANGE = (70.0, 180.0)
ENV_HOP_S = 0.05


def _decode(src: str, af: str | None) -> array:
    args = [tool("ffmpeg"), "-hide_banner", "-loglevel", "error", "-i", src, "-vn", "-ac", "1", "-ar", str(SR)]
    if af:
        args += ["-af", af]
    raw = run(args + ["-f", "s16le", "-"], binary=True).stdout
    pcm = array("h")
    pcm.frombytes(raw[: len(raw) // 2 * 2])
    return pcm


def _energy(pcm: array) -> list[float]:
    n = max(0, (len(pcm) - WIN) // HOP + 1)
    sq = [x * x for x in pcm]
    acc, out = sum(sq[:WIN]), []
    for i in range(n):
        out.append(math.log1p(acc / WIN / 1e4))
        j = i * HOP
        if j + WIN + HOP <= len(sq):
            acc += sum(sq[j + WIN:j + WIN + HOP]) - sum(sq[j:j + HOP])
    return out


def _novelty(energy: list[float]) -> list[float]:
    return [0.0] + [max(0.0, b - a) for a, b in zip(energy, energy[1:])]


def _frame_t(i: float) -> float:
    # Novelty at frame i peaks as an attack enters the window's leading edge.
    return (i * HOP + WIN) / SR


def _peaks(nov: list[float], min_gap_s: float = 0.07, k: float = 1.5) -> list[int]:
    if not nov:
        return []
    mean, sd = statistics.fmean(nov), statistics.pstdev(nov)
    thresh, gap = mean + k * sd, int(min_gap_s * SR / HOP)
    peaks: list[int] = []
    for i in range(1, len(nov) - 1):
        if nov[i] >= thresh and nov[i] >= nov[i - 1] and nov[i] > nov[i + 1]:
            if peaks and i - peaks[-1] < gap:
                if nov[i] > nov[peaks[-1]]:
                    peaks[-1] = i
            else:
                peaks.append(i)
    return peaks


def _tempo_period(nov: list[float]) -> float:
    lo = int(60.0 / BPM_RANGE[1] * SR / HOP)
    hi = int(60.0 / BPM_RANGE[0] * SR / HOP) + 1
    mean = statistics.fmean(nov)
    x = [v - mean for v in nov]
    ac = {lag: sum(a * b for a, b in zip(x, x[lag:])) / (len(x) - lag)
          for lag in range(lo, min(2 * hi, len(x) // 2) + 1)}
    scores = {}
    for lag in range(lo, min(hi, len(x) // 2) + 1):
        bpm = 60.0 * SR / HOP / lag
        # A real beat period also repeats at twice the lag (bars of half-time kicks); a mild prior toward
        # 120 BPM settles the remaining half/double-tempo ambiguity.
        scores[lag] = ((ac[lag] + 0.5 * ac.get(2 * lag, 0.0))
                       * math.exp(-0.5 * (math.log2(bpm / 120.0) / 0.9) ** 2))
    if not scores:
        raise ToolError("audio too short to estimate tempo")
    best = max(scores, key=scores.get)
    a, b, c = scores.get(best - 1, 0.0), scores[best], scores.get(best + 1, 0.0)
    denom = a - 2 * b + c
    return best + (0.5 * (a - c) / denom if denom else 0.0)


def _fit_grid(nov: list[float], period: float, onsets: list[int]) -> tuple[float, float]:
    """Best phase on the novelty curve, then least-squares refine period/offset on nearby onsets."""
    def comb(phase: float) -> float:
        total, k = 0.0, 0
        while (i := int(round(phase + k * period))) < len(nov):
            total += nov[i]
            k += 1
        return total

    phase = max((p for p in range(int(period) + 1)), key=comb)
    pairs = []
    for k in range(int((len(nov) - phase) / period) + 1):
        grid = phase + k * period
        near = [o for o in onsets if abs(o - grid) <= period / 4]
        if near:
            pairs.append((k, min(near, key=lambda o: abs(o - grid))))
    if len(pairs) >= 4:
        ks, fs = [p[0] for p in pairs], [p[1] for p in pairs]
        mk, mf = statistics.fmean(ks), statistics.fmean(fs)
        var = sum((k - mk) ** 2 for k in ks)
        if var:
            period = sum((k - mk) * (f - mf) for k, f in zip(ks, fs)) / var
            phase = mf - period * mk
    return period, phase


def _envelope(pcm: array, duration: float) -> list[float]:
    step = int(ENV_HOP_S * SR)
    vals = []
    for i in range(int(duration / ENV_HOP_S)):
        seg = pcm[i * step:(i + 1) * step]
        vals.append(math.sqrt(sum(x * x for x in seg) / len(seg)) if seg else 0.0)
    top = max(vals, default=0.0) or 1.0
    return [round(v / top, 3) for v in vals]


def analyze_audio(path: Path, bpm: float | None = None) -> dict[str, Any]:
    src = media_path(path)
    full = _decode(src, None)
    duration = len(full) / SR
    bands = {name: _decode(src, af) for name, af in BANDS.items()}
    low_energy = _energy(bands["low"])
    band_nov = {name: _novelty(low_energy if name == "low" else _energy(pcm)) for name, pcm in bands.items()}
    n = min(len(v) for v in band_nov.values())
    if n < 8:
        raise ToolError("audio too short to analyze")
    norm = {}
    for name, nov in band_nov.items():
        top = max(nov[:n]) or 1.0
        norm[name] = [v / top for v in nov[:n]]
    combined = [norm["low"][i] + norm["mid"][i] + 0.5 * norm["high"][i] for i in range(n)]
    onsets = {name: _peaks(nov) for name, nov in norm.items()}
    all_onsets = _peaks(combined)

    period = (60.0 * SR / HOP / bpm) if bpm else _tempo_period(combined)
    period, phase = _fit_grid(combined, period, all_onsets)
    if bpm:
        period = 60.0 * SR / HOP / bpm
    while phase - period >= -period / 4:
        phase -= period
    frames = []
    k = 0
    while (f := phase + k * period) < n:
        if -period / 4 <= _frame_t(f) * SR / HOP and _frame_t(f) <= duration:
            frames.append(f)
        k += 1
    beats = [round(max(0.0, _frame_t(f)), 3) for f in frames]
    # Downbeat = the beat-in-bar position with the most low end over the beat (kick plus a new bass note).
    bar_score = [0.0] * 4
    for idx, f in enumerate(frames):
        i = max(0, int(round(f)))
        seg = [math.expm1(e) for e in low_energy[i:i + int(period)]]
        bar_score[idx % 4] += sum(seg) / len(seg) if seg else 0.0
    first = max(range(4), key=lambda j: bar_score[j])
    return {
        "schema": "demo-reel/audio-events@1",
        "duration": round(duration, 3),
        "bpm": round(60.0 * SR / HOP / period, 2),
        "offset_s": beats[0] if beats else 0.0,
        "beats": beats,
        "downbeats": beats[first::4],
        "onsets": {name: [round(_frame_t(i), 3) for i in idx] for name, idx in onsets.items()},
        "env": {"hop_s": ENV_HOP_S, "rms": _envelope(full, duration),
                **{name: _envelope(pcm, duration) for name, pcm in bands.items()}},
    }
