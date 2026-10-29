"""Single source of truth for the full-body Misanthropic Cow multiview kit."""

TITLE = "THE MISANTHROPIC COW: FULL COSTUME, FOUR-VIEW KIT"
GOAL = ("Goal: one clean, full-body image of the cow with nothing worn over the costume (the FRONT view), "
        "then matching back and side views of the same figure for Tripo multiview.")

BRIEF = """DESIGN BRIEF: THE MISANTHROPIC COW, FULL COSTUME
(Authoritative. Follow it for every image in this chat.)

WHAT IT IS: ONE person wearing a complete handmade cow costume, standing in an A-pose. It's a homemade art-project costume, a little crude and lumpy, not a polished mascot suit and not a cartoon. Nothing else is worn over it: no robe, jacket, cardigan, hat, lingerie, bag or props. The wearer's face, hair and skin are completely hidden.

POSE: Standing straight and symmetrical, facing the camera. Arms straight, held down and away from the body at about 45 degrees, palms facing the thighs, clear of the belly and the udder cups. Feet about hip-width apart, toes forward. Head level, looking straight ahead.

BODY PROPORTIONS (taken from my original photo shoot; image PROPORTION_BASE shows them): measured from the floor to the tips of the horns,
- the mask's chin / bottom of the snout is at about 85% of the height, and the udder cups start right below it (there's almost no visible neck);
- the udder cups cover about 73-85% of the height and are about 25% of the height wide, together;
- the belly is the widest part of the body, at about 60% of the height, and is about 28% of the height wide (wider than the hips);
- the white fur hem ends at about 52%; the beige briefs end at the crotch, at about 46%;
- the legs are fairly slim compared with the huge belly: each leg is about 9% of the height wide at the thigh.
The figure is short, round and bottom-heavy in the torso: a pear / egg-shaped stuffed body on ordinary legs.

PARTS, TOP TO BOTTOM:
1. HORNS (take them from DETAIL_3 / DETAIL_3b, my original shoot): two yellow horns with thin black rings, mounted at each end of a short, sausage-shaped white fur BOLSTER lying across the top of the hood. They are deliberately NOT a matching pair:
   - The wearer's LEFT horn (the viewer's RIGHT in a front view) is the long one: a smooth crescent curving out and up, with three black rings and an intact, smooth, pointed tip. (Some later photos show this tip broken off; that's damage, don't copy it.)
   - The wearer's RIGHT horn (the viewer's LEFT in a front view) is short and stubby, with two black rings, and its end is a deliberate tuft of bare, twisted, dark-silver WIRE strands sticking up and curling slightly outward, about as long as the horn itself, like an exposed wire armature.
2. HOOD: white shaggy fur, one piece with the top, closing around the mask on the sides and top. Rounded at the back.
3. MASK: a rigid, sculpted mask filling the hood opening: matte white with a rough, cracked, painted-plaster texture. It has a heavy, angry, scowling brow ridge. Black cow patches are painted on it: a big one over the wearer's LEFT eye (the viewer's RIGHT) that runs up to the top of the mask; a smaller one over the other brow; and one beside each side of the snout.
4. EYES: two glossy round YELLOW eyes with round black pupils, fairly close together under the brow.
5. SNOUT: the mask sticks out into a broad snout. Its front is a flat oval covered in shaggy RED flocked fabric, with TWO VERTICAL black slit NOSTRILS side by side. No mouth, no teeth, no tongue, no nose ring, no lips.
6. CHEST TUFT: a clump of long black shaggy fur under the snout, at the wearer's right collarbone (viewer's left).
7. UDDER CUPS: two very large, rounded PINK smooth-fabric (fleece / minky) cups across the whole chest, touching in the middle, sewn onto the white fur. Each cup has TWO pink finger-sized TEATS about 8-10 cm long: one sticking out sideways from the outer lower side, and one pointing down from the bottom.
8. TOP / BELLY: long-pile white faux-fur top (long sleeves, hood). Under the cups, a huge, very round, stuffed BELLY: the widest part of the figure. The fur is slightly matted and lumpy.
9. BLACK PATCHES on the fur: sewn-on patches of long black shaggy fur (not printed): a big one on the lower belly, just off-centre; small tufts on both flanks below the armpits; a tuft on the outside of each elbow.
10. GLOVES: the sleeves end in white fuzzy knit gloves. The fingers are covered by glossy black, split (cloven) HOOVES.
11. BRIEFS: high-waisted beige / nude satin briefs with sheer beige lace side panels, worn OVER the leggings, showing between the fur hem and the tops of the thighs.
12. LEGGINGS: opaque black leggings with irregular, slightly rough WHITE painted cow spots of different sizes on the thighs, knees and shins.
13. SLIPPERS: a pair of handmade cow-head slippers (see DETAIL_13): a big white plush muzzle with a thin black stitched smile and two magenta nostrils, black bead eyes, cream "mop" chenille head with black patches, small tan horns, floppy black-and-magenta ears with pearl beads, and a shaggy black chenille fringe around the sole.
14. BACK (only visible from behind): a big black shag patch across the upper back over the wearer's LEFT shoulder blade, two smaller black shag patches lower down, and a small GOLD satin BOW at the centre of the lower back just above the hem, with a thin white cord TAIL hanging from it to about knee height.

NEVER ADD: a visible human face, hair, skin or hands; any clothing over the costume (robe, jacket, cardigan, hat, lingerie, bag); a printed cow-print pattern; spots on the udder cups; a cartoon or cute face; a mouth, teeth, tongue or nose ring; a bell or collar; a long cow tail with a tassel; extra teats; a second person; any props; a background or floor pattern; any text, labels, numbers or arrows."""

