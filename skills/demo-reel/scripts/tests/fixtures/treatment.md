# Shipcast: treatment

## Idea
The changelog is a radio script; the episode card is the studio's ON AIR sign. One waveform line carries the reel: it underlines the hook, scrubs the git log, and becomes the play button.

## Constraints
- Type is the image.
- Every big change lands on a beat.
- Only real Shipcast UI.

## Visual truth
- Process: a real git log becomes a generated episode, then plays in Shipcast's own player.
- Encoding: waveform amplitude follows the rendered episode audio.
- Reference: one peak-amplitude reference is reused across the whole clip.
- Liberty: generation is time-compressed; the input, output, and claim remain unchanged.

## Revisions
- R1: moved the commit count from a corner badge into the git log scroll.
- R2: the CTA command is typed by the waveform cursor instead of fading in.
