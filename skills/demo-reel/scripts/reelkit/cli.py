from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import captions, experiment, specs
from .checks import CATALOG, Check, make, score
from .ffmpeg import ToolError
from .finish import finish
from .hotspots import hotspots
from .media_qa import analyze
from .plan_lint import lint, load, variant_cues


def _print_checks(checks: list[Check]) -> None:
    mark = {True: "PASS", False: "FAIL", None: "SKIP"}
    for c in checks:
        scope = f" [{c.scope}]" if c.scope else ""
        print(f"  {mark[c.passed]:4}  {c.severity:7} {c.id}{scope}: {c.message}")


def _project_root(plan: dict[str, Any], plan_path: Path, override: str | None) -> Path:
    if override:
        return Path(override).resolve()
    return (plan_path.parent / plan.get("project", {}).get("root", ".")).resolve()


def cmd_lint(ns: argparse.Namespace) -> int:
    plan_path = Path(ns.plan).resolve()
    plan = load(plan_path)
    checks, info = lint(plan, _project_root(plan, plan_path, ns.project), plan_path.parent)
    _print_checks(checks)
    if info.get("hook_scores"):
        print("\nHook leaderboard:", ", ".join(f"{k}={v}" for k, v in info["hook_scores"].items()))
    s = score(checks)
    print(f"\nplan checks: {s['passed']} passed, {s['failed']} failed; blockers: {s['blockers'] or 'none'}")
    return 0 if not s["blockers"] and not s["failed"] else 2


def cmd_qa(ns: argparse.Namespace) -> int:
    path = Path(ns.video)
    srt = Path(ns.srt) if ns.srt else path.with_suffix(".srt")
    checks, measured = analyze(path, ns.format, ns.duration, srt if srt.exists() else None, ns.loop)
    _print_checks(checks)
    s = score(checks)
    print(json.dumps({"measured": measured, "score": s}, indent=2, default=str))
    return 0 if s["shippable"] else 2


def cmd_finish(ns: argparse.Namespace) -> int:
    focus = (ns.focus_x, ns.focus_y)
    out = finish(Path(ns.input), Path(ns.out), ns.format, poster_t=ns.poster_t, fit=ns.fit, focus=focus,
                 fps=ns.fps, duration=ns.duration)
    print(out)
    return 0


def cmd_captions(ns: argparse.Namespace) -> int:
    plan = load(Path(ns.plan))
    text = captions.render_srt(variant_cues(plan, ns.variant))
    if ns.out:
        Path(ns.out).write_text(text, encoding="utf-8")
        print(ns.out)
    else:
        print(text)
    return 0


def cmd_hotspots(ns: argparse.Namespace) -> int:
    print(json.dumps(hotspots(Path(ns.video), ns.window, ns.top, ns.min_gap), indent=2))
    return 0


def cmd_learn(ns: argparse.Namespace) -> int:
    print(json.dumps(experiment.evaluate(experiment.load(Path(ns.metrics)), ns.objective), indent=2))
    return 0


def cmd_gates(ns: argparse.Namespace) -> int:
    if ns.count:
        print(len(CATALOG))
        return 0
    for cid, (cat, sev, desc) in CATALOG.items():
        print(f"{cid:28} {cat:12} {sev:7} {desc}")
    by_sev = {s: sum(1 for v in CATALOG.values() if v[1] == s) for s in specs.SEVERITY_WEIGHTS}
    print(f"\n{len(CATALOG)} machine-verified gates: {by_sev}")
    return 0


def cmd_compare(ns: argparse.Namespace) -> int:
    rows = []
    for video in ns.videos:
        path = Path(video)
        srt = path.with_suffix(".srt")
        checks, m = analyze(path, None, None, srt if srt.exists() else None, None, path.name)
        s = score(checks)
        rows.append((path.name, s, m, checks))
    keys = ["vrs", "failed", "blockers"]
    print(f"{'video':32} {'VRS':>6} {'fail':>5}  first_motion  LUFS    TP     static  blockers")
    for name, s, m, _ in rows:
        loud = m.get("loudness", {})
        print(f"{name[:32]:32} {s['vrs']:6.1f} {s['failed']:5d}  {str(m.get('first_motion_s')):12} "
              f"{str(loud.get('integrated')):7} {str(loud.get('true_peak')):6} "
              f"{str(m.get('longest_static_s')):7} {','.join(s['blockers']) or '-'}")
    if ns.json:
        Path(ns.json).write_text(json.dumps(
            [{"video": n, "score": {k: s[k] for k in keys + ['categories', 'shippable']}, "measured": m,
              "checks": [c.to_dict() for c in cs]} for n, s, m, cs in rows], indent=2, default=str))
    return 0


