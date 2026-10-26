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
- four mood animations (Depressed Walk, Crouch and Sit, Crying, Exasperated) and an "alt" set that plays the first seven heavy, awkward and slumped;
- a pass informed by two models the owner made with Tripo (see "Tripo references" below): Blue Shirt's udders, belly and hips, Shy Cow's hoof hands, folding sleeves and slippers.

| File | What it is |
|---|---|
| `models/Misanthropic_Cow_v10.glb` | Static master in the default (rest) pose. 662k triangles, real-world scale in metres, all textures embedded. |
| `models/Misanthropic_Cow_v10_Animated.glb` | Same model with a 54-joint skin and 18 looping animations at 30 fps (11 animations plus 7 "alt" versions), all with baked physics. |
| `reviews/` | Turntable and close-up renders, the before/after sheet, the head-vs-photo sheet, the animation sheets, the dance pose sheet, the Tripo comparison sheet (`Tripo_References_vs_v10.jpg`), the showcase video, the standard-vs-alt video and the validation JSON. |
| `viewer/` | A three.js web viewer with an animation picker, a Standard/Alt toggle, a Default pose button, camera presets and a clay toggle. |
| `textures/` | The user-supplied black shag swatch, the first tuft sheet and the long-lock sheet the tufts now use. |
| `assets/` | `slippers_shy_cow.glb`: the knitted cow-head slippers cut from the Tripo Shy Cow model (made by `pipeline/tripo_slippers.py`). `gloves_tripo.glb` and `gloves_tripo.json`: the hoof gloves cut from the owner's Tripo model of the glove photo (made by `pipeline/tripo_gloves.py`). |
| `pipeline/` | The Python sources that generate everything above. |

Both GLBs pass the Khronos glTF Validator with 0 errors and 0 warnings.

## What changed from v09

**Proportions.** The proportions were measured from the 2012 shoot photos:
- belly width is about 2× the mask width;
- muzzle-to-crotch is about 3 mask heights;
- the crotch is at 46 % of standing height.

The wearer is built at about 1.60 m. v09 had scaled the whole figure to fit an oversized mask, which gave it broad, square shoulders and a short barrel torso. v10 instead scales the scanned mask to 0.75 (about 0.21 m wide). The body has narrow, sloped shoulders and a long, round padded belly that hangs to the crotch. Pink satin panties show under the belly, as in shots 0077, 0120 and 0191.

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
- The black shag follows the patch layout in the photos:
  - upper chest and shoulder on the wearer's right;
  - low belly;
  - both elbows;
  - upper back right and lower back left.
