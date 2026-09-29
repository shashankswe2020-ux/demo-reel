---
name: demo-reel
description: Turn a project directory, a website URL, or a long screen recording into gated, A/B-ready viral launch reels (9:16, 1:1, 16:9) with hook variants, captions, per-platform share copy, and a post-launch learning loop. Every render is scored against 51 machine-verified gates. Use when someone says "/demo-reel", "/reel", "make a launch reel", "make a launch video", "make this go viral", "turn this into a TikTok/Reel/Short", or "brag about this".
---

# /demo-reel

A launch video people *finish, share, and act on*, backed by measurements you can check instead of taste alone.
`/brag` gives you one landscape video behind one lint gate. This skill gives you N hook variants × M native formats,
each one passing the same 51 checks. It also includes a loop that reads real platform analytics and picks the winner.

`<skill-dir>` is the directory containing this file. The toolkit is plain Python 3.10+ (stdlib only) plus FFmpeg:

```
python3 <skill-dir>/scripts/reel.py <lint|check|qa|finish|captions|hotspots|compare|learn|gates> ...
```

## Invocation

`/demo-reel [input] [options]`. Options may be flags or plain language.

| Option | Default |
|---|---|
| input | current project; or an `http(s)://` URL; or a video file (screen recording / demo) |
| `--tone <preset or freeform>` | inferred (see Tones) |
| `--formats vertical,square,landscape` | all three; vertical is mandatory |
| `--duration <s>` | 20 (band 15–30) |
| `--variants <n>` | 3 hook variants |
| `--focus "<feature/version>"` | whole product |
| `--voice` | off; captions carry the story |
| `--no-music` | music on |

Output goes to `reel-output/`, or `reel-output-YYYY-MM-DD-HHmmss/` if that directory already exists. Intermediate files go in its `work/` subfolder.

## Pipeline and gates

Every step ends in a gate. Don't advance until the gate passes. If a gate can't pass, say which check failed and why. Never weaken a threshold.

