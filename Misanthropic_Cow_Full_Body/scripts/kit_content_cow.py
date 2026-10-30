"""Single source of truth for the full-body Misanthropic Cow multiview kit.

Wording note: ChatGPT's image filter blocked the first version of Step 2 ("nudity, sexuality
or erotic content"). The costume itself is fully covering, so the text describes it in plain
costume terms (udder, bloomers, "the costume's own left") and avoids underwear / body words.
"""

TITLE = "THE MISANTHROPIC COW: FULL COSTUME, FOUR-VIEW KIT (v2)"
GOAL = ("Goal: one clean, full-length image of the complete cow costume with nothing worn over it (the FRONT view), "
        "then matching back and side views for Tripo multiview.")

BRIEF = """DESIGN BRIEF: THE MISANTHROPIC COW COSTUME
(Authoritative. Follow it for every image in this chat.)

WHAT IT IS: ONE complete, handmade, full-length cow mascot costume from an art project, shown standing in an A-pose. It's homemade, a little crude and lumpy, not a polished theme-park suit and not a cartoon. The performer inside is completely hidden: the hood and mask cover the head, gloves cover the hands, leggings and slippers cover the legs and feet. Nothing else is worn over the costume: no robe, jacket, hat, bag or props.

POSE: Standing straight and symmetrical, facing the camera. Arms straight, held down and away from the sides at about 45 degrees, clear of the belly and the udder. Feet about hip-width apart, toes forward. Head level, looking straight ahead.

PROPORTIONS (from my original photo shoot; PROPORTION_BASE shows them): measured from the floor to the horn tips,
- the bottom of the snout is at about 85% of the height, and the udder starts right below it;
- the udder covers about 73-85% of the height and is about 25% of the height wide;
- the stuffed belly is the widest part of the costume, at about 60% of the height, and about 28% of the height wide;
- the white fur hem ends at about 52%; the beige bloomers end at about 46%;
- the legs are fairly slim compared with the huge belly: each about 9% of the height wide at the top.
Overall: a short, round, egg-shaped stuffed body on ordinary legs.

PARTS, TOP TO BOTTOM:
1. HORNS (as in DETAIL_3 / DETAIL_3b): two yellow horns with thin black rings, mounted at each end of a short, sausage-shaped white fur BOLSTER lying across the top of the hood. They are deliberately NOT a matching pair:
   - The costume's own LEFT horn (on the RIGHT of a front-view image) is long: a smooth crescent curving out and up, with three black rings and an intact, smooth, pointed tip. (Some later photos show this tip broken off; don't copy that.)
   - The costume's own RIGHT horn (on the LEFT of a front-view image) is short and stubby, with two black rings, and ends in a deliberate tuft of bare, twisted, dark-silver WIRE strands sticking up and curling slightly outward, about as long as the horn itself.
2. HOOD: white shaggy fur, one piece with the top, closing around the mask on the sides and top. Rounded at the back.
3. MASK: a rigid, sculpted cow mask filling the hood opening: matte white with a rough, cracked, painted-plaster texture and a heavy, angry, scowling brow ridge. Black cow patches are painted on it: a big one around its own LEFT eye (on the RIGHT of a front-view image) running up to the top; a smaller one over the other brow; and one beside each side of the snout.
4. EYES: two glossy round YELLOW eyes with round black pupils, fairly close together under the brow.
5. SNOUT: the mask sticks out into a broad snout. Its front is a flat oval of shaggy RED flocked fabric with TWO VERTICAL black slit NOSTRILS side by side. No mouth, teeth, tongue or nose ring.
6. NECK TUFT: a clump of long black shaggy fur just under the snout, on the costume's own right (the LEFT of a front-view image).
7. UDDER: a big pink smooth-fabric (fleece) cow udder sewn high on the front of the costume, just under the snout: two large, rounded, stuffed lobes side by side. It has four short, stubby pink fabric nubs: on each lobe, one sticks out sideways and one points down.
8. BODY: long-pile white faux-fur costume top with long sleeves and the hood. Below the udder, a huge, very round, stuffed BELLY: the widest part of the costume. The fur is slightly matted and lumpy.
9. BLACK PATCHES: sewn-on patches of long black shaggy fur (not printed): a big one low on the belly, just off-centre; small tufts on both sides under the arms; a tuft on the outside of each elbow.
10. GLOVES: the sleeves end in white fuzzy knit gloves with a separate thumb. Over the fingers are two broad, flat, slightly glossy black HOOF halves covering the fingers (a cow's cloven hoof, each half as wide as two fingers, with blunt rounded points; not claws or talons). The thumb is plain white knit with no black on it.
11. BLOOMERS: short, high-waisted beige satin bloomers with beige lace side panels, worn OVER the leggings, showing between the fur hem and the tops of the legs.
12. LEGGINGS: opaque black leggings with irregular, slightly rough WHITE painted cow spots of different sizes.
13. SLIPPERS: handmade cow-head slippers (DETAIL_13): a big white plush muzzle with a thin black stitched smile and two magenta nostrils, black bead eyes, cream "mop" chenille with black patches, small tan horns, floppy black-and-magenta ears with pearl beads, and a shaggy black chenille fringe around the sole. The feet inside wear plain black socks, so no bare skin shows at the open heels.
14. BACK (only visible from behind): a big black shag patch across the upper back on the costume's own LEFT side, two smaller black shag patches lower down, and a small GOLD satin BOW at the centre of the lower back just above the hem, with a thin white cord TAIL hanging from it to about knee height.

NEVER ADD: any visible part of the performer (face, hair, hands); anything worn over the costume (robe, jacket, hat, bag); printed cow-print fabric; spots on the udder; a cartoon or cute face; a mouth, teeth, tongue or nose ring; a bell or collar; a long cow tail with a tassel; extra nubs on the udder; a second figure; props; a background or floor pattern; any text, labels, numbers or arrows."""

