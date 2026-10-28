# The Misanthropic Cow: Hoof Gloves 3D Model, Project Status

Process: `3D_Model_Pipeline_PLAYBOOK` (photos → ChatGPT multiview → Tripo → cleanup in Blender `bpy`).
Worked example followed: the Misanthropic Cow slippers.

## Decisions (from intake, 28 Oct 2026)

| Question | Answer |
|---|---|
| Route | No re-shoot. AI multiview from the existing 16 photos (playbook stages 2–5). |
| Pose | Worn (filled), fingers straight, hoof **closed**. |
| Hoof parts | **Both hoof toes kept as separate objects** so they can be animated individually. Mitten body = one mesh. No armature. |
| Hoof finish | Satin black with grey brush-streak wear (studio photos), not the glossy green-black of the "Alt Image". |
| Pair | Model the LEFT glove; the right glove is the mirror (X scale −1). |

## Ground truth (see `01_references/DESIGN_KEY.png`)

Cream looped-terry mitten with a separate terry thumb (no hoof on it). The four fingers sit in two
compartments, each capped by a hard black toe cap: together a cloven hoof. Closed, the toes meet along a
straight cleft and their tips meet in one point. Thin raised rim on the toe edges. Plain open cuff, no fur
(the white fur in the photos is the bodysuit sleeve).

## Real-world size (measured, ±5 %)

From the mask scan (`01_references/scale_sources/cowMask1.stl`, mm) and the overhead photo of the gloves beside
the mask (`gloves_with_mask_2.jpg`); see `01_references/SCALE_measured_on_photo2.jpg` and `scripts/measure_scale.py`.

| | Left-hand glove | Right-hand glove |
|---|---|---|
| Cuff → hoof tip | 24.7 cm | 24.7 cm |
| Terry, cuff → hoof base | 15.8 cm | 16.0 cm |
| Hoof toe caps (base → tip) | 8.5 / 9.0 cm | 9.4 / 8.3 cm |
| Width at the wrist, laid flat | ~8 cm | ~8.6 cm |

Thumb ≈ 4.5–5 cm. Hoof ≈ 36 % of the length. The empty gloves lie flat, so the widths are half-circumferences;
worn they are narrower (~8–9 cm) and ~4–5 cm thick.

How: sphere fits to the scan's bead eyes give 56.9 mm centre to centre. Photo 2 is the same Nikon D800 / 24 mm
frame as the EXIF-tagged flat-lay photo, so the eye beads' pixel spacing gives the camera height (~44 cm above
the mat), and each part is scaled at its own height. Cross-checks: the beads measure 22.7 mm in the photo vs
23 mm in the scan, and the mat comes out 598 mm wide (a standard 24 in / 610 mm cutting mat).

## Estimated, not measured

- Side profile of the hoof (slim wedge as thick as the hand, tapering to the tip): no photo shows it
  straight on. It is an assumption; check it in Step 1 of the kit.
- Palm side assumed to mirror the back of the hand (true for a sewn mitten).

## Stage tracker

| Stage | Status |
|---|---|
| 0 Intake | done |
| 1 References, design key, brief | done: `01_references/`, `01_design_brief.md`; real size measured (see above) |
| 2 ChatGPT multiview kit | done: `02_chatgpt_kit/` (5 step zips + fix-ups). Guide page with copy buttons is published as a private artifact. **User runs Steps 1–5.** |
| 3 Normalise Tripo inputs | next, after the user sends the approved views |
| 4 Evaluate Tripo model | – |
| 5 Round 2 if needed | – |
| 6 Cleanup + split hoof toes into separate objects with knuckle pivots | – |
| 7–9 Optimise, UVs, bakes, materials (terry + satin black paint) | – |
| 10–11 Deliver pair, package for handoff (<29 MB per file) | – |

## Plan for the separate hoof toes (stage 6)

Tripo returns one fused mesh. After cleanup: segment the black hoof by baked colour plus position, cut it
off the mitten, split it at the cleft into two toe objects, give each a thickness and an open back, and set
each pivot at its knuckle line. The mitten's finger ends are closed under the caps so nothing is hollow when
a toe rotates. If Tripo's hoof geometry is poor, rebuild the two caps in Blender, fitted to Tripo's
silhouette (they are simple rigid shells).

## Files

- `01_references/`: white-background cut-outs (`REF_A–C`), detail crops (`DETAIL_1–5`), `DESIGN_KEY.png`
- `01_design_brief.md`: the brief pasted into every prompt
- `02_chatgpt_kit/`: one zip per step (PROMPT.txt + images numbered in attach order), `FIX_UP_PROMPTS.zip`,
  `guide_page.html` (offline copy of the guide)
- `scripts/`: `prep_refs_gloves.py` (rembg `birefnet-general` cut-outs; run one job per process, see the
  docstring), `design_key_gloves.py`, `kit_content.py` (all prompt text), `build_kit.py`, `build_page.py`
