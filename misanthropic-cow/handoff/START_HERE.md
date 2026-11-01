# The Misanthropic Cow, v10: start here

This is the v10 handoff as of feedback round 29 (1 November 2026). The folder holds:
- the models (round 29 static, rounds 28 and 25 static for comparison, and round 18 animated);
- the web viewer;
- review renders;
- every source file that builds them;
- the v09 inputs the build needs;
- the reference photos and generated views used along the way.

## What to open first

| You want to… | Open |
|---|---|
| See the cow | Double-click `Start_Viewer.bat` (Windows), or run `python start_viewer.py`. The viewer opens your browser on **Round 29**; it needs internet only to load three.js. **Arms raised** shows the fur under the arms. **Light** and **Adjust** change the lighting. Under **Rounds**, pick any of 17, 18, 25, 28 and 29 (17 and 18 are animated; the animation starts on **Idle**), and under **Compare**, show them **Side by side** or as an **Overlay**. |
| Use the newest model in Blender, Unity, Unreal or a glTF viewer | `Cow_v10/models/Misanthropic_Cow_v10_r29.glb` (static, A-pose), or `Misanthropic_Cow_v10_r29_arms_raised.glb` (round 25's are beside them). They have no rig yet. |
| Use the last animated model | `Cow_v10/models/Misanthropic_Cow_v10_Animated.glb` (round 18 body: skinned, 58 joints, 18 animations) |
| See the latest fixes | `Cow_v10/reviews/round_29/`: the fur strip between the udders and the pear shape (rounds 28 and 29); `round_28/`: the udders as full pink globes. `reviews/round_27/` and `round_26/` have the head and hood. |
| See what changed in rounds 19–25 | `Cow_v10/reviews/rounds_19_24/` (it holds round 25 too): before/after sheets, and comparisons with your Gemini views and the original shoot. `Round25_turnaround.jpg` shows where she is now. |
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
  Cow_v10/                 the project (the misanthropic-cow/ folder of the git branch), plus the round 25, 28 and 29 GLBs
    README.md
    models/                round 29, 28 and 25 static GLBs (arms down, arms raised) and the round 18 GLBs
    viewer/                three.js viewer page and its web-sized model copies
    reviews/               renders and comparison sheets (rounds_19_24/ for the new body)
    references/            your four approved Gemini views
    assets/                your gloves, your slippers, and the cleaned Tripo body volume (tripo_body.npz)
    textures/              your black shag swatch and tuft sheets
    pipeline/              Python sources; pipeline/review_tools/ builds and checks rounds 19-24
    handoff/               copies of these handoff documents (kept in git)
  Rebuild_Inputs/          the parts of the v09 handoff the pipeline reuses (mask scan, horns, fabric textures)
  Reference_Photos/
    original_photo_shoot/  "Cow - Original Photo Shoot" (20 photos): proportions, udders, teats
    round_19_to_24/        your photo of the empty suit, and your screenshots from rounds 19-25
    ...                    the earlier folders (2012 Hasselblad shoot, mask, hood, gloves, slippers, round screenshots)
```

The Tripo model itself (OBJ and 8K textures, about 210 MB) is not included. The build uses the cleaned volume made from it (`Cow_v10/assets/tripo_body.npz`). The original is in your Google Drive and in the RAR you uploaded. The full glove and slipper project packages are not included either; the parts the build uses are in `Cow_v10/assets/`.

## Rebuilding from source

See `AI_HANDOFF.md`, section "How to rebuild and check", and `Cow_v10/pipeline/review_tools/README.md`.

## Versions

Every reviewed round is a git commit in the `misanthropic-cow/` folder of the `eccentricexhibits/main` repository; `PROJECT_STATUS.json` lists them. Rounds 18–25 are on branch `claude/quirky-darwin-pij3xe`. Rounds 26–29 and the viewer's round picker are on branch `claude/amazing-davinci-sc9bc8`.