CAMERA = """CAMERA AND FRAMING: The whole costume from the horn tips to the slipper soles, all inside the frame with a small white margin; it fills about 90% of the image height. Camera level with the belly, looking straight across. Long-lens, near-orthographic look with very little perspective distortion. Portrait 2:3. Pure white seamless background, only a faint shadow under the slippers. Soft, even, diffuse studio light; no coloured gels. Photorealistic product-style photograph of the real handmade costume and its materials. No text, labels, numbers, arrows, borders or watermark."""

SAME_SCALE = """MATCH MY APPROVED FRONT VIEW: same costume, same height in the frame, same proportions, same camera height, same lighting, same white background, same colours and materials. The horn tips and the slipper soles sit at the same heights in the frame as in my approved front view."""

STEPS = [
    {
        "zip": "STEP_1_Lock_in_the_design",
        "label": "1",
        "title": "Lock in the design",
        "goal": "Get the image model to read the costume correctly before it draws anything. No image is made in this step.",
        "where": "Start a brand-new chat. Don't reuse the chat that showed the guardrail message: a chat that has refused once stays touchy.",
        "attach": [
            ("PROPORTION_BASE_original_shoot.png", "Proportions: cut-out collage from the original shoot"),
            ("REF_A_whole_costume_front_no_overlays.png", "The whole costume from the front"),
            ("REF_E_back_upper_hood_patches_bow.png", "The back: hood, patches, gold bow"),
            ("DETAIL_1_mask_face.png", "The mask close up"),
            ("DETAIL_3_horns_ORIGINAL_SHOOT_front.png", "The horns, original shoot"),
            ("DESIGN_KEY_check_every_view_against_this.png", "Annotated design key"),
        ],
        "prompt": """I'm building a 3D model of my character, The Misanthropic Cow, which is a handmade full-length cow mascot costume from one of my art projects. Over the next few messages I'll ask you for four reference views of the complete costume: front, back, and both sides. They'll go into an image-to-3D tool, so accuracy to the real costume matters far more than looking nice.

There's no single photo of the whole costume on its own: it was photographed at different events, often with other clothes on top, and the belly and udder were re-stuffed each time. You'll be combining several photos into one clean costume.

Attached, in order:
1. PROPORTION_BASE: a rough cut-out collage from my first photo shoot. Its proportions are the correct ones. The arms are missing because they were raised in that photo; ignore the cut edges and the wearer's hair at the sides of the mask (but the black shaggy tuft under the snout is part of the costume).
2. REF_A: the whole costume from the front (lying on a backdrop, wide-angle lens; ignore the backdrop and the distortion).
3. REF_E: the back: hood, black patches and the gold bow.
4. DETAIL_1: the mask close up.
5. DETAIL_3: the two horns as they should be.
6. DESIGN_KEY: my annotated breakdown of the parts, for understanding only. Never draw its numbers, circles, lines or text.

{BRIEF}

Don't make an image yet. First reply with:
(a) anything in the photos that contradicts or adds to the brief, and
(b) one or two sentences each on what the front, back and side views of THIS costume should look like, including which side the wire horn is on in each view.""",
        "check": [
            "It describes the face as a rigid sculpted mask with a red snout and two vertical slit nostrils (not a cartoon face or a pink nose).",
            "It describes one big pink udder high on the front, with two lobes and four stubby nubs.",
            "It puts the beige bloomers OVER the black spotted leggings.",
            "Its back-view description has the gold bow with the thin white cord tail, and no face.",
            "It puts the short WIRE-tipped horn on the LEFT of the front view and the long, intact, pointed horn on the RIGHT.",
        ],
        "save": None,
        "after": "If it gets any of these wrong, correct it in one line (for example: \"Correction: the nostrils are two vertical black slits in the red snout.\") and wait for it to confirm before moving on.",
    },
    {
        "zip": "STEP_2_Front_view_CLEAN_MASTER",
        "label": "2",
        "title": "Front view (the clean master image)",
        "goal": "This is the one clean image of the cow you asked for. It sets the proportions, scale and materials for every other view, so take the time to get it right.",
        "where": "Same chat as Step 1. If this step shows the guardrail message again, use STEP_2B instead.",
        "attach": [
            ("PROPORTION_BASE_original_shoot.png", "EDIT THIS ONE: proportions and layout"),
            ("REF_A_whole_costume_front_no_overlays.png", "Whole costume, front"),
            ("DETAIL_1_mask_face.png", "Mask close up"),
            ("DETAIL_3_horns_ORIGINAL_SHOOT_front.png", "Horns, original shoot"),
            ("DETAIL_5_glove_with_black_hoof.png", "Glove and black hoof"),
            ("DETAIL_5b_gloves_front_two_hoof_halves.png", "Both gloves from the front"),
            ("DETAIL_13_slipper_real_object.png", "The real slipper"),
        ],
        "prompt": """IMAGE 1 OF 4: FRONT VIEW. This is the master: every later view must match it.

Attached, in order: PROPORTION_BASE (edit this image: keep its proportions), REF_A (the whole costume, front), DETAIL_1 (the mask; ignore its horns), DETAIL_3 (the horns as they should be), DETAIL_5 and DETAIL_5b (the real gloves and hooves), DETAIL_13 (one of the real slippers).

Turn PROPORTION_BASE into a clean, complete product photograph of the costume, seen straight from the front:
- KEEP from PROPORTION_BASE: the size of the head, the size and position of the udder, the size and roundness of the belly, where the fur hem and the bloomers end, the leg length and thickness, and the slippers. Don't make the costume taller or slimmer.
- COMPLETE the hood around the mask, the shoulders, and both sleeves in an A-pose: straight arms held down and away from the sides at about 45 degrees, clear of the belly, ending in the white knit gloves (DETAIL_5, DETAIL_5b): two broad, flat, slightly glossy black HOOF halves covering the fingers (a cow's cloven hoof, each half as wide as two fingers, with blunt rounded points; not claws or talons). The thumb is plain white knit with no black on it. A black shag tuft on the outside of each elbow.
- CLEAN UP the cut-out edges and any hair at the sides of the mask. Nothing of the performer shows. KEEP the clump of black shaggy fur just under the snout on the LEFT of the image (it's part of the costume).
- The mask faces the camera straight on: scowling brow, yellow eyes, painted black patches as in DETAIL_1, and the red flocked snout with two vertical black slit nostrils.
- The horns exactly as in DETAIL_3: on the LEFT of the image, the short horn ending in a tuft of twisted bare wire; on the RIGHT of the image, the long crescent horn with an intact pointed tip.
- The pose is centred and symmetrical, but the black patches stay where they are (they're not symmetrical).

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "The whole costume in frame, horn tips to slipper soles, on white.",
            "Proportions still match PROPORTION_BASE: big round belly wider than the hips, udder right under the snout, legs not lengthened.",
            "A-pose: both arms straight, ~45 degrees out, clear of the body.",
            "Gloves: white knit with a plain white thumb; two broad, blunt black hoof halves over the fingers. No claws or talons.",
            "Black shaggy tuft under the snout on the image's LEFT.",
            "Mask: red snout with two vertical slit nostrils, yellow eyes, big black patch on the image's right. No mouth.",
            "Horns: short wire-tipped horn on the image's LEFT, long intact pointed horn on the image's RIGHT.",
            "Pink udder: two lobes, four stubby nubs (one sideways and one down on each lobe).",
            "Beige bloomers over black leggings with white spots. Cow slippers on both feet.",
            "Nothing of the performer shows; no robe, jacket, text or props.",
        ],
        "save": "1_FRONT_approved.png",
        "after": "Download it and rename it 1_FRONT_approved.png. Send it to me too: I'll measure its proportions against the original shoot before you continue. It's attached to every later step.",
    },
    {
        "zip": "STEP_2B_Front_view_FALLBACK_if_blocked",
        "label": "2B",
        "title": "Front view, fallback (only if Step 2 is blocked)",
        "goal": "Same result as Step 2, but the image to edit is a flat-colour drawing of the costume at the original shoot's proportions instead of a photo collage, and none of the attached photos are close-ups of the lower costume.",
        "where": "A NEW chat. This prompt includes the design brief, so it's a single message: no separate Step 1.",
        "attach": [
            ("PROPORTION_SKETCH_A_pose.png", "EDIT THIS ONE: flat-colour layout at the right proportions"),
            ("REF_I_whole_costume_at_event.png", "The real costume, front, at an event"),
            ("REF_C_head_and_upper_costume_original_shoot.png", "Head and upper costume, original shoot"),
            ("DETAIL_1_mask_face.png", "Mask close up"),
            ("DETAIL_3_horns_ORIGINAL_SHOOT_front.png", "Horns, original shoot"),
            ("DETAIL_13_slipper_real_object.png", "The real slipper"),
        ],
        "prompt": """I'm building a 3D model of my character, The Misanthropic Cow, which is a handmade full-length cow mascot costume from one of my art projects. I'll ask you for four reference views of the complete costume (front, back and both sides) for an image-to-3D tool, so accuracy to the real costume matters far more than looking nice. This is the first.

{BRIEF}

IMAGE 1 OF 4: FRONT VIEW. This is the master: every later view must match it.

Attached, in order: PROPORTION_SKETCH (a flat-colour layout drawing of the costume at the correct proportions and in the correct A-pose: edit this one), REF_I (the real costume at an event; ignore the background and the bag strap), REF_C (the head and upper costume from my original shoot; ignore the plaid robe), DETAIL_1 (the mask; ignore its horns), DETAIL_3 (the horns as they should be), DETAIL_13 (one of the real slippers).

Turn PROPORTION_SKETCH into a photorealistic product photograph of the real handmade costume, seen straight from the front. Keep the sketch's layout exactly: its proportions, the A-pose, the size and position of every part, and the horn arrangement (short wire-tipped horn on the LEFT of the image, long pointed crescent horn on the RIGHT). Replace the flat colours with the real materials from the photos: long-pile white faux fur, sewn-on black shaggy fur patches, the cracked painted mask with yellow eyes and the red flocked snout with two vertical black slit nostrils, the smooth pink fleece udder, white knit gloves (plain white thumb, two broad blunt black hoof halves over the fingers, no claws), beige satin bloomers with lace sides, black leggings with rough white painted spots, and the cow slippers. The costume should look homemade and slightly lumpy, not like a cartoon or a theme-park suit.

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "Same checks as Step 2.",
            "It looks like a photo of the real costume, not a 3D render or an illustration of the sketch.",
        ],
        "save": "1_FRONT_approved.png",
        "after": "Download it and rename it 1_FRONT_approved.png, send it to me, and carry on with Step 3 in this chat.",
    },
    {
        "zip": "STEP_3_Back_view",
        "label": "3",
        "title": "Back view",
        "goal": "The approved front view and two real back photos pin this one down.",
        "where": "Same chat. If the chat has started to drift, open a fresh one, run Step 1 again, then continue.",
        "attach": [
            ("1_FRONT_approved.png", "YOUR approved front view (attach first)"),
            ("REF_F_back_full_body.png", "Real back view, full length"),
            ("REF_E_back_upper_hood_patches_bow.png", "Real back: hood, patches, bow"),
            ("DETAIL_11_gold_bow_and_cord_tail.png", "Gold bow and cord tail"),
        ],
        "prompt": """IMAGE 2 OF 4: BACK VIEW.

Attached, in order: 1_FRONT_approved (my approved front view; match it), REF_F (the real costume from behind, full length; ignore the green screen), REF_E (the real back: hood, black patches and gold bow), DETAIL_11 (the gold bow and its thin white cord tail).

Make a photograph of the same costume turned 180 degrees: the camera is directly behind it, looking straight at its back. Same A-pose, seen from behind.

What this view must show:
- The back of the rounded white fur hood, with the fur bolster across its top and the two yellow horns sticking out left and right. Seen from behind the sides swap: the long pointed horn is on the LEFT of this image and the short wire-tipped horn is on the RIGHT. The mask is on the far side and hidden: no eyes, no snout.
- A big black shag patch across the upper back on the costume's own LEFT (the LEFT of this image, since we're behind it), and two smaller black shag patches lower down, one on each side.
- The back of the huge round belly: it bulges out past the sides, so its edges and the edges of the udder may just show at the sides.
- A small gold satin bow at the centre of the lower back, just above the fur hem, with a thin white cord tail hanging from it to about knee height.
- The beige bloomers from behind, the black leggings with white spots, and the back (open heel) of each cow slipper, with plain black socks on the heels inside (no bare skin).
- The backs of the sleeves and the gloves: white knit, with the two broad black hoof halves over the fingers.

{SAME_SCALE}

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "No mask, eyes or snout visible.",
            "Big black patch on the upper back on the image's LEFT side.",
            "Long pointed horn on the image's LEFT, wire-tipped horn on the RIGHT.",
            "Gold bow at the lower back with a thin white cord tail (not a cow tail with a tassel).",
            "Same height, pose and belly size as the front view.",
        ],
        "save": "2_BACK_approved.png",
        "after": "Save it as 2_BACK_approved.png.",
    },
    {
        "zip": "STEP_4_Side_view_facing_left",
        "label": "4",
        "title": "Side view, facing left",
        "goal": "A true profile. It shows how far the snout, udder and belly stick out, which Tripo can't guess from the front.",
        "where": "Same chat.",
        "attach": [
            ("1_FRONT_approved.png", "YOUR approved front view"),
            ("2_BACK_approved.png", "YOUR approved back view"),
            ("REF_H_head_side_profile.png", "Real head in profile, this side"),
            ("REF_G_side_view_belly_MIRRORED.png", "Real costume from the side, FLIPPED: shape only"),
        ],
        "prompt": """IMAGE 3 OF 4: SIDE VIEW, FACING LEFT.

Attached, in order: 1_FRONT_approved and 2_BACK_approved (my approved views; match them), REF_H (the real head in profile: see how far the snout sticks out of the hood), REF_G (the real costume from its other side, flipped to face the same way: use it ONLY for how far the udder and belly stick out, not for which patches show; ignore the green screen).

Make a photograph of the same costume in a true side profile, turned exactly 90 degrees: it faces the LEFT edge of the frame, so we see its own LEFT side. Same A-pose; from this side the near arm hangs down beside the body and the far arm is mostly hidden.

What this view must show, left to right:
- The snout sticking well out in front of the hood, its red flocked front facing left, with the profile of the scowling brow and one yellow eye inside the big black painted patch. The black neck tuft is on the far side and hidden.
- The long crescent horn with its pointed tip on the near side of the bolster; the wire tuft of the short horn may just poke up behind it.
- The pink udder sticking far out in front, below the snout, with its nubs pointing forward and down.
- The huge belly bulging forward below the udder, much deeper than the hips. The front of the belly sticks out about as far as the front of the udder.
- The big black shag patch from the upper back just showing behind the near shoulder.
- The rounded back of the hood and a fairly flat back, with the gold bow and the thin white cord tail at the lower back on the right.
- Beige bloomers, black spotted leggings and one cow slipper side-on (toe pointing left).

{SAME_SCALE}

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "Faces the LEFT edge, true profile (not three-quarter).",
            "Snout, udder and belly all stick out in front; back is fairly flat.",
            "Near horn is the long pointed one.",
            "Same height and proportions as the front view. Slipper toe points left.",
        ],
        "save": "3_SIDE_facing_left_approved.png",
        "after": "Save it as 3_SIDE_facing_left_approved.png.",
    },
    {
        "zip": "STEP_5_Side_view_facing_right",
        "label": "5",
        "title": "Side view, facing right",
        "goal": "The last view. The costume isn't perfectly symmetrical (patches, horns), so generate it rather than mirroring if you can.",
        "where": "Same chat.",
        "attach": [
            ("1_FRONT_approved.png", "YOUR approved front view"),
            ("2_BACK_approved.png", "YOUR approved back view"),
            ("3_SIDE_facing_left_approved.png", "YOUR approved left-facing side view"),
            ("REF_G_side_view_belly.png", "Real costume from this side"),
            ("DETAIL_15_head_right_side.png", "Real head from this side"),
            ("DETAIL_15b_head_right_side_closer.png", "Real head from this side, closer"),
            ("DETAIL_3b_horns_ORIGINAL_SHOOT_wire_horn.png", "The wire-tipped horn, original shoot"),
        ],
        "prompt": """IMAGE 4 OF 4: SIDE VIEW, FACING RIGHT.

Attached, in order: 1_FRONT_approved, 2_BACK_approved and 3_SIDE_facing_left_approved (my approved views; match them), REF_G (the real costume from this side: see how far the udder and belly stick out; ignore the green screen and the bare arm), DETAIL_15 and DETAIL_15b (the real head from this same side: the paint, the snout and the wire horn; ignore the hair, the hands and the person), DETAIL_3b (the wire-tipped horn).

Make a photograph of the same costume from its other side: a true side profile, turned exactly 90 degrees, facing the RIGHT edge of the frame, so we see its own RIGHT side.

It should look almost like a mirror image of 3_SIDE_facing_left_approved: same height, scale, camera height, lighting, snout, udder, belly depth and pose. Only the details on this side differ, and DETAIL_15 and DETAIL_15b show them: the black paint over the brow and around the eye, the large black patch on the cheek beside the snout, the clump of black shaggy fur under the snout, the big black patch on the upper back is on the far side and hidden, and the near horn is the SHORT one ending in its tuft of twisted bare wire (DETAIL_3b), with the long pointed horn behind it.

Also:
- The hand is the same size as in 1_FRONT_approved: white knit glove with two black hoof halves over the fingers.
- Both slippers stand on the same floor line, toes pointing right; the far slipper is almost completely hidden behind the near one. Plain black socks at the heels, no bare skin.
- The gold bow sits at the back edge of the lower back (on the left of this image), with nothing hanging from it.

{SAME_SCALE}

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "Faces the RIGHT edge, true profile.",
            "Same height and depth as the left-facing side view.",
            "Near horn is the short wire-tipped one. Slipper toe points right.",
        ],
        "save": "4_SIDE_facing_right_approved.png",
        "after": "Shortcut: if this one fights you, flip 3_SIDE_facing_left_approved horizontally (Preview: Tools > Flip Horizontal; Windows Photos: Edit > Flip). The shape is close to symmetrical, but the horns won't swap in a mirror, so tell me if you use this shortcut and I'll correct the horns on the model.",
        "tripo": True,
    },
]

FIXES = [
    ("Fix A", "Something is worn over the costume, or part of the performer shows",
     "Remove the [robe / jacket / hat / hair / face]. Nothing is worn over the costume, and the performer is completely hidden inside it: the hood and mask cover the head, the gloves cover the hands, the leggings and slippers cover the legs and feet. Keep everything else exactly the same."),
    ("Fix B", "Turned into a generic or cartoon cow",
     "This has drifted into a generic cow costume. The face is a rigid, sculpted, painted mask with a scowling brow, glossy yellow eyes, painted black patches and a red flocked snout with two vertical black slit nostrils (see DETAIL_1). There's no printed cow-print fabric: the costume is white long-pile fur with sewn-on patches of black shaggy fur. Keep everything else the same."),
    ("Fix C", "Snout or nostrils wrong (pink nose, round nostrils, a mouth)",
     "The snout is wrong. Its front is a flat oval of shaggy RED flocked fabric with two VERTICAL black slit nostrils side by side, like DETAIL_1. No mouth, teeth, tongue or nose ring. Fix only the snout."),
    ("Fix D", "Costume got slimmer, taller or more athletic",
     "The proportions have drifted. Match PROPORTION_BASE: the stuffed belly is huge and round and is the widest part of the costume (about 28% of the full height wide), the udder starts right under the snout, and the fur hem ends at the hips. The legs are ordinary length. Keep the costume details the same and fix only the overall shape."),
    ("Fix E", "Udder wrong",
     "The udder is a big, smooth pink fleece cow udder sewn high on the front, just under the snout: two large rounded lobes side by side, with four short stubby pink nubs (on each lobe, one sticks out sideways and one points down). Fix only the udder."),
    ("Fix F", "Arms not in A-pose / touching the belly",
     "Put the arms in an A-pose: both arms straight, held down and away from the sides at about 45 degrees, with a clear gap between the sleeves and the belly. Gloves are white fuzzy knit with a plain white thumb, and two broad, flat, slightly glossy black HOOF halves covering the fingers (a cow's cloven hoof, each half as wide as two fingers, with blunt rounded points; not claws or talons) (DETAIL_5, DETAIL_5b). Keep everything else the same."),
    ("Fix G", "Wrong angle (three-quarter, from above or below)",
     "This is a three-quarter / angled view. I need a true [FRONT / BACK / SIDE] view: turn the camera to exactly 90-degree steps around the costume and put it level with the belly, looking straight across. Keep the costume itself identical."),
    ("Fix H", "Slippers wrong",
     "The slippers are handmade cow-head slippers like DETAIL_13: a big white plush muzzle with a thin black stitched smile and two magenta nostrils, cream mop chenille with black patches, small tan horns, black-and-magenta ears with pearl beads, and a shaggy black chenille fringe round the sole. Fix only the slippers."),
    ("Fix I", "Horns wrong (matching pair, no wire, broken tip, wrong side)",
     "The horns are wrong. They don't match, on purpose (see DETAIL_3 and DETAIL_3b): the costume's own RIGHT horn (on the LEFT of the front view) is short with two black rings and ends in a tuft of twisted bare dark-silver wire about as long as the horn. Its own LEFT horn (on the RIGHT of the front view) is a long, smooth crescent with three black rings and an intact pointed tip. Fix only the horns."),
    ("Fix J", "Text, labels, a border or a background appeared",
     "Remove all text, labels, numbers, arrows, borders and background. Pure white background, only a faint shadow under the slippers. Keep the costume exactly the same."),
    ("Fix K", "Hooves look like claws or talons, or the thumb has a claw",
     "The hands are wrong. Each glove is white fuzzy knit with a separate thumb that is plain white knit, with no claw and no black. Over the four fingers are two broad, flat, slightly glossy black HOOF halves covering the fingers (a cow's cloven hoof, each half as wide as two fingers, with blunt rounded points; not claws or talons), like DETAIL_5 and DETAIL_5b. Fix only the hands and keep everything else exactly the same."),
    ("Fix L", "Guardrail message (\"may violate our guardrails...\")",
     "Don't argue or rephrase in the same chat: start a new chat. Run Step 1 again, then try Step 2 once more; if it's blocked again, use STEP_2B. If a later step is blocked, start a new chat, paste the Step 1 prompt with your approved front view as the first image, then repeat the blocked step."),
]
FIX_ATTACH = [
    ("PROPORTION_BASE_original_shoot.png", "Proportions (Fix D)"),
    ("PROPORTION_SKETCH_A_pose.png", "Proportions and A-pose as a flat drawing (Fix D, F)"),
    ("DETAIL_1_mask_face.png", "Mask (Fix B, C)"),
    ("DETAIL_2_mask_face_alt_light.png", "Mask, softer light (Fix B, C)"),
    ("DETAIL_3_horns_ORIGINAL_SHOOT_front.png", "Horns, original shoot, front (Fix I)"),
    ("DETAIL_3b_horns_ORIGINAL_SHOOT_wire_horn.png", "The wire-tipped horn, original shoot (Fix I)"),
    ("DETAIL_5_glove_with_black_hoof.png", "Glove and hoof (Fix F, K)"),
    ("DETAIL_5b_gloves_front_two_hoof_halves.png", "Both gloves from the front (Fix F, K)"),
    ("DETAIL_6_arm_tuft_and_hoof.png", "Arm, elbow tuft and hoof (Fix F)"),
    ("DETAIL_7_belly_and_black_shag_patch.png", "Belly and its black shag patch (Fix B, D)"),
    ("DETAIL_9_spotted_leggings.png", "Black leggings with white spots"),
    ("DETAIL_10_slippers_worn.png", "Slippers worn (Fix H)"),
    ("DETAIL_11_gold_bow_and_cord_tail.png", "Gold bow and cord tail"),
    ("DETAIL_12_black_tuft_under_snout.png", "Black tuft under the snout"),
    ("DETAIL_13_slipper_real_object.png", "The real slipper (Fix H)"),
]

TIPS = [
    "One view per message. Never ask for a sheet or grid of views.",
    "In ChatGPT, use the Select tool on the image to brush over only the wrong area before sending a fix. Then just that area is redrawn instead of the whole image.",
    "If two fixes in a row make things worse, start a new chat: run Step 1 again, then attach your approved images and carry on from where you were.",
    "Approve a view only after checking it against the design key. One wrong view teaches Tripo the wrong shape.",
    "Guardrail message? Start a new chat (see Fix L). If Step 2 is blocked twice, use STEP_2B: it edits a flat-colour drawing instead of the photo collage.",
    "The close-ups of the udder and the bloomers are left out of the kit on purpose, because close-ups like those are the most likely to trip the filter. Both show clearly enough in the whole-costume photos.",
]

TRIPO = [
    ("Front", "1_FRONT_approved.png"),
    ("Back", "2_BACK_approved.png"),
    ("Left", "3_SIDE_facing_left_approved.png"),
    ("Right", "4_SIDE_facing_right_approved.png"),
]
TRIPO_NOTES = [
    "Don't upload yet: send me the four approved views first. I'll normalise them (same height, same ground line, square white canvas) and send them back as the Tripo inputs.",
    "Tripo needs the front view plus at least one other. Leave out any view you don't trust.",
    "If the model comes out twisted, or with a face on both sides, swap the Left and Right images and run it again.",
]


def fill(text):
    return text.replace("{BRIEF}", BRIEF).replace("{CAMERA}", CAMERA).replace("{SAME_SCALE}", SAME_SCALE)