### 1. Inspect → [references/inspect.md](references/inspect.md)
Collect the material: the product in use (entry → key action → result), real UI and copy, exact colors and fonts, a **lexicon** of words that belong only to this product, and **claims**, each with a verbatim quote and its source file.
For a long recording, run `reel.py hotspots <video> --window <duration>` and build from the top windows.
**Gate:** the 12 inspection answers are written down. Every lexicon term and claim quote exists in the source (step 3's lint enforces this).

### 2. Hook lab → [references/hook-lab.md](references/hook-lab.md)
Write at least 10 hooks across at least 4 hook types. Score each one honestly on the 5-part rubric. The linter adds brevity and grounding scores and ranks the hooks. The top-N hooks become variants A/B/C, which must use at least 2 different hook types.
**Gate:** `plan.hook_*` checks pass.

### 3. Plan → [references/plan-schema.md](references/plan-schema.md)
Write `reel-output/reel-plan.json`, the contract that every later step reads. Cover scenes, timing, visual events, text boxes, claims, variants, loop strategy, CTA, and share copy.
**Gate:** `reel.py lint reel-output/reel-plan.json` exits 0 with zero failures.

### 4. Build → [references/build.md](references/build.md)
Build one composition. It takes the variant (which hook fills the `hook` slot) and the format (a native layout for each aspect ratio, not a crop) as parameters. Render a master for every variant × format into `work/`. Then, for each master:
```
reel.py finish work/A-vertical.mp4 --format vertical --poster-t <settled hook frame> --out reel-output/reel-A-vertical.mp4
reel.py captions reel-output/reel-plan.json --variant A --out reel-output/reel-A-vertical.srt
```
Before the full render, look at stills from every scene and from the middle of every transition. Fix overflow, collisions, low contrast, and text in UI zones.

### 5. Verify → [references/metrics.md](references/metrics.md)
```
reel.py check reel-output/reel-plan.json --renders reel-output
```
Writes `qa-report.md` and `qa-report.json`.
**Gate:** every render has **zero blocker failures and VRS ≥ 85**. Fix the cause (don't edit the plan to dodge a measurement), re-render, and re-check. Stop after 3 fix loops and report what is still failing.

### 6. Deliver → [references/experiment.md](references/experiment.md)
- `reel-output/share-copy.md`: per-platform copy taken from `plan.share` (X, LinkedIn, TikTok, Instagram, YouTube title, hashtags).
- `reel-output/posting-plan.md`: which variant goes on which platform, and when. Post the variants as a real test (for example, trial reels or the same slot on different days).
- `reel-output/metrics.csv`: header only, `variant,platform,impressions,views_3s,completions,shares,saves,follows`.
- Tell the user where the files are, give the VRS table from `qa-report.md` and the creative angle in one sentence, and explain how to run `reel.py learn reel-output/metrics.csv` after 72 h.

## Creative laws (each maps to a gate)

| Law | Gate |
|---|---|
| **Frame 0 is the poster.** Bright, high-contrast, postable on its own. | `visual.poster` |
| **Nothing is dead at the start.** Pixels move by 0.5 s and sound starts by 0.3 s. No black frames in the first 2 s. | `visual.first_motion`, `audio.leading_silence`, `visual.black_frames` |
| **The hook fits the budget.** ≤ 8 words, ≤ 3 s, and names something only this product has. | `plan.hook_brevity`, `plan.hook_scene_length`, `plan.hook_grounded` |
| **Pattern interrupt every ≤ 2.5 s.** A cut, an arrival, a click, a swipe, or typing. Nothing frozen for more than 3 s. | `plan.pattern_interrupts`, `visual.static_stretch` |
| **Readable.** Every line stays settled for max(0.8 s, 0.3 s × words). Overall ≤ 2.5 words/s. Pace comes from motion, not from pulling text early. | `plan.reading_time`, `plan.text_density` |
| **True.** Every on-screen number traces to a verbatim quote in the source. No invented metrics, users, or testimonials. | `plan.claims_evidence`, `plan.numbers_backed` |
| **Show the thing.** ≥ 40% of runtime comes from real product source. The demo scene shows **one headline feature** working (input → output), names it on screen, and backs it with a verified claim. | `plan.show_the_thing`, `plan.product_in_use` |
| **Works with sound off, rewards sound on.** Captions sidecar is readable. Mix is at -14 LUFS / ≤ -1 dBTP with no dead air. | `captions.*`, `audio.*` |
| **Native to each feed.** Exact resolution. Text inside the vertical safe zone. Platform UI zones stay quiet. | `media.resolution`, `plan.safe_zone`, `visual.ui_clutter` |
| **Loops.** The ending calls back to the opening, so a replay feels intentional. | `plan.loop`, `visual.loop_seam` |
| **Ends with an action.** The exact command, URL, or handle is on screen in the last scene. | `plan.cta` |
| **No clichés.** "Excited to share", "game-changer", "streamline your workflow", and similar phrases are banned. | `plan.banned_phrases` |
| **Clear to a stranger.** A one-liner of ≤ 15 words: what it is, who it's for. | `plan.one_liner` |

Structure, adapted to the material: **Hook (≤ 3 s) → Reveal (2–4 s) → Product in use (4–8 s) → Proof (2–5 s) → CTA / loop (2–4 s)**.

## Tones

Presets set defaults. Freeform direction ("fake Series A launch from 2016") refines or overrides them.

| Tone | Feel | Scenes / transitions |
|---|---|---|
| `default` | Punchy, playful, clean | 5; soft cuts |
| `polished` | Serious, restrained | 4; long holds, fades |
| `yc-parody` | Deadpan startup launch, played straight | 5; hard cuts |
| `chaotic` | FAST, LOUD | 7–9; flash and zoom cuts |
| `deadpan` | Dry, big empty space | 4; slow fades |
| `cinematic` | Trailer-scale | 5; dramatic wipes |
| `app-store` | Feature cards | 5–6; slides |
| `ugc-demo` | Phone-in-hand, "I built this" POV | 5–7; jump cuts, zooms on taps |
| `terminal` | Dev-native: typing, logs, diffs | 5–6; hard cuts on Enter |

Humor has to come from the product's own absurdity. Don't bolt it on.
