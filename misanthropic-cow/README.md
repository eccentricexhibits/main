# The Misanthropic Cow, v10

v10 rebuilds the body and the rig of the 3D Misanthropic Cow. The body follows the proportions from the original 2012 Hasselblad shoot. The rig fixes the Chicken Dance problems in v09: the "wings" that grew under the armpits, and the hands that came loose from the sleeves.

Later v10 passes added:
- the head rebuilt from the mask and hood photos;
- the shag rebuilt on the user's own swatch and tuft sheet;
- clipping fixes at the arms and teats;
- light baked physics;
- a rounded belly underside;
- an animation library: Idle, Walk, Run, Sneak, Jumping Jacks, Look Around and the Chicken Dance;
- the mask seated on the hood, shoulders that grow out of the body, and the shag tufts rebuilt from the user's long-lock sheet;
- four mood animations (Depressed Walk, Sit Cross-Legged, Crying, Exasperated) and an "alt" set that plays the first seven heavy, awkward and slumped;
- a pass informed by two models the owner made with Tripo (see "Tripo references" below): Blue Shirt's udders, belly and hips, Shy Cow's hoof hands, folding sleeves and slippers;
- the black shag regrown as real strands (clumped, tapered fibre tubes over a short undercoat) instead of flat lock cards, which read as feathers;
- round 18: the proportions re-measured from the two full-length photos of the original shoot, which lengthened the legs by 4 cm and raised the bottom of the belly by 7.6 cm at the front (see "Round 18 proportions" below).

| File | What it is |
|---|---|
| `models/Misanthropic_Cow_v10.glb` | Static master in the default (rest) pose. 1.40M triangles (310k of them the shag strands, 300k the slippers, 200k the gloves, 120k the briefs), real-world scale in metres, all textures embedded. |
| `models/Misanthropic_Cow_v10_Animated.glb` | Same model with a 58-joint skin and 18 looping animations at 30 fps (11 animations plus 7 "alt" versions), all with baked physics. |
| `reviews/` | Turntable and close-up renders, the before/after sheet, the head-vs-photo sheet, the animation sheets, the dance pose sheet, the Tripo comparison sheet (`Tripo_References_vs_v10.jpg`), the showcase video, the standard-vs-alt video and the validation JSON. |
| `viewer/` | A three.js web viewer with an animation picker, a Standard/Alt toggle, a Default pose button, camera presets and a clay toggle. |
| `textures/` | The user-supplied black shag swatch (under the strands), the first tuft sheet and the long-lock sheet. The two sheets were the lock cards' textures; the strands no longer use them. |
| `assets/` | `slippers_cow_mule.glb`: the owner's own model of the costume slippers, open-back cow mules (made by `pipeline/cow_mule_slippers.py`). `gloves_hoof.glb` and `gloves_hoof.json`: the owner's own model of the costume gloves, a terry mitten with a thumb and two painted hoof toes (made by `pipeline/hoof_gloves.py`). |
| `pipeline/` | The Python sources that generate everything above. |

Both GLBs pass the Khronos glTF Validator with 0 errors and 0 warnings.

## What changed from v09

**Proportions.** The proportions were measured from the 2012 shoot photos:
- belly width is about 2× the mask width;
- muzzle-to-crotch is about 3 mask heights;
- the crotch is at 46 % of standing height.

The wearer is built at about 1.60 m. v09 had scaled the whole figure to fit an oversized mask, which gave it broad, square shoulders and a short barrel torso. v10 instead scales the scanned mask to 0.75 (about 0.21 m wide). The body has narrow, sloped shoulders and a long, round padded belly that hangs to the crotch. Pink satin panties show under the belly, as in shots 0077, 0120 and 0191.

**Round 18 proportions.** The owner asked for the proportions of the original photo session only: the costume was later worn by other people, restuffed, and worn with a replacement pair of briefs, so photos from later shoots inform details (spots, textures) but not proportions. Two photos of the original session show the whole standing figure: 0077 and "Cow - Original Photo Shoot (5 of 15)" (the same session, mask off). Measured as a share of the wearer's height, crown to floor:

| | Crotch | Bottom of the belly (front) | Briefs showing under the belly |
|---|---|---|---|
| Shot 0077 | 45.1 % | 52.2 % | 11 cm |
| Shot "5 of 15" | 47.9 % | 53.1 % | 8 cm |
| Round 17 model | 43.7 % (0.708 m) | 47.9 % (0.767 m) | 6.6 cm |
| **Round 18 model** | **46.7 % (0.747 m)** | **52.5 % (0.840 m)** | **9.3 cm** |

- **Legs:** 4.0 cm longer (`design.LEG_LIFT`). The leg chain stretches evenly from the ankle to the hip joint; the hips, pelvis, seat, back-fat roll, briefs (leg line and waistband), tail knot and the rig's hip and leg weight bands all move up with them. Everything from the waist up is unchanged, so the wearer stays 1.60 m. The lift is exactly ten steps of the leggings' 4 mm meshing grid: at 3.8 cm the gluteal fold was meshed half a step differently and its thin triangles stretched 3–9 % more in every animation.
- **Belly:** its bottom is 7.6 cm higher at the front (`design.HEM_LIFT`). Only the lower half of the belly is shorter (`design.ellipsoid_low`); its upper half, under the cups where the teats hang and the arms rest, is exactly as before. The extra front lift fades out round the sides (`HEM_SIDE`), so at the sides and back the hem keeps its round-17 place relative to the hips: it stays clear of the thighs when they swing up, the briefs' side panel shows under the hem as before, and the approved back is unchanged.
- **Belly patch:** the black shag patch below the udder is centred on the belly, its top under the teats, as in both photos (centre 0.96 m; at 0.875 m it sat on the hem, and its locks would have hung over the briefs once the hem rose).
- The camera in both photos is above the waist, and the bottom of the belly stands about 30 cm closer to it than the legs, so its true height may be 2–3 cm above the measured one.
- Reference: the Tripo model made from four generated views (round 18) has the crotch at about 40 %; the generated front view itself has it at about 44 %, so the 3D reconstruction, not the drawing, shortened the legs. Its udder cups are about 20 % shorter and sit 4 cm further back than the photos show; v10's cups already match the photos (pair width 0.88 of the belly's, height 0.51), so they are unchanged.

