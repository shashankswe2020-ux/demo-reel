# Step 3a: Treatment and director passes

The gates set the floor: a reel that passes all 51 is watchable, readable, true, and native to the feed. They can't set the ceiling. The ceiling comes from a clear creative vision, firm constraints, and repeated revision. The benchmark is [pdoom-video](https://github.com/mexicat/pdoom-video) ([watch](https://www.youtube.com/watch?v=5EoO5413dBY)). It's a code-rendered music video made entirely in conversation with an agent. It wasn't a one-shot prompt: the author started with a vague vision and a few hard constraints, then made tens of small and big revisions. Approach the reel the same way, as the **director**, not as a template filler.

The visual-truth discipline below is adapted from [On Growth and Form](https://github.com/paulina-duda/on-growth-and-form): show a process happening, make color carry a real quantity, calibrate that quantity consistently across time, disclose modeling liberties, and reject a candidate on its weakest moment rather than accepting it on average. Its code is PolyForm Noncommercial and its renders/text are all rights reserved; learn from the method, but do not copy its code, media, or wording without permission.

Write `reel-output/treatment.md` after the hook lab and before `reel-plan.json`. Summarize it in `plan.treatment` (see [plan-schema.md](plan-schema.md)).

## 1. The idea in one paragraph

- **One visual metaphor from the product's own world**, built from the lexicon and the real UI, not stock "tech" imagery. For a diff tool, the reel could be a printed proof sheet with editor's marks. For a CLI, it could be a terminal that keeps growing until it becomes the set.
- **One through-line motif that transforms.** pdoom's spark writes the first lyric, draws a loss curve, becomes a stock chart, bends into a paperclip, and turns out to be a burning fuse. In a 20 s reel, one object (the cursor, a token, the product's logo mark, a single line) should carry the viewer from hook to CTA and change role at every cut.
- **Transformations and visual puns, not literal illustration.** Don't show "fast" with a speed line. Have the progress bar outrun its own frame.

## 2. Constraints (3–5 hard rules)

Constraints create the style. Pick a few, write them as rules you can check, and keep to them. pdoom's were: maximalist typography, a limited palette, not a literal rendition of each line, and lyrics always perfectly in sync. Good reel constraints:

- "Type is the image": the copy is set big and becomes part of the scene, not subtitles laid on top.
- "Every big change lands on a beat": cuts on downbeats, arrivals on kicks, holds between them, then a snap.
- "Only real UI": every surface is the product's own component, screenshot, or footage.
- "One signal color": it marks only the thing that matters right now.

## 3. Palette

- 2–4 neutrals taken from the brand (background, panel, mid-tone, type), plus **one signal color** reserved for the moving thing, the key noun, and the CTA.
- Optionally, **one rare accent owned by one moment** (about 2 s), and nowhere else.
- Alternating light plates (paper/UI) and dark plates gives the edit a rhythm. The signal color stays the same on both.
- Only the signal color may glow. Type stays crisp.

## 4. Type system

- At most 3 voices: a **display** voice (big, tight, confident; animate width/weight for emphasis), a **machine** voice (mono: commands, labels, numbers, footnotes), and optionally a rare **accent** register for one moment.
- Swiss-grid discipline: asymmetric compositions, generous negative space, hairline rules, small mono annotations next to big display type. Don't center everything unless centering is the point.
- Use kerned text and typographic punctuation (’ “ ” … – —) in the display voice. The mono voice keeps straight quotes when it shows typed input.
- To keep text legible over busy UI, prefer solid plates or bands to outlines, halos, or glows.

## 5. Information lives in the world, not on a HUD

pdoom's first draft kept its P(doom) number in a permanent corner HUD. Moving it *into* each scene (a contour label, a scope readout, a form field, a stamp) is what made the video interesting. Do the same with claims and numbers: a counter ticking in the product's own status bar, a stamp on the output, a label riding the cursor. Persistent corner chrome is a smell.

## 6. Visual truth

Write `treatment.visual_truth` before building:

