# Step 4: Build

Build with whatever renderer the machine has. The toolkit only cares about the resulting MP4s. The requirements are what matter.

## Renderer requirements

1. **Deterministic.** Every frame is a pure function of `t`. No wall-clock animation, no `Math.random()` without a seed. Wait for fonts, images, and video to load before capturing each frame. Per-frame flicker or jitter keys off the frame index (`Math.floor(t * fps + 1e-6)`), held constant across that frame, never off continuous `t`.
2. **Parameterized.** One composition takes `variant` (the hook text for the `hook` slot) and `format` (`vertical` 1080×1920, `square` 1080×1080, `landscape` 1920×1080, or `portrait` 1080×1350).
3. **Native per format.** Re-lay out for each aspect ratio: stack in vertical, sit side by side in landscape. `reel.py finish --fit blur|crop` is a fallback for footage you can't re-lay out, such as recordings.
4. **Reuse the real thing.** Import or render the project's actual components, CSS, fonts, images, and demo clips. Rebuild only what you can't reuse.
5. **Text renders in the composition.** Don't rely on FFmpeg `drawtext` or `subtitles` (many builds don't include them). Style on-screen captions and callouts in the composition itself: large type (≥ 64 px on vertical), a high-contrast plate or stroke, and word-level emphasis on the key noun.
6. **Visually truthful.** Show the process declared in `treatment.visual_truth`. Semantic color, size, brightness, and motion use one fixed reference across the clip; never normalize each frame independently when the channel is meant to show change over time.
7. **Reproducible.** Pin seeds, dimensions, duration, fps, palette/look, inputs, and renderer flags. Save the exact commands in `work/render-recipe.txt`; variant renders go beside one another and never silently overwrite a prior cut.

Before installing browser dependencies or starting a full render, run:

```sh
python3 <skill-dir>/scripts/reel.py preflight
```

This performs a real H.264/yuv420p + AAC encode and reads it back with ffprobe. A codec appearing in `ffmpeg -encoders` is not enough; some builds advertise a path that fails during encoding.

## Suggested renderers (use the first one that works)

| Available | Approach |
|---|---|
| Node + Playwright (default) | The bundled runtime and renderer, described next |
| Hyperframes (`npx hyperframes doctor` ok) | Compose in Hyperframes, and also run `npx hyperframes check` (WCAG contrast plus layout overflow) before rendering |
| Remotion in the project | `<Composition>` per format, `inputProps={{variant}}` |
| Python only | Pillow frames piped to `ffmpeg -f image2pipe -framerate 30 -i - -c:v libx264 -pix_fmt yuv420p` |

### Bundled runtime and renderer

```sh
mkdir -p reel-output/work/composition && cd reel-output/work
cp <skill-dir>/scripts/runtime/reel-runtime.js composition/
cp <skill-dir>/scripts/runtime/template.html composition/index.html     # starting point
npm i -D playwright && npx playwright install chromium
python3 <skill-dir>/scripts/reel.py beats audio.wav --out audio-events.json
```

[`reel-runtime.js`](../scripts/runtime/reel-runtime.js) is a dependency-free timeline. The composition calls `Reel.define({ fonts, setup(cfg, R), render(f, R) })`, and `render` receives a frame `f` for time `f.t`:
- `scene`, `lt` (local time), `p` (scene progress)
- `beat`, `beatPhase`, `bar`, `barPhase` from the analyzed beat grid
- `a.kick|snare|hat` (decaying pulses from real onsets) and `a.rms|low|mid|high` (envelopes)
- `frame` (for per-frame flicker)
- `cfg` (`variant`, `hook`, `hooks`, `format`, `plan`, `events`)

`R` adds eases (`outExpo`, `inOutCubic`, `outBack`, and others), `prog`, `keys` (keyframes), `spring`, a seeded `mulberry32`/`hash`, `remapProgress` (map output progress to a measured cumulative-change curve), `fit` (shrink-to-fit text), and `audio.timeOfBeat`/`beatBefore`/`nearestBeat`/`hit`/`env`. Size everything with `var(--u)` (1% of the short side), never `vw`/`vh`. No CSS animations or transitions: style is set from `f` alone. Measure layout with `offsetTop`/`offsetLeft`/`clientWidth`, not `getBoundingClientRect()`, because the preview scales the page to fit the window.

