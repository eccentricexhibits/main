# The general moves: rig checks per clip

Full-resolution build (44B), baked with the performance layer and physics. Stretch is the 99.9th-percentile edge stretch over the clip; the depths are 99.5th percentiles of how far one surface passes into the other, the worst frame of the clip; "Belly into legs" and "Legs into belly" count only surface that shows at rest. Three earlier clips are there to compare with (from the quick build).

| Clip | Length | Torso stretch × | Sleeve stretch × | Leggings stretch × | Arms into cups/torso (mm) | Gloves into body (mm) | Teats into belly (mm) | Belly into legs (mm) | Legs into belly (mm) | Lowest slipper point (mm) | Tail lowest point (mm) | Loop error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jump | 2.20 s | 1.92 | 1.93 | 3.14 | 0.0 | 0.0 | 2.0 | 1.3 | 20.6 | 3.0 | 306.6 | 1e-16 |
| Jump (alt) | 2.75 s | 1.88 | 1.55 | 3.07 | 0.0 | 0.0 | 4.5 | 2.5 | 21.6 | 3.0 | 315.4 | 2e-16 |
| Skid | 3.00 s | 1.94 | 1.71 | 2.55 | 0.0 | 0.0 | 3.1 | 0.0 | 16.1 | 3.0 | 312.3 | 1e-16 |
| Skid (alt) | 3.75 s | 1.83 | 1.54 | 2.53 | 0.0 | 0.0 | 4.7 | 0.0 | 18.2 | 3.0 | 311.4 | 2e-16 |
| Death | 7.40 s | 2.71 | 1.72 | 6.27 | 0.0 | 0.0 | 6.5 | 15.0 | 33.6 | 3.0 | -0.3 | 3e-16 |
| Death (alt) | 9.25 s | 2.71 | 1.63 | 6.18 | 0.0 | 0.0 | 6.5 | 15.8 | 36.8 | 2.9 | -0.5 | 2e-16 |
| Victory | 6.40 s | 1.95 | 1.97 | 2.25 | 0.0 | 0.0 | 0.4 | 0.0 | 14.2 | 3.0 | 281.5 | 1e-16 |
| Victory (alt) | 8.00 s | 1.94 | 1.87 | 2.2 | 0.0 | 0.0 | 0.6 | 0.0 | 16.1 | 3.0 | 296.4 | 1e-16 |
| *Jumping Jacks (for comparison)* | 4.00 s | 2.06 | 1.92 | 2.01 | 0.0 | 0.0 | 1.2 | 2.8 | 35.0 | 3.2 | 322.3 | 1e-15 |
| *Sit Cross-Legged (for comparison)* | 8.80 s | 1.8 | 2.0 | 4.54 | 0.0 | 0.0 | 4.9 | 7.8 | 25.4 | 3.0 | -0.3 | 2e-16 |
| *Chicken Dance (for comparison)* | 9.60 s | 2.06 | 2.66 | 1.89 | 0.0 | 0.8 | 3.7 | 0.0 | 31.7 | 3.0 | 310.3 | 1e-16 |

Notes: every one loops seamlessly (loop error at float precision) and starts and ends standing on her spot. Nothing goes into the body (arms, gloves 0 mm). Death is the hardest on the suit: lying with the legs kicked up the leggings stretch 6.27× at the hip crease (as in the game version), and getting up through the squat the belly settles 15 mm into the thighs (Sit Cross-Legged 7.8 mm) and the teats 6.5 mm into the belly. The tail cord rests on the floor (0 mm) as she lies on it.
