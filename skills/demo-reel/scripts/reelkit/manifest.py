"""Content-addressed provenance for reel inputs, tools, and deliverables."""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from .ffmpeg import ToolError, run, tool


def _hash(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"bytes": path.stat().st_size, "sha256": digest.hexdigest()}


def _version(command: list[str]) -> str | None:
    try:
        output = run(command).stdout.strip()
    except (ToolError, OSError):
        return None
    return output.splitlines()[0] if output else None


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _resolve_declared(value: str, project_root: Path, plan_dir: Path) -> Path | None:
    for root in (project_root, plan_dir):
        candidate = (root / value).resolve()
        if _inside(candidate, root) and candidate.is_file():
            return candidate
    return None


def _label(path: Path, plan_dir: Path, project_root: Path) -> str:
    if _inside(path, plan_dir):
        return path.relative_to(plan_dir).as_posix()
    if _inside(path, project_root):
        return "project/" + path.relative_to(project_root).as_posix()
    return path.name


def build_manifest(plan_path: Path, project_root: Path, artifact_roots: list[Path]) -> dict[str, Any]:
    plan_path = plan_path.resolve()
    plan_dir = plan_path.parent
    project_root = project_root.resolve()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    inputs: dict[str, Path] = {_label(plan_path, plan_dir, project_root): plan_path}
    warnings: list[str] = []

    treatment = plan.get("treatment") or {}
    declared = [str(treatment.get("file") or "")]
    declared += [str((claim.get("evidence") or {}).get("file") or "") for claim in plan.get("claims", [])]
    declared += [str(source) for scene in plan.get("scenes", []) for source in scene.get("sources", [])]
    for value in declared:
        if not value:
            continue
        resolved = _resolve_declared(value, project_root, plan_dir)
        if resolved:
            inputs[_label(resolved, plan_dir, project_root)] = resolved
        else:
            warnings.append(f"declared source not found: {value}")

    for optional in (plan_dir / "work" / "sources.md", plan_dir / "work" / "package-lock.json",
                     plan_dir / "work" / "audio-events.json"):
        if optional.is_file():
            inputs[_label(optional, plan_dir, project_root)] = optional

    artifacts: dict[str, Path] = {}
    for root in {path.resolve() for path in artifact_roots}:
        if not root.is_dir():
            warnings.append(f"artifact root not found: {root}")
            continue
        for path in root.rglob("*"):
            if not path.is_file() or "work" in path.relative_to(root).parts or path.name == "artifact-manifest.json":
                continue
            artifacts[f"{root.name}/{path.relative_to(root).as_posix()}"] = path

    git_commit = _version(["git", "-C", str(project_root), "rev-parse", "HEAD"]) if shutil.which("git") else None
    git_status = _version(["git", "-C", str(project_root), "status", "--porcelain"]) if git_commit else None
    tools = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "ffmpeg": _version([tool("ffmpeg"), "-version"]),
        "ffprobe": _version([tool("ffprobe"), "-version"]),
        "node": _version([shutil.which("node"), "--version"]) if shutil.which("node") else None,
    }
    lock = plan_dir / "work" / "package-lock.json"
    if lock.is_file():
        package_data = json.loads(lock.read_text(encoding="utf-8"))
        tools["playwright"] = ((package_data.get("packages") or {}).get("node_modules/playwright") or {}).get("version")

    return {
        "schema": "demo-reel/manifest@1",
        "python_implementation": sys.implementation.name,
        "project": {"git_commit": git_commit, "dirty": bool(git_status)},
        "tools": tools,
        "inputs": {label: _hash(path) for label, path in sorted(inputs.items())},
        "artifacts": {label: _hash(path) for label, path in sorted(artifacts.items())},
        "warnings": sorted(set(warnings)),
    }


def write_manifest(plan_path: Path, project_root: Path, artifact_roots: list[Path], out: Path) -> Path:
    data = build_manifest(plan_path, project_root, artifact_roots)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return out