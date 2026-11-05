# The Misanthropic Cow, v10: start here

This is the v10 handoff as of the final model, 44B (5 November 2026): the round 37 body rigged and animated, with less robotic animations, steady teats, smooth shoulders and armpits (with corrective shapes where arm and body meet), hooves that hang down, an Idle with attitude, a textured tail, armpit hair, a faster Chicken Dance and blended transitions between animations. Only the final model, 44B, is kept; the others were removed at the owner's request (rounds 40 to 48 are all in the round 48 handoff ZIPs, and every round is in git history). The folder holds:
- the final animated model, 44B (round 44 with chosen later fixes; every other model is in git history);
- the web viewer;
- review renders;
- every source file that builds them;
- the v09 inputs the build needs;
- the reference photos and generated views used along the way.

## What to open first

| You want to… | Open |
|---|---|
| See the cow | Double-click `Start_Viewer.bat` (Windows), or run `python start_viewer.py`. The viewer opens your browser on **44B** (animated, in daylight); it needs internet only to load three.js. **Arms raised** shows the fur under the arms. **Light** and **Adjust** change the lighting. The animation starts on **Idle**; **Style** switches between the standard and lumbering version of each animation; the **Platformer** row plays the game moves, and **Jump sequence** chains a whole jump. |
| Use the newest, animated model in Blender, Unity, Unreal or a glTF viewer | `Cow_v10/models/Misanthropic_Cow_v10_r44B_Animated.glb` (44B, the final model): the round 37 body with a 58-joint skeleton and 41 animations (Idle, Walk, Run, Sneak, Jumping Jacks, Look Around, Chicken Dance, Depressed Walk, Sit Cross-Legged, Crying, Exasperated, Jump, Skid, Death and Victory (a dance), each in a standard and a lumbering alt version; loose-armed Idle and Walk; and a platformer set: Jump Start, Jump Rise, Jump Apex, Fall, Land, Hard Landing, Skid (game), Hurt, Death (game)), baked physics included. Checks: `Cow_v10/reviews/general_moves/` and `Cow_v10/reviews/platformer/`. Before/after: `Cow_v10/reviews/round_44B_final/`, `round_44D/` and `round_44C/` (dropped), `round_44B/`, `round_50/`, `round_49/`, `round_48/`, `round_47/`, `round_46/`, `round_45/`, `round_44/`, `round_43/`, `round_42/`, `round_41/`, `round_40/` (teats and armpits), `round_39/` and `round_38/`. It has 20 morph targets (`ArmUp_L`, `ArmUp_R` and the shoulder correctives `Relax0_L` ... `Relax8_R`) that the animations drive; keep morph targets on when importing. Each animation's glTF extras say how to blend into it from another (`transition`). |
| See the latest fixes | `Cow_v10/reviews/round_37/`: round 33's neck shape with the round 36 neckline (rounds 33, 36 and 37); `round_36/`: the hooded neck going down into the costume (rounds 35 and 36); `round_35/`: the hood cleaned up (rounds 34 and 35); `round_34/`: the fuller hood and the rounded top of the chest (rounds 33 and 34); `round_33/`: the udders and hem checked against the original 2012 shoot, and the head comparison (rounds 32 and 33); `round_32/`: the hood's flare at the neck and the smaller udders and belly front (rounds 31 and 32); `round_31/`: raised-arm flaps, leg spots and the black spots under the left arm (rounds 30 and 31); `round_30/`: armpits, spots and the neck patch (rounds 29 and 30); `round_29/`: the fur strip between the udders and the pear shape (rounds 28 and 29); `round_28/`: the udders as full pink globes. `reviews/round_27/` and `round_26/` have the head and hood. |
| See what changed in rounds 19–25 | `Cow_v10/reviews/rounds_19_24/` (it holds round 25 too): before/after sheets, and comparisons with your Gemini views and the original shoot. `Round25_turnaround.jpg` shows where she is now. |
| Make new texture images (the tail, horns and wires have yours since rounds 47 and 48) | `Cow_v10/handoff/TEXTURE_PROMPTS.md`: image prompts (for ChatGPT or another image generator) and where to save the results (`Cow_v10/textures/`). |
| Hand the project to another AI session | Read `AI_HANDOFF.md`. Then paste `CONTINUE_PROMPT.txt` into the new session along with this folder. |
| Check nothing is missing or damaged | Run `python validate_handoff.py`. It checks every file against `MANIFEST.json`. |
| Get back any earlier model or round (49, 50, 44C, 44D, 44, 40-48, ...) | `History/`: the whole git history of the project as a bundle in parts. Run `python History/restore_history.py`; it joins and checks the parts and makes `Cow_v10_git/`, a full git clone with every commit since round 1 (then `git checkout <commit> -- misanthropic-cow/models/...`). The commits for each removed model are given in `AI_HANDOFF.md`. |
| Read the whole conversation behind rounds 38 to 44B final | `Conversation_Log.md`: your messages and the replies, in order (tool output left out). |

