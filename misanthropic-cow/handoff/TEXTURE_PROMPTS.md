# Image prompts for the tail textures (round 46)

The tail's bow and cord are textured procedurally (round 45; the cord is a worn off-white since round 46).
Images made from the prompts below replace those textures: save them in `misanthropic-cow/textures/` under the
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

## 3. The rest of the cow

Every other part already has a proper texture: the fur suit, hood, sleeves and horn tube (fur), the mask and jaws
(projected from the reference photos), the slippers and gloves (4096-pixel photo textures), the leggings, briefs
and udders (fabric tiles), the horns (colour maps) and the black shag (real strands, so no texture is needed).
Three could be better:

1. **The exposed wires on the horns** (`Exposed_Dark_Wires`) are still one flat dark grey. They would look better
   as dark rubber-insulated wire with a little sheen and some scuffs. This can be done procedurally in the next
   round (no image needed), or from a prompt like the cord's: "seamless tileable texture swatch of worn black
   rubber-insulated electrical wire, fine lengthwise texture, flat even lighting, no text".
2. **The horns** have colour but no normal map, so their surface reads smooth up close. A normal map for their
   material can also be made procedurally.
3. **The udders, briefs and leggings** use made-up fabric tiles. They read correctly at viewing distance; if you
   want them closer to the real costume, square seamless photo swatches of each fabric (as for the cord, "flat
   material scan, even lighting, seamless") would replace them.
