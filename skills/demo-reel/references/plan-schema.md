# Step 3: reel-plan.json

The plan is the contract. Build, captions, and QA all read it, so write it before any pixels. A complete, passing example lives at [../scripts/tests/fixtures/reel-plan.json](../scripts/tests/fixtures/reel-plan.json).

## Shape

```jsonc
{
  "schema": "demo-reel/plan@1",
  "project": {
    "name": "Shipcast",
    "root": "..",                        // project root, relative to this plan file
    "one_liner": "≤ 15 words: what it is and who it's for",
    "audience": "…",
    "cta": {"text": "npx shipcast init", "target": "npx shipcast init"},
    "lexicon": ["git log", "changelog", "episode"]   // each must occur in the project
  },
  "claims": [
    {"id": "c1", "text": "…", "evidence": {"file": "README.md", "quote": "verbatim sentence"}}
  ],
  "hooks": [                              // ≥ 10, ≥ 4 types
    {"id": "h1", "type": "demo_first", "text": "Your git log, now a podcast",
     "visual": "terminal log morphs into the episode card", "claim": "c1?",
     "scores": {"curiosity": 4, "specificity": 5, "stakes": 3, "visual_proof": 5, "pattern_break": 4}}
  ],
  "variants": [{"id": "A", "hook": "h3"}, {"id": "B", "hook": "h4"}, {"id": "C", "hook": "h1"}],
  "formats": ["vertical", "square", "landscape"],
  "tone": "default",
  "duration_s": 20,
  "music": {"bpm": 120, "offset_s": 0.0},   // optional: beat grid of the soundtrack (first beat at offset_s)
  "treatment": {                            // summary of reel-output/treatment.md (see treatment.md)
    "file": "treatment.md",
    "idea": "the changelog is a printed proof sheet; the cursor is the editor's red pen",
    "motif": "the red pen: underlines the hook, ticks the diff, signs the CTA",
    "constraints": ["type is the image", "every big change on a beat", "only real UI"],
    "palette": ["#111214", "#1C1D21", "#EEE9DF", "#FF4D12"],
    "visual_truth": {
      "process": "a real git log becomes an episode, then plays in the real player",
      "encodings": ["waveform amplitude follows the rendered episode audio"],
      "reference": "one peak-amplitude reference is reused across the whole clip",
      "liberties": ["generation is time-compressed; input and output are unchanged"]
    },
    "revisions": ["R1: moved the commit counter from a corner badge into the git log itself"]
  },
  "loop": {"strategy": "callback", "note": "how the end returns to the start"},
  "scenes": [
    {
      "id": "s1", "role": "hook", "start": 0, "duration": 2.8,
      "visual": "what is on screen",
      "sources": ["src/EpisodeCard.jsx"],       // real files shown or reused in this scene
      "events": [0.15, 1.2, 2.0],               // seconds from scene start: cuts, arrivals, clicks
      "text": [
        {"slot": "hook", "in": 0.15, "out": 2.8, "box": [0.1, 0.35, 0.76, 0.2]},
        {"content": "500 commits", "claim": "c1", "in": 0.3, "out": 2.0, "box": [0.1, 0.6, 0.76, 0.1]}
      ]
    }
  ],
  "share": {
    "x": "≤ 280", "linkedin": "≤ 3000", "tiktok": "≤ 2200", "instagram": "≤ 2200",
    "youtube_title": "≤ 100", "hashtags": ["#a", "#b", "#c"]
  }
}
```

## Field rules

- `scenes` are contiguous: each `start` equals the sum of the previous durations (±0.05 s), and durations sum to `duration_s` (±0.25 s).
- `role` is one of `hook | reveal | demo | proof | highlight | cta | outro`. Scene 1 must be `hook` and last ≤ 3 s. The last scene must be `cta` or `outro`, and its text must contain `cta.target` or `cta.text`.
- Text `in` / `out` are seconds from scene start, and `out − in` is the **settled** hold: fully visible, not entering or exiting.
- A `slot: "hook"` text is filled per variant. Its reading time is checked against the **longest** variant hook.
- `box` is `[x, y, w, h]` in fractions of the **vertical** frame and must sit inside the safe zone: top 12%, bottom 22%, left 6%, right 11%. Other formats reuse the same relative layout intent.
- Any text containing a digit needs `claim` (a verified claim id) or `"illustrative": true`.
- `events` should include every visible change. Scene starts and text arrivals count automatically. The longest gap between events, including the one up to `duration_s`, must be ≤ 2.5 s, and there must be one event in (0, 0.5] s.
- `sources` resolve against the project root, then the plan directory. They can't escape either one. Sourced scenes must cover ≥ 40% of runtime.
- The `demo` scene carries `"feature": {"title": "Line-level review comments", "claim": "c2"}`: the one headline feature it shows working. The title must appear in that scene's on-screen text, and the claim must be verified. Show it as input → output using the project's own examples (a README before/after, a sample prompt and its result, a real API call). An install command is not a feature.
- `loop.strategy`: `seamless` (last frame ≈ opening; checked by SSIM), `match_cut`, `callback`, or `none`.
- `music` (optional): when `bpm` is set, `lint` lists every scene start more than one frame (34 ms) off the beat grid. It's advisory, not a gate. Derive cut times from the grid (`offset_s + k × 60 / bpm`, snapped to the beat at or just before the text it introduces) instead of hand-typing them.
- `treatment`: `lint` prints an advisory (not a gate) when it's missing, the file doesn't resolve, `idea` or `motif` is empty, there are fewer than 3 `constraints`, `palette` isn't 2–6 hex colors, `visual_truth` does not define a process, one or more semantic encodings, a fixed cross-frame reference, and explicit liberties, or there are fewer than 2 `revisions` (expected after the director passes, so lint flags it until they're done).

## Commands

```
reel.py lint reel-output/reel-plan.json            # --project overrides project.root
reel.py captions reel-output/reel-plan.json --variant A --out reel-output/reel-A-vertical.srt
```