def cmd_check(ns: argparse.Namespace) -> int:
    plan_path = Path(ns.plan).resolve()
    plan = load(plan_path)
    renders = Path(ns.renders).resolve()
    plan_checks, info = lint(plan, _project_root(plan, plan_path, ns.project), plan_path.parent)
    loop = (plan.get("loop") or {}).get("strategy")
    results = []
    for variant in plan.get("variants", []):
        for fmt in plan.get("formats", []):
            scope = f"{variant.get('id')}/{fmt}"
            video = renders / f"reel-{variant.get('id')}-{fmt}.mp4"
            if video.is_file():
                media_checks, measured = analyze(video, fmt, float(plan["duration_s"]), video.with_suffix(".srt"),
                                                 loop, scope)
            else:
                media_checks, measured = [make("media.container", False, f"missing render {video.name}",
                                               scope=scope)], {}
            s = score(plan_checks + media_checks)
            results.append({"variant": variant.get("id"), "format": fmt, "video": str(video), "score": s,
                            "measured": measured, "checks": [c.to_dict() for c in media_checks]})
    plan_score = score(plan_checks)
    report = {
        "plan": {"score": plan_score, "hook_scores": info.get("hook_scores"),
                 "checks": [c.to_dict() for c in plan_checks]},
        "renders": results,
        "min_vrs": min((r["score"]["vrs"] for r in results), default=0.0),
        "shippable": bool(results) and all(r["score"]["shippable"] for r in results),
        "gates": len(CATALOG),
    }
    out_dir = Path(ns.out).resolve() if ns.out else renders
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "qa-report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    (out_dir / "qa-report.md").write_text(_markdown(report), encoding="utf-8")
    print("Plan:")
    _print_checks(plan_checks)
    for r in results:
        failed = [c for c in r["checks"] if c["passed"] is False]
        print(f"\n{r['variant']}/{r['format']}: VRS {r['score']['vrs']} "
              f"{'SHIPPABLE' if r['score']['shippable'] else 'NOT SHIPPABLE'}")
        for c in failed:
            print(f"  FAIL  {c['severity']:7} {c['id']}: {c['message']}")
    print(f"\nmin VRS {report['min_vrs']} across {len(results)} renders; shippable={report['shippable']}")
    print(f"report: {out_dir / 'qa-report.md'}")
    return 0 if report["shippable"] else 2


def _markdown(report: dict[str, Any]) -> str:
    lines = ["# demo-reel QA report", "",
             f"- Gates evaluated: {report['gates']}",
             f"- Minimum Viral Readiness Score: **{report['min_vrs']}** (ship at >= {specs.SHIP_MIN_SCORE}, "
             "zero blockers)",
             f"- Shippable: **{report['shippable']}**", "",
             "| Variant | Format | VRS | Hook | Retention | Truth | Audio | Platform | Distribution | Blockers |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for r in report["renders"]:
        cats = r["score"]["categories"]
        cells = " | ".join(str(cats.get(k, "-")) for k in specs.CATEGORY_WEIGHTS)
        lines.append(f"| {r['variant']} | {r['format']} | {r['score']['vrs']} | {cells} | "
                     f"{', '.join(r['score']['blockers']) or '-'} |")
    lines += ["", "## Plan checks", ""]
    for c in report["plan"]["checks"]:
        lines.append(f"- {'PASS' if c['passed'] else 'FAIL' if c['passed'] is False else 'SKIP'} "
                     f"`{c['id']}` ({c['severity']}): {c['message']}")
    if report["plan"].get("hook_scores"):
        lines += ["", "## Hook leaderboard", "", "| Hook | Score |", "|---|---|"]
        lines += [f"| {k} | {v} |" for k, v in report["plan"]["hook_scores"].items()]
    for r in report["renders"]:
        lines += ["", f"## {r['variant']} / {r['format']}", ""]
        for c in r["checks"]:
            if c["passed"] is not None:
                lines.append(f"- {'PASS' if c['passed'] else 'FAIL'} `{c['id']}`: {c['message']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="reel", description="demo-reel toolkit")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("lint", help="check reel-plan.json against the creative and truth gates")
    s.add_argument("plan")
    s.add_argument("--project", help="project root (default: plan.project.root relative to the plan)")
    s.set_defaults(fn=cmd_lint)

    s = sub.add_parser("qa", help="measure one rendered video")
    s.add_argument("video")
    s.add_argument("--format", choices=sorted(specs.FORMATS))
    s.add_argument("--duration", type=float)
    s.add_argument("--srt")
    s.add_argument("--loop", choices=sorted(specs.LOOP_STRATEGIES))
    s.set_defaults(fn=cmd_qa)

    s = sub.add_parser("finish", help="frame, loudness-normalize, poster-bake, and faststart a master")
    s.add_argument("input")
    s.add_argument("--out", required=True)
    s.add_argument("--format", required=True, choices=sorted(specs.FORMATS))
    s.add_argument("--poster-t", type=float, help="timestamp of the strongest settled frame")
    s.add_argument("--fit", choices=["blur", "crop"], default="blur")
    s.add_argument("--focus-x", type=float, default=0.5)
    s.add_argument("--focus-y", type=float, default=0.5)
    s.add_argument("--fps", type=int, default=30)
    s.add_argument("--duration", type=float)
    s.set_defaults(fn=cmd_finish)

    s = sub.add_parser("captions", help="write an SRT for one variant from the plan")
    s.add_argument("plan")
    s.add_argument("--variant", required=True)
    s.add_argument("--out")
    s.set_defaults(fn=cmd_captions)

    s = sub.add_parser("hotspots", help="find the strongest windows in a long recording")
    s.add_argument("video")
    s.add_argument("--window", type=float, default=20.0)
    s.add_argument("--top", type=int, default=3)
    s.add_argument("--min-gap", type=float, default=5.0)
    s.set_defaults(fn=cmd_hotspots)

    s = sub.add_parser("check", help="full gate run: plan + every variant x format render")
    s.add_argument("plan")
    s.add_argument("--renders", required=True)
    s.add_argument("--project")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("compare", help="score any videos side by side (e.g. a /brag render vs a reel)")
    s.add_argument("videos", nargs="+")
    s.add_argument("--json")
    s.set_defaults(fn=cmd_compare)

    s = sub.add_parser("learn", help="pick a winner from post-launch analytics CSV")
    s.add_argument("metrics")
    s.add_argument("--objective", choices=sorted(experiment.OBJECTIVES), default="hook_rate")
    s.set_defaults(fn=cmd_learn)

    s = sub.add_parser("gates", help="list every machine-verified gate")
    s.add_argument("--count", action="store_true")
    s.set_defaults(fn=cmd_gates)

    ns = p.parse_args(argv)
    try:
        return ns.fn(ns)
    except (ToolError, FileNotFoundError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
