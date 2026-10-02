"""Every threshold the toolkit enforces lives here, so metrics.md and code cannot drift."""

from __future__ import annotations

FORMATS: dict[str, tuple[int, int]] = {
    "vertical": (1080, 1920),
    "portrait": (1080, 1350),
    "square": (1080, 1080),
    "landscape": (1920, 1080),
}

# Conservative union of TikTok / Reels / Shorts UI overlays, as fractions of the frame.
SAFE_ZONE = {"top": 0.12, "bottom": 0.22, "left": 0.06, "right": 0.11}

DURATION_BAND_S = (15.0, 30.0)
DURATION_TOLERANCE_S = 0.5
PLAN_SUM_TOLERANCE_S = 0.25

HOOK_MAX_SCENE_S = 3.0
HOOK_MAX_WORDS = 8
HOOK_MIN_CANDIDATES = 10
HOOK_MIN_TYPES = 4
FIRST_EVENT_MAX_S = 0.5
MAX_EVENT_GAP_S = 2.5
READ_FLOOR_S = 0.8
READ_S_PER_WORD = 0.3
MAX_WORDS_PER_SECOND = 2.5
ONE_LINER_MAX_WORDS = 15
PRODUCT_SCREEN_SHARE_MIN = 0.4
MIN_VARIANTS = 3

HOOK_TYPES = frozenset({
    "question", "statistic", "bold_claim", "teaser", "contrarian", "before_after",
    "demo_first", "pain_point", "challenge", "negative", "social_proof",
})
LOOP_STRATEGIES = frozenset({"seamless", "match_cut", "callback", "none"})
SCENE_ROLES = frozenset({"hook", "reveal", "demo", "proof", "highlight", "cta", "outro"})

# Weights over the agent-scored rubric (0-5) plus two auto-computed dimensions.
HOOK_WEIGHTS = {
    "curiosity": 0.22, "specificity": 0.18, "stakes": 0.15, "visual_proof": 0.15,
    "pattern_break": 0.10, "brevity": 0.10, "grounded": 0.10,
}
HOOK_RUBRIC_KEYS = ("curiosity", "specificity", "stakes", "visual_proof", "pattern_break")

BANNED_PHRASES = (
    "streamline your workflow", "revolutionize", "game-changer", "game changer",
    "next-generation", "next generation", "cutting-edge", "cutting edge", "seamless experience",
    "unlock the power", "supercharge", "leverage the power", "all-in-one solution",
    "excited to share", "thrilled to announce", "we're excited", "we are excited",
    "take it to the next level", "empower", "synergy", "best-in-class", "world-class",
)

SHARE_LIMITS = {"x": 280, "linkedin": 3000, "tiktok": 2200, "instagram": 2200, "youtube_title": 100}
SHARE_FOLD_CHARS = 125
HASHTAG_RANGE = (3, 5)

LOUDNESS_TARGET_LUFS = -14.0
LOUDNESS_TOLERANCE_LU = 1.5
TRUE_PEAK_MAX_DBTP = -1.0
LRA_MAX_LU = 12.0
SILENCE_NOISE_DB = -50
LEADING_SILENCE_MAX_S = 0.3
DEAD_AIR_MAX_S = 1.5

FPS_RANGE = (24.0, 60.0)
MAX_FILE_MB = 250.0
AUDIO_RATES = (44100, 48000)

ANALYSIS_WIDTH = 160
MOTION_YDIF = 0.15
BLACK_YAVG = 24.0
POSTER_MIN_YAVG = 30.0
POSTER_MIN_CONTRAST = 80.0
BLACK_MAX_FRACTION = 0.02
HOOK_WINDOW_S = 2.0
STATIC_MAX_STRETCH_S = 3.0
CUT_SCORE = 10.0
SHOT_LENGTH_RANGE_S = (0.8, 5.0)
UI_CLUTTER_MAX_RATIO = 0.8
LOOP_SEAM_MIN_SSIM = 0.5
# Advisory (lint info, not a gate): a scene cut within one 30 fps frame of a beat counts as on the beat.
BEAT_SNAP_TOLERANCE_S = 0.034
# Advisory treatment checks (references/treatment.md), not gates.
TREATMENT_MIN_CONSTRAINTS = 3
TREATMENT_PALETTE_RANGE = (2, 6)
TREATMENT_MIN_REVISIONS = 2

CAPTION_MAX_LINE_CHARS = 42
CAPTION_MAX_LINES = 2
CAPTION_MAX_CPS = 20.0
CAPTION_MIN_S = 0.7

SHIP_MIN_SCORE = 85.0
CATEGORY_WEIGHTS = {
    "hook": 25.0, "retention": 20.0, "truth": 20.0,
    "audio": 10.0, "platform": 15.0, "distribution": 10.0,
}
SEVERITY_WEIGHTS = {"blocker": 5.0, "major": 3.0, "minor": 1.0}

# Post-launch experiment defaults, carried over from yt-clipper's A/B evaluator.
MIN_IMPRESSIONS = 500
WIN_PROBABILITY = 0.95
