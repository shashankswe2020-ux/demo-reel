"""Static checks over reel-plan.json. Every check is reproducible from the plan plus the project files."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import specs
from .checks import Check, make

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next",
             ".cache", "coverage", "target", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
TEXT_EXTS = {".md", ".mdx", ".txt", ".html", ".htm", ".css", ".scss", ".js", ".jsx", ".ts", ".tsx",
             ".vue", ".svelte", ".astro", ".py", ".rs", ".go", ".rb", ".java", ".kt", ".swift", ".json",
             ".yaml", ".yml", ".toml", ".c", ".h", ".cpp", ".cs", ".php", ".sh"}
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 5000


def words(text: str) -> list[str]:
    return re.findall(r"[\w'’%$#@.+-]+", text)


# "one" and "zero" are left out: too common in ordinary copy to treat as quantities.
NUMBER_RE = re.compile(
    r"\d|\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|"
    r"seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundreds?|"
    r"thousands?|millions?|billions?|dozens?|percent|twice|double|triple|half|tenfold|ninefold)\b",
    re.IGNORECASE,
)


def has_number(text: str) -> bool:
    return bool(NUMBER_RE.search(text))


class Resolver:
    """Resolves plan-relative references without letting them escape the allowed roots."""

    def __init__(self, *roots: Path):
        self.roots = [r.resolve() for r in roots]

    def find(self, ref: str) -> Path | None:
        if not ref or ref.startswith(("http://", "https://")):
            return None
        for root in self.roots:
            candidate = (root / ref).resolve()
            if candidate.is_relative_to(root) and candidate.is_file():
                return candidate
        return None


def iter_project_text(root: Path):
    count = 0
    for path in sorted(root.rglob("*")):
        if count >= MAX_FILES:
            return
        if any(part in SKIP_DIRS or part.startswith("reel-output") for part in path.relative_to(root).parts[:-1]):
            continue
        if path.is_file() and path.suffix.lower() in TEXT_EXTS and path.stat().st_size <= MAX_FILE_BYTES:
            count += 1
            try:
                yield path, path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def hook_score(hook: dict[str, Any], lexicon: list[str], verified_claims: set[str]) -> float:
    scores = hook.get("scores") or {}
    n = len(words(hook.get("text", "")))
    brevity = 5 if n <= 5 else 4 if n <= 7 else 2 if n <= 10 else 0
    grounded = 5 if is_grounded(hook, lexicon, verified_claims) else 0
    dims = {k: max(0.0, min(5.0, float(scores.get(k, 0)))) for k in specs.HOOK_RUBRIC_KEYS}
    dims.update(brevity=brevity, grounded=grounded)
    return round(sum(specs.HOOK_WEIGHTS[k] * v for k, v in dims.items()) * 20, 1)


def is_grounded(hook: dict[str, Any], lexicon: list[str], verified_claims: set[str]) -> bool:
    if hook.get("claim") in verified_claims:
        return True
    text = _norm(hook.get("text", ""))
    return any(re.search(rf"(?<!\w){re.escape(_norm(term))}(?!\w)", text) for term in lexicon if term.strip())


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def lint(plan: dict[str, Any], project_root: Path, plan_dir: Path) -> tuple[list[Check], dict[str, Any]]:
    checks: list[Check] = []
    info: dict[str, Any] = {}
    required = ("project", "hooks", "variants", "scenes", "duration_s", "formats", "share")
    missing = [k for k in required if k not in plan]
    checks.append(make("plan.schema", not missing and plan.get("schema") == "demo-reel/plan@1",
                       f"missing: {missing}" if missing else f"schema={plan.get('schema')}"))
    if missing:
        return checks, info

    resolver = Resolver(project_root, plan_dir)
    project = plan["project"]
    scenes: list[dict[str, Any]] = plan["scenes"]
    duration = float(plan["duration_s"])
    lexicon = [t for t in project.get("lexicon", []) if isinstance(t, str)]

    # Truth: claims and lexicon are checked first because hook scoring depends on them.
    verified: set[str] = set()
    bad_claims = []
    for claim in plan.get("claims", []):
        ev = claim.get("evidence") or {}
        file = resolver.find(ev.get("file", ""))
        quote = _norm(ev.get("quote", ""))
        if file and quote and quote in _norm(file.read_text(encoding="utf-8", errors="ignore")):
            verified.add(claim.get("id"))
        else:
            bad_claims.append(claim.get("id"))
    checks.append(make("plan.claims_evidence", not bad_claims,
                       f"unverified: {bad_claims}" if bad_claims else f"{len(verified)} claims verified",
                       len(bad_claims), 0))

    remaining = {t.lower() for t in lexicon}
    if remaining and project_root.is_dir():
        for _, text in iter_project_text(project_root):
            low = text.lower()
            remaining = {t for t in remaining if t not in low}
            if not remaining:
                break
    checks.append(make("plan.lexicon_grounded", bool(lexicon) and not remaining,
                       f"not found in project: {sorted(remaining)}" if remaining
                       else f"{len(lexicon)} terms" if lexicon else "lexicon is empty",
                       len(remaining), 0))

    # Hook lab.
    hooks = {h.get("id"): h for h in plan["hooks"]}
    scored = {hid: hook_score(h, lexicon, verified) for hid, h in hooks.items()}
    info["hook_scores"] = dict(sorted(scored.items(), key=lambda kv: -kv[1]))
    checks.append(make("plan.hook_candidates", len(hooks) >= specs.HOOK_MIN_CANDIDATES,
                       f"{len(hooks)} candidates", len(hooks), specs.HOOK_MIN_CANDIDATES))
    types = {h.get("type") for h in hooks.values()}
    unknown = sorted(t for t in types if t not in specs.HOOK_TYPES)
    checks.append(make("plan.hook_type_diversity", len(types - {None}) >= specs.HOOK_MIN_TYPES and not unknown,
                       f"types={sorted(t for t in types if t)}" + (f", unknown={unknown}" if unknown else ""),
                       len(types), specs.HOOK_MIN_TYPES))

    variants = plan["variants"]
    variant_hooks = [hooks.get(v.get("hook")) for v in variants]
    dangling = [v.get("id") for v, h in zip(variants, variant_hooks) if h is None]
    live = [h for h in variant_hooks if h is not None]
    checks.append(make("plan.variant_count",
                       len({h.get("id") for h in live}) >= specs.MIN_VARIANTS and not dangling,
                       f"{len(live)} variants" + (f", dangling hook refs: {dangling}" if dangling else ""),
                       len(live), specs.MIN_VARIANTS))
    checks.append(make("plan.variant_diversity", len({h.get("type") for h in live}) >= 2,
                       f"variant hook types={sorted({str(h.get('type')) for h in live})}"))
    long_hooks = [h.get("id") for h in live if len(words(h.get("text", ""))) > specs.HOOK_MAX_WORDS]
    checks.append(make("plan.hook_brevity", bool(live) and not long_hooks,
                       f"too long: {long_hooks}" if long_hooks else "ok", long_hooks, specs.HOOK_MAX_WORDS))
    ranked = sorted(scored.values(), reverse=True)
    cutoff = ranked[min(len(live), len(ranked)) - 1] if live and ranked else 0
    weak = [h.get("id") for h in live if scored.get(h.get("id"), 0) < cutoff]
    checks.append(make("plan.hook_selection", bool(live) and not weak,
                       f"below top-{len(live)} cutoff {cutoff}: {weak}" if weak else f"cutoff {cutoff}",
                       [scored.get(h.get("id")) for h in live], cutoff))
    ungrounded = [h.get("id") for h in live if not is_grounded(h, lexicon, verified)]
    checks.append(make("plan.hook_grounded", bool(live) and not ungrounded,
                       f"generic hooks: {ungrounded}" if ungrounded else "ok"))

    # Timeline.
    total = sum(float(s.get("duration", 0)) for s in scenes)
    gaps = []
    cursor = 0.0
    for s in scenes:
        if abs(float(s.get("start", -1)) - cursor) > 0.05:
            gaps.append(s.get("id"))
        cursor += float(s.get("duration", 0))
    checks.append(make("plan.duration_sum",
                       abs(total - duration) <= specs.PLAN_SUM_TOLERANCE_S and not gaps and bool(scenes),
                       f"sum={total:.2f}s vs duration_s={duration:.2f}s" + (f"; non-contiguous: {gaps}" if gaps else ""),
                       round(total, 2), duration))
    lo, hi = specs.DURATION_BAND_S
    checks.append(make("plan.duration_band", lo <= duration <= hi, f"{duration}s", duration, [lo, hi]))

    first = scenes[0] if scenes else {}
    checks.append(make("plan.hook_scene_length",
                       first.get("role") == "hook" and float(first.get("duration", 99)) <= specs.HOOK_MAX_SCENE_S,
                       f"scene 1 role={first.get('role')} duration={first.get('duration')}",
                       first.get("duration"), specs.HOOK_MAX_SCENE_S))

    events: list[float] = []
    longest_hook_words = max((len(words(h.get("text", ""))) for h in live), default=0)
    read_issues, all_words = [], 0
    number_issues, box_issues = [], []
    for s in scenes:
        start = float(s.get("start", 0))
        events.append(start)
        events.extend(start + float(e) for e in s.get("events", []))
        for item in s.get("text", []):
            t_in, t_out = float(item.get("in", 0)), float(item.get("out", 0))
            events.append(start + t_in)
            n = longest_hook_words if item.get("slot") == "hook" else len(words(item.get("content", "")))
            all_words += n
            need = max(specs.READ_FLOOR_S, specs.READ_S_PER_WORD * n)
            if t_out - t_in + 1e-6 < need:
                read_issues.append(f"{s.get('id')}: '{item.get('content', '<hook>')[:30]}' holds "
                                   f"{t_out - t_in:.2f}s, needs {need:.2f}s")
            if t_out > float(s.get("duration", 0)) + 1e-6:
                read_issues.append(f"{s.get('id')}: text outlives its scene")
            if (item.get("slot") != "hook" and has_number(item.get("content", ""))
                    and item.get("claim") not in verified and not item.get("illustrative")):
                number_issues.append(f"{s.get('id')}: '{item.get('content', '')[:40]}'")
            box = item.get("box")
            if "vertical" in plan["formats"] and not _in_safe_zone(box):
                box_issues.append(f"{s.get('id')}: {box}")
    for h in live:
        if has_number(h.get("text", "")) and h.get("claim") not in verified and not h.get("illustrative"):
            number_issues.append(f"hook {h.get('id')}: '{h.get('text', '')[:40]}'")

    events = sorted(e for e in events if 0 <= e <= duration)
    early = [e for e in events if 0 < e <= specs.FIRST_EVENT_MAX_S]
    checks.append(make("plan.first_event", bool(early),
                       f"first event after t=0 at {min((e for e in events if e > 0), default=None)}s",
                       early[0] if early else None, specs.FIRST_EVENT_MAX_S))
    timeline = events + [duration]
    max_gap = max((b - a for a, b in zip(timeline, timeline[1:])), default=duration)
    checks.append(make("plan.pattern_interrupts", max_gap <= specs.MAX_EVENT_GAP_S + 1e-6,
                       f"longest gap {max_gap:.2f}s", round(max_gap, 2), specs.MAX_EVENT_GAP_S))
    checks.append(make("plan.reading_time", not read_issues, "; ".join(read_issues[:5]) or "ok",
                       len(read_issues), 0))
    rate = all_words / duration if duration else 0
    checks.append(make("plan.text_density", rate <= specs.MAX_WORDS_PER_SECOND,
                       f"{rate:.2f} words/s", round(rate, 2), specs.MAX_WORDS_PER_SECOND))
    checks.append(make("plan.numbers_backed", not number_issues, "; ".join(number_issues[:5]) or "ok",
                       len(number_issues), 0))
    checks.append(make("plan.safe_zone", not box_issues,
                       f"outside safe zone or missing box: {box_issues[:5]}" if box_issues else "ok",
                       len(box_issues), 0))
    loop = (plan.get("loop") or {}).get("strategy")
    checks.append(make("plan.loop", loop in specs.LOOP_STRATEGIES, f"strategy={loop}"))

    # Advisory, not a gate: cuts that land on the music's beat grid read as intentional.
    music = plan.get("music") or {}
    if float(music.get("bpm") or 0) > 0:
        period, offset = 60.0 / float(music["bpm"]), float(music.get("offset_s") or 0)
        off_beat = []
        for s in scenes[1:]:
            t = float(s.get("start", 0))
            delta = t - (offset + round((t - offset) / period) * period)
            if abs(delta) > specs.BEAT_SNAP_TOLERANCE_S:
                off_beat.append(f"{s.get('id')} @ {t:.2f}s ({delta:+.2f}s)")
        info["beat_grid"] = {"bpm": float(music["bpm"]), "offset_s": offset, "off_beat": off_beat}

    info["treatment"] = _treatment_notes(plan.get("treatment"), resolver)

    # Show the thing.
    shown, missing_sources = 0.0, []
    for s in scenes:
        refs = s.get("sources", [])
        found = [r for r in refs if resolver.find(r)]
        missing_sources += [r for r in refs if r not in found]
        if found:
            shown += float(s.get("duration", 0))
    share = shown / duration if duration else 0
    checks.append(make("plan.show_the_thing",
                       share >= specs.PRODUCT_SCREEN_SHARE_MIN and not missing_sources,
                       f"{share:.0%} of runtime sourced from product" +
                       (f"; missing sources: {missing_sources[:5]}" if missing_sources else ""),
                       round(share, 2), specs.PRODUCT_SCREEN_SHARE_MIN))
    demos = [s for s in scenes if s.get("role") == "demo" and s.get("sources")]
    feature_issue = "needs a sourced scene with role=demo"
    for s in demos:
        feat = s.get("feature") or {}
        title = _norm(feat.get("title", ""))
        on_screen = any(title and title in _norm(t.get("content", "")) for t in s.get("text", []))
        if not title:
            feature_issue = f"{s.get('id')}: demo scene must name one headline feature (feature.title)"
        elif feat.get("claim") not in verified:
            feature_issue = f"{s.get('id')}: feature '{feat.get('title')}' needs a verified claim"
        elif not on_screen:
            feature_issue = f"{s.get('id')}: feature '{feat.get('title')}' is not shown as on-screen text"
        else:
            feature_issue = ""
            break
    checks.append(make("plan.product_in_use", not feature_issue,
                       feature_issue or f"feature: {demos[0].get('feature', {}).get('title')}"))

    # Copy.
    corpus = [project.get("one_liner", "")] + [h.get("text", "") for h in live]
    corpus += [t.get("content", "") for s in scenes for t in s.get("text", [])]
    corpus += [v for k, v in plan["share"].items() if isinstance(v, str)]
    hits = sorted({p for p in specs.BANNED_PHRASES for text in corpus if p in text.lower()})
    checks.append(make("plan.banned_phrases", not hits, f"found: {hits}" if hits else "ok", hits, []))
    n = len(words(project.get("one_liner", "")))
    checks.append(make("plan.one_liner", 0 < n <= specs.ONE_LINER_MAX_WORDS, f"{n} words", n,
                       specs.ONE_LINER_MAX_WORDS))

    cta = project.get("cta") or {}
    last = scenes[-1] if scenes else {}
    last_text = " ".join(t.get("content", "") for t in last.get("text", [])).lower()
    needles = [x.lower() for x in (cta.get("target"), cta.get("text")) if x]
    checks.append(make("plan.cta",
                       last.get("role") in {"cta", "outro"} and bool(cta.get("target"))
                       and any(x in last_text for x in needles),
                       f"last role={last.get('role')}, target={cta.get('target')!r}"))

    formats = plan["formats"]
    checks.append(make("plan.formats", "vertical" in formats and all(f in specs.FORMATS for f in formats),
                       f"{formats}"))

    over, missing_share = [], []
    for key, limit in specs.SHARE_LIMITS.items():
        text = plan["share"].get(key)
        if not text:
            missing_share.append(key)
        elif len(text) > limit:
            over.append(f"{key}: {len(text)}>{limit}")
    checks.append(make("plan.share_limits", not over and not missing_share,
                       "; ".join(over + [f"missing {k}" for k in missing_share]) or "ok"))
    folds = [k for k in ("linkedin", "tiktok", "instagram")
             if len((plan["share"].get(k) or "").split("\n", 1)[0]) > specs.SHARE_FOLD_CHARS]
    checks.append(make("plan.share_fold", not folds, f"first line too long: {folds}" if folds else "ok"))
    tags = plan["share"].get("hashtags", [])
    lo_t, hi_t = specs.HASHTAG_RANGE
    tags_ok = lo_t <= len(tags) <= hi_t and all(re.fullmatch(r"#\w+", t or "") for t in tags)
    checks.append(make("plan.hashtags", tags_ok, f"{tags}", len(tags), [lo_t, hi_t]))
    return checks, info


def _treatment_notes(t: Any, resolver: Resolver) -> list[str]:
    """Advisory only: what the director's treatment is still missing."""
    if not isinstance(t, dict):
        return ["no treatment: write treatment.md and summarize it in plan.treatment (references/treatment.md)"]
    notes = []
    if not (t.get("file") and resolver.find(t["file"])):
        notes.append(f"treatment file not found: {t.get('file')!r}")
    notes += [f"empty {k}" for k in ("idea", "motif") if not str(t.get(k) or "").strip()]
    if len(t.get("constraints") or []) < specs.TREATMENT_MIN_CONSTRAINTS:
        notes.append(f"{len(t.get('constraints') or [])} constraints, want >= {specs.TREATMENT_MIN_CONSTRAINTS}")
    palette = t.get("palette") or []
    lo, hi = specs.TREATMENT_PALETTE_RANGE
    if not (lo <= len(palette) <= hi and all(re.fullmatch(r"#[0-9A-Fa-f]{6}", str(c)) for c in palette)):
        notes.append(f"palette must be {lo}-{hi} hex colors, got {palette}")
    visual_truth = t.get("visual_truth")
    if not isinstance(visual_truth, dict):
        notes.append("missing visual_truth contract (process, encodings, reference, liberties)")
    else:
        notes += [f"empty visual_truth.{key}" for key in ("process", "reference")
                  if not str(visual_truth.get(key) or "").strip()]
        for key in ("encodings", "liberties"):
            values = visual_truth.get(key)
            if not (isinstance(values, list) and values
                    and all(str(value).strip() for value in values)):
                notes.append(f"visual_truth.{key} must be a non-empty list")
    if len(t.get("revisions") or []) < specs.TREATMENT_MIN_REVISIONS:
        notes.append(f"{len(t.get('revisions') or [])} director revisions logged, want >= "
                     f"{specs.TREATMENT_MIN_REVISIONS}")
    return notes


