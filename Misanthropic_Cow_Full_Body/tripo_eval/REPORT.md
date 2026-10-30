# Tripo model, round 1: evaluation

Model: `cow_costume_3d_model.obj` with base colour, normal, roughness and metallic maps. It's the user's upload and isn't stored in the repo (194 MB).

| Measure | Result |
|---|---|
| Size | 0.978 tall × 0.623 wide (arm span) × 0.301 deep (units). The scale is arbitrary: the real height is needed. |
| Triangles | 1,923,634 (993,968 vertices, split at UV seams; 961,815 after welding) |
| Connected parts | 1, so no floating debris |
| Silhouette IoU vs input views | front 0.856, back 0.861, left 0.901, right 0.882 |
| Front/back width | 4–8% wider than the view at belly and chest height |
| Side depth | within ~3% of the views. The model's udder matches the left view; the enlarged right view ran ~13% deeper at udder height. |
| Metallic map | mean 0.141, 95th percentile 0.259, max 0.765. Needs to be 0 for fabric. |
| Roughness map | mean 0.716 |

Made as geometry: the mask (brow, eyes, snout, nostril slits), both horns (the wire tuft as thin strands), the hood and bolster, the udder lobes and nubs, the shaggy patches, the bow, the gloves (thumb and two hoof halves), the shorts, the legs and both slippers.

Files:
- `sheet_tex.jpg` / `sheet_clay.jpg`: textured and clay renders from eight directions.
- `sil_sheet.jpg`: silhouette overlays. Grey is both, red is the view only, blue is the model only.
- `closeups.jpg`: the head, udder, hand, slippers and back.

Camera convention for renders: OBJ +Y is up and the front faces +Z. The costume's own left is at +X, so `left_side` is a camera on +X.
