# Round 44C: rig checks per clip, against round 44B

Each cell is round 44B → round 44C (quick-resolution build; the clips are the ones in the round 44C GLB, which are 44B's). Stretch is the 99.9th-percentile edge stretch over the clip;
the depths are 99.5th percentiles of how far one surface passes into the other, the worst frame of the clip. "Belly into legs" and "Legs into belly" count only surface that shows at rest;
"Legs into belly" also counts the tops of the briefs that the hem covers as the body bends (see the handoff notes). Teats are measured against the posed belly fur.
Round 44C is 44B with the shoulder trim (correctives.shoulder_trim: the cap's overhang drawn in as the arm swings) and more armpit hair (groom.ARMPIT_LOW).
Nothing goes into the body in any clip and no depth changed; the torso stretch is the same or a little lower (Chicken Dance 2.06 -> 1.99). GLB 104.5 MB
(99.7 MiB), glTF validator 0 errors and 0 warnings.
| Clip | Torso stretch × | Sleeve stretch × | Leggings stretch × | Arms into cups/torso (mm) | Gloves into body (mm) | Teats into belly (mm) | Belly into legs (mm) | Legs into belly (mm) |
|---|---|---|---|---|---|---|---|---|
| Idle | 1.33 → **1.33** | 1.83 → **1.83** | 1.58 → **1.58** | 0.0 → **0.0** | 0.0 → **0.0** | 0.4 → **0.4** | 0.0 → **0.0** | 18.0 → **18.0** |
| Walk | 1.41 → **1.4** | 1.83 → **1.83** | 2.11 → **2.11** | 0.0 → **0.0** | 0.0 → **0.0** | 1.3 → **1.3** | 0.6 → **0.6** | 45.1 → **45.1** |
| Run | 1.71 → **1.71** | 1.93 → **1.93** | 2.85 → **2.85** | 0.0 → **0.0** | 0.0 → **0.0** | 2.1 → **2.1** | 0.0 → **0.0** | 17.8 → **17.8** |
| Sneak | 1.74 → **1.74** | 2.51 → **2.51** | 2.92 → **2.92** | 0.0 → **0.0** | 0.0 → **0.0** | 1.2 → **1.2** | 0.0 → **0.0** | 20.7 → **20.7** |
| Jumping Jacks | 2.06 → **2.05** | 1.92 → **1.92** | 2.01 → **2.01** | 0.0 → **0.0** | 0.0 → **0.0** | 1.2 → **1.2** | 2.8 → **2.8** | 35.0 → **35.0** |
| Look Around | 2.14 → **2.14** | 2.16 → **2.16** | 1.32 → **1.32** | 0.0 → **0.0** | 0.0 → **0.0** | 0.3 → **0.3** | 0.0 → **0.0** | 6.9 → **6.9** |
| Chicken Dance | 2.06 → **1.99** | 2.66 → **2.66** | 1.89 → **1.89** | 0.0 → **0.0** | 0.8 → **0.8** | 3.7 → **3.7** | 0.0 → **0.0** | 31.7 → **31.7** |
| Depressed Walk | 1.45 → **1.45** | 1.36 → **1.36** | 2.0 → **2.0** | 0.0 → **0.0** | 0.0 → **0.0** | 1.2 → **1.2** | 2.8 → **2.8** | 43.7 → **43.7** |
| Sit Cross-Legged | 1.82 → **1.82** | 1.99 → **1.99** | 4.56 → **4.56** | 0.0 → **0.0** | 0.0 → **0.0** | 5.8 → **5.8** | 8.6 → **8.6** | 26.1 → **26.1** |
| Crying | 1.66 → **1.64** | 2.29 → **2.29** | 1.62 → **1.62** | 0.0 → **0.0** | 0.0 → **0.0** | 1.9 → **1.9** | 0.0 → **0.0** | 26.5 → **26.5** |
| Exasperated | 1.63 → **1.6** | 2.41 → **2.41** | 1.36 → **1.36** | 0.0 → **0.0** | 0.0 → **0.0** | 0.7 → **0.7** | 0.0 → **0.0** | 9.5 → **9.5** |
| Idle (alt) | 1.29 → **1.29** | 1.83 → **1.83** | 1.71 → **1.71** | 0.0 → **0.0** | 0.0 → **0.0** | 0.9 → **0.9** | 0.0 → **0.0** | 25.8 → **25.8** |
| Walk (alt) | 1.34 → **1.34** | 1.83 → **1.83** | 2.06 → **2.06** | 0.0 → **0.0** | 0.0 → **0.0** | 1.4 → **1.4** | 1.0 → **1.0** | 44.2 → **44.2** |
| Run (alt) | 1.59 → **1.59** | 1.81 → **1.81** | 2.6 → **2.6** | 0.0 → **0.0** | 0.0 → **0.0** | 2.0 → **2.0** | 0.0 → **0.0** | 18.5 → **18.5** |
| Sneak (alt) | 1.65 → **1.64** | 2.5 → **2.5** | 2.69 → **2.69** | 0.0 → **0.0** | 0.0 → **0.0** | 1.6 → **1.6** | 0.0 → **0.0** | 19.9 → **19.9** |
| Jumping Jacks (alt) | 1.89 → **1.88** | 1.82 → **1.82** | 2.01 → **2.01** | 0.0 → **0.0** | 0.0 → **0.0** | 0.9 → **0.9** | 3.1 → **3.1** | 32.7 → **32.7** |
| Look Around (alt) | 2.02 → **2.02** | 2.16 → **2.16** | 1.48 → **1.48** | 0.0 → **0.0** | 0.0 → **0.0** | 0.2 → **0.2** | 0.0 → **0.0** | 16.8 → **16.8** |
| Chicken Dance (alt) | 1.87 → **1.85** | 2.65 → **2.65** | 1.87 → **1.87** | 0.0 → **0.0** | 0.0 → **0.0** | 4.1 → **4.1** | 0.0 → **0.0** | 32.7 → **32.7** |