**Head.** The head is built as the costume is worn, following the mask and hood photos (`IMG_2003`–`2034`, `0006`, `0013`, `0014`, `Nathan 32`). There are three separate pieces:
- **Hood.** A snug fur balaclava, about 2 cm of fur over a 1.6 m wearer's head. Its neck tucks into the torso garment's neckline, which stops at the base of the neck. The head is skinned only to the Head and Neck bones, so it turns freely without dragging the torso up into a hump.
- **Mask.** The scanned papier-mâché mask covers the hood's whole front, and its rim sits on the hood all the way round. The mask, tube and horns were pushed 2.5 cm back as one rigid piece, so the tube and horns keep exactly their size and placement relative to the mask. The hood has a padded face opening shaped to the mask's outline: the outline is a Fourier fit to the scanned rim, with an rms error of 1.3 mm. Just behind the rim the opening is 2 mm inside that outline, and it tapers back into the head. Earlier the rim floated 2–7 cm in front of a plain egg-shaped hood, which showed as a gap from the side.
- **Tube and horns.** The fur-covered cardboard tube that joins the horns belongs to the mask. It sits directly on the mask's arched top edge, as in the photos of the mask laid out with its horns: its underside rests on the rim at the crown. The scanned horns ride on its ends, within a few millimetres of their scanned positions. In the previous pass the tube sat 2 cm behind the rim, with a band of hood showing between them.
- **Back of the head.** The hood's dome is 2 cm shallower front to back and a little narrower and lower, so the back of the head no longer bulges behind the mask.

The white paint in the mask photo gets a lift; the eyes, the muzzle and the weathered grey wash keep their colour.

**Udder, shag and leggings.**
- The udder is two large, soft, stuffed-cloth pink cups. Each has one teat hanging forward over the belly and one pointing out and down. Following the Blue Shirt reference, the cups:
  - are pillows wider than they are tall, each about 22 cm across as in the photo, hanging low on the chest and pressing together in the middle;
  - settle into a lobe that hangs forward and down, so from the side each cup is a teardrop with the bottom teat at its lower front tip;
  - are hand-made and not identical: the character's left cup is slightly larger, lower and further out, and the teats sit at different angles on the two sides;
  - have teats that stand out about 7 cm, with the cloth puckered in radial folds round each teat where it is sewn on.
  - are closed at every teat tip. The two forward teats used to reach past the edge of the volume the udder was meshed in, which left a hole in each tip.
- The black shag follows the patch layout in the photos:
  - upper chest and shoulder on the wearer's right;
  - the belly, centred under the teats (round 18; it sat on the hem before);
  - both elbows;
  - upper back right and lower back left.
- Under the strands, each patch is painted on the suit from the user's black shag swatch (`textures/black_shag_tile.jpg`), with edges that break into hanging tufts. It is painted at half brightness: only the black backing shows in the gaps between strands, and the swatch photo is lighter than that.
- The shag itself is grown as strands (`groom.py`), about 15,000 of them in two layers:
  - an undercoat of short strands (1.4–2.6 cm) in loose clumps of 5–8. They stand off the suit at 40–80° in all directions and give each patch its matted volume;
  - long locks (4.5–7.6 cm) over it. Each lock is a clump of 8–12 strands that root in a disc 7–13 mm across, leave the suit at 30–62°, droop under gravity with a gentle wave, and gather toward the tip. About one strand in eight is a stray that stays loose and kinks outward, which breaks up the outline the way the costume's fur does.
  - Toward a patch's edge the locks get shorter and flatter, so the strands end where the painted patch does.
