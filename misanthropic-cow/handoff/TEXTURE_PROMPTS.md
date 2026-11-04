# Image prompts for the tail, horn and wire textures (rounds 46-47)

**Status (round 48):** all four images are in `textures/` and in use: the bow and cord (`tail_bow.png`,
`tail_cord.png`) since round 47, the horns and wires (`horn_paint.png`, `horn_wire.png`) since round 48. Their normal
maps come from the images' own shading. Replacing a file and rebuilding is all a new image needs.

Images made from the prompts below replace the procedural textures: save them in `misanthropic-cow/textures/` under the
names given and rebuild (`pipeline/tail_textures.py` picks them up; nothing else needs changing). PNG or JPG both work.

## 1. Electrical cord: `textures/tail_cord.png`

Ask for a **square** image (1024 × 1024). Prompt:

> A seamless, tileable texture swatch of the outer jacket of an old, worn, off-white two-conductor lamp cord (flat
> "zip cord", PVC insulation), seen straight on and filling the whole frame, as a flat material scan: even,
> shadowless studio lighting, no perspective, no background, no cord edges visible. Very fine parallel ribs run
> vertically from top to bottom of the image. The plastic is a slightly yellowed off-white, with soft grey grime
> in the grooves, faint scuffs and fine scratches running mostly lengthwise, a few small dull smudges, and a
> subtle satin sheen, not glossy. No lettering, no logos, no text. The left and right edges and the top and bottom
> edges must match exactly so the image tiles seamlessly in both directions. Photorealistic, high detail.

Optional, for raised ribs and scratches in the lighting: a matching height map, `textures/tail_cord_height.png`:

> The same texture as a grayscale height map: white for the raised ribs, black for the grooves and scratches,
> mid-grey for the flat plastic. Same framing, seamless in both directions, no shading or lighting.

(Ask for it in the same conversation, right after the colour image, so the two line up.)

Notes: the swatch covers the cord's girth across (about 18 mm round both cores) and is repeated three times along
every 5 cm of cord, so keep its features small and evenly spread; one large stain would repeat visibly. The
rating line ("SPT-1 18AWG ...") is left out on purpose: lettering on a swatch that repeats reads as a pattern.

## 2. Bow tie: `textures/tail_bow.png`

Attach the photo of the costume's bow to the conversation, ask for a **landscape** image (1536 × 1024), and use:

> Using the attached photo as the reference, create a straight-on, front-view product photo of the same bow tie:
> the same gold satin fabric and colour, the same shape and proportions, the same pleats gathered into the pinched
> centre knot, the same soft folds and wrinkles. The bow is centred, seen exactly face-on (no tilt, no
> perspective), and fills most of the frame left to right, with a small margin all round. Plain, flat, uniform
> pure white background, even soft lighting with gentle satin highlights along the folds, no cast shadow, no
> strap, band, clip, hands, cord or anything else in the frame. Photorealistic, sharp, high detail.

Notes: the bow on the model is about 12 cm wide and 5.2 cm tall with a knot about 2.3 cm wide, so a bow about 2.3
times as wide as it is tall fits best. The build cuts it out against the background (it looks at the four corners
for the background colour, so keep them empty and plain), stretches its outline over the bow mesh and mirrors it
to the view from behind the cow. If the bow in the photo is lopsided, the generated one may be too; that is fine.

Optional height map, `textures/tail_bow_height.png`: "The same bow as a grayscale height map: white where the
fabric bulges toward the viewer, black in the deep pleats and creases, the background black; same framing, no
lighting."

## 3. Horns: `textures/horn_paint.png`

The horns are papier-mache, painted yellow with black bands. The bands stay where they are (from the horns' own
colour maps); a photo swatch adds the real surface: its brightness detail is laid over the colour and it makes the
relief in the normal map. Ask for a **square** image (1024 × 1024):

> A seamless, tileable texture swatch of a hand-made papier-mache surface painted with bright yellow acrylic
> paint, seen straight on and filling the whole frame, as a flat material scan: even, shadowless lighting, no
> perspective, no background. Soft uneven lumps and faint overlapping edges of the pasted paper strips under the
> paint, fine brush marks, slightly matte paint with a little sheen on the raised bits, a few tiny paper fibres and
> specks in the paint. One even yellow overall, no stripes, no bands, no text. The left and right edges and the top
> and bottom edges must match exactly so the image tiles seamlessly in both directions. Photorealistic, high detail.

Notes: the swatch is taken as about 3 cm across, so lumps a few millimetres across look right; keep the yellow even
(dark patches would read as stains on every horn).

## 4. Exposed horn wires: `textures/horn_wire.png`

Ask for a **square** image (1024 × 1024):

> A seamless, tileable texture swatch of the surface of old dark galvanised steel wire (the bare armature wire
> inside a craft prop), seen straight on and filling the whole frame, as a flat material scan: even, shadowless
> lighting, no perspective, no background, no wire edges visible. Fine drawing lines run vertically from top to
> bottom of the image; a mottled grey zinc coat with darker dull patches, small dark specks, and a few tiny rust
> freckles. Metallic, slightly worn. No text. The left and right edges and the top and bottom edges must match
> exactly so the image tiles seamlessly in both directions. Photorealistic, high detail.

Notes: the wires are only 1.5 mm thick, so this is detail you see only close up; the swatch spans a wire's girth
across and repeats along it.

## 5. The rest of the cow

Every other part has a proper texture: the fur suit, hood, sleeves and horn tube (fur), the mask and jaws
(projected from the reference photos), the slippers and gloves (4096-pixel photo textures), the leggings, briefs
and udders (fabric tiles), the black shag (real strands, so no texture is needed), and from round 47 the tail
(your images), the horns (normal maps) and the wires (texture and normal map). The udders, briefs and leggings use
made-up fabric tiles; they read correctly at viewing distance, but square seamless photo swatches of each fabric
("flat material scan, even lighting, seamless") would bring them closer to the costume.
