# AI handoff: The Misanthropic Cow, v10 at round 34

Read this, then `Cow_v10/README.md`, then `PROJECT_STATUS.json`. Everything needed to continue is in this folder. Nothing depends on a network service except three.js, which the viewer loads from jsDelivr.

## Where the project stands

There are two models, and they come from two different builds.

- **Round 34 (the newest, a static preview).** Round 33 with the hood fuller round the mask and at the neck, as in the 2012 shoot, and the top of the chest rounded where the flat neckline cut left a ledge under the chin (34). Round 33: round 32 checked against the original 2012 shoot only: the udders rounder (the pair about 2 cm narrower, each reaching a little lower) and the hem 2.5 cm higher at the front and sides (33). Round 32: round 31 with the hood fanning out a little at the neck and the udders and belly front slightly smaller (32). Round 31: round 30 with no flaps under the raised arms, the leg spots matched to the approved front view, and two black spots under the left arm removed (31). Round 30: round 29 with the armpit lumps removed, two stray spots removed and the neck patch moved to the cow's right upper chest (30). Round 29: Round 25 with the head and hood as in rounds 17/18 (feedback 26–27: the hood is a hood, and the head sits over the shoulders), the udders as full pink globes with a strip of fur between them (28–29), and a slightly more pronounced pear shape at the sides (29). Rounds 28 to 33 are kept for comparison. The owner has approved the new body, built in rounds 19–24. It starts from the owner's Tripo model, is fitted to four approved Gemini views, and was corrected against the original 2012 photo shoot and the owner's notes. It has **no rig or animations yet**. It comes in two poses: arms down (A-pose), and arms raised (to show the armpit fur). Build it with `pipeline/review_tools/build_static.py`. In the handoff package the built GLBs are `Cow_v10/models/Misanthropic_Cow_v10_r34.glb` and `..._r34_arms_raised.glb` (every round from 25 to 33 beside them, in both poses); round 25's are kept beside them for comparison.
- **Round 18 (animated).** This is the last rigged model: 58 joints, 18 clips and baked physics, built by `pipeline/build_v10.py`. It uses the older body, made from SDF primitives.

The viewer opens on round 34, with the Idle animation selected. Its Rounds row shows any combination of rounds 17, 18, 25 and 28–34, side by side or overlaid.

**The next step the owner asked for is the rig and the animations on the round 34 body.** Earlier they said: "let's get the rig working first, then do the animations", and the old animations felt robotic. `build_v10.py` has not been run on the round 19+ body; see "Next steps" below.

## The project