- Each strand is a solid 3-sided tube, about 1 mm across at the root and tapering to a point. It has no texture and no alpha cut: its round shading does the work, and each strand is a slightly different black. Every strand point is kept outside the body, belly and cups, so long locks never dive into them.
- The strands replace hanging lock cards, which were flat panes alpha-cut from the user's long-lock sheet (`textures/black_shag_locks_sheet.png`). However they were laid, their outlines and the grey highlights in the photo read as feathers. `reviews/shag/` compares the two from six views.
- The strand material is near-black with little specular and no sheen. In the viewer's room lighting, thousands of thin glossy tubes otherwise catch light from every side and the black turns charcoal grey.
- Each patch belongs to one garment piece only, so no patch spills across a sleeve seam.
- The leggings use smaller, irregular painted white spots.
- The belly's underside is a shallow bowl with a soft edge, so it reads round from below instead of sliced flat.
- The sides of the belly are rounded off (owner's note). Below the waist the belly blends into the sides with a wider, softer join (above it, under the cups, it is unchanged), and the suit's hem rises more gently round the sides, so the bottom of the belly stays round from the side instead of being cut off on a steep diagonal. At the back the hem still tucks under the roll of back fat.
- The belly is fuller and sits lower and further forward (Blue Shirt), and sags over the panty waistband in a soft fold across the front. The hips and the tops of the thighs are about 3 cm wider, so the panties stretch across a broad seat.
- **Legs.** The legs are separated a little more (owner's note). Each thigh's axis sits 2.4 cm out from the hip joint, and the thigh is slimmer at the top, so the hips keep their width while the inner thighs part below a natural crotch at about 0.75 m (0.71 m before round 18), as in the Blue Shirt photo. Before, the thighs overlapped down to 0.66 m and left only a narrow slot below.
- **Briefs.** The briefs are grown from the leggings' own surface (`garments.build_briefs`). They are the leggings' triangles over the hips, seat and crotch, subdivided once and lifted 1.2 mm along their normals. Each briefs vertex sits over a point of the leggings and takes exactly that point's skin weights, so the briefs wrap the leggings in every pose and move with them. Until round 13 they were a separate, looser surface 4.5 mm out, weighted from the six nearest leggings points, and they stood off the tights like a floating lip.
  - **Leg line:** one smooth closed curve round each thigh, a periodic spline of its height by angle about the thigh (`LEG_LINE`), so the openings have no corners anywhere. It is cut like full briefs, following the owner's photos and videos of the same kind of briefs worn over black tights. It runs low under the crotch, rises diagonally across the front of the thigh to the side, and at the back runs diagonally from the gluteal fold up across the cheek. The back keeps the shape the owner approved in round 9. The side sits at about 0.84 m (0.80 m before round 18), below the suit's hem, so the side panel shows under the belly from the front and the side, also while walking. Until round 13 the front rose to 0.87 m at the hip, under the hem, and a box-shaped gusset met the leg lines in sharp corners. `reviews/v10_briefs_before_after.jpg` compares the two.
  - **Crotch:** the leg lines meet under the crotch, so the briefs cover it and show pink when the legs spread (Jumping Jacks). Along the centre of the back the line drops by up to 4.5 cm (`MID_DROP`, within about 2 cm of the midline, behind the crotch only), so the back panel runs down the cleft into the crotch in one piece. In round 13 it stopped in a V above the cleft and the briefs didn't connect in the middle.
  - **Fabric cues:** the leg openings are finished with a rolled elastic hem about 5 mm wide and 1.2 mm proud, and the hem tucks down onto the leggings, so the edge never shows a gap. The fabric just inside the hem is gathered into small ruches, a few shallow tension wrinkles fan out from the crotch, and the fabric weave has the same fine scale everywhere. The briefs stay a separate surface rather than a texture on the tights, so the hems stand up as real edges.
- **Tail.** A gold satin bowtie is tied on at the back, on the roll of back fat at the bottom of the white fur. It has two puffed, pleated wings flaring from a pinched centre knot and is about 12 cm wide. A tan two-core lamp cord hangs from the knot to about mid-thigh, 43 cm, and ends in a two-prong plug with brass blades (`tail.py`).
- **Back.** The suit's back isn't flat: a padded roll of back fat across the lower back bulges out and overhangs the panty waistband as a lip, and the back hem tucks under it.
- **Sleeves.** The fur sleeves are roomy and fold the way the costume's do (Shy Cow): soft, uneven folds gather round each elbow, deepest in its crook, the cuff bunches above the glove, and the rest of the sleeve has a loose drape.
- **Slippers and socks.** The slippers are the owner's own model of the real handmade prop (round 15, from their slipper project's "v3 fabric" GLB; `pipeline/cow_mule_slippers.py`). They are open-back mules, 27 cm long:
  - a white plush muzzle with a stitched black smile and magenta nostrils, bead eyes on the seam, two stubby tan velour horns, floppy black-and-magenta ears with a pearl on each;
  - a cream mop-chenille head with black chenille patches, a shaggy black chenille fringe round the sole, and a flat black plush footbed open for the rear ~42 %;
  - one 150k-triangle mesh with the project's 4K baked colour, roughness and normal maps. The right slipper is the left one mirrored, as in the owner's file.

  The costume is tights with black socks over the feet. Below the calf the leggings are plain black knit, with no painted spots, and a ribbed cuff that stands slightly proud. Because the slippers are open at the back, the leggings now end in a socked foot (`design.legging_parts`): the heel stands on the footbed, 1 mm into it, and the front of the foot runs into the slipper's head, where it ends hidden. Foot placement in every animation uses the slipper's real sole, so the slippers sit 2–3 mm above the floor. Until round 15 the slippers were the knitted cow heads cut from the Tripo Shy Cow model, and the leggings ended at the ankle inside them.
  - The slipper project baked ambient occlusion into the colour texture (at 0.6). That goes against the no-baked-lighting rule; it stays until the AO map from that project (its Part 3, `ao_4096`) is available to take it back out.
- **Gloves.** Since round 17 the gloves are the owner's own finished glove model (the glove project's v4, `Glove_pair.glb`), converted by `pipeline/hoof_gloves.py` into `assets/gloves_hoof.glb` and placed on the hands by `gloves.py`.
  - **What they are:** a cream looped-terry mitten with a separate terry thumb, and the four fingers in two compartments, each capped by a black painted-card toe: satin black with grey drag strokes running base to tip and a thin beaded rim. Together the toes make a cloven hoof, closed along a straight cleft. One baked 4K atlas (colour, roughness, tangent normal) covers both gloves.
  - **Parts:** each glove is three meshes, 100k triangles in all: the palm (with the thumb and the closed cuff, 60k) and two toes (20k each), each a finger compartment plus its toe cap. The right glove is the left one mirrored, as in the glove project.
  - **Size and placement:** real size, 24.7 cm from cuff to hoof tip. The hoof base (the paint edge) sits where the previous gloves' did, 10.3 cm past the wrist, and the hoof tip lands 19.1 cm past it (19.8 cm before). The closed cuff sits 5.6 cm inside the sleeve, 8–18 mm clear of the sleeve opening all round, so nothing pokes through and no gap shows.
  - **Rigging:** each toe is rigid on its own bone, pivoting on the middle/ring finger web at mid-thickness, as the glove project set them up: HoofFingers carries the index-middle toe and the new HoofRingLittle the ring-little toe. They curl together (the existing hoof motion and its spring), and a new `spread` setting parts them like a Vulcan salute; Exasperated's arm fling uses it. The top 2.5 cm of the palm follows the toe above it, split across the cleft, so the knuckle line bends with the toes instead of opening a gap. The thumb is part of the palm mesh; its lobe (beyond the mitten's thumb-side edge, `gloves.THUMB_A`) follows the Thumb bone through smooth weights and curls toward the palm about its own hinge. The cuff follows the arm like the sleeve end, so the glove stays tucked in.
  - **No baked lighting:** the glove project multiplied its ambient occlusion into the colour map at 50 %. `hoof_gloves.py` divides it back out using that project's AO map (`ao_2048.jpg`, from the live-material textures), so the grey shading on the inner walls and in the creases is gone and all shading comes from the renderer.
  - **Earlier gloves:** rounds 11–16 used the owner's Tripo model of the glove photo, cut out, closed and rebuilt as smooth solids by `tripo_gloves.py`, `repair_gloves.py` and `rebuild_gloves.py` (their assets are in the git history). The procedural gloves from before that remain in `gloves.py` as a fallback for builds without the asset.