def _in_safe_zone(box: Any) -> bool:
    if not (isinstance(box, list) and len(box) == 4):
        return False
    x, y, w, h = (float(v) for v in box)
    z = specs.SAFE_ZONE
    return (w > 0 and h > 0 and x >= z["left"] - 1e-6 and y >= z["top"] - 1e-6
            and x + w <= 1 - z["right"] + 1e-6 and y + h <= 1 - z["bottom"] + 1e-6)


def variant_cues(plan: dict[str, Any], variant_id: str):
    """Caption cues for one variant, with the hook slot filled by that variant's hook."""
    from .captions import Cue, wrap

    hooks = {h.get("id"): h for h in plan["hooks"]}
    variant = next((v for v in plan["variants"] if v.get("id") == variant_id), None)
    if variant is None:
        raise KeyError(f"unknown variant {variant_id!r}")
    hook_text = hooks[variant["hook"]]["text"]
    cues = []
    for s in plan["scenes"]:
        start = float(s.get("start", 0))
        for item in s.get("text", []):
            content = hook_text if item.get("slot") == "hook" else item.get("content", "")
            if content.strip():
                cues.append(Cue(start + float(item["in"]), start + float(item["out"]), wrap(content)))
    cues.sort(key=lambda c: c.start)
    merged: list[Cue] = []
    for cue in cues:
        prev = merged[-1] if merged else None
        if prev and cue.start < prev.end - 0.05:
            prev.lines = wrap(" ".join(prev.lines + cue.lines))
            prev.end = max(prev.end, cue.end)
        else:
            if prev and prev.end > cue.start:
                prev.end = cue.start
            merged.append(cue)
    return merged
