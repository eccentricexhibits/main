# Round 46: rig checks per clip, against round 45

Each cell is round 45 → round 46 (quick-resolution build; the clips are the ones in the round 46 GLB). Stretch is the 99.9th-percentile edge stretch over the clip;
the depths are 99.5th percentiles of how far one surface passes into the other, the worst frame of the clip. "Belly into legs" and "Legs into belly" count only surface that shows at rest;
"Legs into belly" also counts the tops of the briefs that the hem covers as the body bends (see the handoff notes). Teats are measured against the posed belly fur.
Round 46 made the hood follow the head round the mask (rig.hood_follow_mask), slimmed the neck under the chin, turned the relaxed hands palms-in with a
softer elbow and a straight wrist (RELAXED_TWIST, REST_ARM, RELAXED_DIR), made the sleeve heads smaller and the shoulder correctives' fillet tighter, and
added armpit hair. Nothing goes into the body in any clip and no depth changed; the torso stretch is a little lower in every clip (Walk 1.50 -> 1.35,
Crying 1.78 -> 1.65) and the sleeve stretch in Idle and Walk 1.90 -> 1.59. The largest arm turn in one frame is unchanged in most clips; Exasperated's
fling from the rest pose is the same curve, a little faster at its end (one frame 36.6 -> 45.9 degrees), as the new rest arm starts further from it.
| Clip | Torso stretch × | Sleeve stretch × | Leggings stretch × | Arms into cups/torso (mm) | Gloves into body (mm) | Teats into belly (mm) | Belly into legs (mm) | Legs into belly (mm) |
|---|---|---|---|---|---|---|---|---|
| Idle | 1.37 → **1.32** | 1.9 → **1.59** | 1.58 → **1.58** | 0.0 → **0.0** | 0.0 → **0.0** | 0.4 → **0.4** | 0.0 → **0.0** | 18.0 → **18.0** |
| Walk | 1.5 → **1.35** | 1.9 → **1.59** | 2.11 → **2.11** | 0.0 → **0.0** | 0.0 → **0.0** | 1.3 → **1.3** | 0.6 → **0.6** | 45.1 → **45.1** |
| Run | 1.75 → **1.69** | 1.93 → **1.93** | 2.85 → **2.85** | 0.0 → **0.0** | 0.0 → **0.0** | 2.1 → **2.1** | 0.0 → **0.0** | 17.8 → **17.8** |
| Sneak | 1.81 → **1.73** | 2.51 → **2.51** | 2.92 → **2.92** | 0.0 → **0.0** | 0.0 → **0.0** | 1.2 → **1.2** | 0.0 → **0.0** | 20.7 → **20.7** |
| Jumping Jacks | 2.1 → **2.04** | 1.98 → **1.95** | 2.01 → **2.01** | 0.0 → **0.0** | 0.0 → **0.0** | 1.2 → **1.2** | 2.8 → **2.8** | 35.0 → **35.0** |
| Look Around | 2.17 → **2.1** | 2.16 → **2.16** | 1.32 → **1.32** | 0.0 → **0.0** | 0.0 → **0.0** | 0.3 → **0.3** | 0.0 → **0.0** | 6.9 → **6.9** |
| Chicken Dance | 2.07 → **2.02** | 2.66 → **2.66** | 1.89 → **1.89** | 0.0 → **0.0** | 0.8 → **0.8** | 3.7 → **3.7** | 0.0 → **0.0** | 31.7 → **31.7** |
| Depressed Walk | 1.49 → **1.4** | 1.36 → **1.36** | 2.0 → **2.0** | 0.0 → **0.0** | 0.0 → **0.0** | 1.2 → **1.2** | 2.8 → **2.8** | 43.7 → **43.7** |
| Sit Cross-Legged | 1.87 → **1.79** | 2.0 → **2.0** | 4.56 → **4.56** | 0.0 → **0.0** | 0.0 → **0.0** | 5.8 → **5.8** | 8.6 → **8.6** | 26.1 → **26.1** |
| Crying | 1.78 → **1.65** | 2.29 → **2.29** | 1.62 → **1.62** | 0.0 → **0.0** | 0.0 → **0.0** | 1.9 → **1.9** | 0.0 → **0.0** | 26.5 → **26.5** |
| Exasperated | 1.68 → **1.56** | 2.41 → **2.41** | 1.36 → **1.36** | 0.0 → **0.0** | 0.0 → **0.0** | 0.7 → **0.7** | 0.0 → **0.0** | 9.5 → **9.5** |
| Idle (alt) | 1.34 → **1.29** | 1.9 → **1.59** | 1.71 → **1.71** | 0.0 → **0.0** | 0.0 → **0.0** | 0.9 → **0.9** | 0.0 → **0.0** | 25.8 → **25.8** |
| Walk (alt) | 1.38 → **1.29** | 1.9 → **1.59** | 2.06 → **2.06** | 0.0 → **0.0** | 0.0 → **0.0** | 1.4 → **1.4** | 1.0 → **1.0** | 44.2 → **44.2** |
| Run (alt) | 1.64 → **1.58** | 1.81 → **1.81** | 2.6 → **2.6** | 0.0 → **0.0** | 0.0 → **0.0** | 2.0 → **2.0** | 0.0 → **0.0** | 18.5 → **18.5** |
| Sneak (alt) | 1.74 → **1.63** | 2.5 → **2.5** | 2.69 → **2.69** | 0.0 → **0.0** | 0.0 → **0.0** | 1.6 → **1.6** | 0.0 → **0.0** | 19.9 → **19.9** |
| Jumping Jacks (alt) | 1.93 → **1.83** | 1.83 → **1.82** | 2.01 → **2.01** | 0.0 → **0.0** | 0.0 → **0.0** | 0.8 → **0.8** | 3.1 → **3.1** | 32.7 → **32.7** |
| Look Around (alt) | 2.03 → **2.0** | 2.16 → **2.16** | 1.48 → **1.48** | 0.0 → **0.0** | 0.0 → **0.0** | 0.2 → **0.2** | 0.0 → **0.0** | 16.8 → **16.8** |
| Chicken Dance (alt) | 1.92 → **1.85** | 2.65 → **2.65** | 1.87 → **1.87** | 0.0 → **0.0** | 0.0 → **0.0** | 4.1 → **4.1** | 0.0 → **0.0** | 32.7 → **32.7** |