- **Process:** show the product's actual transformation, not only a finished beauty shot. Preserve input → action → output long enough that a stranger can infer causality.
- **Encodings:** motion, color, size, and brightness should carry a state the product or source already has: progress, status, latency, audio amplitude, changed lines. Write down what each channel means. Decoration can decorate, but it must not look like data.
- **Reference:** hold semantic mappings against one fixed reference for the whole clip. If green means success or bar length means progress, it must mean the same thing in every frame. Do not normalize each frame independently; that can flatten real change or manufacture it.
- **Liberties:** list every time compression, staged input, illustrative label, reconstructed UI, or simulated result. `liberties` must still be a non-empty list; use `"none"` when nothing is staged. A liberty may clarify the demo, but it may not alter a claim.

The plan summary uses this shape:

```json
"visual_truth": {
	"process": "A real git log becomes a generated episode, then plays in the product's own player.",
	"encodings": ["Waveform amplitude follows the rendered episode audio."],
	"reference": "One peak-amplitude reference is reused across the whole clip.",
	"liberties": ["Generation is time-compressed; the input and output are unchanged."]
}
```

## 7. Sync to everything

Since you make the soundtrack, you know every event time. Run `reel.py beats audio.wav --out work/audio-events.json` and drive animation from the result (beats, downbeats, kick/snare/hat onsets, envelopes) through the runtime's `f.beat`, `f.a.kick`, and `audio.timeOfBeat(i)`, not through hand-typed times. This works for user-supplied tracks too. Copy the printed `plan_music` into `plan.music` so `lint` flags off-beat cuts. Text reveals, card arrivals, and clicks land on hits. Motion eases *into* the downbeat.

## 8. Motion and taste

- Use strong eases (expo, cubic, springs): hold, then snap. Avoid floaty screensaver drift.
- Each scene gets its **own idiom** (terminal, paper, blueprint, chart, UI), while palette, type, and motif stay shared. The look changes often, but the film stays one film.
- **No slop:** no purple/cyan neon, glowing brains, matrix rain, lens-flare soup, particle nebulae, stock "AI" imagery, mascots, or emoji. Nothing that looks AI-generated. Don't imitate other products' UIs or existing artworks.
- Humor is deadpan and comes from the product's own absurdity (see the tones in SKILL.md).

## 9. Plate by plate

For each plan scene, write a short paragraph: the idiom, what is on screen, **what transforms into what**, which beat each change lands on, and how it hands off to the next plate (the motif should carry across the cut). For the hook, describe how the same typographic slam escalates across variants, so A/B/C differ in words but not in production value.

## Director passes (after the first stills)

The first render is a draft. Before the full render, and again after it, run at least **two revision rounds**. In each round, look at the per-scene stills and `reel.py sheet <master> --cuts`, answer the questions below honestly, change the composition, and log the change in `treatment.md` under `## Revisions` (and in `plan.treatment.revisions`):

1. Is anything **literal** where a transformation or pun would land harder?
2. Is any information sitting in **chrome** (HUD, corner badge, floating caption) that could live inside the scene?
3. Does every plate have its **own idiom**, while still sharing the palette, type, and motif?
4. Does every big change land **on a beat**, and does every text reveal match its sound?
5. Is anything **generic**? Could this frame belong to another product's reel?
6. Does the motif visibly **change role** at each cut and hand off cleanly?
7. Would **frame 0** earn a tap on its own? Does the last frame loop back to it?
8. Does any frame use an **error, warning, or red banner** as proof, even an intended one (a fail-closed retry, a blocked input)? In a feed it reads as the product breaking. Show the safeguard holding instead: the state that stayed correct, with a calm label for the condition (for example, "network: offline").
9. Do numbers **agree across surfaces**? A CLI that says 67 next to a GUI that says 66 makes viewers doubt both.
10. What is the **weakest sampled frame** in each motion or transition? A sequence that looks good on average still fails if one frame collapses, crosses, clips, or becomes unreadable.
11. Does every semantic color, size, brightness, or motion channel keep the meaning and reference declared in `visual_truth`? Could a viewer mistake decoration for measured state?

Example of a good revision note, modeled on pdoom's: "R2: removed the always-on stats bar; the 3× number now ticks inside the build log and stamps the output card on the downbeat."

Gates still decide what ships. Revisions decide whether anyone remembers it.
