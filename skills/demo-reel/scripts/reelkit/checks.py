from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from . import specs


@dataclass
class Check:
    id: str
    category: str
    severity: str
    passed: bool | None
    message: str = ""
    value: Any = None
    threshold: Any = None
    scope: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if not data["extra"]:
            del data["extra"]
        return data


def make(check_id: str, passed: bool | None, message: str = "", value: Any = None,
         threshold: Any = None, scope: str = "") -> Check:
    category, severity, _ = CATALOG[check_id]
    return Check(check_id, category, severity, passed, message, value, threshold, scope)


def score(checks: list[Check]) -> dict[str, Any]:
    """Viral Readiness Score: severity-weighted pass rate per category, then category-weighted."""
    per_cat: dict[str, list[float]] = {}
    for c in checks:
        if c.passed is None:
            continue
        w = specs.SEVERITY_WEIGHTS[c.severity]
        got, total = per_cat.setdefault(c.category, [0.0, 0.0])
        per_cat[c.category] = [got + (w if c.passed else 0.0), total + w]
    categories = {cat: round(100.0 * got / total, 1) for cat, (got, total) in per_cat.items() if total}
    weight_sum = sum(specs.CATEGORY_WEIGHTS[c] for c in categories)
    vrs = sum(specs.CATEGORY_WEIGHTS[c] * s for c, s in categories.items()) / weight_sum if weight_sum else 0.0
    blockers = [c.id + (f"[{c.scope}]" if c.scope else "") for c in checks
                if c.passed is False and c.severity == "blocker"]
    return {
        "vrs": round(vrs, 1),
        "categories": categories,
        "blockers": blockers,
        "failed": sum(1 for c in checks if c.passed is False),
        "passed": sum(1 for c in checks if c.passed),
        "skipped": sum(1 for c in checks if c.passed is None),
        "shippable": not blockers and vrs >= specs.SHIP_MIN_SCORE,
    }


# id -> (category, severity, description)
CATALOG: dict[str, tuple[str, str, str]] = {
    "plan.schema": ("platform", "blocker", "Plan parses and has the required top-level fields"),
    "plan.duration_sum": ("retention", "blocker", "Scene durations sum to duration_s and scenes are contiguous"),
    "plan.duration_band": ("retention", "major", "Total runtime within the launch band"),
    "plan.hook_scene_length": ("hook", "major", "Scene 1 is the hook and lasts at most 3 s"),
    "plan.hook_candidates": ("hook", "blocker", "Hook lab explored enough candidates"),
    "plan.hook_type_diversity": ("hook", "major", "Hook candidates span enough distinct hook types"),
    "plan.hook_brevity": ("hook", "major", "Every variant hook fits the word budget"),
    "plan.hook_selection": ("hook", "major", "Variant hooks are the top-scored candidates"),
    "plan.hook_grounded": ("hook", "major", "Every variant hook names a project term or backed claim"),
    "plan.first_event": ("hook", "blocker", "A visual event lands within the first 0.5 s"),
    "plan.variant_count": ("distribution", "major", "At least 3 hook variants for A/B testing"),
    "plan.variant_diversity": ("distribution", "minor", "Variants test at least 2 hook types"),
    "plan.pattern_interrupts": ("retention", "major", "No gap between visual events longer than 2.5 s"),
    "plan.reading_time": ("retention", "major", "Every text line holds long enough to read"),
    "plan.text_density": ("retention", "minor", "On-screen word rate stays readable overall"),
    "plan.loop": ("retention", "minor", "A loop strategy is declared"),
    "plan.lexicon_grounded": ("truth", "major", "Every lexicon term occurs in the project files"),
    "plan.claims_evidence": ("truth", "blocker", "Every claim quote exists verbatim in its evidence file"),
    "plan.numbers_backed": ("truth", "blocker", "Every on-screen number (digits or number words) is backed by a claim or marked illustrative"),
    "plan.show_the_thing": ("truth", "major", "Product-sourced scenes cover enough runtime; sources exist"),
    "plan.product_in_use": ("truth", "major", "The demo scene shows one named, claim-backed headline feature working"),
    "plan.banned_phrases": ("truth", "major", "No generic launch clichés in text or share copy"),
    "plan.one_liner": ("truth", "minor", "One-liner fits in 15 words"),
    "plan.cta": ("distribution", "blocker", "Final scene carries a concrete call to action"),
    "plan.safe_zone": ("platform", "major", "Every text box sits inside the vertical safe zone"),
    "plan.formats": ("platform", "major", "Formats include vertical and are all known"),
    "plan.share_limits": ("distribution", "major", "Share copy exists per platform and fits limits"),
    "plan.share_fold": ("distribution", "minor", "Share copy's first line fits above the fold"),
    "plan.hashtags": ("distribution", "minor", "3-5 hashtags"),
    "media.container": ("platform", "blocker", "MP4 with H.264 yuv420p video and AAC audio"),
    "media.resolution": ("platform", "blocker", "Exact resolution for the declared format"),
    "media.fps": ("platform", "major", "Constant frame rate between 24 and 60"),
    "media.duration": ("platform", "major", "Runtime matches the plan and the launch band"),
    "media.faststart": ("platform", "major", "moov atom precedes mdat for instant playback"),
    "media.file_size": ("platform", "minor", "File size under the upload ceiling"),
    "media.audio_stream": ("audio", "major", "Stereo audio at 44.1 or 48 kHz"),
    "audio.loudness": ("audio", "major", "Integrated loudness at -14 LUFS +/- 1.5"),
    "audio.true_peak": ("audio", "major", "True peak at or below -1 dBTP"),
    "audio.lra": ("audio", "minor", "Loudness range at most 12 LU for phone speakers"),
    "audio.leading_silence": ("hook", "major", "Sound starts within 0.3 s"),
    "audio.dead_air": ("retention", "minor", "No silence longer than 1.5 s"),
    "visual.poster": ("distribution", "major", "Frame 0 is a bright, high-contrast poster"),
    "visual.first_motion": ("hook", "blocker", "Pixels move within 0.5 s of the poster frame"),
    "visual.black_frames": ("retention", "major", "No black frames in the hook, at most 2% overall"),
    "visual.static_stretch": ("retention", "major", "No frozen stretch longer than 3 s"),
    "visual.shot_length": ("retention", "minor", "Average shot length between 0.8 and 5 s"),
    "visual.ui_clutter": ("platform", "minor", "Platform UI zones carry less detail than the center"),
    "visual.loop_seam": ("retention", "minor", "Last frame resembles the opening when a seamless loop is planned"),
    "captions.present": ("distribution", "major", "SRT sidecar exists and parses"),
    "captions.timing": ("distribution", "major", "Cues are ordered, non-overlapping, and inside the runtime"),
    "captions.readability": ("distribution", "minor", "Cue lines, line count, CPS, and duration are readable"),
}