**Preview:** serve `reel-output/` over HTTP (`python3 -m http.server`) and open `work/composition/index.html`. Keys: space play/pause with the soundtrack, ←/→ ±1 s (shift ±5), `,`/`.` ±1 frame, `[`/`]` previous/next scene, `l` loop the current scene, `v` next variant, `f` next format, `h` hide the HUD. `?t=6.2&variant=B&format=square` jumps straight to a moment.

**Render** with [`render.mjs`](../scripts/render.mjs), run from `reel-output/work`:

```sh
node <skill-dir>/scripts/render.mjs --composition composition/index.html --plan ../reel-plan.json \
  --events audio-events.json --audio audio.wav --stills auto --verify-determinism
node <skill-dir>/scripts/render.mjs --composition composition/index.html --plan ../reel-plan.json \
  --events audio-events.json --audio audio.wav --samples 8 --jobs 3     # all variant × format masters
```

`--samples N` motion-blurs: every output frame averages N sub-frames spread over `--shutter` (default 0.35 of a frame), centred on the frame, and **never across a scene cut**, so cuts stay hard. Frames whose shutter edges render identically are treated as still and captured once. Other flags:
- `--png` for lossless capture;
- `--only A-vertical,B-square` to pick jobs; `--formats vertical` to pick formats;
- `--from`/`--to` to render a segment;
- `--stills 0,1.4` for explicit still times.
- `--verify-determinism` to seek and capture opening, middle, and ending frames twice and abort on any byte difference.

Page errors from the composition are printed after each job. Read them.

Render masters to `work/<variant>-<format>.mp4` with audio muxed. Then:

```
reel.py finish work/A-vertical.mp4 --format vertical --poster-t 1.4 --out reel-output/reel-A-vertical.mp4
```

`finish` does four things:
1. Frames the video to the exact resolution at 30 fps CFR, limited-range BT.709 yuv420p with color tags. Untagged BT.601, which is FFmpeg's default for RGB sources, shifts brand colors in players that assume BT.709 for HD.
2. Runs two-pass EBU R128 `loudnorm` to -14 LUFS / -1.5 dBTP target and outputs 48 kHz stereo AAC.
3. Replaces **only frame 0** with the poster, so duration and sync stay the same.
4. Applies `+faststart`.

Choose `--poster-t` at the strongest **settled** hook frame. For variants, it's usually the moment the hook line has fully landed.

## Craft from code-rendered music videos

