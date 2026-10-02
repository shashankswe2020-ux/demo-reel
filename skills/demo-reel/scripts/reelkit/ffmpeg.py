"""Thin, shell-free wrappers around ffmpeg/ffprobe. Arguments are always lists."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


class ToolError(RuntimeError):
    pass


def tool(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise ToolError(f"{name} not found on PATH")
    return path


def run(args: list[str], cwd: Path | None = None, binary: bool = False) -> subprocess.CompletedProcess:
    if binary:
        proc = subprocess.run(args, capture_output=True, cwd=cwd, check=False)
        err = proc.stderr.decode(errors="replace")
    else:
        proc = subprocess.run(args, capture_output=True, text=True, errors="replace", cwd=cwd, check=False)
        err = proc.stderr
    if proc.returncode != 0:
        raise ToolError(f"{Path(args[0]).name} exited {proc.returncode}: {err.strip()[-1500:]}")
    return proc


def media_path(path: str | Path) -> str:
    """Absolute path so ffmpeg never reads a leading '-' as an option or a 'proto:' as a protocol."""
    p = Path(path).resolve()
    if not p.is_file():
        raise ToolError(f"no such file: {p}")
    return str(p)


def probe(path: str | Path) -> dict[str, Any]:
    out = run([tool("ffprobe"), "-v", "error", "-print_format", "json",
               "-show_format", "-show_streams", media_path(path)]).stdout
    return json.loads(out)


def ratio(value: str | None) -> float:
    if not value or value in ("0/0", "N/A"):
        return 0.0
    if "/" in value:
        num, den = value.split("/", 1)
        return float(num) / float(den) if float(den) else 0.0
    return float(value)


def frame_metadata(path: str | Path, vf: str) -> list[dict[str, float]]:
    """Run a video filter chain ending in metadata=print:file=- and return one dict per frame."""
    out = run([tool("ffmpeg"), "-hide_banner", "-nostats", "-i", media_path(path), "-an",
               "-vf", vf, "-f", "null", "-"]).stdout
    return parse_metadata(out)


def parse_metadata(text: str) -> list[dict[str, float]]:
    frames: list[dict[str, float]] = []
    for line in text.splitlines():
        if line.startswith("frame:"):
            m = re.search(r"pts_time:(\S+)", line)
            frames.append({"t": float(m.group(1)) if m else float(len(frames))})
        elif frames and line.startswith("lavfi.") and "=" in line:
            key, _, val = line.partition("=")
            try:
                frames[-1][key.rsplit(".", 1)[-1]] = float(val)
            except ValueError:
                pass
    return frames


def loudness(path: str | Path) -> dict[str, float]:
    err = run([tool("ffmpeg"), "-hide_banner", "-nostats", "-i", media_path(path), "-vn",
               "-af", "ebur128=peak=true:framelog=quiet", "-f", "null", "-"]).stderr
    summary = err[err.rfind("Summary:"):] if "Summary:" in err else err
    result: dict[str, float] = {}
    for key, pattern in (("integrated", r"I:\s+(-?[\d.]+|-inf) LUFS"),
                         ("lra", r"LRA:\s+(-?[\d.]+) LU"),
                         ("true_peak", r"True peak:\s+Peak:\s+(-?[\d.]+|-inf) dBFS")):
        m = re.search(pattern, summary, re.S)
        if m:
            result[key] = float(m.group(1))
    return result


def momentary_loudness(path: str | Path) -> list[tuple[float, float]]:
    out = run([tool("ffmpeg"), "-hide_banner", "-nostats", "-i", media_path(path), "-vn",
               "-af", "ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-",
               "-f", "null", "-"]).stdout
    series = []
    for frame in parse_metadata(out):
        if "M" in frame:
            series.append((frame["t"], frame["M"]))
    return series


def silences(path: str | Path, noise_db: float, min_s: float) -> list[tuple[float, float]]:
    err = run([tool("ffmpeg"), "-hide_banner", "-nostats", "-i", media_path(path), "-vn",
               "-af", f"silencedetect=noise={noise_db}dB:d={min_s}", "-f", "null", "-"]).stderr
    spans: list[tuple[float, float]] = []
    start: float | None = None
    for line in err.splitlines():
        if m := re.search(r"silence_start:\s*(-?[\d.]+)", line):
            start = max(0.0, float(m.group(1)))
        elif (m := re.search(r"silence_end:\s*([\d.]+)", line)) and start is not None:
            spans.append((start, float(m.group(1))))
            start = None
    if start is not None:
        spans.append((start, float("inf")))
    return spans


def top_level_atoms(path: str | Path, limit: int = 64) -> list[str]:
    atoms: list[str] = []
    with open(media_path(path), "rb") as fh:
        fh.seek(0, 2)
        size = fh.tell()
        pos = 0
        while pos + 8 <= size and len(atoms) < limit:
            fh.seek(pos)
            header = fh.read(8)
            box = int.from_bytes(header[:4], "big")
            atoms.append(header[4:8].decode("latin-1"))
            if box == 1:
                box = int.from_bytes(fh.read(8), "big")
            elif box == 0:
                break
            if box < 8:
                break
            pos += box
    return atoms
