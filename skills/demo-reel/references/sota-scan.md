# State-of-the-art scan

This decision record compares the skill with `paulina-duda/on-growth-and-form` and current code-rendered media practice. It records methods, not protected implementation or aesthetics. The reference repository's code is PolyForm Noncommercial; its text and renders are all rights reserved.

## Adopted

| Practice | Implementation here |
|---|---|
| Show process, not only outcome | `treatment.visual_truth.process` and product input → action → output |
| Semantic visual channels | `visual_truth.encodings` plus one fixed cross-frame reference |
| Declare staging and time compression | `visual_truth.liberties` |
| Progress-paced compression | `R.remapProgress()` maps output time to monotonic cumulative meaningful change |
| Judge the weakest moment | `reel.py sheet --weakest` surfaces measured review risks; director still decides |
| Cheap preview before full render | poster → scene/transition stills → risky segment → full matrix |
| Fail before expensive encoding | `reel.py preflight` performs a real H.264/yuv420p + AAC round trip |
| Deterministic replay | seeded runtime plus renderer `--verify-determinism` byte checks |
| Preserve hard-won decisions | `work/production-log.md` records measurements and rejected alternatives |
| Rights and methodological provenance | `work/sources.md` separates reusable assets from inspiration |
| Reproducible delivery | automatic `artifact-manifest.json` hashes inputs/artifacts and records tool/Git state |
| Exact loop and cut review | SSIM loop gate and cut-boundary contact sheets |

## Conditional

- **VMAF:** useful only when comparing an encoded output with a trustworthy reference. It is not a no-reference quality score and does not rank creative variants.
- **CAMBI:** useful for banding checks when the installed FFmpeg includes `libvmaf`; keep optional because standard builds differ.
- **WCAG contrast:** apply to known text/background regions in the composition. Inferring text from arbitrary finished pixels is unreliable; Hyperframes users should run its structured check.
- **Flash safety:** should be evaluated for flash-heavy compositions against the applicable accessibility standard. A generic scene-change count is not a valid seizure-safety certification.
- **Audio description:** needed for some publication contexts, but it is a creative deliverable and cannot be inferred from caption presence.
- **C2PA:** add when a supported signing tool and a credential/claim policy exist. Unsigned JSON metadata is provenance documentation, not authenticity proof.
- **AI disclosure:** follow the target platform and jurisdiction. Do not claim a legal requirement from a generic automated check.

## Rejected as defaults

- Simulation-specific splatting, bloom, tone mapping, palettes, biological models, and layout constants: valuable for that artwork, not general product-reel infrastructure.
- Optical flow, face detection, and neural quality models: external dependencies and little benefit over current YDIF/scdet for this workflow.
- Pixel identity against an old published render as a universal gate: appropriate for reproducing deterministic scientific films, but product reels intentionally revise. The manifest identifies each shipped baseline instead.
- Per-frame normalization of semantic color or brightness: it destroys cross-frame meaning and can manufacture motion.
- More blocker gates for advisory creative judgments: measurable readiness is useful, but a proxy must not masquerade as truth, accessibility certification, or taste.

## Revisit triggers

Re-evaluate optional techniques when the bundled FFmpeg exposes `libvmaf`, distribution requires broadcast captions or audio description, a platform consumes C2PA video claims, or real audience data shows a current proxy fails to predict outcomes.