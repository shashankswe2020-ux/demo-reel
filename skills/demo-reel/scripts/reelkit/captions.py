from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from . import specs
from .checks import Check, make

_TS = re.compile(r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})")


@dataclass
class Cue:
    start: float
    end: float
    lines: list[str]


def _seconds(ts: str) -> float:
    m = _TS.fullmatch(ts.strip())
    if not m:
        raise ValueError(f"bad timestamp: {ts!r}")
    h, mi, s, ms = (int(g) for g in m.groups())
    return h * 3600 + mi * 60 + s + ms / 1000


def _stamp(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3_600_000:02d}:{ms // 60_000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def parse_srt(text: str) -> list[Cue]:
    cues = []
    for block in re.split(r"\r?\n\s*\r?\n", text.strip()):
        rows = [r for r in block.splitlines() if r.strip()]
        if not rows:
            continue
        if "-->" not in rows[0]:
            rows = rows[1:]
        if not rows or "-->" not in rows[0]:
            raise ValueError(f"cue without timing: {block[:60]!r}")
        a, b = rows[0].split("-->", 1)
        cues.append(Cue(_seconds(a), _seconds(b.split()[0]), rows[1:]))
    return cues


def wrap(text: str, width: int = specs.CAPTION_MAX_LINE_CHARS) -> list[str]:
    lines: list[str] = []
    for word in text.split():
        if lines and len(lines[-1]) + 1 + len(word) <= width:
            lines[-1] += " " + word
        else:
            lines.append(word)
    return lines


def render_srt(cues: list[Cue]) -> str:
    return "\n".join(f"{i}\n{_stamp(c.start)} --> {_stamp(c.end)}\n" + "\n".join(c.lines) + "\n"
                     for i, c in enumerate(cues, 1))


def validate(path: Path | None, duration: float | None, scope: str = "") -> list[Check]:
    if path is None or not path.is_file():
        msg = f"missing sidecar {path}" if path else "no sidecar provided"
        return [make("captions.present", False, msg, scope=scope),
                make("captions.timing", None, "skipped", scope=scope),
                make("captions.readability", None, "skipped", scope=scope)]
    try:
        cues = parse_srt(path.read_text(encoding="utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as exc:
        return [make("captions.present", False, str(exc), scope=scope),
                make("captions.timing", None, "skipped", scope=scope),
                make("captions.readability", None, "skipped", scope=scope)]
    out = [make("captions.present", bool(cues), f"{len(cues)} cues", len(cues), ">=1", scope)]

    timing_issues = []
    for i, c in enumerate(cues):
        if c.end <= c.start:
            timing_issues.append(f"cue {i + 1} ends before it starts")
        if i and c.start < cues[i - 1].end - 1e-3:
            timing_issues.append(f"cue {i + 1} overlaps cue {i}")
        if duration is not None and c.end > duration + specs.DURATION_TOLERANCE_S:
            timing_issues.append(f"cue {i + 1} ends after the video ({c.end:.2f}s > {duration:.2f}s)")
    out.append(make("captions.timing", not timing_issues, "; ".join(timing_issues[:5]) or "ok",
                    len(timing_issues), 0, scope))

    read_issues = []
    for i, c in enumerate(cues):
        span = c.end - c.start
        chars = sum(len(line) for line in c.lines)
        if len(c.lines) > specs.CAPTION_MAX_LINES:
            read_issues.append(f"cue {i + 1}: {len(c.lines)} lines")
        if any(len(line) > specs.CAPTION_MAX_LINE_CHARS for line in c.lines):
            read_issues.append(f"cue {i + 1}: line over {specs.CAPTION_MAX_LINE_CHARS} chars")
        if span < specs.CAPTION_MIN_S:
            read_issues.append(f"cue {i + 1}: {span:.2f}s on screen")
        elif span > 0 and chars / span > specs.CAPTION_MAX_CPS:
            read_issues.append(f"cue {i + 1}: {chars / span:.1f} chars/s")
    out.append(make("captions.readability", not read_issues, "; ".join(read_issues[:5]) or "ok",
                    len(read_issues), 0, scope))
    return out
