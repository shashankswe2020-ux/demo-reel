# Step 4: Build

Build with whatever renderer the machine has. The toolkit only cares about the resulting MP4s. The requirements are what matter.

## Renderer requirements

1. **Deterministic.** Every frame is a pure function of `t`. No wall-clock animation, no `Math.random()` without a seed. Wait for fonts, images, and video to load before capturing each frame.
2. **Parameterized.** One composition takes `variant` (the hook text for the `hook` slot) and `format` (`vertical` 1080×1920, `square` 1080×1080, `landscape` 1920×1080, or `portrait` 1080×1350).
3. **Native per format.** Re-lay out for each aspect ratio: stack in vertical, sit side by side in landscape. `reel.py finish --fit blur|crop` is a fallback for footage you can't re-lay out, such as recordings.
4. **Reuse the real thing.** Import or render the project's actual components, CSS, fonts, images, and demo clips. Rebuild only what you can't reuse.
5. **Text renders in the composition.** Don't rely on FFmpeg `drawtext` or `subtitles` (many builds don't include them). Style on-screen captions and callouts in the composition itself: large type (≥ 64 px on vertical), a high-contrast plate or stroke, and word-level emphasis on the key noun.

## Suggested renderers (use the first one that works)

| Available | Approach |
|---|---|
| Hyperframes (`npx hyperframes doctor` ok) | Compose in Hyperframes, and also run `npx hyperframes check` (WCAG contrast plus layout overflow) before rendering |
| Remotion in the project | `<Composition>` per format, `inputProps={{variant}}` |
| Node + Playwright | HTML page exposing `window.seek(t)`. Capture `page.screenshot()` per frame at 30 fps and pipe PNGs to `ffmpeg -f image2pipe -framerate 30 -i - -c:v libx264 -pix_fmt yuv420p` |
| Python only | Pillow frames piped to FFmpeg the same way |

Render masters to `work/<variant>-<format>.mp4` with audio muxed. Then:

```
reel.py finish work/A-vertical.mp4 --format vertical --poster-t 1.4 --out reel-output/reel-A-vertical.mp4
```

`finish` does four things:
1. Frames the video to the exact resolution at 30 fps CFR, yuv420p.
2. Runs two-pass EBU R128 `loudnorm` to -14 LUFS / -1.5 dBTP target and outputs 48 kHz stereo AAC.
3. Replaces **only frame 0** with the poster, so duration and sync stay the same.
4. Applies `+faststart`.

Choose `--poster-t` at the strongest **settled** hook frame. For variants, it's usually the moment the hook line has fully landed.

## Motion and retention

- Plan a visible event every ≤ 2.5 s: a cut, a card arriving, a cursor click, a swipe, typing, or a counter ticking.
- Keep something moving during reading holds (a slow push-in, a cursor idle wiggle, a waveform) so no stretch is frozen for more than 3 s.
- Entrances and transitions take 0.2–0.5 s. Then the text holds.
- Don't use plain crossfades between two busy layouts. Stagger them (old content out, then new content in) or dip through the background.
- Show the product **doing** its job: type the command, click the button, show the result.
- For `loop.strategy = seamless`, the last frame should visually match the opening beat, which is checked by SSIM ≥ 0.5 against frame 1.

## Sound

- Music: generate it locally (for example with a small synth script) or use a track the user supplies **and has rights to**. Never pull unlicensed audio.
- SFX in the same key and space as the music, sitting under it. Tie them to on-screen events (keypress ticks, card whooshes, a click on the CTA).
- Something audible by 0.3 s. No silence longer than 1.5 s. `finish` handles loudness, but a hot master that clips before normalization will still sound bad.
- `--voice`: record or synthesize narration that complements the visuals instead of reading them out. Captions then mirror the narration.

## Stills review (before the full render)

Export one still per scene plus one from the middle of each transition, for each format. Check:
- Text is inside the safe zone and not covered by the right-rail buttons or the bottom caption area.
- There's no overflow or collision, and contrast holds even on busy UI.
- Frame 0 (the poster) would earn a tap on its own.
