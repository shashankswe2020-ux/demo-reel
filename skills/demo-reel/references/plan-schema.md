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
- `sources` resolve against the project root, then the plan directory. They can't escape either one. Sourced scenes must cover ≥ 40% of runtime, and at least one `demo` scene must be sourced.
- `loop.strategy`: `seamless` (last frame ≈ opening; checked by SSIM), `match_cut`, `callback`, or `none`.

## Commands

```
reel.py lint reel-output/reel-plan.json            # --project overrides project.root
reel.py captions reel-output/reel-plan.json --variant A --out reel-output/reel-A-vertical.srt
```