CAMERA = """CAMERA AND FRAMING: Full body from the tips of the horns to the soles of the slippers, all inside the frame with a small white margin; the figure fills about 90% of the image height. Camera level with the middle of the body (around the belly), looking straight across, not up or down. Long-lens, near-orthographic look with very little perspective distortion. Portrait 2:3. Pure white seamless background, only a faint contact shadow under the slippers. Soft, even, diffuse studio light from the front; no coloured gels. Photorealistic photograph of the real handmade costume with its real materials. No text, labels, numbers, arrows, borders or watermark."""

SAME_SCALE = """MATCH MY APPROVED FRONT VIEW: same figure, same height in the frame, same proportions, same camera height, same lighting, same white background, same colours and materials. The horn tips and the slipper soles sit at the same heights in the frame as in my approved front view."""

STEPS = [
    {
        "zip": "STEP_1_Lock_in_the_design",
        "title": "Lock in the design",
        "goal": "Get the image model to read the costume correctly before it draws anything. No image is made in this step.",
        "where": "Start a brand-new chat.",
        "attach": [
            ("PROPORTION_BASE_original_wearer.png", "Body proportions: cut-out photo collage of the original wearer"),
            ("REF_A_whole_costume_front_no_overlays.png", "The whole costume from the front, nothing over it"),
            ("REF_C_head_and_torso_front_ORIGINAL_WEARER.png", "Head and torso, original wearer"),
            ("REF_E_back_upper_hood_patches_bow.png", "The back: hood, patches, gold bow"),
            ("DETAIL_1_mask_face.png", "The mask close up"),
            ("DESIGN_KEY_check_every_view_against_this.png", "Annotated design key"),
        ],
        "prompt": """I'm making a 3D model of my character, The Misanthropic Cow: a person in a handmade cow costume. Over the next few messages I'll ask you for four reference views of the full costume: front, back, and both sides. They'll be fed into an image-to-3D tool, so being accurate to the real costume matters far more than looking nice.

There's no single photo of the whole costume. Different people wore it over the years, usually with other clothes on top, and the belly and udders were re-stuffed each time. You'll be combining several photos into one clean figure.

Attached, in order:
1. PROPORTION_BASE: a rough cut-out collage of the original wearer's body and head from my first photo shoot. Its proportions are the correct ones. The arms are missing because they were raised in the photo; ignore the cut edges, hair and dark scraps at the neck.
2. REF_A: the whole costume from the front, nothing over it (lying on a backdrop, wide-angle lens; ignore the knife, the backdrop and the distortion).
3. REF_C: head and torso of the original wearer. Ignore the plaid robe.
4. REF_E: the back of the costume: hood, black patches and the gold bow.
5. DETAIL_1: the mask close up (from a later photo: the long horn's tip is broken there; take the horns from the brief instead).
6. DESIGN_KEY: my annotated breakdown of the parts. It's for understanding only. Never draw its numbers, circles, lines or text.

{BRIEF}

Don't make an image yet. First reply with:
(a) anything in the photos that contradicts or adds to the brief, and
(b) one or two sentences each on what the front, back and side views of THIS costume should look like, including which side the wire horn is on in each view.""",
        "check": [
            "It describes the face as a rigid sculpted mask with a red snout and two vertical slit nostrils (not a cartoon cow face or a pink nose).",
            "It describes two pink udder cups on the chest, each with two teats (one sideways, one down), not one udder at the belly.",
            "It puts the beige briefs OVER the black spotted leggings.",
            "Its back-view description includes the gold bow with the thin white cord tail, and no face.",
            "It lists nothing worn over the costume (no robe, jacket or hat).",
            "It puts the short WIRE-tipped horn on the wearer's right (viewer's left in the front view) and the long, intact, pointed horn on the other side.",
        ],
        "save": None,
        "after": "If it gets any of these wrong, correct it in one line (for example: \"Correction: the nostrils are two vertical black slits in the red snout.\") and wait for it to confirm before moving on.",
    },
    {
        "zip": "STEP_2_Front_view_CLEAN_MASTER",
        "title": "Front view (the clean master image)",
        "goal": "This is the one clean image of the cow you asked for. It sets the proportions, scale and materials for every other view, so take the time to get it right.",
        "where": "Same chat as Step 1.",
        "attach": [
            ("PROPORTION_BASE_original_wearer.png", "EDIT THIS ONE: proportions and layout"),
            ("REF_A_whole_costume_front_no_overlays.png", "Whole costume, front"),
            ("DETAIL_1_mask_face.png", "Mask close up"),
            ("DETAIL_3_horns_ORIGINAL_SHOOT_front.png", "Horns, original shoot"),
            ("DETAIL_4_udder_cups_and_teats.png", "Udder cups and teats"),
            ("DETAIL_5_glove_with_black_hoof.png", "Glove and black hoof"),
            ("DETAIL_13_slipper_real_object.png", "The real slipper"),
        ],
        "prompt": """IMAGE 1 OF 4: FRONT VIEW. This one is the master: every later view must match it.

Attached, in order: PROPORTION_BASE (edit this image: keep its proportions), REF_A (the whole costume, front), DETAIL_1 (the mask; ignore its horns), DETAIL_3 (the horns as they should be), DETAIL_4 (the udder cups and teats), DETAIL_5 (a glove with its black hoof), DETAIL_13 (one of the real slippers).

Turn PROPORTION_BASE into a clean, complete photograph of the full costume, seen straight from the front:
- KEEP from PROPORTION_BASE: the height of the head, the size and position of the udder cups, the size and roundness of the belly, where the fur hem and the briefs end, the leg length and thickness, and the slippers. Don't make the figure taller, slimmer or more athletic.
- COMPLETE the hood around the mask, the shoulders, and both arms in an A-pose: straight arms held down and away from the body at about 45 degrees, clear of the belly, ending in the white knit gloves with black cloven hooves (DETAIL_5), with a black shag tuft on the outside of each elbow.
- REMOVE everything that isn't the costume: the wearer's hair, the dark scraps at the neck and the cut-out edges. The wearer's face and skin are hidden.
- The mask faces the camera straight on: scowling brow, yellow eyes, painted black patches as in DETAIL_1, and the red flocked snout with two vertical black slit nostrils.
- The horns exactly as in DETAIL_3: on the LEFT of the image, the short horn ending in a tuft of twisted bare wire; on the RIGHT of the image, the long crescent horn with an intact pointed tip.
- The figure is centred and symmetrical in pose, though the black patches stay where they are (they're not symmetrical).

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "Full body in frame: horn tips to slipper soles, on white.",
            "Proportions still match PROPORTION_BASE: big round belly wider than the hips, udder cups right under the snout, legs not lengthened.",
            "A-pose: both arms straight, ~45 degrees out, clear of the body; white knit gloves with black hooves.",
            "Mask: red snout with two vertical slit nostrils, yellow eyes, big black patch on the viewer's right. No mouth.",
            "Horns: short wire-tipped horn on the image's LEFT, long intact pointed horn on the image's RIGHT.",
            "Two pink udder cups, two teats each (one sideways, one down). Nothing else pink except the slipper details.",
            "Beige briefs over black leggings with white spots. Cow slippers on both feet.",
            "No hair, skin, robe, jacket, text or props.",
        ],
        "save": "1_FRONT_approved.png",
        "after": "Download it and rename it 1_FRONT_approved.png. Send it to me too: I'll measure its proportions against the original shoot before you continue. It's attached to every later step.",
    },
    {
        "zip": "STEP_3_Back_view",
        "title": "Back view",
        "goal": "The approved front view and two real back photos pin this one down.",
        "where": "Same chat. If the chat has started to drift, open a fresh one, run Step 1 again, then continue.",
        "attach": [
            ("1_FRONT_approved.png", "YOUR approved front view (attach first)"),
            ("REF_F_back_full_body.png", "Real back view, full body"),
            ("REF_E_back_upper_hood_patches_bow.png", "Real back: hood, patches, bow"),
            ("DETAIL_11_gold_bow_and_cord_tail.png", "Gold bow and cord tail"),
        ],
        "prompt": """IMAGE 2 OF 4: BACK VIEW.

Attached, in order: 1_FRONT_approved (my approved front view; match it), REF_F (the real costume from behind, full body; ignore the person's bare hands and the green screen), REF_E (the real back: hood, black patches and gold bow), DETAIL_11 (the gold bow and its thin white cord tail).

Make a photograph of the same figure turned 180 degrees: the camera is directly behind it, looking straight at its back. Same A-pose, arms ~45 degrees out, mirrored correctly for a view from behind.

What this view must show:
- The back of the rounded white fur hood, with the fur bolster across its top and the two yellow horns sticking out left and right. Seen from behind the sides swap: the long pointed horn is on the LEFT of this image and the short wire-tipped horn is on the RIGHT. The mask and face are on the far side and hidden: no eyes, no snout.
- A big black shag patch across the upper back over the wearer's LEFT shoulder blade (that's the LEFT side of this image, since we're behind the figure), and two smaller black shag patches lower down, one on each side.
- The back of the huge round belly: it bulges out past the sides of the body, so the edges of the belly and the udder cups may just show at the sides.
- A small gold satin bow at the centre of the lower back, just above the fur hem, with a thin white cord tail hanging from it to about knee height.
- The beige briefs from behind, the black leggings with white spots, and the back (open heel) of each cow slipper.
- The backs of the arms and the gloves, with the black hooves.

{SAME_SCALE}

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "No face, eyes or snout visible.",
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
        "title": "Side view, facing left",
        "goal": "A true profile. It shows how far the snout, udder cups and belly stick out, which Tripo can't guess from the front.",
        "where": "Same chat.",
        "attach": [
            ("1_FRONT_approved.png", "YOUR approved front view"),
            ("2_BACK_approved.png", "YOUR approved back view"),
            ("REF_H_head_side_profile.png", "Real head in profile"),
            ("REF_G_side_body_udders_belly.png", "Real body from the side"),
        ],
        "prompt": """IMAGE 3 OF 4: SIDE VIEW, FACING LEFT.

Attached, in order: 1_FRONT_approved and 2_BACK_approved (my approved views; match them), REF_H (the real head in profile: see how far the snout sticks out of the hood), REF_G (the real body from the side: see how far the udder cups and belly stick out; ignore the bare arm and the green screen).

Make a photograph of the same figure in a true side profile, turned exactly 90 degrees: it faces the LEFT edge of the frame, so we see the figure's LEFT side. Same A-pose, but from this side the near arm hangs down beside the body, and the far arm is mostly hidden.

What this view must show, left to right:
- The snout sticking well out in front of the hood, its red flocked front facing left, with the profile of the scowling brow and one yellow eye inside the big black painted patch (the patch over the wearer's left eye). The chest tuft is on the far side and hidden.
- The big black shag patch from the upper back just showing behind the near shoulder.
- The long crescent horn with its pointed tip on the near side of the bolster; the wire tuft of the short horn may just poke up behind it.
- The two pink udder cups sticking far out in front of the chest, with the teats pointing forward-down.
- The huge belly bulging forward below the cups, much deeper than the hips. The front of the belly sticks out about as far as the front of the cups.
- The rounded back of the hood and a fairly flat back, with the gold bow and the thin white cord tail at the lower back on the right.
- Beige briefs, black spotted leggings and one cow slipper side-on (toe pointing left).

{SAME_SCALE}

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "Faces the LEFT edge, true profile (not three-quarter).",
            "Snout, udder cups and belly all stick out in front; back is fairly flat.",
            "Same height and proportions as the front view.",
            "Slipper toe points left.",
        ],
        "save": "3_SIDE_facing_left_approved.png",
        "after": "Save it as 3_SIDE_facing_left_approved.png.",
    },
    {
        "zip": "STEP_5_Side_view_facing_right",
        "title": "Side view, facing right",
        "goal": "The last view. The costume isn't perfectly symmetrical (the black patches differ), but for Tripo's SHAPE a mirror image works.",
        "where": "Same chat.",
        "attach": [
            ("1_FRONT_approved.png", "YOUR approved front view"),
            ("2_BACK_approved.png", "YOUR approved back view"),
            ("3_SIDE_facing_left_approved.png", "YOUR approved left-facing side view"),
            ("REF_H_head_side_profile.png", "Real head in profile"),
            ("DETAIL_3b_horns_ORIGINAL_SHOOT_wire_horn.png", "The wire-tipped horn, original shoot"),
        ],
        "prompt": """IMAGE 4 OF 4: SIDE VIEW, FACING RIGHT.

Attached, in order: 1_FRONT_approved, 2_BACK_approved and 3_SIDE_facing_left_approved (my approved views; match them), REF_H (the real head in profile), DETAIL_3b (the wire-tipped horn).

Make a photograph of the same figure from its other side: a true side profile, turned exactly 90 degrees, facing the RIGHT edge of the frame, so we see the figure's RIGHT side.

It should look almost like a mirror image of 3_SIDE_facing_left_approved: same height, scale, camera height, lighting, snout, udder cups, belly depth and pose. Only the details on this side differ: here the eye is in mostly white mask with the smaller painted patch above the brow, the black shag chest tuft shows under the snout, the big black patch on the upper back is on the far side and hidden, and the near horn is the SHORT one ending in its tuft of twisted bare wire (DETAIL_3b), with the long pointed horn behind it.

{SAME_SCALE}

{CAMERA}

Follow the design brief exactly.""",
        "check": [
            "Faces the RIGHT edge, true profile.",
            "Same height and depth as the left-facing side view.",
            "Slipper toe points right.",
            "Near horn is the short wire-tipped one.",
        ],
        "save": "4_SIDE_facing_right_approved.png",
        "after": "Shortcut: if this one fights you, flip 3_SIDE_facing_left_approved horizontally (Preview: Tools > Flip Horizontal; Windows Photos: Edit > Flip). The body shape is close to symmetrical; the patches get fixed later when we texture the model. The horns won't swap in a mirror, so tell me if you use this shortcut and I'll correct the horns on the model.",
    },
]

FIXES = [
    ("Fix A", "Something is worn over the costume, or a face / hair shows",
     "Remove the [robe / jacket / hat / hair / face]. Nothing is worn over the costume, and the wearer is completely hidden: the hood and mask cover the head, the gloves cover the hands, and the leggings cover the legs. Keep everything else exactly the same."),
    ("Fix B", "Turned into a generic or cartoon cow",
     "This has drifted into a generic cow costume. The face is a rigid, sculpted, painted mask with a scowling brow, glossy yellow eyes, painted black patches and a red flocked snout with two vertical black slit nostrils (see DETAIL_1). There's no printed cow-print fabric: the top is white long-pile fur with sewn-on patches of black shaggy fur. Keep everything else the same."),
    ("Fix C", "Snout or nostrils wrong (pink nose, round nostrils, a mouth)",
     "The snout is wrong. Its front is a flat oval of shaggy RED flocked fabric with two VERTICAL black slit nostrils side by side, like DETAIL_1. No mouth, no teeth, no tongue, no lips, no nose ring. Fix only the snout."),
    ("Fix D", "Body got slimmer, taller or more athletic",
     "The proportions have drifted. Match PROPORTION_BASE: the belly is huge and round and is the widest part of the body (about 28% of the full height wide), the udder cups start right under the snout, and the fur hem ends at the hips. The legs are ordinary length. Keep the costume details the same and fix only the body shape."),
    ("Fix E", "Udder cups or teats wrong",
     "The udder cups are two very large, smooth PINK fabric domes across the whole chest, touching in the middle. Each has exactly two pink finger-sized teats: one sticks out sideways from the outer lower side, one points down from the bottom (see DETAIL_4). Fix only the cups."),
    ("Fix F", "Arms not in A-pose / touching the belly",
     "Put the arms in an A-pose: both arms straight, held down and away from the body at about 45 degrees, with a clear gap between the arms and the belly. Gloves are white fuzzy knit with glossy black cloven hooves over the fingers (DETAIL_5). Keep everything else the same."),
    ("Fix G", "Wrong angle (three-quarter, from above or below)",
     "This is a three-quarter / angled view. I need a true [FRONT / BACK / SIDE] view: turn the camera to exactly 90-degree steps around the figure and put it level with the belly, looking straight across. Keep the figure itself identical."),
    ("Fix H", "Slippers wrong",
     "The slippers are handmade cow-head slippers like DETAIL_13: a big white plush muzzle with a thin black stitched smile and two magenta nostrils, cream mop chenille with black patches, small tan horns, black-and-magenta ears with pearl beads, and a shaggy black chenille fringe round the sole. Fix only the slippers."),
    ("Fix I", "Horns wrong (matching pair, no wire, broken tip, wrong side)",
     "The horns are wrong. They don't match, on purpose (see DETAIL_3 and DETAIL_3b): the wearer's RIGHT horn (the image's LEFT in the front view) is short with two black rings and ends in a tuft of twisted bare dark-silver wire about as long as the horn. The wearer's LEFT horn (the image's RIGHT in the front view) is a long, smooth crescent with three black rings and an intact pointed tip. Fix only the horns."),
    ("Fix J", "Text, labels, a border or a background appeared",
     "Remove all text, labels, numbers, arrows, borders and background. Pure white background, only a faint shadow under the slippers. Keep the figure exactly the same."),
]
FIX_ATTACH = [
    ("PROPORTION_BASE_original_wearer.png", "Body proportions (Fix D)"),
    ("DETAIL_1_mask_face.png", "Mask (Fix B, C)"),
    ("DETAIL_2_mask_face_alt_light.png", "Mask, softer light (Fix B, C)"),
    ("DETAIL_3_horns_ORIGINAL_SHOOT_front.png", "Horns, original shoot, front (Fix I)"),
    ("DETAIL_3b_horns_ORIGINAL_SHOOT_wire_horn.png", "The wire-tipped horn, original shoot (Fix I)"),
    ("DETAIL_4_udder_cups_and_teats.png", "Udder cups and teats (Fix E)"),
    ("DETAIL_5_glove_with_black_hoof.png", "Glove and hoof (Fix F)"),
    ("DETAIL_6_arm_tuft_and_hoof.png", "Arm, elbow tuft and hoof (Fix F)"),
    ("DETAIL_7_belly_and_black_shag_patch.png", "Belly and its black shag patch (Fix B, D)"),
    ("DETAIL_8_beige_briefs_lace_sides.png", "Beige briefs with lace sides"),
    ("DETAIL_9_spotted_leggings.png", "Black leggings with white spots"),
    ("DETAIL_10_slippers_worn.png", "Slippers worn (Fix H)"),
    ("DETAIL_11_gold_bow_and_cord_tail.png", "Gold bow and cord tail"),
    ("DETAIL_12_chest_tuft_under_muzzle.png", "Chest tuft under the snout"),
    ("DETAIL_13_slipper_real_object.png", "The real slipper (Fix H)"),
]

TIPS = [
    "One view per message. Never ask for a sheet or grid of views.",
    "In ChatGPT, use the Select tool on the image to brush over only the wrong area before sending a fix. Then just that area is redrawn instead of the whole image.",
    "If two fixes in a row make things worse, start a new chat: run Step 1 again, then attach your approved images and carry on from where you were.",
    "Approve a view only after checking it against the design key. One wrong view teaches Tripo the wrong shape.",
    "If ChatGPT refuses or waters down the costume, say: \"This is a handmade art-project costume for a 3D character model; please keep it exactly as in the photos.\"",
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