**Wings under the armpits (fixed).** v09 split the arm from the torso with x-coordinate thresholds. Raising the elbows dragged a strip of torso flank along with the upper arm. v10 builds the sleeves as separate tubes set into the shoulder, the way the costume is sewn. The torso keeps its own complete surface, and a clavicle bone carries the top of the shoulder.

**Shoulders.** Earlier passes plugged the round top of each sleeve tube into the side of the torso, so the shoulders read as tubes. Now the torso garment carries a padded shoulder cap that blends into the trapezius and chest, and the sleeve comes out from under it. The setup works like a ball and socket:
- The cap is a ball centred on the arm's pivot.
- The sleeve's head is a narrower ball on the same centre.
- However the arm swings, the sleeve head turns inside the cap and never pokes through.
- Because the cap only ever turns about its own centre, it can follow the half-rotation helper without tearing the torso. The torso stretch in Jumping Jacks is 2.2×, against 1.8× before the cap.
- Only the outer half of the cap exists, so the armpit stays open and cannot web.

The second pass made the shoulders lower and less bulky:
- The pivot is 2.7 cm lower than in the first v10 pass.
- The cap's radius dropped from 7.1 to 6.4 cm, and it blends into the trapezius with a smaller fillet.
- The upper sleeve is 5 mm slimmer.
- The arms hang at 20° (one more degree in the Tripo pass, so the relaxed arms clear the fuller udder).

Where a sleeve meets the torso at the shoulder, both pieces are shaded with the normals of one smoothly blended surface, which removes the seam line. The blend reaches only 7.5–11 cm from the shoulder pivot. It used to reach anywhere the sleeve came within 18 mm of the torso, which in the rest pose is the whole side of the body under the hanging arm. When the arm rose, that strip kept normals bent toward where the arm had been, and the side of the belly and the inner sleeves shaded as a crease with bright spots that looked like holes. `reviews/v10_sides_before_after.jpg` shows the Claps pose before and after. The sleeve also leaves the cap at a shallow 17° angle instead of 29°.

**Hands that don't connect (fixed).** Each glove's cuff tucks up inside its sleeve end. The sleeve and the glove are weighted by the same function of position along the forearm, so they move as one. In the wing pose the fists follow the forearm instead of being bent 90° at the wrist. v08's flared cuff ring and its halo strands were removed, because at this scale they z-fought with the sleeve.