"The Misanthropic Cow" is the owner's costume character. The costume is:
- fur sleeves (**not stuffed**: fabric over the wearer's arms);
- a **stuffed** fur midsection, with stuffed udder cups sewn into holes in the fur;
- worn by a person in a snug fur hood (balaclava) under a papier-mâché mask, black leggings painted with white spots, pink briefs over the leggings, terry mitten gloves with painted hoof toes, and cow mule slippers;
- a gold satin bowtie at the back with a lamp-cord tail.

The owner reminded us more than once: "this is a person inside a stuffed body, so there must be a person underneath." The sculpt and the movement should reflect that.

The owner reviews on a phone, in the published web viewer and in screenshots, and gives numbered feedback. The owner makes reference models with Tripo (image-to-3D) and Gemini (generated views), and can shoot photos on request.

## Fixed constraints (the owner asked for these explicitly)

**Sources of truth**
- Proportions follow the original photo session only: the 2012 Hasselblad set and the "Cow - Original Photo Shoot" photos, in `Reference_Photos/original_photo_shoot`. Other shoots used other wearers, restuffing and a replacement pair of briefs, so they inform details only.
- The four approved Gemini views (`Cow_v10/references/approved_views`) are "guaranteed correct" for:
  - the black patch layout;
  - the leggings' white spots;
  - the belly shape in the side views;
  - the underwear.
- **Exception (round 21):** Gemini drew the udders too small and flat. Their size and stuffing come from the original shoot (shots 4–7 of 15).

**Body**
- The body is the Tripo model (`assets/tripo_body.npz`), cleaned and fitted height by height to the Gemini outlines. Its legs follow the original photos: crotch at 0.747 m.
- **Midsection:** a stuffed sack below the cups (`tripo_body.SACK`), full and round down to the hem, with no corset and no bustle. The sides dip in under the udders before the belly swells out, a pear shape: 18.4 cm half-width at 1.10 m, 22.5 cm at 0.98 m (rounds 25 and 29). The back runs straight down, and there is **no back-fat roll** any more (removed in round 19b). The hem is at 0.81 m at the front, 0.845 m at the sides and 0.85 m at the back (round 33, from the 2012 shoot: about 10 cm of the briefs shows under the front of the belly; rounds 19b–32 had 0.785, 0.82 and 0.835 m).
- **Head:** the snug hood is kept (the owner chose it over Gemini's loose hood); round 34 makes it fuller round the mask and at the neck, as in the 2012 shoot (still a hood, not a cowl). The mask, horns, tube and hood are carried 4° chin-up and lifted 1 cm (`design.head_pose`). The head sits over the shoulders, as in rounds 17/18 (`HEAD_DZ` = 0, round 27): rounds 19–26 carried it 5 cm forward onto Tripo's deeper chest, and the upper back then stood behind the hood as a hump. The hood is a hood (round 26): the round back of the head over a snug neck tucked into the suit's neckline. Do not fill the hood's back down to the shoulders (rounds 19c–25 did: "a smoothed back"), and do not pad the suit's top behind the neck (round 26 did: "a weird artificial hunchback"). The hood's neck fans out a little over the suit's neckline (round 32, `HOOD_FLARE`; the owner: subtle). Do not change the size of the tube and horns relative to the mask.
- **Shoulders** slope away from the neck. The body is stuffed and rigid: when the arms lift, the body does not deform. The sleeves turn out of rounded, padded shoulders like a ball in a socket (`design._lifted_shoulders`; "v18 was more faithful"). Folds there should be very minor, if any.
- **The person underneath:** from mid-thigh up, the leggings follow a real pelvis and thighs (`design._person_hips`), meeting in a soft groin crease. There is a round seat with a cleft under the briefs. The lower legs taper cleanly to a slim ankle, and the heels stand on the slipper footbeds.

**Udders and teats**
- Each cup is a stuffed pink globe sewn onto the fur (round 28): about 19 cm wide and 25 cm tall, standing out about 14 cm (round 32: a little smaller in front; round 33: rounder, as in the 2012 shoot, where from the front the pair is 1.9–2.0 times as wide as the visible cups are tall: 1.96 now, 2.1 in round 32). The tops are at 1.29 m. The two nearly touch, with a narrow strip of white fur down between them (round 29, from the owner's photo).
- **Each cup is pink all over: a full pink globe from the front and the side** (round 28, the owner's request). It replaces round 23's white fur over the tops; the cloth still runs **all the way under**, down to the seam with the suit (round 24).
- Teats sit on the cloth, not at the rim, as in shots 4 and 5 of 15. Each is about 6 cm long and droops slightly:
  - a lower teat, low and a little inside of centre, pointing down;
  - an outer teat on the lower outer face. The two outer teats are level (round 23).

**Markings**
- The black shag is grown as strands (`groom.py`). Never use flat cards. Patches are clean tufted ellipses fitted to the Gemini layout, including the armpit fur.
- The leggings' white spots are decals taken whole from the Gemini view that sees each one most squarely, so they keep the drawn brush outline (`approved_views.spot_decals`).

**Other**
- The bow sits just above the back of the hem (0.895 m), with a lamp cord ending in a plug.
- The briefs, gloves and slippers are the owner's own models (see the history below).
- No lighting is baked into the model; the viewer or engine does the lighting.
- The alt animations play heavy and lumbering, with the eyes level.

## Feedback history (most recent last)

1. v09's Chicken Dance grew "wings" under the armpits and the hands came off the sleeves. Fixed with separate sleeves and shared glove/sleeve weights.
2. The tufts were too pronounced; there was clipping at the arm joints and teats; the head was wrong (it should be a mask over a hood, with the horn tube restored); add light physics. All done. The physics is baked springs: teats, shag, belly and cups.
3. The head looked like a hunchback (it was fused to the body), so the hood became separate. The tube and horns belong to the mask. The belly underside was too flat. The tufts still looked off, so the owner supplied new textures. New animations: default pose, walk, run, sneak, jumping jacks, look around.
4. The mask hovered in front of the head; the shoulders looked like CGI tubes; the tufts looked like feathers (the owner then supplied a long-lock sheet). The owner asked for an alt set of every animation and four new clips (crouch and sit, very depressed walk, crying, exasperated). All done.
5. Seven fixes, all done:
   - the tube no longer touched the mask;
   - the shoulders were too high, too buff and had a seam line;
   - a broken seam showed behind the arms (the old glove cuff);
   - the crotch stretched in Jumping Jacks;
   - the back of the head was bulbous;
   - the gloves needed refining from the new close-ups;
   - the alt clips should look up more.
6. Tripo round: the owner made Tripo models of the costume. The model took Blue Shirt's udders, belly and hips, and Shy Cow's hooves, sleeve folds and slippers (with black socks).
7. Four requests:
   - use the Tripo gloves;
   - add the tail (a bow tied on the back and an electrical cord);
   - fix glitches in Exasperated's left arm;
   - make the briefs cover the crotch like real underwear.
8. Four more:
   - the bow should be a bowtie;
   - the tail was twice too long;
   - the briefs covered too much of the back and looked smeared on at the front (the owner pointed to Blue Shirt's front);
   - add back fat as a lip over the waist.

   The glove model arrived as a split archive.
9. Three fixes; the owner liked the briefs' back shape this round:
   - the briefs didn't go under the crotch (the leggings showed in Jumping Jacks);
   - the glove thumb had no joint and bent outward, and the hand clipped the back of the arm;
   - wheel zoom jumped straight to close-up.
10. Four requests:
    - the hand looked like it floated in the sleeve, so add material at the wrist without clipping;
    - the briefs vanished at the front while walking;
    - separate the legs;
    - the briefs should fit the contours of the hips, thighs and crotch, not look painted on.

    The owner also asked for hoof and thumb movement in the animations.
11. Three requests, all done:
    - round off the side of the tummy;
    - the briefs' front still needed work, so the owner shot photos and videos of the same kind of briefs over black tights, including jumping jacks and running;
    - two teats had holes at their tips.

    The first try at the belly made it fuller under the cups and pushed the teats and arms into it. The final version rounds only the lower belly.
12. The black shag patches looked like feathers. They are now grown as strands: about 15,000 tapered 3-sided tubes, in clumps of long drooping locks over a short tangled undercoat, with a few loose strays (`groom.py`). The strand material is near-black with low specular and no sheen, so it stays black in the viewer's room lighting. Then two follow-ups:
    - "holes" down both sides of the belly when the arms were raised: these were shading normals. The sleeve/torso normal blend reached the whole side of the body under the hanging arm; it now reaches only 7.5–11 cm from the shoulder pivot;
    - dark shading under the arms and on the belly was ambient occlusion baked into the vertex colours in the rest pose. All baked lighting was removed, and the viewer got lighting rigs.
13. Underwear and hands:
    - the briefs had sharp corners where the leg lines met a box-shaped gusset, their sides were hidden under the belly, and they floated over the tights. They are now grown from the leggings' surface with one smooth leg line per thigh, and the side sits below the hem (`garments.build_briefs`, `LEG_LINE`);
    - the gloves had hairline cracks (over 6,000 open edges each, from the original conversion). `repair_gloves.py` rebuilt them as closed surfaces and re-baked their textures;
    - the owner asked for a handoff (round 13 set).
14. Two follow-ups:
    - the briefs didn't connect in the middle: at the back the leg line sat just above the leggings in the cleft, so a strip of tights showed between the back panel and the crotch. The line now drops along the centre of the back (`MID_DROP`);
    - the hands were still rough: saw-tooth spikes along the edges and ragged frills at the wrist where gloves.py bent the cuff to fit the sleeve. `rebuild_gloves.py` rebuilt each glove as a smooth solid from the closed Tripo glove, with a designed round cuff inside the sleeve; gloves.py now only places it.
15. The owner replaced the slippers with their own finished model of the real prop (a separate slipper project; `cow_mule_slippers.py` converts its `Cow_Slippers_pair.glb`). The slippers are open-back mules, so the leggings got a socked foot (`design.legging_parts`, `FOOTBED`). The slipper project baked ambient occlusion into the colour map; it stays until that project's AO map (its Part 3) is available to divide it back out.
16. Clipping in the sitting animation (the owner suggested cross-legged). The belly hangs to the crotch and the suit's hem was rigid on the hips, so in the crouch the thighs passed 5–6 cm up through the belly and hem; the seat also sank 3–4 cm into the floor and the arms pressed into the cups. "Crouch and Sit" became **Sit Cross-Legged** (`clips.SitCrossLegged`): she crosses the right foot over, sinks with the knees open, reaches back and lands leaning back with the belly on her legs, slumps with the forearms on the knees, then rises. Two hem helper bones (`Hem_L/R`, children of Hips) lift the front of the hem over a raised thigh, driven in `anim.pose` by a share of the thigh's lift, only in clips that set `p['hem']`. `validate.py` gained belly/legs clipping checks. Belly into legs fell from 60 to 2.6 mm.
17. The owner replaced the gloves with their own finished glove model (a separate glove project; `hoof_gloves.py` converts its `Glove_pair.glb` into the hand frame at real size and divides the project's baked AO back out of the colour map with its `ao_2048.jpg`). Rigging: the toes are rigid on HoofFingers / HoofRingLittle at the web pivot; the top of the palm follows the toes (`toe_w`) so the knuckle line bends without a gap; the thumb lobe follows the Thumb bone (`thumb_w`, `THUMB_A`). New `spread` pose setting (Exasperated's fling). The fuller palm brushed the cup in Run, so Run's arm pump opens 3° (`fk` abduction .47).

18. Proportions from the original photo session (the owner's call, after comparing Claude's rig with a Tripo model made from four generated views). Measured on 0077 and "5 of 15": round 17's legs were 2–4 % of height short and the belly hung 4–5 % too low. Changes:
    - legs 4.0 cm longer (`design.LEG_LIFT`; a whole number of the leggings' 4 mm grid steps, because 3.8 cm meshed the gluteal fold half a step off and raised the leggings stretch 3–9 % in every clip);
    - the hips, pelvis, seat, back-fat roll, briefs (`LEG_LINE`, `WAISTBAND`), tail knot, Sit's `DROP` and the rig's hip/leg weight bands move up with them; the leggings' hidden top stays at 1.02 m (raised, it met the backs of the cups inside the suit);
    - the bottom of the belly 7.6 cm higher at the front (`HEM_LIFT`, `hem_lift(x, z)`): only the belly's lower half is shorter (`ellipsoid_low`), and the extra lift fades round the sides (`HEM_SIDE`), so the sides and the approved back keep their place relative to the hips (a wider lift put the hem's side on the thigh in Sit);
    - the belly shag patch centred on the belly under the teats (0.96 m; it sat on the hem).
    The owner also asked whether the Tripo model's udders were too small: they are (about 20 % too short, 4 cm too far back against the photos); v10's cups match the photos and were left alone. `validate.py` gained visible-only body/legs readings, because the plain ones count hidden geometry (see Working notes).

19. The owner compared Claude's v10 with a Tripo model made from four generated views, and asked for a radical rework: "new body shape, new spots, etc. Let's get just the model right (no animations) before moving on to the animations". The body became the Tripo model (`tripo_body.py`, `assets/tripo_body.npz`), fitted to the approved Gemini views (`approved_views.py`). The markings are projected from those views.
    - **19b:** the head looked hunched, there was a corset-like waist and the body was too short, there were zig-zag ankles, and the black patches looked patchy. Fixes:
      - the head pitch;
      - the stuffed sack midsection with a lower hem;
      - a clean shin tube;
      - patches fitted as tufted ellipses.
    - **19c:** the head looked upward (pitch eased from 10° to 4°). Also:
      - the hood's back falls straight to the shoulders;
      - a round seat under the briefs;
      - the bow moved down;
      - the heels moved onto the footbeds.
    - **19d:** the tops of the thighs looked unnatural, so they became a person's pelvis and thighs. The udders looked bolted on, so they became pink panels sewn into the fur.
20. Requests:
    - a lifted-arm mode to see the armpit fur (the **Arms raised** model and viewer toggle);
    - the leggings' spots still didn't match Gemini (now decals from the best view);
    - more lighting options (five new rigs, plus brightness, light turn and height, cast shadows and backdrop).

    Follow-ups:
    - "the arms are not stuffed, the body is", so the lifted arms now turn in rounded shoulders with no folds;
    - the folds on the back were Tripo surface lumps and a crease where the sack met the chest (both smoothed, and the sack joined by a smooth union).
21. The udders were too small and flat (Gemini). They are now sized and stuffed from the original shoot.
22. The teats were placed more naturally, from the shoot close-ups.
23. The right-hand udder's outer teat was lowered to match the left-hand one's. Too much pink bled into the chest and shoulders, so the fur now covers the swelling up to the stuffed cups (from the owner's photo of the empty suit, `Reference_Photos/round_19_to_24/empty_suit_on_stool.jpg`).
24. There was too much fur under the udders; the tops were fine. The cups are now pink all the way under, with their outer sides rounded and no fin.
25. The body felt like one big square block. In the original shoot (4 of 15) the sides come in a little under the udders before the belly swells out. The sides now dip by about 2.8 cm at 1.10 m: `tripo_body.SACK` widths, `SIDE_DIP` on the chest, and a tighter sack/chest join. The briefs no longer went under the crotch: since round 19d's person hips, the level leg line left the leggings showing between the legs. A gusset now runs down the middle (`garments.GUSSET_DROP`), and the seat's cleft is a soft crease that the fabric bridges.
    - **25b:** there were holes in the body with the arms raised. The arm-stub trim cut a cylinder through the chest, and the cups' solid stopped short of the body at their outer edges, leaving pockets and slivers of skin under the arm. The trim now stays outside the body's side wall, and the body is filled back in solid behind it (`_lifted_shoulders`). The cup solid reaches back to the body wherever it is within 3 cm (`cup_solid`, for the fur join only; the cloth shell keeps the plain limit). The udder build now drops any vertex the remesher flings off the surface (a thin sliver of cloth once threw a spike 0.8 m sideways), then keeps the main piece. Check: `ndimage.binary_fill_holes` finds no enclosed pockets in either pose, and the udder meshes stay inside their boxes.
26. The hood looked like a smoothed back instead of a hood on a larger torso costume; the owner asked for it to look more like rounds 17/18. Two causes:
    - the round 19c cowl (a round cone from the crown down to 1.36 m behind the hood, from the approved side views) filled the hood's back down to the shoulders. It is removed, so the hood is rounds 17/18's again: the round back of the head over a snug neck tucked into the neckline. This overrules 19c's "the hood's back falls straight to the shoulders"; the hood's back now departs from the Gemini side views on purpose;
    - Tripo's upper back is a person's: between 1.30 and 1.38 m it sloped 8.5 cm in towards the neck (round 18: 2.7 cm), and the shoulders by the neck were 3 cm lower. `design.padded_yoke` adds round 18's padded shoulders (a capsule across them) over a full upper back, moved forward with the head (`HEAD_DZ`), and the shoulder-slope cut falls away less steeply behind the neck (`YOKE_BACK_SLOPE` = 0.35). Now the back comes in 5.2 cm over that height and the shoulders beside the neck are 2 cm fuller; sideways the shoulders still slope as the approved views have them.
    Everything else is round 25's. Before/after: `reviews/round_26/`.
27. Round 26's head looked "like a weird artificial hunchback", and the side of the udder looked weird.
    - **Head:** round 26's padding (`padded_yoke`) is removed. The cause of the hump was the head's position: since round 19 it sat 5 cm forward (`HEAD_DZ` .05), so the neck was 5 cm in front of Tripo's shoulder joints and the upper back rose behind it. `HEAD_DZ` is now 0, so the head sits over the shoulders as in rounds 17/18 (their neck at z −0.035; Tripo's shoulder joints at z −0.03). The mask, horns, tube and hood move back together; nothing else changes. In the Gemini side views the head is further forward.
    - **Udders:** the pink's front outline was a shape pushed straight back, so on the cup's steep outer side it ran along the surface: the cloth went down the flank and ended in a saw-tooth edge, and from the side the cup read as a flat pink wall. On the outer side the pink now ends at a plane through a point 3 cm inside the cup (`cup_apex`), tilted `CUP_SEAM_DEG` (58°) out from straight ahead, so the seam crosses the side steeply and cleanly; below it the fur covers the flank, with a wider fillet into the body there (`CUP_FLANK`). No shag patch is fitted where the pink used to cover the cups (rounds 24–26) any more (`textures.fit_projected_patches`): a fragment fitted under the old pink showed on the flank as a bare black streak. Fronts, teats and undersides are unchanged.
    - Before/after: `reviews/round_27/`. The arms-raised hole check finds no pockets now (rounds 25–26 had one 5 mm² speck at 1.12 m).
28. The owner asked for each udder to be a full pink globe from the side. Each cup is now a stuffed ellipsoid globe sitting on the chest, sunk part-way in (`design.GLOBE`, fitted to rounds 21–27's cup fronts, rms 1.2 cm), instead of a raised panel grown out of the chest. The pink covers each globe wherever it stands outside the suit's body (`pink_sdf`), so it runs round the sides and underneath to the crease where the globe meets the suit: a clean seam. Round 23's fur over the top of each cup is dropped (`GLOBE_CAP` = None; set it to bring a fur cap back, though its edge reads as a straight line from the front). The fur follows each globe just inside the cloth (`with_cups`), the teats sit on the globes, and no shag patch is fitted within 2 cm of them (`textures.fit_projected_patches`). Round 27's seam plane and flank fillet (`cup_apex`, `CUP_SEAM_DEG`, `CUP_FLANK`) are gone. Before/after: `reviews/round_28/`.
29. From two photos of the costume: the udders have a narrow strip of white fur between them, and the "pear" curve on the sides (in under the udders, out over the belly) should be a little more pronounced.
    - **Fur strip:** the globes press together less (each 8 mm further out and 4 mm narrower), and no pink is drawn within `GLOBE_GAP`/2 (6 mm) of the middle, so a 1.2 cm strip of fur runs down the seam between them. (Pulling the globes fully apart instead opened a wide V at the top; the photo shows them almost touching.)
    - **Pear:** `tripo_body.SIDE_DIP` 0.075 → 0.115 and the `SACK` half-widths at 1.06–1.14 m narrower and at 0.90–1.02 m wider. From the front the half-width is now 18.4 cm at 1.10 m (19.2 before) and 22.5 cm at 0.98 m (21.9 before): a 4.1 cm step per side instead of 2.7.
    Round 28 is kept beside it (the viewer has both). Before/after: `reviews/round_29/`.
30. The owner's "Things To Do" (screenshots and photos of the costume):
    - **Armpit lumps:** Tripo's torso kept a nub at the front of each armpit, where its arm had met the body: up to 4 cm (cow's right) and 2.8 cm (left) proud of the side wall at 1.14–1.18 m, just in front of the side. `design._trim_armpit_nubs` caps the front of the side wall there at its width 3 cm further back (`ARMPIT_WALL`), fading out by 1.215 m where the shoulder begins.
    - **Spots removed** (`textures.PATCH_REMOVE`, matched by position): a small patch high on the cow's left shoulder (0.14, 1.35 m) and a small one on the right side of the belly (−0.145, 0.975 m).
    - **Neck patch:** the Gemini views drew a patch at the front of the neck, which the fit made into five pieces; they are removed. From the owner's photos it is one round shag patch on the cow's right upper chest, just above the right udder, its inner edge clear of the mask's chin: `textures.PATCH_ADD` (centre x −0.105, y 1.34 m, about 13 × 12 cm), placed on the suit's front surface. Rounds 18's was nearer, but central.
    The patch edits are applied before the markings cache, so the arms-raised build gets them too. Before/after: `reviews/round_30/`.
31. Arms-raised flaps, leg spots against the approved front view, and two black spots under the cow's left arm.
    - **Flaps:** with the arms lifted, Tripo's armpit (the top of its arm root, 1.16–1.26 m, up to 5 cm proud of the side wall) hung below each sleeve. `_lifted_shoulders` now caps the side wall there all round (`RAISED_WALL`, smooth fades at 1.10 and 1.29 m) before the shoulder ball is added. The shoulder ball was not the cause.
    - **Leg spots:** spots taken from the front view are painted straight from it (`approved_views.front_direct_decals`, `_paint_direct`): the leg matched to the drawing's leg row by row, as seen from the front, instead of the round-20 unwrap, which stretched the inner-thigh and outer-knee spots. White spots on a drawn leg's outer edge read as backdrop, so the drawing's leg outline is straightened first (`_leg_rows_smooth`: the outermost edge over 9 cm, ignoring rows merged with a glove) and the spots are cut out against it (`_front_paint`). Two small spots just under the briefs at the outer hips (`FRONT_TOP_SPOTS`) are taken from the drawing by paint detection and moved down `FRONT_TOP_DY` (5 cm), because the model's briefs come lower on the outer thigh. Fragments seen only at grazing angles and the left view's copy of the outer-knee spot are dropped (`DROP_SPOTS`). The paint in the drawing is mid-grey (luminance 110–140), not white.
    - **Black spots:** the patch at the back of the cow's left armpit and a sleeve patch under that arm (`PATCH_REMOVE`; it now matches sleeve patches too).
    Before/after: `reviews/round_31/`.
32. Two small edits. The sides of the neck looked like a fur-textured head; the hood should fan out a little (subtly). The front of the belly and the udders were very slightly too big.
    - **Hood flare:** `design.HOOD_FLARE`: the hood's neck widens smoothly from 1.46 m down to 1.383 m by up to 2.2 cm at the sides, about half that at the back and hardly at the front (under the mask's chin), so it lies over the suit's neckline like a balaclava's neck spreading onto the shoulders.
    - **Smaller in front:** each `GLOBE` is 1 cm less deep and 4 mm less wide and tall; the `SACK` front is about 1 cm less forward from 0.82 to 1.06 m. The side widths (the pear shape) are unchanged.
    Round 31 is kept beside it. Before/after: `reviews/round_32/`. The owner's screenshots and photos for rounds 26–31 are in the handoff's `Reference_Photos/round_26_to_32/`.
33. A proportion check against the original 2012 shoot only (the owner: not the Gemini views or later shoots). The photos are dated by their EXIF (30 Nov–1 Dec 2012, Leaf Aptus 22): the 20 "Cow - Original Photo Shoot" images and the `MisCow_original2012HasselbladShoot__*` files. `SHOULDER REFERENCE ONLY.jpg`, `IMG_2236.JPG` and `Nathan 32.jpg` are from 2014 and were left out. Each standing shot was scaled by its floor and crotch (where perspective matters least); the camera was close and above, so things high up read large, and local ratios (cups against each other, the belly, the mask) were preferred.
    - **Matched:** leg widths knee to ankle (within 1 cm), hip width, belly width at 0.97 m, the udders' tops, the mask's size against the udders, the arms' length.
    - **Udders:** from the front the pair was wider and flatter than in every photo (width/height 2.1 against 1.9–2.0). Each `GLOBE`'s outer side is 7 mm further in (the inner sides still press together) and its bottom 1.5 cm lower, the top unchanged; the teats follow (`TEAT_SPECS`: the lower ones 1.2 cm lower, the outer ones 7 mm lower and 6 mm further in). From the front the cloth's lower edge only shows about 0.5–1 cm lower: the belly's top hides the rest.
    - **Hem:** 10–12 cm of the briefs shows under the front of the belly in shots 2, 4 and 5; round 32 showed 8 cm. `hem_height` now takes `HEM_BASE`, `HEM_TILT`, `HEM_SIDES` (0.83, 0.02, 0.015; round 32: 0.81, 0.025, 0.01): 0.81 m at the front, 0.845 m at the sides, 0.85 m at the back, under the bow (0.869 m).
    - **Head** (the owner asked whether its size or position was off): scaled by the udders, the mask (a scan, so its size is real) comes out about 15 % larger than in shot 0071 and 5–12 % smaller than in shot 7, so its size is within what the photos can tell; its height over the udders matches standing shot 7 within about 1 cm (seated shots push the udders up towards the chin). The hood is what differs in both: the photos show 1.5–3 cm of fur beside the mask, where the model's hood hardly shows past it, and the neck under the snout is about 20 cm wide against the model's 15–17 cm (its 12.6 cm hood neck flaring where it meets the suit). Not changed in round 33; offered to the owner. Sheets: `reviews/round_33/`.
    Round 32 is kept beside it. Before/after: `reviews/round_33/`.
34. The hood fuller round the mask (the owner, after the round 33 head check), and a hard angular bit at the top of the chest under the chin (the owner's screenshot).
    - **Hood:** `HOOD_HEAD_R` (0.112, 0.122, 0.104; was 0.090, 0.118, 0.099), `HOOD_NECK_R` (0.084 at the bottom, 0.076 at the top; was 0.060, 0.064) and `HOOD_FLARE_R` (0.082; was 0.063). From the front the hood now shows about 1–2 cm beside the mask on each side at eye level (1.50–1.54 m), and the head and neck under the snout are 18.7–19.6 cm across at 1.38–1.42 m (round 33: 14.5–16 cm; the 2012 shots about 20 cm). Outside the mask's outline the hood's front no longer stops flat at the rim's plane: it rolls back `HOOD_ROLL` (30 × the distance outside the outline squared, at most 3 cm), so the fur framing the mask is rounded.
    - **Chest top:** the neckline was cut flat at 1.345 m across the front (`tripo_suit_parts`), where Tripo's chest stands 10–11 cm forward: from the side a ledge ending in a hard corner just above the udders (on the centre line the front jumped from 2.7 to 10.4 cm forward within 2 cm of height). `_round_chest_top` adds a dome in front of the neck (`CHEST_DOME`: a quarter ellipse from the neck at 1.38 m down to the chest's front at 1.26 m, 12.5 cm deep) that fills the ledge and trims the corner, fading out towards the shoulders by |x| = 0.15 m and below its base (`CHEST_DOME_FADE`: gone about 5 cm below it), and doing nothing behind the front of the neck. Its fill's base is rounded and stays inside the chest. Two tries went wrong: with the fill's widest part at its base it left an 8 mm ridge between the udders at 1.26 m, and a trim that faded too weakly below the base cut a slot down the middle of the belly. Check any change to it against the body without it over the whole torso (a voxel comparison): in round 34 it changes only 1.24–1.39 m, |x| < 0.09 m, in front of the neck. The front on the centre line now runs 3.9, 6.9, 8.7, 9.6, 10.1, 10.2, 10.6, 11.4, 12.4 cm forward at 1.36, 1.34, 1.32, 1.30, 1.28, 1.26, 1.24, 1.22 and 1.20 m. It stays about 2 cm clear of the mask's jaw; the udders are added after it and are unchanged.
    Round 33 is kept beside it. Before/after: `reviews/round_34/`.

## Where things are

Rounds 19–24 added these modules and functions (everything else is as in round 18, listed further down).

- `pipeline/textures.py`: `fit_projected_patches` fits the shag patches from the approved views; `PATCH_REMOVE` / `PATCH_ADD` (round 30) edit them.
- `pipeline/tripo_body.py`: the body. It loads `assets/tripo_body.npz`, which was made once by `tripo_body_volume.py` from the owner's Tripo OBJ. The OBJ is not in this folder; the owner has it.
  - The torso volume is smoothed by about 16 mm.
  - `fitted_torso_sdf`: the outline fit to the Gemini views, per height.
  - `SACK` and `sack_sdf`: the stuffed midsection.
  - `stuffed_torso_sdf`: the smooth union of the sack and the chest, starting at 1.06 m.
  - `body_legs_sdf`: the legs at the photo length.
  - `sleeve_sdf`: tubes along Tripo's arms, using Tripo's radius profile.
  - `ARM_RAISE` and `arm_rotation`: the arms-raised pose.
  - `leg_section`.
- `pipeline/design.py`:
  - **Head:** `tripo_suit_parts` builds the shoulder slope and neckline. `HEAD_DZ` (0 since round 27) is how far forward the head sits. `HEAD_PITCH`, `HEAD_LIFT`, `head_pose` and `head_unpose` place the head; the cowl is in `head_parts`.
  - **Legs:** `_person_hips` and `THIGH_*` for the person's hips and thighs; the seat cheeks; `SHIN_*` and `ANKLE_R`. These are all in `tripo_legging_parts`.
  - **Udders:**
    - `PANEL` holds the outlines; `pillow_h` is the stuffing height. It is steep only along the bottom, and fades where the chest faces sideways.
    - `chest_base` is a smoothed chest heightfield, and `cloth_sdf` is the cloth surface built on it.
    - `cup_solid` is the cup solid, limited to the chest. `pink_sdf` is the visible pink outline. `with_cups` sinks the fur under the cloth.
    - `udder_sdf` is the cloth shell plus the teats.
    - `GLOBE`, `globe_sdf` and `globes` (round 28): the cups as stuffed globes; `cup_solid` returns them, and `pink_sdf` is pink wherever a globe stands outside the body (`_pink_panel` keeps rounds 24–26's outline, used only to keep shag patches off where the pink was). `GLOBE_CAP` would add a fur cap; `GLOBE_GAP` is the fur strip between the cups (round 29). The panel functions (`PANEL`, `pillow_h`, `chest_base`, `cloth_sdf`) now only place the teats' positions.
    - `TEAT_SPECS` holds the teat positions (panel coordinates), directions, lengths and droop; `_tripo_teats` seats them on the cloth.
  - **Lifted arms:** `_lifted_shoulders` trims the arm stub to a rounded shoulder ball.
- `pipeline/approved_views.py`: the Gemini views in model coordinates.
  - `profiles` gives the outline profiles.
  - `Occluders` holds per-view depth maps.
  - `project_patches` projects the black patches; `textures.fit_projected_patches` turns them into ellipses.
  - `spot_decals` and `paint_decals` handle the leggings' spots.
- `pipeline/textures.py`: `fit_projected_patches` and `_markings_cache`. The arms-raised build reuses the arms-down markings, turns the sleeve patches with the arms, and moves the armpit patches onto the body side.
- `pipeline/review_tools/`: the round 19–24 build (`build_static.py`) and the review tools. See their README.
- `reviews/rounds_19_24/`: before/after and Gemini/photo comparison sheets for every round.
- `references/approved_views/`: the four approved Gemini views.

**Round 18 modules (the rigged pipeline)**

- `Cow_v10/pipeline/`:
  - `design.py`: the body as signed-distance primitives:
    - the mask/hood/tube placement (`MASK_SEAT`, `TUBE_C`, the mask-rim Fourier fit);
    - the shoulder pivot (`arm_points`);
    - the legs (`THIGH_OUT`, `THIGH_R`);
    - the back-fat roll and the suit's hem;
    - the udder (`udder_sdf`).
  - `garments.py`: meshes and UV charts for the suit, hood, tube, sleeves, leggings, briefs and udder.
    - The briefs are `build_briefs`: the leggings' triangles over the hips, seat and crotch, subdivided once, lifted 1.2 mm along their normals and cut along `leg_line` (a periodic spline per thigh, `LEG_LINE`) with an exact iso-line cut (`clip_mesh`). Each vertex carries the leggings' skin weights from the point under it. The leg openings get a rolled hem that tucks down onto the leggings. Only the largest connected piece is kept.
    - It also blends the shading normals at the sleeve/torso junction, only near the shoulder (`junction_normals`, `reach`).
  - `gloves.py`: places the owner's gloves on the hands (three meshes per hand, rigid in the hand frame), with the thumb weights (`THUMB_A`, `THUMB_U`) and its hinge, the palm-top weights that follow the toes, and the toe pivot from `gloves_hoof.json`. The earlier procedural gloves remain as a fallback.
  - `tail.py`: the bowtie, the cord and plug meshes, and the rope simulation.
  - `textures.py`: the shag patches and legging spots.
  - `groom.py`: grows the shag strands (undercoat and locks) on the patches.
  - `assets.py`: the kept v09 parts (mask, horns).
  - `assemble.py`: puts the static model together (including the briefs' contact shadow on the leggings).
  - `rig.py`: the 58-joint skeleton (40 body joints, the tail bow, 12 cord segments and the plug, the two hem helpers and the two ring-little hoof toes) and all the skin weights. The new joints are appended at the end, so earlier joint indices are unchanged.
  - `anim.py`: the solver:
    - arm IK/FK with soft reach and a collision-aware elbow swivel (Viterbi);
    - continuous wrist twist;
    - foot IK;
    - baked springs for the belly, cups, shag, teats, hooves and thumbs;
    - the tail rope;
    - the Chicken Dance.
  - `clips.py`: every other animation, plus `lumbering()`, which turns any clip into its alt version. `SitCrossLegged` keeps its seated layout in class constants (`SEAT`, `STAND`, `DROP`, `BACK`, `LAP_OFF`, `SUPPORT`).
  - `validate.py`: the per-clip metrics, including belly into legs and legs into belly (`leg_body_metrics`). The legs-into-belly reading is high in every walking clip too (45 mm in Walk) because it counts the tops of the briefs and leggings tucked under the hem; use it only as a before/after comparison.
  - `build_v10.py`: builds everything and writes the GLBs, the validation JSON and `rigged.pkl`.
  - `render_reviews.py` and `render_dance.py`: review images and videos, drawn by a CPU rasteriser (`raster.cpp` / `render.py`).
  - `web_textures.py`: downscales textures inside a GLB for the web copies, keeping the skin and animations byte for byte.
  - `hoof_gloves.py`: the one-off conversion of the owner's glove model into `assets/gloves_hoof.glb` (real size, hand frame, hoof base 10.3 cm past the wrist; baked AO divided out when `ao_2048.jpg` is given). Its inputs are the glove project's Part 2 (`Glove_pair.glb`) and Part 4 (`textures/ao_2048.jpg`), which are with the owner, not in this folder.
  - `tripo_gloves.py`, `repair_gloves.py`, `rebuild_gloves.py`, `tripo_slippers.py`: earlier one-off conversions of the owner's Tripo models (gloves rounds 11–16, Shy Cow slippers). No longer used; their outputs are only in git history.
  - `cow_mule_slippers.py`: the one-off conversion of the owner's slipper model into `assets/slippers_cow_mule.glb` (scaled to metres, ankle axis at the origin, right slipper mirrored).
  - `render_shag.py`: before/after close-ups of the shag (`reviews/shag/`).
- `Cow_v10/viewer/index.html`: the three.js viewer, with Light (Studio, Soft, Spotlight, No lighting) and Clay controls. Its Rounds row picks any of rounds 17, 18, 25 and 28–34 and its Compare row shows them side by side (oldest on the left) or overlaid (the newest solid, the others as ghosts in each round's colour: 17 amber, 18 blue, 25 red, 28 green, 29 purple, 30 dark cyan, 31 dark gold, 32 raspberry), with height lines. Round 18 is the main model (`mainRoot`), whose clips drive the page; round 17 (`cow-r17-meshopt.glb`) copies its clip and time every frame, and rounds 25 and 28–32 (`cow-r25-meshopt.glb`, `cow-r25-up-meshopt.glb`, `cow-r28-meshopt.glb`, `cow-r28-up-meshopt.glb`, `cow-r29-meshopt.glb`, `cow-r29-up-meshopt.glb`, `cow-r30-meshopt.glb`, `cow-r30-up-meshopt.glb`, `cow-r31-meshopt.glb`, `cow-r31-up-meshopt.glb`, `cow-r32-meshopt.glb`, `cow-r32-up-meshopt.glb`) are static. The page opens on round 32 with Idle selected. `cow-meshopt.glb` and `cow-plain.glb` are gltfpack copies of the round 18 animated GLB. The claude.ai copy of the viewer loads base64 versions of them, because that host serves only text and limits each file to 16 MB. Each base64 copy is now over that limit, so it is published in numbered parts (`cow-meshopt.b64.1.txt`, `.2.txt`); the page joins them.

## How to rebuild and check

**Round 34 static models** (about 12 minutes each at full resolution; `--quick` takes about 2 minutes):

```bash
pip install numpy scipy pillow scikit-image vtk xatlas     # plus g++ on PATH
cd Cow_v10/pipeline
export REBUILD=../../Rebuild_Inputs/project COW_MARKINGS_CACHE=../build/markings.pkl
python review_tools/build_static.py . ../build/Misanthropic_Cow_v10_r34.glb
COW_ARM_RAISE=70 python review_tools/build_static.py . ../build/Misanthropic_Cow_v10_r34_arms_raised.glb
```

Build the arms-down model first, because it writes the markings cache that the arms-raised build reads. Then:
1. Compare with the approved views: `review_tools/pair_sheet.py`, `spot_cmp.py` and `head_cmp.py`.
2. Compare with the original shoot. The comparison sheets in `reviews/rounds_19_24/` show the crops used.
3. Make the web copies:
   - run `web_textures.py <glb> <out.glb> 1024`;
   - run gltfpack 0.22 with `-cc -kn -km -ke`;
   - for the claude.ai viewer, base64-encode the result and split it into two parts under 16 MB.
4. Test the viewer headless with `review_tools/test_viewer.js`.

**Round 18 animated model:** see "How to rebuild" in `Cow_v10/README.md` (`build_v10.py`, about 40 minutes). It still builds the round 18 body.

## Next steps (the owner's plan)

1. **Rig the round 34 body.** `rig.py`, `anim.py` and `build_v10.py` were written for the round 18 SDF body. Expect to re-check:
   - joint positions: `design.J` already follows the Tripo legs and arms, and `J['Head']` follows the head pose;
   - skin-weight bands: the torso is now the stuffed sack plus the Tripo chest;
   - the udders, which are now part of the suit surface. They should move with the chest and have only a little give. The teat bones should come from `TEAT_SPECS` and `TEAT_MID`.
   - the shoulder: the sleeves should turn in the rounded shoulder (the ball-and-socket idea of round 18). The stuffed body should never fold.
   - the tail knot, which is now at 0.895 m on the sack's back.
2. **Make the animations less robotic.** The round 18 clips are sine-based, procedural motion. One option is motion capture from the owner's own video.
3. Offered earlier and not yet done: lace side panels on the briefs, as in the Gemini views and the shoot.

## Known open items

**Round 34 static model**
- Front-view leg spots are painted as seen from the front; on the sides of the legs they fade out where the leg turns away from the front (round 31). The mid-thigh spot on the cow's left keeps a short straight edge at its lower right, from the drawing's leg outline there.
- The shag patches no longer all come from the approved views: `PATCH_REMOVE` and `PATCH_ADD` edit them from the owner's photos (round 30).
- The udders are full pink globes (round 28); the approved Gemini views and the empty suit show white fur over their tops.
- The head and hood no longer match the approved Gemini side views: they draw the head further forward and the hood's back falling straight to the shoulders. The owner preferred rounds 17/18's (rounds 26–27).
- The Gemini views disagree with each other about the 3D positions of some leggings spots. Front and back match closely; the side views are close but not exact. The view facing a spot most squarely wins.
- The stuffed sack meets the Tripo chest at about 1.06–1.12 m. It is smooth now, but any reshaping of the sack's top rows (`SACK` 1.06–1.22) needs a check from the back with the arms raised.
- The arms-raised pose is a separate static build at 70°, not a rig pose. Its armpit fur patches are moved onto the body side by a heuristic (`textures._raise_sleeve_blobs`).
- The udder cloth is a separate mesh per side, because the mesher keeps only the largest connected piece.
- The viewer's "Default pose" caption is hard to read on the dark backdrops.

**Round 18 animated model** (unchanged)

- **Sit Cross-Legged:** the leggings stretch up to 4.6× at the seat (the deep seated hip bend); the tail plug lies on the floor, 0.4 mm into it.
- **Run and Sneak:** the belly meets the tops of the thighs at the highest knee lift (16.5 and 21 mm; 19 and 20 mm in the alt versions; 20 and 33 mm before round 18). The hem helpers could take that up (set `p['hem']` in those clips and check the torso stretch); left off so those clips stay as they were.
- **Teats:** they dip into the belly in a few clips: 2.1 mm in Sit Cross-Legged, 2.5 mm in the Chicken Dance, 3.6 mm in Run (alt), 2.0 mm in Sneak (alt) and 5.6 mm in the alt Chicken Dance.
- **Sit Cross-Legged (round 18):** the side of the hem touches the thighs a little more on the way down and up (visible 99.5th percentile 3.1 mm; 2.5 mm at quick resolution before), and the sleeve stretch rose from 2.00× to 2.11× as the hooves reach the higher knees. The leggings now pass less into the belly there.
- **Proportions:** the bottom of the belly may sit 2–3 cm higher in the photos than measured (the camera was above it and it stands closer to the lens than the legs).
- **Claps:** with the round-17 gloves the palms stop 2.1 mm apart (they touched before), and in the alt Chicken Dance each glove brushes the other hand's sleeve end by 1.4 mm. The claps are placed from the glove's 99.5th-percentile palm thickness (`build_v10.py`); moving the hands closer pushes each glove further into the other sleeve.
- **Glove spread** is used only in Exasperated's fling so far.
- **File size:** the animated GLB is 95.5 MB, near GitHub's 100 MB per-file limit, mostly the gloves' 4K maps. Dropping those to 2K is the easy way to make room.
- **Mask side view:** the side-jaw photo projection on the mask is stretched in pure side views (inherited from v09).
- **Shag:** strands don't collide with the arms. A few strays on the small elbow patches splay out a little.
- **Briefs' fallback copy:** the simplified web fallback (`cow-plain.glb`, gltfpack `-si 0.3`) thins the shag strands; the full-detail copy keeps them all.
- **Photographed textures** (mask scan, fabric swatches) keep whatever light was in their photos.
- **Slipper colour map** has the slipper project's ambient occlusion baked in (at 0.6). Remove it with that project's `ao_4096` map (its Part 3) when the owner supplies it.
- **Tail:** the cord collides with the seat, legs, slippers and floor, but not with the arms or itself.
- **Root motion:** locomotion plays in place.

## Working notes

**From rounds 19–24**

- **Blending two shapes:** never average two SDFs to blend shapes (a lerp of distances). Where the surfaces disagree it makes hollows and creases; that was the fold on the back. Use a smooth union or a smooth max, after cutting one shape off.
- **Heightfields:** a heightfield written as `z - f(x, y)` is not a distance where the surface slopes. Divide by `sqrt(1 + |grad f|^2)` (as `cloth_sdf` does), or thin layers on the slopes break up.
- **Surfaces that must meet flush,** such as the fur and the udder cloth, need the same underlying function. Two "almost equal" surfaces cross each other and come out patchy.
- **Mesh pieces:** `garments.mesh_from` keeps only the largest connected piece. Mesh separate pieces one at a time.
- **Rigid moves:** move a rigid group, such as the head, as a whole. Pose the asset vertices, and evaluate its SDFs at un-posed points (`head_pose` / `head_unpose`).
- **Lifted arms:** keep the stuffed body rigid. Trim only outside the body's side wall: a half-space trim cut into the chest side and made a pinch, and a plain cylinder trim cut through the chest and left pockets and slivers (holes, round 25b). Check cross-sections of `torso_sdf` at 1.10–1.22 m, and count enclosed pockets with `binary_fill_holes`.
- **Approved views:** their side outlines include the hanging arms, so smooth fits over about 4 cm. Their white backdrop shows between the legs; it is excluded from the spots by removing pure-background pixels. Paint in shade is mid-grey (luminance about 95–140).
- **Build times:** quick builds take about 2 minutes and full builds about 12 minutes per pose. The CPU renderer (`render.py`) gives comparison sheets in seconds.
- **The claude.ai viewer's size limit:** one version may hold at most 256 MiB of files. With rounds 17, 18, 25, 28 and 31–34 it holds about 246 MB (rounds 29 and 30 were taken off the published copy in rounds 33 and 34 to make room; they are still in `viewer/` and git, and the published page has no buttons for them); the simplified round 18 fallback (`cow-plain.b64.*.txt`) was removed from the published copy in round 32 to make room (it is still in `viewer/` and git). Each further round adds about 34 MB, so drop an older round's files (both poses) from the published copy first.
- **The claude.ai viewer** is published from a copy of `viewer/index.html`, with base64 model parts named `cow-r32-meshopt.b64.1.txt` and so on. Each viewer round adds or renames its files (r19 → r25, then r26, r27, r28 beside r25, r29 beside r28, r30, r31, r32, r33, and now r34, with r29 and r30 dropped): rename the keys in `index.html` (`ROUNDS`, `COLORS`, `NAMES`, `FIGS`, `GUIDES`, labels and the round buttons) with them.

**From earlier rounds**

- Every clip is baked at 30 fps and loops seamlessly. The physics is simulated over three loops and the last one is kept; the tail rope's last loop is cross-faded into the one before it.
- After any geometry change, check the torso stretch. Arm-following weights on the torso near the shoulder tore it badly once. The shoulder cap is a ball centred on the arm pivot, which is why it can follow the half-rotation helper without tearing.
- Keep body-shape changes local. Widening a blend everywhere (round 11's first belly try) grew the belly under the cups and made the teat and arm contact worse. Compare cross-section widths before and after.
- The elbow-swivel collision cost is measured relative to the rest pose, because the relaxed arms already rest against the padded body.
- The glove-into-body metric counts only points within 4 cm of the body surface; without that limit, far hoof tips give false readings. The clap check is the smallest glove-to-glove distance at the four clap frames.
- The plain body/legs readings (`body_into_legs`, `legs_into_body`) count hidden geometry: the tops of the leggings and briefs inside the suit, and the backs of the cups against the chest. Judge clipping by the `visible_` readings (round 18), which count only surface that shows at rest.
- The SDF meshing grids are fixed in space; moving a part by a fraction of a grid step changes how thin creases are triangulated and can move the stretch percentiles by several per cent. Move parts by whole grid steps when comparing before/after (leggings 4 mm, suit 4.2 mm at full resolution).
- Body/legs clipping work goes fastest with a static test bench: pose a clip without springs, skin only the parts you measure, and score depth into the other surface by nearest vertex and normal, masking what already overlaps at rest. Bound KD-tree queries (`distance_upper_bound`); unbounded queries from far-away points are very slow.
- Driving a corrective bone automatically from joint angles changed other clips (the hem helper stretched the hem in Run and Sneak); gate such helpers per clip.
- Mesh bounds: every `mesh_from` box must contain the whole surface, or the mesh is left open where it is cut. That is what left holes in two teat tips.
- Never write the web copies with a generic GLB reader/writer: one dropped the skin and animations. Use `web_textures.py`.
- Never bake lighting into the model (vertex colours or textures). It was removed in round 12 at the owner's request.
- The CPU review renderer has no anti-aliasing, so single shag strands stair-step in the standard review renders; `render_shag.py` renders at 2x and downsamples.
- To check the real viewer without a GPU, headless Chromium with SwiftShader works. Serve three.js from a local npm copy if the CDN is blocked.
- When copying review videos into the project, wait until `render_dance.py` has finished. Round 10's videos were once copied mid-render.
