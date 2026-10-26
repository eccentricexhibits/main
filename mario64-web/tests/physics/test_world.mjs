// Builds the synthetic collision world used by the physics tests.
//
// Layout (SM64 units, y up, Mario forward = +z when cameraYaw = 0x8000):
//   - flat floor tiles (512x512) covering x,z in [-4096, 4096] at y = 0, except:
//       * a hole column x in [-4096, -3584] with a SURFACE_DEATH_PLANE floor at y = -3000
//       * a SURFACE_BURNING tile at x in [-3072, -2560], z in [-512, 0]
//       * tiles under the ramp are omitted (the ramp replaces them)
//   - "tall wall" box  x in [-2000, -1500], z in [1500, 2000], height 3000 (wall kicks)
//   - "ledge" box      x in [ 1500,  2000], z in [1500, 2000], height LEDGE_H (ledge grab)
//   - steep ramp       x in [ 2560,  3072], z in [-512, 512], rising from y=0 to y=RAMP_H (~50 deg)
//     followed by a plateau x in [3072, 3584] at y = RAMP_H
//   - boundary walls around the map

import { CollisionWorld } from '../../src/engine/surface.js';
import {
    SURFACE_DEFAULT, SURFACE_BURNING, SURFACE_DEATH_PLANE, SURFACE_HANGABLE,
} from '../../src/engine/surface_terrains.js';

export const LEDGE_H = 300;
export const RAMP_H = 600;
export const DEATH_Y = -3000;

function sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }

/** Normal using the SM64 convention: (v2 - v1) x (v3 - v2). */
function sm64Normal(v1, v2, v3) {
    return cross(sub(v2, v1), sub(v3, v2));
}

export function buildTestTris() {
    const tris = [];

    // Adds a planar quad (a, b, c, d in order around the edge), oriented so its
    // SM64 normal points along `outward`.
    function quad(a, b, c, d, outward, type = SURFACE_DEFAULT) {
        let t1 = [a, b, c];
        let t2 = [a, c, d];
        if (dot(sm64Normal(...t1), outward) < 0) {
            t1 = [c, b, a];
            t2 = [d, c, a];
        }
        tris.push({ v: t1, type, force: 0 });
        tris.push({ v: t2, type, force: 0 });
    }

    // Axis-aligned box with walls and a top face.
    function box(x0, z0, x1, z1, y0, y1, type = SURFACE_DEFAULT) {
        quad([x0, y1, z0], [x1, y1, z0], [x1, y1, z1], [x0, y1, z1], [0, 1, 0], type); // top
        quad([x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [0, 0, -1], type); // -z
        quad([x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1], [0, 0, 1], type); // +z
        quad([x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0], [-1, 0, 0], type); // -x
        quad([x1, y0, z0], [x1, y0, z1], [x1, y1, z1], [x1, y1, z0], [1, 0, 0], type); // +x
    }

    const T = 512;
    for (let x = -4096; x < 4096; x += T) {
        for (let z = -4096; z < 4096; z += T) {
            if (x < -3584) continue; // hole column
            if (x >= 2560 && x < 3584 && z >= -512 && z < 512) continue; // ramp + plateau footprint
            const type = (x === -3072 && z === -512) ? SURFACE_BURNING : SURFACE_DEFAULT;
            quad([x, 0, z], [x + T, 0, z], [x + T, 0, z + T], [x, 0, z + T], [0, 1, 0], type);
        }
    }

    // Death plane under the hole, and the cliff wall facing into the hole.
    quad([-4096, DEATH_Y, -4096], [-3584, DEATH_Y, -4096], [-3584, DEATH_Y, 4096], [-4096, DEATH_Y, 4096], [0, 1, 0], SURFACE_DEATH_PLANE);
    quad([-3584, DEATH_Y, -4096], [-3584, DEATH_Y, 4096], [-3584, 0, 4096], [-3584, 0, -4096], [-1, 0, 0]);

    // Tall wall box (wall kicks) and ledge box (ledge grab).
    box(-2000, 1500, -1500, 2000, 0, 3000);
    box(1500, 1500, 2000, 2000, 0, LEDGE_H);

    // Steep ramp rising along +x, plateau, and side / end walls.
    const rx0 = 2560, rx1 = 3072, rx2 = 3584, rz0 = -512, rz1 = 512;
    quad([rx0, 0, rz0], [rx1, RAMP_H, rz0], [rx1, RAMP_H, rz1], [rx0, 0, rz1], [-1, 1, 0]); // ramp
    quad([rx1, RAMP_H, rz0], [rx2, RAMP_H, rz0], [rx2, RAMP_H, rz1], [rx1, RAMP_H, rz1], [0, 1, 0]); // plateau
    // ramp side walls (triangles) + plateau side walls
    tris.push({ v: orient([[rx0, 0, rz0], [rx1, 0, rz0], [rx1, RAMP_H, rz0]], [0, 0, -1]), type: 0, force: 0 });
    tris.push({ v: orient([[rx0, 0, rz1], [rx1, 0, rz1], [rx1, RAMP_H, rz1]], [0, 0, 1]), type: 0, force: 0 });
    quad([rx1, 0, rz0], [rx2, 0, rz0], [rx2, RAMP_H, rz0], [rx1, RAMP_H, rz0], [0, 0, -1]);
    quad([rx1, 0, rz1], [rx2, 0, rz1], [rx2, RAMP_H, rz1], [rx1, RAMP_H, rz1], [0, 0, 1]);
    quad([rx2, 0, rz0], [rx2, 0, rz1], [rx2, RAMP_H, rz1], [rx2, RAMP_H, rz0], [1, 0, 0]);

    // A hangable ceiling (optional hanging test): a thin slab at y=400..410 over x,z in [500, 1000]x[-3000,-2500]
    quad([500, 400, -3000], [1000, 400, -3000], [1000, 400, -2500], [500, 400, -2500], [0, -1, 0], SURFACE_HANGABLE);

    // Boundary walls (inward facing).
    const B = 4096, H = 4000;
    quad([-B, DEATH_Y, -B], [B, DEATH_Y, -B], [B, H, -B], [-B, H, -B], [0, 0, 1]);
    quad([-B, DEATH_Y, B], [B, DEATH_Y, B], [B, H, B], [-B, H, B], [0, 0, -1]);
    quad([-B, DEATH_Y, -B], [-B, DEATH_Y, B], [-B, H, B], [-B, H, -B], [1, 0, 0]);
    quad([B, DEATH_Y, -B], [B, DEATH_Y, B], [B, H, B], [B, H, -B], [-1, 0, 0]);

    return tris;

    function orient(t, outward) {
        return dot(sm64Normal(...t), outward) < 0 ? [t[2], t[1], t[0]] : t;
    }
}

export function buildTestWorld() {
    return new CollisionWorld(buildTestTris());
}