## Folder layout

```
Misanthropic_Cow_v10_Handoff/
  START_HERE.md            this file
  AI_HANDOFF.md            full project context for a new AI session (rounds 1 to 44B final, feedback 1-59)
  Conversation_Log.md      the conversation from round 38 on: your messages and the replies
  CONTINUE_PROMPT.txt      a ready-to-paste opening message for that session
  PROJECT_STATUS.json      versions, files, commits, open items
  MANIFEST.json            size and SHA-256 of every file
  validate_handoff.py      checks the folder against MANIFEST.json
  start_viewer.py          serves Cow_v10/viewer locally and opens it
  Start_Viewer.bat         Windows double-click version of the above
  History/                 the project's full git history (Cow_v10_history.bundle.part01 ...) and restore_history.py
  Cow_v10/                 the project (the misanthropic-cow/ folder of the git branch)
    README.md
    models/                the final animated GLB, 44B
    viewer/                three.js viewer page and its web-sized model copies
    reviews/               renders, before/after sheets and checks (rounds_19_24/, round_26/ to round_50/, round_44B/ to round_44D/, round_44B_final/, loose_arms/, hand_fix/, platformer/, general_moves/); no videos since round 48
    references/            your four approved Gemini views
    assets/                your gloves, your slippers, and the cleaned Tripo body volume (tripo_body.npz)
    textures/              your black shag swatch and tuft sheets (tail_bow.png, tail_cord.png since round 47; horn_paint.png, horn_wire.png since round 48)
    pipeline/              Python sources; pipeline/review_tools/rig_bench.py builds, bakes and checks the animated rounds
    handoff/               copies of these handoff documents (kept in git)
  Rebuild_Inputs/          the parts of the v09 handoff the pipeline reuses (mask scan, horns, fabric textures)
  Reference_Photos/
    original_photo_shoot/  "Cow - Original Photo Shoot" (20 photos): proportions, udders, teats
    round_19_to_24/        your photo of the empty suit, and your screenshots from rounds 19-25
    round_26_to_32/        your screenshots and costume photos from rounds 26-31, and the "Things To Do" folder
    round_39_to_48/        your screenshots and images from rounds 39-48 (the bow, cord, horn and wire images among them)
    round_49_to_44B_final/ your screenshots after round 48: the 44B run shoulder, the hand angled back
    ...                    the earlier folders (2012 Hasselblad shoot, mask, hood, gloves, slippers, round screenshots)
```

The Tripo model itself (OBJ and 8K textures, about 210 MB) is not included. The build uses the cleaned volume made from it (`Cow_v10/assets/tripo_body.npz`). The original is in your Google Drive and in the RAR you uploaded. The full glove and slipper project packages are not included either; the parts the build uses are in `Cow_v10/assets/`.

## Rebuilding from source

See `AI_HANDOFF.md`, section "How to rebuild and check", and `Cow_v10/pipeline/review_tools/README.md`.

## Versions

Every reviewed round is a git commit in the `misanthropic-cow/` folder of the `eccentricexhibits/main` repository; `PROJECT_STATUS.json` lists them. Rounds 18–25 are on branch `claude/quirky-darwin-pij3xe`. Rounds 26–32 and the viewer's round picker are on branch `claude/amazing-davinci-sc9bc8`; rounds 33 to 37 are on branch `claude/peaceful-ride-pz9yub`.
