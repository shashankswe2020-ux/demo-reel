# RigSpark catalog update: treatment

## Idea
One signed revision is a token you can follow. It's born in the terminal (`--update` verifies and activates it), shows up unchanged in the Models view, and survives the network going away. The viewer follows a single number, **revision 1**, across two real surfaces.

## Motif
The mint verification beam, plus the revision token. The beam sweeps the terminal while the signature verifies. In the GUI it becomes a spotlight that walks from the **Update catalog** button to the "updated to revision 1" result, and finally rests on the status line that stays put while offline.

## Constraints
- Only real surfaces: captured CLI output and the GUI fixture's own capture. No mocked UI.
- One number on screen at a time, and it's the same revision everywhere.
- Every big change lands on a beat (120 BPM; cuts at 3, 6, 12, 17 s).
- Show trust, not alarms: the reel never shows an error state as its proof.

## Palette
Near-black #08090c, panel #111419, warm white #f4f1e8, mint #72e6a2 (signal: verified/active), coral #ff9b78 (brand mark and cut wipes only).

## Revisions
- R1: removed the GUI capture showing a red "Catalog download failed (offline)." banner. On screen it read as the product being broken. Fail-closed recovery is now shown positively: a "network: offline" chip appears while the spotlight rests on the unchanged "revision 1" status line, captioned "Offline retry. Revision 1 stays."
- R2: the cursor now clicks the real **Update catalog** button on the 13.0 beat, instead of landing on the "Known context fit only" checkbox. A spotlight walks the viewer from the button to the "Catalog updated to revision 1" result. The CLI's model count (67, from the live channel) was dropped because it contradicted the GUI fixture's "66 models". Cuts moved from 2.7 to 3.0 so every cut lands on a beat, and the soundtrack's SFX were re-timed to RigSpark's own events; they had been copied from another reel.
