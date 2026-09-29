# Step 5: Metrics and the Viral Readiness Score

Every number here comes from [scripts/reelkit/specs.py](../scripts/reelkit/specs.py). `reel.py gates` prints the live catalog.

## How a render is scored

Each gate has a **category** and a **severity** (blocker = 5, major = 3, minor = 1).

```
category_score = 100 × Σ(weight of passed gates) / Σ(weight of evaluated gates)
VRS            = Σ(category_weight × category_score) / Σ(category_weight)
category_weight: hook 25 · retention 20 · truth 20 · platform 15 · audio 10 · distribution 10
shippable      = zero blocker failures AND VRS ≥ 85
```

Plan gates are evaluated once and apply to every render. Media and caption gates are evaluated per variant × format. Skipped gates (for example, loop seam when no seamless loop is planned) don't count either way.

## Gate catalog (51)

| Gate | Cat. | Sev. | Threshold | Verifies |
|---|---|---|---|---|
| `plan.schema` | platform | blocker | — | Plan parses with required fields |
| `plan.duration_sum` | retention | blocker | ±0.25 s | Scenes contiguous; durations sum to `duration_s` |
| `plan.duration_band` | retention | major | 15–30 s | Runtime within launch band |
| `plan.hook_scene_length` | hook | major | ≤ 3.0 s | Scene 1 is the hook |
| `plan.hook_candidates` | hook | blocker | ≥ 10 | Hook lab breadth |
| `plan.hook_type_diversity` | hook | major | ≥ 4 types | Hook lab variety |
| `plan.hook_brevity` | hook | major | ≤ 8 words | Variant hooks fit the budget |
| `plan.hook_selection` | hook | major | top-N | Variants are the best-scored hooks |
| `plan.hook_grounded` | hook | major | — | Hooks name a lexicon term or a verified claim |
| `plan.first_event` | hook | blocker | ≤ 0.5 s | Something happens right away |
| `plan.variant_count` | distribution | major | ≥ 3 | Enough variants for A/B |
| `plan.variant_diversity` | distribution | minor | ≥ 2 types | The A/B tests something |
| `plan.pattern_interrupts` | retention | major | gap ≤ 2.5 s | Visual event cadence |
| `plan.reading_time` | retention | major | max(0.8, 0.3·words) s | Every line is readable |
| `plan.text_density` | retention | minor | ≤ 2.5 words/s | Not a slide deck |
| `plan.loop` | retention | minor | — | Loop strategy declared |
| `plan.lexicon_grounded` | truth | major | — | Lexicon terms exist in source |
| `plan.claims_evidence` | truth | blocker | verbatim | Claim quotes exist in evidence files |
| `plan.numbers_backed` | truth | blocker | — | No unsourced numbers on screen |
| `plan.show_the_thing` | truth | major | ≥ 40% | Runtime sourced from real product files |
| `plan.product_in_use` | truth | major | — | A sourced `demo` scene exists |
| `plan.banned_phrases` | truth | major | — | No launch clichés |
| `plan.one_liner` | truth | minor | ≤ 15 words | Clear to a stranger |
| `plan.cta` | distribution | blocker | — | Last scene shows the exact CTA |
| `plan.safe_zone` | platform | major | T12 B22 L6 R11 % | Text avoids platform UI |
| `plan.formats` | platform | major | — | Vertical included; formats known |
| `plan.share_limits` | distribution | major | X 280 · LI 3000 · TT/IG 2200 · YT 100 | Share copy per platform |
| `plan.share_fold` | distribution | minor | ≤ 125 chars | First line above the fold |
| `plan.hashtags` | distribution | minor | 3–5 | Hashtag count and syntax |
| `media.container` | platform | blocker | — | MP4 / H.264 yuv420p / AAC |
| `media.resolution` | platform | blocker | exact | 1080×1920, 1080×1080, 1920×1080, 1080×1350 |
| `media.fps` | platform | major | 24–60, CFR | Frame rate |
| `media.duration` | platform | major | plan ±0.5 s | Runtime |
| `media.faststart` | platform | major | moov < mdat | Instant playback |
| `media.file_size` | platform | minor | ≤ 250 MB | Upload ceiling |
| `media.audio_stream` | audio | major | 2 ch, 44.1/48 kHz | Audio layout |
| `audio.loudness` | audio | major | -14 ±1.5 LUFS | Feed-normalized loudness |
| `audio.true_peak` | audio | major | ≤ -1.0 dBTP | No inter-sample clipping |
| `audio.lra` | audio | minor | ≤ 12 LU | Phone-speaker dynamics |
| `audio.leading_silence` | hook | major | ≤ 0.3 s @ -50 dB | Sound in the hook |
| `audio.dead_air` | retention | minor | ≤ 1.5 s | No silent holes |
| `visual.poster` | distribution | major | YAVG ≥ 30, YHIGH−YLOW ≥ 80 | Frame 0 thumbnail quality |
| `visual.first_motion` | hook | blocker | YDIF ≥ 0.15 by 0.5 s | Motion right after the poster |
| `visual.black_frames` | retention | major | 0 in first 2 s, ≤ 2 % | No dead frames |
| `visual.static_stretch` | retention | major | ≤ 3.0 s | No frozen stretch |
| `visual.shot_length` | retention | minor | 0.8–5 s avg | Cut cadence (scdet ≥ 10) |
| `visual.ui_clutter` | platform | minor | edge ratio ≤ 0.8 | Bottom and right UI bands quieter than center (vertical) |
| `visual.loop_seam` | retention | minor | SSIM ≥ 0.5 | End matches start (seamless loops) |
| `captions.present` | distribution | major | — | SRT sidecar parses |
| `captions.timing` | distribution | major | — | Ordered, non-overlapping, in range |
| `captions.readability` | distribution | minor | ≤ 42 chars/line, ≤ 2 lines, ≤ 20 CPS, ≥ 0.7 s | Caption legibility |

All visual measurements run on a 160 px-wide downscale using FFmpeg `signalstats` and `scdet`. Audio measurements use `ebur128` and `silencedetect`. The same file always gives the same numbers.

## Scorecard against /brag (reproducible)

| Metric | How to verify | /brag | /demo-reel |
|---|---|---|---|
| Machine-verified gate types | `reel.py gates --count`; brag's SKILL.md gates | ~5 (hyperframes check: lint, contrast, layout; plan duration; files exist) | **51** (10×) |
| Gate evaluations per run | count `checks` in `qa-report.json` | ~5 | **227** (29 plan + 22 × 9 renders) |
| Hooks generated and scored | `plan.hooks` | 1 | **≥ 10**, ranked by formula |
| Shipped renders per run | files in `reel-output/` | 1 (one format) | **9** (3 hooks × 3 native formats) |
| Measured media properties | `measured` in `qa-report.json` | 0 | loudness, true peak, LRA, silences, motion onset, black, freeze, cuts, poster, faststart, UI clutter, loop SSIM |
| Claims checked against source | `plan.claims_evidence` | 0 | every claim, verbatim |
| Post-launch learning | `reel.py learn` | none | Bayesian P(best) + next traffic split |

**Same-yardstick comparison:** `reel.py compare brag-output/brag.mp4 reel-output/reel-A-vertical.mp4` scores both videos on the media gates.

**The only real virality test:** post the /brag render as a control variant (`variant=brag`) next to A/B/C, then run `reel.py learn`. Pre-launch gates predict that a video is *ready*. Only audience data shows it *won*.