- The shag uses the user's black shag swatch (`textures/black_shag_tile.jpg`) as its base, with edges that break into hanging tufts.
- On top of the base sit hanging lock cards (5–7.6 cm long, about 2.5 cm wide). They are alpha-cut from the user's long-lock sheet (`textures/black_shag_locks_sheet.png`): the white background becomes transparency, and each card uses one of the 12 locks. The cards lie along the fur and only their tips lift, by about 1 cm. They overlap densely (about 3,000 per m² of patch) and are rolled slightly at random. Together this reads as one shaggy mat. The previous cards were short, wide and lifted 2–3 cm at the tip, so each one stood out like a feather.
- Each patch belongs to one garment piece only, so no patch spills across a sleeve seam.
- The leggings use smaller, irregular painted white spots.
- The belly's underside is a shallow bowl with a soft edge, so it reads round from below instead of sliced flat.
- The belly is fuller and sits lower and further forward (Blue Shirt), and sags over the panty waistband in a soft fold across the front. The hips and the tops of the thighs are about 3 cm wider, so the panties stretch across a broad seat.
- **Legs.** The legs are separated a little more (owner's note). Each thigh's axis sits 2.4 cm out from the hip joint, and the thigh is slimmer at the top, so the hips keep their width while the inner thighs part below a natural crotch at about 0.71 m, as in the Blue Shirt photo. Before, the thighs overlapped down to 0.66 m and left only a narrow slot below.
- **Panties.** The briefs are their own surface over the leggings and follow the contours of the hips, thighs and crotch. They ease a little over the front of the crotch and span the cleft of the seat, as stretched fabric does.
  - **Front:** the leg line runs low and nearly straight across the tops of the thighs (about 0.69 m) and rises into the crotch at the middle and at the outer hip. The briefs show as a band below the belly, as in the photos, and stay in view while walking.
  - **Back:** the leg line runs diagonally from the hip down across each cheek, leaving the lower outer cheeks in leggings.
  - **Gusset:** a strip under the crotch joins front and back and wraps just onto the tops of the inner thighs, so the crotch shows pink when the legs spread (Jumping Jacks).
  - **Fabric cues:** the briefs sit 4.5 mm proud of the leggings. The leg openings are cut exactly along those lines and finished with rolled elastic edges about 3 mm proud, with the fabric just inside gathered into small ruches. The leggings take a contact shadow along every edge, so the briefs read as a layer on top rather than a painted-on texture. A few shallow tension wrinkles fan out from the crotch, and the fabric weave has the same fine scale everywhere.
- **Tail.** A gold satin bowtie is tied on at the back, on the roll of back fat at the bottom of the white fur. It has two puffed, pleated wings flaring from a pinched centre knot and is about 12 cm wide. A tan two-core lamp cord hangs from the knot to about mid-thigh, 43 cm, and ends in a two-prong plug with brass blades (`tail.py`).
- **Back.** The suit's back isn't flat: a padded roll of back fat across the lower back bulges out and overhangs the panty waistband as a lip, and the back hem tucks under it.
- **Sleeves.** The fur sleeves are roomy and fold the way the costume's do (Shy Cow): soft, uneven folds gather round each elbow, deepest in its crook, the cuff bunches above the glove, and the rest of the sleeve has a loose drape.
- **Slippers and socks.** The slippers are the knitted cow-head slippers cut from the Shy Cow model: low, round, popcorn-knit heads with horns, ears and a smiling white face on a fuzzy black rim. The costume is tights with black socks over the feet, pushed into the slippers. So below the calf the leggings are plain black knit, with no painted spots, and end in a ribbed cuff that stands slightly proud. Foot placement in every animation uses the slipper's real sole, so the slippers sit 2–3 mm above the floor. The v04 slippers had a tall black padded collar that read as a boot.
- **Gloves.** The gloves are the owner's Tripo model of the glove photo: the mask and both gloves lying on a mat (`pipeline/tripo_gloves.py`, `assets/gloves_tripo.glb`). Each glove was cut out and given its own frame from its shape: along the hand, across toward the thumb, and out of the palm. The red-chipped glove is the left and the green-chipped one the right. Each was then scaled so the model's horn span matches the v10 mask (×0.653), placed on the hand with the hoof tips 20 cm past the wrist, re-unwrapped, and its colour and roughness baked from the Tripo maps.
  - **What they are:** a long cream terry mitten with a thumb, and two glossy black hoof halves over the fingertips, chipped to show red card on the left glove and green on the right, as in the photos.
  - **Touch-ups:** the photo's lighting had left the terry grey-green, so it is white-balanced back to cream. The model's metallic map is ignored, so nothing on the glove reads as metal.
  - **Rigging:** each glove is one seamless mesh, so nothing can crack where the mitten meets the hooves. The hoof halves follow the HoofFingers bone through smooth per-vertex weights. The thumb is its own lobe along the thumb-side edge of the mitten, rooted at the wrist (`gloves.THUMB_LINE`). Only that lobe follows the Thumb bone, which sits at the thumb's root and curls it toward the palm about its own hinge. Earlier the whole thumb-side edge of the mitten was weighted to the thumb and bent outward.
  - **Wrist and cuff:** the Tripo mitten's wrist was slimmer than the sleeve end, so the hand looked as if it floated in the opening. The back and sides of the wrist now flare out to fill the sleeve: up to 1.1 cm inside the sleeve's surface where hidden, fading out over the first 6 cm past its end. The palm side stays as it is, so the claps still meet palm to palm. The cuff was also wider than the sleeve on the little-finger side and poked out through the back of the sleeve; where it is hidden it is now pulled inside the sleeve's surface.
  - The procedural gloves from earlier rounds remain in `gloves.py` as a fallback for builds without the asset.

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

Where a sleeve meets the torso, both pieces are shaded with the normals of one smoothly blended surface, which removes the seam line. The sleeve also leaves the cap at a shallow 17° angle instead of 29°.

**Hands that don't connect (fixed).** Each glove's cuff tucks up inside its sleeve end. The sleeve and the glove are weighted by the same function of position along the forearm, so they move as one. In the wing pose the fists follow the forearm instead of being bent 90° at the wrist. v08's flared cuff ring and its halo strands were removed, because at this scale they z-fought with the sleeve.

**Glitching arms (fixed).** In Exasperated, Crying and the Chicken Dance a forearm sometimes spun half a turn in a single frame. The wrist twist was read from a rotation whose sign can flip, and when the hoof was rolled far over (palms up in the fling, on the face in the face-palm), the twist given to the forearm jumped by 180°. It is now kept continuous over time. The largest forearm rotation between frames fell from 178° to 15–30° in every animation. Two other jerks are smoothed out as well:
- an elbow pop when an arm moved in from just out of reach (at the start of Exasperated's fling);
- a corner in the hands' path round the cups (Look Around, Crying and the face-palm).

Peak hand acceleration fell from 82 to 23 m/s² in Look Around, from 53 to 12 in Crying and from 38 to 18 in Exasperated.

**Clipping (fixed).**
- Each elbow swings around its shoulder-wrist line to stay clear of the udder cups and torso. The swing is chosen frame by frame from a collision cost and kept continuous with a Viterbi pass, then smoothed around the loop.
- Half-rotation helper joints at the sleeve head and the elbow keep both joints full when they bend.
- The torso just around each sleeve head follows the arm slightly.
- **Crotch.** The leggings' leg weights used to switch hard from one leg to the other on the centre line, and the two sides were treated differently. Spreading the legs (Jumping Jacks, Run) tore that line open into a stretched panel. Now the two legs share the crotch with a smooth, symmetric blend, half each on the seam. The leggings' worst-frame stretch fell from 8.5× to 2.1× in Jumping Jacks and from 11.1× to 3.1× in Run.
- The belly's fullest point was lowered 2.7 cm and the bottom teats angled forward. This gives the teats clearance at rest, matching the dip under the cups in shots 0120 and 0071.

**Light physics (baked).** glTF has no live physics, so damped springs are simulated over three loops of each animation and the last loop is baked into the bones. It plays in any glTF viewer and every animation loops seamlessly.
- **Teats:** each teat swings on its own bone and collides with the belly. In the dance it peaks at about 20° and averages about 5°.
- **Shag patches:** six spring bones drag the tuft tips, with up to about 4 cm of lag at the elbows.
- **Hooves and thumbs:** each hand's HoofFingers and Thumb bones carry a damped spring driven by the hand's swing: its angular acceleration about the hinge and its acceleration toward the palm. The hooves and thumb lag a swing and settle after it, with a soft limit of about 13°. The Chicken Dance damps this where the hooves are posed on purpose (the beak snaps and the claps), so the claps still meet cleanly. On top of that, resting hands keep the hooves and thumb slightly curled. A slow, small curl-and-release, out of step between the hands, keeps them from looking frozen; it is a whole number of cycles per clip, so it loops.
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

  Its shapes were matched in the cups, teats, belly, belly fold and hips described above. The model was compared with ours at the same scale: slipper sole to horn tip, aligned at the knees. The black belly patch stays a flat shag patch with hanging locks: Tripo had modelled it as a solid lump, which the owner disliked.
- **Shy Cow** (from the Ryerson photo). The owner praised:
  - the hoof hands' shape and texture;
  - arms that fold the way the costume does;
  - slippers that read as slippers, with black socks inside.

  The hooves and the sleeve folds were rebuilt to match. The slippers themselves were cut out of the Shy Cow mesh and given a new UV layout. Their colour was baked from its 8K texture, and they are rigid on the foot bones.

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
| Crouch and Sit | 11.0 s | Crouches with the hooves on the outside of the knees, reaches back and sits down heavily on the floor, and stretches the legs out. Then slumps with the hooves on the knees and sighs. Finally pulls the feet in, pushes up to a crouch and stands. |
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

| Animation | Arms into cups or torso | Teats into belly | Gloves into body | Leggings stretch, worst frame | Lowest slipper point | Lowest tail point (cord or plug) |
|---|---|---|---|---|---|---|
| Idle | 0 mm | 0 mm | 0 mm | 1.16× | 3.0 mm above floor | 436 mm above floor |
| Walk | 0 mm | 0 mm | 0 mm | 2.50× | 2.8 mm above floor | 387 mm above floor |
| Run | 1.3 mm | 0.2 mm | 0 mm | 3.47× | 2.7 mm above floor | 400 mm above floor |
| Sneak | 0 mm | 0 mm | 0 mm | 3.49× | 2.6 mm above floor | 400 mm above floor |
| Jumping Jacks | 0 mm | 0 mm | 0 mm | 2.15× | 3.0 mm above floor | 360 mm above floor |
| Look Around | 0 mm | 0 mm | 0 mm | 1.26× | 3.0 mm above floor | 431 mm above floor |
| Chicken Dance | 0 mm | 2.7 mm | 0 mm | 2.10× | 3.0 mm above floor | 345 mm above floor |
| Depressed Walk | 0 mm | 0 mm | 0 mm | 2.30× | 2.9 mm above floor | 390 mm above floor |
| Crouch and Sit | 17.5 mm | 0 mm | 0 mm | 5.02× | 2.7 mm above floor | 1.3 mm above floor |
| Crying | 0 mm | 0 mm | 0 mm | 1.66× | 3.0 mm above floor | 406 mm above floor |
| Exasperated | 0 mm | 0 mm | 0 mm | 1.30× | 3.0 mm above floor | 430 mm above floor |
| Idle (alt) | 0 mm | 0 mm | 0 mm | 1.47× | 3.0 mm above floor | 420 mm above floor |
| Walk (alt) | 0 mm | 0 mm | 0 mm | 2.36× | 2.7 mm above floor | 382 mm above floor |
| Run (alt) | 0 mm | 3.8 mm | 0 mm | 3.12× | 3.0 mm above floor | 380 mm above floor |
| Sneak (alt) | 0 mm | 2.3 mm | 0 mm | 3.17× | 2.4 mm above floor | 399 mm above floor |
| Jumping Jacks (alt) | 0 mm | 0 mm | 0 mm | 2.03× | 3.0 mm above floor | 368 mm above floor |
| Look Around (alt) | 0 mm | 0 mm | 0 mm | 1.47× | 3.0 mm above floor | 420 mm above floor |
| Chicken Dance (alt) | 0 mm | 5.8 mm | 1.4 mm | 2.07× | 3.0 mm above floor | 350 mm above floor |

The relaxed arms no longer press into the sides of the body in Look Around, Crying or Exasperated (2–5 mm before): the soft IK leaves the elbows slightly bent instead of locking them straight against the sides. Crouch and Sit is the exception, at 17.5 mm: at the bottom of the squat the upper arms press into the sides of the soft udder cups. The fuller Blue Shirt udder hangs lower, so the teats touch the belly in a few clips: 2.7 mm at the bottom of the Wiggle squat in the Chicken Dance, and up to 5.8 mm in the slumped alt Chicken Dance. With the Tripo gloves the hooves no longer press into the mask in Crying (7 mm before); they stay clear in Exasperated too. The shortened cord ends about 35–44 cm above the floor while standing; when she sits, the plug rests on the floor. While seated in Crouch and Sit, the suit's hem rests on the floor, 0 to 2 cm above it, and the leggings stretch up to 5.0× at the seat. That is the 90° seated hip bend, which linear skinning handles poorly.

In every animation the gloves stay tucked into the sleeves: within a clip the sleeve-to-glove distance changes by at most 0.4 mm. The glove-into-body check counts only points within 4 cm of the body surface. The hooves reach about 20 cm past the wrist, and without that limit, hoof tips far from the body that happened to lie behind a surface's normal plane were counted as deep penetrations.

## Measured over the dance

| Check | v09 | v10 |
|---|---|---|
| Arms and gloves into the udder cups or torso, 99.5th percentile | not measured | 0 mm in all four phases |
| Teats into the belly, 99.5th percentile | not measured | 0 mm, except 2.7 mm at the bottom of the Wiggle squat |
| Torso edge stretch, 99.9th percentile, worst frame | 4.08× | 1.99× |
| Sleeve edge stretch, 99.9th percentile, worst frame | 12.85× | 2.56× |
| Sleeve end to glove distance, at rest and at the worst frame | not measured | 31.8 mm at both (the real mitten is slimmer than the sleeve end, which sits loosely round its wrist) |
| Glove into body, 99.5th percentile | not measured | 0 mm in all four phases |
| Clap contact gap | not measured | 0.3 mm |
| Loop seam error | 0 | 0 |
| Planted-foot drift | ~0 | 0.05 mm |

Most of the remaining sleeve stretch is on the outside of the elbow at the top of each wing flap. That is the usual limit of linear-blend skinning on a sharply bent elbow. The torso stretch is higher than in the first v10 pass (1.40×) because the shoulder cap follows the arm's half-rotation helper; that keeps the sleeve head inside the cap. The full numbers are in `reviews/validation_v10.json`. `reviews/v09_same_metrics.json` has the same metric run on the v09 rig.

## The rig

There are 54 joints:
- **Spine and head:** Hips, Spine, Belly, Chest, Neck, Head.
- **Each side:** Shoulder (clavicle), UpperArm, Forearm, Hand, HoofFingers, Thumb, Thigh, Shin and Foot.
- **Udder:** one Udder bone per cup.
- **Helpers:** UpperArmRoot and Elbow on each side. Each takes half its joint's rotation.
- **Teats:** four bones (Teat_L/R_bottom, Teat_L/R_outer).
- **Shag:** six patch bones (Shag_chest_R, Shag_belly, Shag_back_upper_R, Shag_back_lower_L, Shag_elbow_L, Shag_elbow_R).
- **Tail:** Tail_bow (the bowtie, rigid on the Hips), a chain of 12 cord bones (Tail_cord_1 to Tail_cord_12) and Tail_plug.

The teat, shag, belly and udder bones carry the baked physics. If you use the rig in a game engine, those 12 bones, the 13 cord and plug bones, and the HoofFingers and Thumb bones are the ones to put live spring or "jiggle" components on; the dance clip then only needs the body bones. Bind rotations are identity, and all inverse bind matrices are translations.

The solver is shared by all the animations:
- **Arms:** IK or FK, with the elbow swivel for collision avoidance. The IK is soft for the last 2 cm of reach, so an arm straightens gradually instead of the elbow popping when a target moves in from just out of reach. The wrist twist is kept continuous from frame to frame, and half of it goes to the forearm, so a hoof rolled far over never flips the forearm half a turn. Hand reaches that travel round the cups (shading the eyes, the face-palms) follow B-spline paths with no corners.
- **Legs:** foot IK with heel and toe contact.
- **Helpers:** the half-rotation joints.
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

## Rebuilding

You need Python 3.12 or later with `numpy scipy pillow scikit-image vtk`, plus `g++` and `ffmpeg`. The pipeline reuses two things from the v09 handoff:
- the review GLB, which supplies the mask scan and horns (the gloves come from `assets/gloves_tripo.glb` and the slippers from `assets/slippers_shy_cow.glb`);
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
- `gloves.py`: places the Tripo gloves on the hands (and keeps the earlier procedural gloves as a fallback);
- `tripo_gloves.py`: the one-off conversion of the gloves from the owner's Tripo model into `assets/gloves_tripo.glb`. It needs that OBJ and its texture folder, plus `pip install xatlas`;
- `tripo_slippers.py`: the one-off conversion of the Shy Cow slippers into `assets/slippers_shy_cow.glb`. It needs the Shy Cow OBJ and texture, plus `pip install xatlas`;
- `tail.py`: the bowtie, the cord and plug meshes, and the cord's rope simulation;
- `web_textures.py`: downscales textures inside a GLB for the web copies;
- `rig.py`: skin weights;
- `anim.py` and `clips.py`: the choreography.

The web copies in `viewer/` were made with gltfpack 0.22:
- `cow-meshopt.glb` uses `-cc -kn -km -ke` (full detail). It is made from a copy of the animated master whose glove and slipper textures are capped at 1024 px (`python web_textures.py <in> <out> 1024 Glove_ Slipper_`).
- `cow-plain.glb` uses `-kn -km -ke -si 0.3` (a simplified fallback). It is made from a copy with every texture capped at 1024 px (`python web_textures.py <in> <out> 1024`).

Both copies keep their base64 versions under the viewer host's 16 MB limit. `web_textures.py` rewrites only the images and leaves everything else in the file byte for byte. An earlier copying step dropped the rig, so the plain fallback had no animations until this round. The page also accepts base64 copies (`cow-meshopt.b64.txt`, `cow-plain.b64.txt`) for hosts that only serve text; make them with `base64 -w0`.

The page zooms with the scroll wheel in proportion to how far the wheel or trackpad scrolled. three.js r160's OrbitControls divides the scroll by `devicePixelRatio | 0`, which is 0 when the browser is zoomed out below 100%, so one wheel tick used to jump straight to the closest distance. Pinch zoom is still OrbitControls'.

To view them locally, run `python3 -m http.server` inside `viewer/` and open the page. three.js loads from the jsDelivr CDN.

## Known limits

- The proportions come from photos at an assumed 1.6 m height. Nothing was measured from the costume.
- The side-jaw photo projection on the mask is still stretched in pure side views, as in v09.
- The black shag is a texture plus alpha-cut lock cards, not a simulated groom. In a web viewer the cards use an alpha test, so very thin tips can flicker when the model is small on screen. The viewer lowers the cutoff and turns on anisotropic filtering to reduce this.
- The physics is baked springs, not live simulation. Only the teats (with the belly) and the tail cord (with the seat, legs, slippers and floor) collide with anything. The cord does not collide with the arms or with itself.
- Locomotion plays in place; feet slide back during stance like a treadmill, so add root motion in your engine.
- There's no cloth simulation. The suit deforms by skinning only.
- The elbow stretch noted above remains.
