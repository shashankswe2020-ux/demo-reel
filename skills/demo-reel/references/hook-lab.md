# Step 2: Hook lab

The first 2 seconds decide whether anyone sees the other 18. Don't write one hook. Write a field of at least 10, score them, and let the math choose which ones to test.

## Hook types (`hooks[].type`)

| Type | Pattern | Example shape |
|---|---|---|
| `question` | Opens a curiosity gap the video closes | "What if your git log had a podcast?" |
| `statistic` | A striking, **sourced** number | "500 commits. One episode. 40 seconds." |
| `bold_claim` | A confident, falsifiable statement | "Your CI is lying to you." |
| `teaser` | Withholds the payoff | "Watch the last card." |
| `contrarian` | Goes against the default belief | "Release notes should be heard." |
| `before_after` | The old way next to the new way | "Spreadsheet → dashboard in one paste" |
| `demo_first` | Opens on the result itself | "Your git log, now a podcast" |
| `pain_point` | Names a pain the audience feels | "Nobody reads your changelog" |
| `challenge` | Dares the viewer | "Find the bug before it does." |
| `negative` | "Stop / never / don't" | "Stop writing release notes nobody reads" |
| `social_proof` | **Sourced** adoption proof | "Used by the Tauri team" (only with evidence) |

Pair each hook with the **visual** that opens on it. A hook the first frame can't prove is weaker.

## Rubric (agent-scored, 0–5 each; be harsh)

| Key | 5 means |
|---|---|
| `curiosity` | You have to see the next beat |
| `specificity` | It couldn't be about any other product |
| `stakes` | The viewer's time, money, or pride is involved |
| `visual_proof` | Frame 0–1 s shows it happening, not just says it |
| `pattern_break` | It breaks the scroll rhythm (unexpected phrasing, motion, or contrast) |

## Auto-scored by the linter

- `brevity`: 5 at ≤ 5 words, 4 at ≤ 7, 2 at ≤ 10, 0 above. Variant hooks over 8 words fail `plan.hook_brevity`.
- `grounded`: 5 if the hook contains a lexicon term (whole word) or references a verified claim, otherwise 0.

```
hook_score = 20 × (0.22·curiosity + 0.18·specificity + 0.15·stakes + 0.15·visual_proof
                   + 0.10·pattern_break + 0.10·brevity + 0.10·grounded)        # 0–100
```

`reel.py lint` prints the leaderboard. Variants must be the top-N hooks (ties allowed), which is `plan.hook_selection`. They must also use at least 2 different hook types, which is `plan.variant_diversity`, so the A/B test actually tests something.

## Anti-patterns

- Opening on a logo, a black frame, or "Introducing…".
- A hook that only makes sense after the reveal.
- A number with no evidence. This is a blocker (`plan.numbers_backed`).
- Inflating rubric scores. The linter can't check your honesty, but the post-launch `learn` loop will show when you guessed wrong.
