# The Misanthropic Cow, v10: start here

This is the v10 handoff as of feedback round 47 (4 November 2026): the round 37 body rigged and animated, with less robotic animations, steady teats, smooth shoulders and armpits (with corrective shapes where arm and body meet), hooves that hang down, an Idle with attitude, a textured tail, armpit hair, a faster Chicken Dance and blended transitions between animations. Only the round 40 to 47 models are kept; the earlier ones were removed at the owner's request (they remain in git history). The folder holds:
- the models (round 37 static, every earlier new-body round from 25 to 36 static for comparison, and round 18 animated);
- the web viewer;
- review renders;
- every source file that builds them;
- the v09 inputs the build needs;
- the reference photos and generated views used along the way.

## What to open first

| You want to… | Open |
|---|---|
| See the cow | Double-click `Start_Viewer.bat` (Windows), or run `python start_viewer.py`. The viewer opens your browser on **Round 47** (animated); it needs internet only to load three.js. **Arms raised** shows the fur under the arms. **Light** and **Adjust** change the lighting. Under **Rounds**, add **Round 46** or **Round 44** (the animation starts on **Idle**), and under **Compare**, show them **Side by side** or as an **Overlay**. |
| Use the newest, animated model in Blender, Unity, Unreal or a glTF viewer | `Cow_v10/models/Misanthropic_Cow_v10_r47_Animated.glb` (round 47; rounds 40 to 46 beside it): the round 37 body with a 58-joint skeleton and 18 animations (Idle, Walk, Run, Sneak, Jumping Jacks, Look Around, Chicken Dance, Depressed Walk, Sit Cross-Legged, Crying, Exasperated, and alt versions of the first seven), baked physics included. Before/after: `Cow_v10/reviews/round_47/`, `round_46/`, `round_45/`, `round_44/`, `round_43/`, `round_42/`, `round_41/`, `round_40/` (teats and armpits), `round_39/` and `round_38/`. It has 20 morph targets (`ArmUp_L`, `ArmUp_R` and the shoulder correctives `Relax0_L` ... `Relax8_R`) that the animations drive; keep morph targets on when importing. Each animation's glTF extras say how to blend into it from another (`transition`). |
| See the latest fixes | `Cow_v10/reviews/round_37/`: round 33's neck shape with the round 36 neckline (rounds 33, 36 and 37); `round_36/`: the hooded neck going down into the costume (rounds 35 and 36); `round_35/`: the hood cleaned up (rounds 34 and 35); `round_34/`: the fuller hood and the rounded top of the chest (rounds 33 and 34); `round_33/`: the udders and hem checked against the original 2012 shoot, and the head comparison (rounds 32 and 33); `round_32/`: the hood's flare at the neck and the smaller udders and belly front (rounds 31 and 32); `round_31/`: raised-arm flaps, leg spots and the black spots under the left arm (rounds 30 and 31); `round_30/`: armpits, spots and the neck patch (rounds 29 and 30); `round_29/`: the fur strip between the udders and the pear shape (rounds 28 and 29); `round_28/`: the udders as full pink globes. `reviews/round_27/` and `round_26/` have the head and hood. |
| See what changed in rounds 19–25 | `Cow_v10/reviews/rounds_19_24/` (it holds round 25 too): before/after sheets, and comparisons with your Gemini views and the original shoot. `Round25_turnaround.jpg` shows where she is now. |
| Give the horns and wires photo textures (the tail has yours since round 47) | `Cow_v10/handoff/TEXTURE_PROMPTS.md`: image prompts (for ChatGPT or another image generator) and where to save the results (`Cow_v10/textures/`). |
| Hand the project to another AI session | Read `AI_HANDOFF.md`. Then paste `CONTINUE_PROMPT.txt` into the new session along with this folder. |
| Check nothing is missing or damaged | Run `python validate_handoff.py`. It checks every file against `MANIFEST.json`. |

## Folder layout

```
Misanthropic_Cow_v10_Handoff/
  START_HERE.md            this file
  AI_HANDOFF.md            full project context for a new AI session (rounds 1-25)
  CONTINUE_PROMPT.txt      a ready-to-paste opening message for that session
  PROJECT_STATUS.json      versions, files, commits, open items
  MANIFEST.json            size and SHA-256 of every file
  validate_handoff.py      checks the folder against MANIFEST.json
  start_viewer.py          serves Cow_v10/viewer locally and opens it
  Start_Viewer.bat         Windows double-click version of the above
  Cow_v10/                 the project (the misanthropic-cow/ folder of the git branch), plus the round 25–37 GLBs
    README.md
    models/                round 25–37 static GLBs (arms down, arms raised) and the round 18 GLBs
    viewer/                three.js viewer page and its web-sized model copies
    reviews/               renders and comparison sheets (rounds_19_24/ for the new body)
    references/            your four approved Gemini views
    assets/                your gloves, your slippers, and the cleaned Tripo body volume (tripo_body.npz)
    textures/              your black shag swatch and tuft sheets (tail_bow.png, tail_cord.png since round 47; horn_paint.png, horn_wire.png when you add them)
    pipeline/              Python sources; pipeline/review_tools/ builds and checks rounds 19-24
    handoff/               copies of these handoff documents (kept in git)
  Rebuild_Inputs/          the parts of the v09 handoff the pipeline reuses (mask scan, horns, fabric textures)
  Reference_Photos/
    original_photo_shoot/  "Cow - Original Photo Shoot" (20 photos): proportions, udders, teats
    round_19_to_24/        your photo of the empty suit, and your screenshots from rounds 19-25
    round_26_to_32/        your screenshots and costume photos from rounds 26-31, and the "Things To Do" folder
    ...                    the earlier folders (2012 Hasselblad shoot, mask, hood, gloves, slippers, round screenshots)
```

The Tripo model itself (OBJ and 8K textures, about 210 MB) is not included. The build uses the cleaned volume made from it (`Cow_v10/assets/tripo_body.npz`). The original is in your Google Drive and in the RAR you uploaded. The full glove and slipper project packages are not included either; the parts the build uses are in `Cow_v10/assets/`.

## Rebuilding from source

See `AI_HANDOFF.md`, section "How to rebuild and check", and `Cow_v10/pipeline/review_tools/README.md`.

## Versions

Every reviewed round is a git commit in the `misanthropic-cow/` folder of the `eccentricexhibits/main` repository; `PROJECT_STATUS.json` lists them. Rounds 18–25 are on branch `claude/quirky-darwin-pij3xe`. Rounds 26–32 and the viewer's round picker are on branch `claude/amazing-davinci-sc9bc8`; rounds 33 to 37 are on branch `claude/peaceful-ride-pz9yub`.
