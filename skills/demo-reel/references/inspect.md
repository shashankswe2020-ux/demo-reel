# Step 1: Inspect

What you want from this step is the product **in use**, not a description of it.

## By input type

| Input | Recognize | Where material comes from |
|---|---|---|
| Project | No input, and cwd has code | Routes, main components, styles, README, package metadata, CHANGELOG |
| Website | `http(s)://…` or a bare domain | The rendered page. Use a headless browser if raw HTML is an empty JS shell. Dismiss overlays and scroll section by section so lazy content loads |
| Recording | A video file (`.mp4`, `.mov`, `.webm`, `.mkv`) | `reel.py hotspots <file> --window <duration> --top 3`, then cut the top windows |

For websites, save the rendered HTML, CSS, and text you rely on under `work/site/`. The linter resolves claim evidence and scene sources against the project root **and** the plan's directory, so saved pages still count as verifiable evidence.

### Hotspot scoring (recordings)
`hotspots` ranks sliding windows with a weighted ensemble of normalized signals, the same approach as yt-clipper's hot-zone detector:
`0.35·motion (mean YDIF) + 0.20·cut density (scdet ≥ 10) + 0.30·momentary loudness (EBU R128 M) + 0.15·hook motion (first 2 s)`. Picks don't overlap and are kept apart by `--min-gap`. Use the top window as the demo spine. Use the second window as B-roll or proof.

## The 12 inspection answers

Write these down before you plan anything:

1. What is it, in one sentence of ≤ 15 words? (This becomes `project.one_liner`.)
2. Who is it for, and what changes for them?
3. What does it do that nothing else does?
4. Entry → key action → result: the 2–3 beats of the product in use. Pick the **one headline feature** the demo scene will show, and find the README example (before/after, sample prompt and output, API call) that proves it.
5. Which real files, components, or screens show those beats? (These become `scenes[].sources`.)
6. Most impressive **verifiable** claim, with the file and verbatim quote.
7. Funniest or most surprising true thing about it.
8. Exact colors (hex) and fonts from the source.
9. Strongest single visual, the frame someone would screenshot.
10. What does "trying it" look like? The exact command, URL, or handle (this becomes `project.cta`).
11. Lexicon: 5–10 words or phrases that belong to this product (names, features, domain nouns). Each must appear in the source.
12. Which tone fits, and why?

## Claims discipline

- A claim is anything a viewer could fact-check: numbers, speeds, counts, "first", "only", compatibility lists.
- Record each claim as `{id, text, evidence: {file, quote}}`. The `quote` must be copied **verbatim** from the file. Whitespace and case differences are tolerated; anything else fails.
- If the product doesn't state a number, you can't put one on screen. Illustrative UI text that is clearly not a claim (a filename, a fake timestamp in a mock UI) must set `"illustrative": true`.
- Never invent testimonials, user counts, logos, or benchmarks.

## Rights and credit ledger

Create `work/sources.md`. For every external asset or substantive inspiration, record:

| Source | Creator | URL or file | License / permission | Required credit | Use in reel |
|---|---|---|---|---|---|

Include footage, images, music, SFX, fonts, generated assets, datasets, visual models, and an artwork or reel whose composition materially informed the treatment. Distinguish reusable assets from methodological inspiration. If rights are unknown or incompatible with the intended distribution, do not use the asset. If everything is owned by the product repository, write that explicitly instead of leaving the ledger blank.