**Glitching arms (fixed).** In Exasperated, Crying and the Chicken Dance a forearm sometimes spun half a turn in a single frame. The wrist twist was read from a rotation whose sign can flip, and when the hoof was rolled far over (palms up in the fling, on the face in the face-palm), the twist given to the forearm jumped by 180°. It is now kept continuous over time. The largest forearm rotation between frames fell from 178° to 15–30° in every animation. Two other jerks are smoothed out as well:
- an elbow pop when an arm moved in from just out of reach (at the start of Exasperated's fling);
- a corner in the hands' path round the cups (Look Around, Crying and the face-palm).

Peak hand acceleration fell from 82 to 23 m/s² in Look Around, from 53 to 12 in Crying and from 38 to 18 in Exasperated.

**Clipping (fixed).**
- Each elbow swings around its shoulder-wrist line to stay clear of the udder cups and torso. The swing is chosen frame by frame from a collision cost and kept continuous with a Viterbi pass, then smoothed around the loop.
- Half-rotation helper joints at the sleeve head and the elbow keep both joints full when they bend.
- The torso just around each sleeve head follows the arm slightly.
- **Sitting.** Two hem helper bones (Hem_L and Hem_R) carry the front of the suit's hem over each thigh. When a clip asks for it (only Sit Cross-Legged does), each one turns with a share of its thigh's lift, forward or out to the side, so the hem rides up over a raised leg as the fabric would, instead of the leggings and briefs passing up through it. Their weights fade smoothly from the leg line up into the belly, which keeps the stretch low. In every other animation they stay still, so those animations are unchanged.
- **Crotch.** The leggings' leg weights used to switch hard from one leg to the other on the centre line, and the two sides were treated differently. Spreading the legs (Jumping Jacks, Run) tore that line open into a stretched panel. Now the two legs share the crotch with a smooth, symmetric blend, half each on the seam. The leggings' worst-frame stretch fell from 8.5× to 2.1× in Jumping Jacks and from 11.1× to 3.1× in Run.
- The belly's fullest point was lowered 2.7 cm and the bottom teats angled forward. This gives the teats clearance at rest, matching the dip under the cups in shots 0120 and 0071.

**Light physics (baked).** glTF has no live physics, so damped springs are simulated over three loops of each animation and the last loop is baked into the bones. It plays in any glTF viewer and every animation loops seamlessly.
- **Teats:** each teat swings on its own bone and collides with the belly. In the dance it peaks at about 20° and averages about 5°.
- **Shag patches:** six spring bones drag the strand tips, with up to about 4 cm of lag at the elbows. A strand's root follows the suit face it grows from, and its weight shifts to its patch's spring bone toward the tip.
- **Hooves and thumbs:** each hand's hoof toes (HoofFingers and HoofRingLittle, which share one spring) and its Thumb bone carry a damped spring driven by the hand's swing: its angular acceleration about the hinge and its acceleration toward the palm. The hooves and thumb lag a swing and settle after it, with a soft limit of about 13°. The Chicken Dance damps this where the hooves are posed on purpose (the beak snaps and the claps), so the claps still meet cleanly. On top of that, resting hands keep the hooves and thumb slightly curled. A slow, small curl-and-release, out of step between the hands, keeps them from looking frozen; it is a whole number of cycles per clip, so it loops.
- **Tail cord:** a 12-segment rope pinned to the bowtie, plus a 13th segment for the plug. It has gravity, damping and a little stiffness, so a lamp cord never folds sharply. It collides with the seat, thighs, shins, slippers and the floor, with friction, so it swings behind the walk and drapes over her seat and the floor when she sits. Every segment keeps its exact length: the plug tips over and lies down rather than poking through the floor. The rope is simulated over three loops, and the last loop is cross-faded into the one before it, so its end state meets its start and the animation loops seamlessly.
- **Belly and cups:** they jiggle; the cups are kept from sinking into the belly.

## Tripo references

The owner tried a different modelling approach with Tripo and judged two results. Only the parts the owner singled out were used. Everything else was ignored: the head, the back, Blue Shirt's shirt and hat, and the stuffing poking out of its belly.

- **Blue Shirt** (from shoot 0120). The owner praised:
  - the size of the belly and the udders;
  - the teats' size and position;
  - udders that are somewhat asymmetrical, with teats that don't line up exactly;
  - the fluff and udder texture;
  - hips and thighs whose width shows as the panties stretch over them.

  Its shapes were matched in the cups, teats, belly, belly fold and hips described above. The model was compared with ours at the same scale: slipper sole to horn tip, aligned at the knees. The black belly patch stays a flat shag patch with hanging locks (now strands): Tripo had modelled it as a solid lump, which the owner disliked.
- **Shy Cow** (from the Ryerson photo). The owner praised:
  - the hoof hands' shape and texture;
  - arms that fold the way the costume does;
  - slippers that read as slippers, with black socks inside.

  The hooves and the sleeve folds were rebuilt to match. The slippers were cut out of the Shy Cow mesh at first; since round 15 they are the owner's own slipper model.

## Animations

All 18 animations loop seamlessly and play in place, with no root travel.

| Animation | Length | What it does |
|---|---|---|
| Idle | 4.0 s | Breathing, a small weight shift, and the arms relaxed at the sides. |
| Walk | 1.12 s cycle | 36 cm stride; heel strike and toe-off; hips sway and roll; the arms swing opposite the legs, clear of the belly. |
| Run | 0.72 s cycle | Flight phase, high knee lift, forward lean, bent pumping arms. |
| Sneak | 2.6 s cycle | Cartoon tiptoe: crouched, high knees, pointed toes, hooves dangling in front of the chest, head scanning side to side. |
| Jumping Jacks | 4.0 s (4 jacks) | Airborne between the open and closed positions; arms overhead; knees bend on landing. |
| Look Around | 6.0 s | Looks left and then right with the near-side hoof shading the eyes, leans in to peer, looks up, then settles. |
| Chicken Dance | 12.0 s | Beaks, Wings, Wiggle, Claps (3 s each, four moves each). |
| Depressed Walk | 1.6 s cycle | Head hung low, shoulders dropped, a 24 cm shuffle with the feet barely lifting, the arms hanging plumb and the head nodding with each heavy step. |
| Sit Cross-Legged | 11.0 s | Steps the right foot across in front of the left, sinks down with the knees falling open, reaches back for the floor and lands heavily, cross-legged, about 30 cm behind where she stood. Leans back with the belly resting on her legs, then slumps with the forearms over the knees and sighs. Finally reaches back again, pushes up onto her crossed feet and steps out of it. Replaces Crouch and Sit (round 16). |
| Crying | 7.0 s | Hunches over and brings both hooves up to the mask's eyes. Sobs with shaking shoulders and catches its breath, then lowers the hooves. |
| Exasperated | 6.5 s | Flings both arms out palms-up with the head thrown back, then drops them heavily onto the hips and shakes its head. Finishes with a face-palm and a slow head shake inside the hoof. |

**Alt set.** Each of the first seven has an alt version, named `<Animation> (alt)`. The alt versions play the character as it is: heavy, awkward, lumbering and a bit depressed, without going overboard. One function (`lumbering` in `clips.py`) re-voices the original choreography:
- It plays 25 % slower.
- The lower spine slumps forward and the neck juts, but the head tips back up so the eyes stay level and she can see where she's going. The head also has a slight tilt, and the shoulders drop.
- The weight shifts further side to side and the hips roll more. The body sags a little lower and breathes.
- The chest, neck and head trail the hips by 0.07 s, so the upper body follows through.
- The arms swing less and hang plumb.
- The feet lift 38 % less and point 25 % less, so they drag; jumps are lower.
- The belly, cups and shag springs are slightly softer and swing a little further.

The four mood animations are already written in that style, so they have no alt version.

The **default pose** is the rest pose: arms relaxed and down at the sides. In the viewer the Default pose button resets the skeleton to it, and the static master is exported in it.

### Animation clipping

All depths are the 99.5th percentile over every frame.

| Animation | Arms into cups or torso | Teats into belly | Gloves into body | Belly into legs | Leggings stretch, worst frame | Lowest slipper point | Lowest tail point (cord or plug) |
|---|---|---|---|---|---|---|---|
| Idle | 0 mm | 0 mm | 0 mm | 0 mm | 1.17× | 3.0 mm above floor | 436 mm above floor |
| Walk | 0 mm | 0 mm | 0 mm | 2.1 mm | 2.44× | 3.0 mm above floor | 387 mm above floor |
| Run | 0 mm | 0.1 mm | 0 mm | 19.9 mm | 3.40× | 3.0 mm above floor | 400 mm above floor |
| Sneak | 0 mm | 0 mm | 0 mm | 32.5 mm | 3.47× | 3.0 mm above floor | 400 mm above floor |
| Jumping Jacks | 0 mm | 0 mm | 0 mm | 0.1 mm | 2.14× | 3.0 mm above floor | 360 mm above floor |
| Look Around | 0 mm | 0 mm | 0 mm | 0 mm | 1.27× | 3.0 mm above floor | 431 mm above floor |
| Chicken Dance | 0 mm | 2.7 mm | 0 mm | 0 mm | 2.08× | 3.0 mm above floor | 345 mm above floor |
| Depressed Walk | 0 mm | 0 mm | 0 mm | 3.4 mm | 2.25× | 3.0 mm above floor | 390 mm above floor |
| Sit Cross-Legged | 0 mm | 2.1 mm | 0 mm | 2.6 mm | 4.61× | 3.0 mm above floor | on the floor (0.4 mm into it) |
| Crying | 0 mm | 0 mm | 0 mm | 0 mm | 1.65× | 3.0 mm above floor | 406 mm above floor |
| Exasperated | 0 mm | 0 mm | 0 mm | 0 mm | 1.31× | 3.0 mm above floor | 430 mm above floor |
| Idle (alt) | 0 mm | 0 mm | 0 mm | 0 mm | 1.47× | 3.0 mm above floor | 420 mm above floor |
| Walk (alt) | 0 mm | 0 mm | 0 mm | 1.1 mm | 2.30× | 3.0 mm above floor | 382 mm above floor |
| Run (alt) | 0 mm | 3.7 mm | 0 mm | 18.6 mm | 3.04× | 3.0 mm above floor | 380 mm above floor |
| Sneak (alt) | 0 mm | 2 mm | 0 mm | 28.3 mm | 3.16× | 3.0 mm above floor | 399 mm above floor |
| Jumping Jacks (alt) | 0 mm | 0 mm | 0 mm | 0.7 mm | 2.02× | 3.0 mm above floor | 368 mm above floor |
| Look Around (alt) | 0 mm | 0 mm | 0 mm | 0 mm | 1.48× | 3.0 mm above floor | 420 mm above floor |
| Chicken Dance (alt) | 0 mm | 5.7 mm | 1.4 mm | 0 mm | 2.06× | 3.0 mm above floor | 350 mm above floor |

The relaxed arms no longer press into the sides of the body in Look Around, Crying or Exasperated (2–5 mm before): the soft IK leaves the elbows slightly bent instead of locking them straight against the sides. The fuller Blue Shirt udder hangs lower, so the teats touch the belly in a few clips: 2.7 mm at the bottom of the Wiggle squat in the Chicken Dance, and up to 5.7 mm in the slumped alt Chicken Dance. The hooves stay clear of the mask in Crying and in Exasperated's face-palm. With the round-17 gloves, which are about 6 mm fuller on the palm side than the Tripo ones, the left glove brushed the left cup at the front of Run's arm pump (up to 4.3 mm in the alt version); Run now holds the arms 3° further out (0 mm). In the alt Chicken Dance's claps the palm of each glove brushes the other hand's sleeve end by 1.4 mm (0 before). The shortened cord ends about 35–44 cm above the floor while standing; when she sits, the cord and plug lie on the floor.

**Sitting (round 16).** Crouch and Sit clipped badly: the belly hangs to the crotch, so in the crouch the thighs passed 5–6 cm up through the belly and the suit's hem (60 mm in the belly-into-legs column), the seat sank 3.3–3.8 cm through the floor, and the upper arms pressed 19 mm into the cups. Sit Cross-Legged replaces it:
- She leans back 26° as she lands, which takes most of the bend out of the hips, and the belly settles onto her crossed legs.
- The hem helper bones lift the front of the suit over each thigh as it rises, so the leggings and briefs no longer pass up through the hem. Their weights fade from the leg line well up into the belly, so the fabric spreads the lift: the torso's worst stretch in the clip is 1.65× (1.98× in Crouch and Sit).
- The seat lands on the floor instead of in it. The right foot lifts over the left on its way across, and the shins rest one on the other without crossing through.
- Reaching back for the floor, the arms go round the outside of the body; seated, the forearms rest on the outside of the knees, elbows out, so the arms stay clear of the cups (2 mm).
- The chest stays back as she slumps, so the cups don't fold down onto the belly (the teats touch it by 2.1 mm at the bottom of a sigh).

In Run and Sneak the belly still meets the tops of the thighs at the highest knee lift (20 and 33 mm). The same hem helpers could take that up; they are left off there for now, so those animations are exactly as they were. The leggings' stretch is highest at the seat (4.6×, 5.0× before), from the deep seated hip bend, which linear skinning handles poorly. `validate.py` also measures how far the leggings and briefs pass into the suit (`legs_into_body_p995_max_m`). That reading is high in every walking animation too (45 mm in Walk, 73 mm in Run) because it counts the tops of the briefs and leggings tucked up under the hem, which are never seen; for the sit it fell from 75 to 46 mm.

In every animation the gloves stay tucked into the sleeves: within a clip the sleeve-to-glove distance changes by at most 0.4 mm. The glove-into-body check counts only points within 4 cm of the body surface. The hooves reach about 19 cm past the wrist, and without that limit, hoof tips far from the body that happened to lie behind a surface's normal plane were counted as deep penetrations.

## Measured over the dance

| Check | v09 | v10 |
|---|---|---|
| Arms and gloves into the udder cups or torso, 99.5th percentile | not measured | 0 mm in all four phases |
| Teats into the belly, 99.5th percentile | not measured | 0 mm, except 2.7 mm at the bottom of the Wiggle squat |
| Torso edge stretch, 99.9th percentile, worst frame | 4.08× | 1.99× |
| Sleeve edge stretch, 99.9th percentile, worst frame | 12.85× | 2.56× |
| Sleeve end to glove distance, at rest and at the worst frame | not measured | 17.3 mm at rest, 17.6 mm at the worst frame (the mitten is slimmer than the sleeve end, which sits loosely round its wrist; 25.8 mm with the previous gloves) |
| Glove into body, 99.5th percentile | not measured | 0 mm in all four phases |
| Clap contact gap | not measured | 2.1 mm (0.2–0.4 mm with the previous gloves: the claps are placed from the glove's palm thickness, and this smoother glove's fullest point stands 0.8 mm proud of the 99.5th percentile used; moving the hands closer pushes each glove into the other sleeve) |
| Loop seam error | 0 | 0 |
| Planted-foot drift | ~0 | 0.05 mm |

Most of the remaining sleeve stretch is on the outside of the elbow at the top of each wing flap. That is the usual limit of linear-blend skinning on a sharply bent elbow. The torso stretch is higher than in the first v10 pass (1.40×) because the shoulder cap follows the arm's half-rotation helper; that keeps the sleeve head inside the cap. The full numbers are in `reviews/validation_v10.json`. `reviews/v09_same_metrics.json` has the same metric run on the v09 rig.

## The rig

There are 58 joints:
- **Spine and head:** Hips, Spine, Belly, Chest, Neck, Head.
- **Each side:** Shoulder (clavicle), UpperArm, Forearm, Hand, HoofFingers (the glove's index-middle toe), HoofRingLittle (its ring-little toe), Thumb, Thigh, Shin and Foot.
- **Udder:** one Udder bone per cup.
- **Helpers:** UpperArmRoot and Elbow on each side. Each takes half its joint's rotation. Hem_L and Hem_R (children of Hips, at the hip joints) lift the front of the hem over a raised thigh when sitting.
- **Teats:** four bones (Teat_L/R_bottom, Teat_L/R_outer).
- **Shag:** six patch bones (Shag_chest_R, Shag_belly, Shag_back_upper_R, Shag_back_lower_L, Shag_elbow_L, Shag_elbow_R).
- **Tail:** Tail_bow (the bowtie, rigid on the Hips), a chain of 12 cord bones (Tail_cord_1 to Tail_cord_12) and Tail_plug.

The teat, shag, belly and udder bones carry the baked physics. If you use the rig in a game engine, those 12 bones, the 13 cord and plug bones, and the HoofFingers, HoofRingLittle and Thumb bones are the ones to put live spring or "jiggle" components on; the dance clip then only needs the body bones. Bind rotations are identity, and all inverse bind matrices are translations.

The solver is shared by all the animations:
- **Arms:** IK or FK, with the elbow swivel for collision avoidance. The IK is soft for the last 2 cm of reach, so an arm straightens gradually instead of the elbow popping when a target moves in from just out of reach. The wrist twist is kept continuous from frame to frame, and half of it goes to the forearm, so a hoof rolled far over never flips the forearm half a turn. Hand reaches that travel round the cups (shading the eyes, the face-palms) follow B-spline paths with no corners.
- **Legs:** foot IK with heel and toe contact.
- **Helpers:** the half-rotation joints, and the hem helpers, which follow a share of each thigh's lift (`HEM_GAIN`, `HEM_FREE` in `anim.py`) in clips that set `hem`.
- **Physics:** the baked springs.

Each animation is a small class in `clips.py`. The Chicken Dance is in `anim.py` and runs 3 s per phase, with four moves in each:
- **Beaks:** the hoof "beaks" snap open and shut in front of the chest.
- **Wings:** fists at the chest corners while the elbows flap.
- **Wiggle:** knees bend and the hips swish.
- **Claps:** four claps above the udder.

## Orientation and naming

- +Y is up and +Z is the way the character faces. The model is in metres.
- **+X is the character's left.** Bone and mesh names now use the character's own left and right.
- v09 named some parts by screen side. Its "Left" glove was the character's right. The broken horn with the exposed wire is on the character's right (-X), which matches the photos.

## Lighting

The model carries no lighting: no ambient occlusion or contact shadows in its vertex colours or textures. Shading is left to whatever renders it, so it follows the pose. Until round 12 the suit, leggings, briefs, udder, gloves and the v09 mask and horns had ambient occlusion baked into their vertex colours in the rest pose (the suit averaged 68% brightness, the briefs 50%). When the arms rose, the dark band where the arm had hung stayed on the side of the body.

What remains is colour only:
- the photographed textures (the mask scan, the fabric swatches) keep whatever light was in their photos, and the slippers' colour map still has its project's ambient occlusion baked in (see Slippers and socks);
- the black patch under the shag is painted darker than the swatch;
- each shag strand has its own shade of black (the strands' only vertex colour).

If an engine wants ambient occlusion, compute it there (screen-space AO), or bake it into a glTF `occlusionTexture`. Engines apply that only to ambient light, not to the direct lights.

The viewer has four lighting rigs:
- **Studio:** key and rim lights over a soft room reflection (the default);
- **Soft:** even light from every side;
- **Spotlight:** one spotlight from above and in front, casting real shadows on the body and the floor;
- **No lighting:** the materials' own colours, unshaded.

## Rebuilding

You need Python 3.12 or later with `numpy scipy pillow scikit-image vtk xatlas` (xatlas unwraps the briefs), plus `g++` and `ffmpeg`. The pipeline reuses two things from the v09 handoff:
- the review GLB, which supplies the mask scan and horns (the gloves come from `assets/gloves_hoof.glb` and the slippers from `assets/slippers_cow_mule.glb`);
- the `textures-v09` folder, which supplies the fur, shag and cotton swatches.

```bash
cd pipeline
python build_v10.py <handoff>/project/dist/assets/geometry-v09.glb \
                    <handoff>/project/model-source/textures-v09  ../build
python render_reviews.py ../build/rigged.pkl ../reviews <geometry-v09.glb> <shoot photos...> --head=<head photo folder>
python render_dance.py   ../build/rigged.pkl showcase ../reviews/Misanthropic_Cow_v10_Animations.mp4
python render_dance.py   ../build/rigged.pkl sheet    ../reviews/Animation_Clips_v10.jpg
python render_dance.py   ../build/rigged.pkl moodsheet ../reviews/Animation_Mood_Clips_v10.jpg
python render_dance.py   ../build/rigged.pkl altsheet  ../reviews/Animation_Alt_Clips_v10.jpg
python render_dance.py   ../build/rigged.pkl alt       ../reviews/Misanthropic_Cow_v10_Standard_vs_Alt.mp4
python compare_v09.py <handoff>/project/dist/assets/cow-dance-test.glb \
                      <handoff>/project/dist/assets/dance-matrices.bin ../reviews/v09_same_metrics.json
```

Add `--quick` to `build_v10.py` for a half-resolution build that takes about 5 minutes. The full build takes about 20 minutes; most of that time goes to solving the elbow paths and simulating the physics for all 18 animations. `preview_clips.py` poses a few frames of each animation in seconds, for working on the choreography.

Where things live:
- `design.py`: proportions, as signed-distance primitives;
- `textures.py`: shag patch and spot placement;
- `groom.py`: grows the shag strands on the patches;
- `render_shag.py`: before/after close-ups of the shag (`reviews/shag/`);
- `gloves.py`: places the owner's gloves on the hands, with the thumb and knuckle weights (and keeps the earlier procedural gloves as a fallback);
- `hoof_gloves.py`: the one-off conversion of the owner's glove model (`Glove_pair.glb`) into `assets/gloves_hoof.glb`, with the baked AO divided out when the project's `ao_2048.jpg` is given;
- `tripo_gloves.py`, `repair_gloves.py`, `rebuild_gloves.py`: the earlier one-off conversion of the gloves from the owner's Tripo model (rounds 11–16; no longer used, and their outputs are only in the git history);
- `cow_mule_slippers.py`: the one-off conversion of the owner's slipper model (`Cow_Slippers_pair.glb`) into `assets/slippers_cow_mule.glb`: scaled to metres, ankle axis at the origin, right slipper mirrored;
- `tripo_slippers.py`: the earlier conversion of the Shy Cow slippers (no longer used; `tripo_gloves.py` still borrows its OBJ reader);
- `tail.py`: the bowtie, the cord and plug meshes, and the cord's rope simulation;
- `web_textures.py`: downscales textures inside a GLB for the web copies;
- `rig.py`: skin weights;
- `anim.py` and `clips.py`: the choreography.

The web copies in `viewer/` were made with gltfpack 0.22:
- `cow-meshopt.glb` uses `-cc -kn -km -ke` (full detail). It is made from a copy of the animated master whose glove and slipper textures are capped at 1024 px (`python web_textures.py <in> <out> 1024 Glove_ Slipper_`).
- `cow-plain.glb` uses `-kn -km -ke -si 0.3` (a simplified fallback). It is made from a copy with every texture capped at 1024 px (`python web_textures.py <in> <out> 1024`).

`web_textures.py` rewrites only the images and leaves everything else in the file byte for byte. An earlier copying step dropped the rig, so the plain fallback had no animations until this round. The page also accepts base64 copies for hosts that only serve text. Make them with `base64 -w0`. With the strands, each base64 copy is about 17 MB, over the viewer host's 16 MB limit per file, so split it into numbered parts (`cow-meshopt.b64.1.txt`, `cow-meshopt.b64.2.txt`, ...). The page tries `<name>.glb`, then `<name>.b64.txt`, then the numbered parts in order. A split at any point works, because the page joins the parts before decoding.

The plain fallback's simplification (`-si 0.3`) thins the shag strands noticeably; the full-detail copy keeps every strand.

The page zooms with the scroll wheel in proportion to how far the wheel or trackpad scrolled. three.js r160's OrbitControls divides the scroll by `devicePixelRatio | 0`, which is 0 when the browser is zoomed out below 100%, so one wheel tick used to jump straight to the closest distance. Pinch zoom is still OrbitControls'.

To view them locally, run `python3 -m http.server` inside `viewer/` and open the page. three.js loads from the jsDelivr CDN.

## Known limits

- The proportions come from two full-length photos of the original session at an assumed 1.6 m height (round 18). Nothing was measured from the costume itself, and the camera's height puts about ±2–3 cm of uncertainty on the bottom of the belly.
- The side-jaw photo projection on the mask is still stretched in pure side views, as in v09.
- The black shag is a static groom of strand meshes that follow six baked spring bones; it is not a simulated groom. Strands don't collide with the arms, so an arm that swings against a patch can pass through its strands. The strands add about 310k triangles and 2 MB to the compressed web copy.
- The physics is baked springs, not live simulation. Only the teats (with the belly) and the tail cord (with the seat, legs, slippers and floor) collide with anything. The cord does not collide with the arms or with itself.
- Locomotion plays in place; feet slide back during stance like a treadmill, so add root motion in your engine.
- There's no cloth simulation. The suit deforms by skinning only.
- The elbow stretch noted above remains.