Techniques adapted from [pdoom-video](https://github.com/mexicat/pdoom-video), a code-rendered music video where every frame is a function of song time:

- **Cut on the beat.** Make or pick the soundtrack first. Run `reel.py beats audio.wav --out work/audio-events.json` and copy its `plan_music` into `plan.music`. Then place scene starts on beats (downbeats for the big ones). Anchor each cut to the content it introduces: the last beat at or before the text arrives, never after it. `reel.py lint` lists the off-beat cuts. For a synth track whose tempo you set, pass `--bpm` so only the phase is estimated.
- **Motion blur for fast moves.** Whips, slams, and fast zooms rendered as single instants look stepped at 30 fps. `render.mjs --samples 8` averages sub-frames over a short shutter (use 4 for drafts). It needs a fully deterministic composition, and it never spreads the shutter across a scene boundary, so `visual.shot_length` still counts every cut.
- **A scrubbable preview.** The runtime's preview mode (`?t=` plus keys) is much faster to iterate on than re-rendering.
- **Render in segments.** `render.mjs --from 0 --to 10` and `--from 10 --to 20` split a heavy render across machines or processes. Join the parts with `ffmpeg -f concat -c copy`; every segment uses the same encoder settings.
- **Lossless frames when color matters.** Capture PNG (or raw RGBA) instead of JPEG for brand-critical flat colors and gradients. `finish` converts whatever arrives to tagged BT.709, but it can't recover banding or chroma lost to JPEG.

## Motion and retention

- Plan a visible event every ≤ 2.5 s: a cut, a card arriving, a cursor click, a swipe, typing, or a counter ticking.
- Keep something moving during reading holds (a slow push-in, a cursor idle wiggle, a waveform) so no stretch is frozen for more than 3 s.
- Entrances and transitions take 0.2–0.5 s. Then the text holds.
- Don't use plain crossfades between two busy layouts. Stagger them (old content out, then new content in) or dip through the background.
- A hard cut between two dark plates may not register as a cut, which shortens the shot count `visual.shot_length` measures. `reel.py sheet --cuts` shows which boundaries count. Flash the signal color on the cut and decay to the new plate in about 0.15 s. The self-demo's terminal "powers on" this way.
- Show the product **doing** its job: type the command, click the button, show the result.
- For `loop.strategy = seamless`, the last frame should visually match the opening beat, which is checked by SSIM ≥ 0.5 against frame 1.
- When a long build, simulation, migration, or generation has uneven activity, pace the compressed demo by **cumulative meaningful change**, not uniform source time. Measure a product-native progress signal (changed lines, completed items, output delta, bytes processed), then use `R.remapProgress(outputProgress, cumulativeMeasurements)` to sample at roughly equal increments of that signal. It enforces a monotonic curve before interpolation, preventing noisy measurements from running time backward. This keeps setup from consuming the reel and avoids racing past the payoff. Declare the remapping in `visual_truth.liberties`; never use it to imply speed. Any performance claim needs a clearly labeled real-time segment or source-backed timing.

## Sound

- Music: generate it locally (for example with a small synth script) or use a track the user supplies **and has rights to**. Never pull unlicensed audio.
- SFX in the same key and space as the music, sitting under it. Tie them to on-screen events (keypress ticks, card whooshes, a click on the CTA).
- Something audible by 0.3 s. No silence longer than 1.5 s. `finish` handles loudness, but a hot master that clips before normalization will still sound bad.
- **Easy on the ears.** Passing the loudness gates doesn't make a track pleasant. Synthesized soundtracks are harsh when:
  - **Sounds start or stop abruptly.** Put a smooth attack (≥ 2 ms) and release (≥ 15 ms) on every sound, including the end of each pad.
  - **Raw white noise is used for hats or bursts.** It hisses above 8 kHz. Low-pass it (≤ 3.5 kHz) and keep it quiet.
  - **Pure high sines are used for ticks or beeps (≥ 1.5 kHz).** Use muted noise taps or chord tones an octave lower.
  - **Quick reveals get one sound per item.** They machine-gun. Allow at most one SFX per 0.14 s.
  - **`tanh` or clipping is used as a master.** Peak-normalize linearly instead, and let `finish` set the loudness.
- Before muxing, compare the energy above 8 kHz with the full mix (a high-pass into `ebur128`). Aim for ≤ −25 LU. The first demo-reel soundtrack measured −15.9 LU and sounded harsh; the fix brought it to −32 LU.
- `--voice`: record or synthesize narration that complements the visuals instead of reading them out. Captions then mirror the narration.

## Stills review (before the full render)

Spend render cost in steps: export the poster first; then one still per scene, the middle and both shoulders of every transition, and the extrema of any repeated motion cycle; then render only the riskiest short segment. Expand to every variant and format only after these pass. After rendering, `reel.py sheet <master> --cuts` tiles the frame before and after every detected cut. `reel.py sheet <master> --weakest` creates a second sheet from measured dark, low-contrast, abrupt-change, and long-static candidates and prints the reason for each pick.

Judge each transition or motion cycle by its **weakest** sampled frame, not its average impression. A single crossed, clipped, muddy, or semantically false frame rejects the candidate. Check:
- Text is inside the safe zone and not covered by the right-rail buttons or the bottom caption area.
- There's no overflow or collision, and contrast holds even on busy UI.
- Frame 0 (the poster) would earn a tap on its own.
- Visual channels still mean what `treatment.visual_truth` says they mean, with the same reference across frames.

Record measurements, rejected alternatives, and the reason for every non-obvious parameter while they are fresh. Use [production-record.md](production-record.md); a decision that was expensive to learn should not survive only as an unexplained number.
