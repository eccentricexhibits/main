# The platformer set: rig checks per clip

Full-resolution build (44B), baked with the performance layer and physics. Stretch is the 99.9th-percentile edge stretch over the clip; the depths are 99.5th percentiles of how far one surface passes into the other, the worst frame of the clip; "Belly into legs" and "Legs into belly" count only surface that shows at rest. Sit Cross-Legged (the standard version, from the quick build) is there to compare with: the deepest squat and the only other clip on the floor.
The one-shots do not loop (their first and last frames differ on purpose), so the loop check does not apply to them. Jump Rise, Fall and Victory loop seamlessly (loop error 0).

| Clip | Length | Torso stretch × | Sleeve stretch × | Leggings stretch × | Arms into cups/torso (mm) | Gloves into body (mm) | Teats into belly (mm) | Belly into legs (mm) | Legs into belly (mm) | Lowest slipper point (mm) | Tail lowest point (mm) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Jump Start | 0.4 s | 1.87 | 1.54 | 2.93 | 0.0 | 0.0 | 0.0 | 0.0 | 19.2 | 3.0 | 317.5 |
| Jump Rise | 0.6 s | 2.16 | 1.95 | 3.8 | 0.0 | 0.0 | 0.0 | 0.3 | 23.5 | 158.0 | 408.6 |
| Jump Apex | 0.3 s | 2.1 | 1.93 | 3.68 | 0.0 | 0.0 | 0.1 | 1.3 | 22.7 | 53.0 | 408.6 |
| Fall | 0.8 s | 1.77 | 1.54 | 2.62 | 0.0 | 0.0 | 0.0 | 0.0 | 14.6 | 53.0 | 411.7 |
| Land | 0.5 s | 1.69 | 1.54 | 2.71 | 0.0 | 0.0 | 0.0 | 0.0 | 18.5 | 3.0 | 317.1 |
| Hard Landing | 1.1 s | 2.26 | 1.59 | 3.75 | 0.0 | 0.0 | 1.2 | 1.9 | 28.2 | 3.0 | 272.1 |
| Skid | 0.6 s | 1.88 | 1.54 | 1.92 | 0.0 | 0.0 | 1.7 | 0.0 | 6.8 | 3.0 | 306.1 |
| Hurt | 0.6 s | 1.84 | 1.54 | 2.05 | 0.0 | 0.0 | 0.0 | 0.0 | 15.4 | 3.0 | 348.0 |
| Death | 2.6 s | 2.45 | 1.61 | 6.27 | 0.0 | 0.0 | 3.5 | 6.8 | 33.7 | 3.0 | -0.3 |
| Victory | 2.4 s | 2.0 | 1.81 | 1.63 | 0.0 | 0.0 | 0.0 | 0.0 | 9.3 | 3.0 | 359.1 |
| *Sit Cross-Legged (for comparison)* | 11.0 s | 1.8 | 2.0 | 4.54 | 0.0 | 0.0 | 4.9 | 7.8 | 25.4 | 3.0 | -0.3 |

Notes: the airborne clips (Jump Rise, Jump Apex, Fall) hold the slippers off the floor by design (lowest point 158 mm in Jump Rise). Death ends lying on her back: the leggings stretch most there (6.27, at the hip crease with the legs kicked up; Sit Cross-Legged 4.54); nothing passes into the body. The tail cord rests on the floor (0 mm) as she lies on it.

The 24 earlier animations are byte-for-byte as they were (keyframes compared between the old and new GLB); their glTF extras gained only `loop: true`.
