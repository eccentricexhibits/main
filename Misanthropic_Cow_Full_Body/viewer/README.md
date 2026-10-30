# Browser viewer

`cow_viewer.html` is the page published as the claude.ai artifact "The Misanthropic Cow"
(https://claude.ai/artifact/XipWA3XmE5baJ84temvRp6). It loads three.js 0.160.0 from jsDelivr and three lighter
GLBs made by `scripts/bl_export_web_cow.py` from `deliver/Misanthropic_Cow.glb`:
`cow_body.glb` (10.5 MB, the mask included) and `cow_slippers.glb` (7.0 MB).
The artifact host serves only standard web file types, so each GLB is published base64-encoded as
`<name>.glb.b64.txt` (`base64 -w 0 cow_body.glb > cow_body.glb.b64.txt`) and decoded in the page. (`cow_mask.glb` comes out empty with face=tripo; it is not published.)
To rebuild: run the export script, encode the three files, publish the page with them as supporting files.
