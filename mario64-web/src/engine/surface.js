// Port of src/engine/surface_load.c (surface creation + static spatial
// partition) and src/engine/surface_collision.c (floor / ceiling / wall
// queries). Only static (level) surfaces are supported; the dynamic partition
// of the original is always empty here, which matches a level without
// collidable objects.

import { s16 } from './math_util.js';
import {
    SURFACE_CAMERA_BOUNDARY,
    SURFACE_INTANGIBLE,
    SURFACE_FLAG_DYNAMIC,
    SURFACE_FLAG_NO_CAM_COLLISION,
    SURFACE_FLAG_X_PROJECTION,
    SURFACE_0004,
    SURFACE_FLOWING_WATER,
    SURFACE_DEEP_MOVING_QUICKSAND,
    SURFACE_SHALLOW_MOVING_QUICKSAND,
    SURFACE_MOVING_QUICKSAND,
    SURFACE_HORIZONTAL_WIND,
    SURFACE_INSTANT_MOVING_QUICKSAND,
    SURFACE_NO_CAM_COLLISION,
    SURFACE_NO_CAM_COLLISION_77,
    SURFACE_NO_CAM_COL_VERY_SLIPPERY,
    SURFACE_SWITCH,
} from './surface_terrains.js';

export { SURFACE_FLAG_DYNAMIC };

// Range level area is 16384x16384 (-8192 to +8192 in x and z)
export const LEVEL_BOUNDARY_MAX = 0x2000;
export const CELL_SIZE = 1 << 10;
export const NUM_CELLS = 2 * LEVEL_BOUNDARY_MAX / CELL_SIZE; // 16
export const NUM_CELLS_INDEX = NUM_CELLS - 1;
export const CELL_HEIGHT_LIMIT = 20000;
export const FLOOR_LOWER_LIMIT = -11000;
export const FLOOR_LOWER_LIMIT_MISC = FLOOR_LOWER_LIMIT + 1000;

export const SPATIAL_PARTITION_FLOORS = 0;
export const SPATIAL_PARTITION_CEILS = 1;
export const SPATIAL_PARTITION_WALLS = 2;

/** struct Surface */
export class Surface {
    constructor() {
        this.type = 0;
        this.force = 0;
        this.flags = 0;
        this.room = 0;
        this.lowerY = 0;
        this.upperY = 0;
        this.vertex1 = [0, 0, 0];
        this.vertex2 = [0, 0, 0];
        this.vertex3 = [0, 0, 0];
        this.normal = { x: 0, y: 0, z: 0 };
        this.originOffset = 0;
        this.object = null;
        this.index = -1; // index of the source triangle in the input array
    }
}

/** struct WallCollisionData */
export function createWallCollisionData(x = 0, y = 0, z = 0, offsetY = 0, radius = 0) {
    return { x, y, z, offsetY, radius, numWalls: 0, walls: [null, null, null, null] };
}

function surface_has_force(surfaceType) {
    switch (surfaceType) {
        case SURFACE_0004: // Unused
        case SURFACE_FLOWING_WATER:
        case SURFACE_DEEP_MOVING_QUICKSAND:
        case SURFACE_SHALLOW_MOVING_QUICKSAND:
        case SURFACE_MOVING_QUICKSAND:
        case SURFACE_HORIZONTAL_WIND:
        case SURFACE_INSTANT_MOVING_QUICKSAND:
            return true;
        default:
            return false;
    }
}

function surf_has_no_cam_collision(surfaceType) {
    switch (surfaceType) {
        case SURFACE_NO_CAM_COLLISION:
        case SURFACE_NO_CAM_COLLISION_77: // Unused
        case SURFACE_NO_CAM_COL_VERY_SLIPPERY:
        case SURFACE_SWITCH:
            return SURFACE_FLAG_NO_CAM_COLLISION;
        default:
            return 0;
    }
}

function min_3(a0, a1, a2) {
    if (a1 < a0) a0 = a1;
    if (a2 < a0) a0 = a2;
    return a0;
}

function max_3(a0, a1, a2) {
    if (a1 > a0) a0 = a1;
    if (a2 > a0) a0 = a2;
    return a0;
}

/** Lower cell index for a coordinate (with a 50 unit buffer). */
function lower_cell_index(coord) {
    // Move from range [-0x2000, 0x2000) to [0, 0x4000)
    coord = s16(coord + LEVEL_BOUNDARY_MAX);
    if (coord < 0) {
        coord = 0;
    }

    // [0, 16)
    let index = (coord / CELL_SIZE) | 0;

    // Include extra cell if close to boundary
    //! Some wall checks are larger than the buffer, meaning wall checks can
    //  miss walls that are near a cell border.
    if (coord % CELL_SIZE < 50) {
        index--;
    }

    if (index < 0) {
        index = 0;
    }

    // Potentially > 15, but since the upper index is <= 15, not exploitable
    return index;
}

/** Upper cell index for a coordinate (with a 50 unit buffer). */
function upper_cell_index(coord) {
    coord = s16(coord + LEVEL_BOUNDARY_MAX);
    if (coord < 0) {
        coord = 0;
    }

    let index = (coord / CELL_SIZE) | 0;

    if (coord % CELL_SIZE > CELL_SIZE - 50) {
        index++;
    }

    if (index > NUM_CELLS_INDEX) {
        index = NUM_CELLS_INDEX;
    }

    // Potentially < 0, but since lower index is >= 0, not exploitable
    return index;
}

/**
 * read_surface_data: initializes a Surface from 3 vertices (s16 coordinates).
 * Returns null for degenerate triangles.
 */
function read_surface_data(v1, v2, v3) {
    const x1 = v1[0], y1 = v1[1], z1 = v1[2];
    const x2 = v2[0], y2 = v2[1], z2 = v2[2];
    const x3 = v3[0], y3 = v3[1], z3 = v3[2];

    // (v2 - v1) x (v3 - v2), computed in s32 then converted to f32
    let nx = Math.fround((y2 - y1) * (z3 - z2) - (z2 - z1) * (y3 - y2));
    let ny = Math.fround((z2 - z1) * (x3 - x2) - (x2 - x1) * (z3 - z2));
    let nz = Math.fround((x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2));
    let mag = Math.fround(Math.sqrt(Math.fround(Math.fround(nx * nx) + Math.fround(ny * ny)) + Math.fround(nz * nz)));

    let minY = y1;
    if (y2 < minY) minY = y2;
    if (y3 < minY) minY = y3;

    let maxY = y1;
    if (y2 > maxY) maxY = y2;
    if (y3 > maxY) maxY = y3;

    // Checking to make sure no DIV/0
    if (mag < 0.0001) {
        return null;
    }
    mag = Math.fround(1.0 / mag);
    nx = Math.fround(nx * mag);
    ny = Math.fround(ny * mag);
    nz = Math.fround(nz * mag);

    const surface = new Surface();
    surface.vertex1 = [x1, y1, z1];
    surface.vertex2 = [x2, y2, z2];
    surface.vertex3 = [x3, y3, z3];
    surface.normal = { x: nx, y: ny, z: nz };
    surface.originOffset = Math.fround(-(nx * x1 + ny * y1 + nz * z1));
    surface.lowerY = minY - 5;
    surface.upperY = maxY + 5;
    return surface;
}

function toTerrainData(v) {
    return s16(Math.round(v));
}

/**
 * The level's static collision. `tris` is an array of
 * { v: [[x,y,z],[x,y,z],[x,y,z]], type: SURFACE_*, force: 0 } in SM64 units and
 * SM64 winding (normal = normalized (v2-v1) x (v3-v2)).
 */
export class CollisionWorld {
    constructor(tris = []) {
        // gStaticSurfacePartition[cellZ][cellX][listType] -> array of surfaces in list order
        this.partition = [];
        for (let z = 0; z < NUM_CELLS; z++) {
            const row = [];
            for (let x = 0; x < NUM_CELLS; x++) {
                row.push([[], [], []]);
            }
            this.partition.push(row);
        }
        this.surfaces = [];
        /** Optional environment regions: [{ type, x1, z1, x2, z2, y }] (water < 50, gas >= 50). */
        this.environmentRegions = null;
        /** Mirrors gCheckingSurfaceCollisionsForCamera. */
        this.checkingForCamera = false;
        /** Mirrors gFindFloorIncludeSurfaceIntangible. */
        this.findFloorIncludeSurfaceIntangible = false;

        for (let i = 0; i < tris.length; i++) {
            const t = tris[i];
            this.addTriangle(t.v[0], t.v[1], t.v[2], t.type | 0, t.force | 0, i);
        }
    }

    /** load_static_surfaces for a single triangle. */
    addTriangle(a, b, c, type = 0, force = 0, index = -1) {
        const surface = read_surface_data(
            [toTerrainData(a[0]), toTerrainData(a[1]), toTerrainData(a[2])],
            [toTerrainData(b[0]), toTerrainData(b[1]), toTerrainData(b[2])],
            [toTerrainData(c[0]), toTerrainData(c[1]), toTerrainData(c[2])],
        );
        if (surface === null) {
            return null;
        }
        surface.room = 0;
        surface.type = type;
        surface.flags = surf_has_no_cam_collision(type);
        surface.force = surface_has_force(type) ? force : 0;
        surface.index = index;
        this.surfaces.push(surface);
        this.add_surface(surface);
        return surface;
    }

    /** add_surface: add the surface to every cell its bounding box (plus buffer) touches. */
    add_surface(surface) {
        const minX = min_3(surface.vertex1[0], surface.vertex2[0], surface.vertex3[0]);
        const minZ = min_3(surface.vertex1[2], surface.vertex2[2], surface.vertex3[2]);
        const maxX = max_3(surface.vertex1[0], surface.vertex2[0], surface.vertex3[0]);
        const maxZ = max_3(surface.vertex1[2], surface.vertex2[2], surface.vertex3[2]);

        const minCellX = lower_cell_index(minX);
        const maxCellX = upper_cell_index(maxX);
        const minCellZ = lower_cell_index(minZ);
        const maxCellZ = upper_cell_index(maxZ);

        for (let cellZ = minCellZ; cellZ <= maxCellZ; cellZ++) {
            for (let cellX = minCellX; cellX <= maxCellX; cellX++) {
                this.add_surface_to_cell(cellX, cellZ, surface);
            }
        }
    }

    /** add_surface_to_cell: sorted insertion as in the original. */
    add_surface_to_cell(cellX, cellZ, surface) {
        let listIndex;
        let sortDir;

        if (surface.normal.y > 0.01) {
            listIndex = SPATIAL_PARTITION_FLOORS;
            sortDir = 1; // highest to lowest, then insertion order
        } else if (surface.normal.y < -0.01) {
            listIndex = SPATIAL_PARTITION_CEILS;
            sortDir = -1; // lowest to highest, then insertion order
        } else {
            listIndex = SPATIAL_PARTITION_WALLS;
            sortDir = 0; // insertion order

            if (surface.normal.x < -0.707 || surface.normal.x > 0.707) {
                surface.flags |= SURFACE_FLAG_X_PROJECTION;
            }
        }

        //! (Surface Cucking) Surfaces are sorted by the height of their first vertex.
        const surfacePriority = s16(surface.vertex1[1] * sortDir);
        const list = this.partition[cellZ][cellX][listIndex];

        let i = 0;
        while (i < list.length) {
            const priority = s16(list[i].vertex1[1] * sortDir);
            if (surfacePriority > priority) {
                break;
            }
            i++;
        }
        list.splice(i, 0, surface);
    }

    // -----------------------------------------------------------------------
    // WALLS
    // -----------------------------------------------------------------------

    /** find_wall_collisions_from_list */
    find_wall_collisions_from_list(list, data) {
        let radius = data.radius;
        const x = data.x;
        const y = data.y + data.offsetY;
        const z = data.z;
        let numCols = 0;

        // Max collision radius = 200
        if (radius > 200.0) {
            radius = 200.0;
        }

        for (let n = 0; n < list.length; n++) {
            const surf = list[n];

            // Exclude a large number of walls immediately to optimize.
            if (y < surf.lowerY || y > surf.upperY) {
                continue;
            }

            const offset = surf.normal.x * x + surf.normal.y * y + surf.normal.z * z + surf.originOffset;

            if (offset < -radius || offset > radius) {
                continue;
            }

            const px = x;
            const pz = z;

            //! (Quantum Tunneling) Due to issues with the vertices walls choose and
            //  the fact they are floating point, certain floating point positions
            //  along the seam of two walls may collide with neither wall or both walls.
            if (surf.flags & SURFACE_FLAG_X_PROJECTION) {
                const w1 = -surf.vertex1[2], w2 = -surf.vertex2[2], w3 = -surf.vertex3[2];
                const y1 = surf.vertex1[1], y2 = surf.vertex2[1], y3 = surf.vertex3[1];

                if (surf.normal.x > 0.0) {
                    if ((y1 - y) * (w2 - w1) - (w1 - -pz) * (y2 - y1) > 0.0) continue;
                    if ((y2 - y) * (w3 - w2) - (w2 - -pz) * (y3 - y2) > 0.0) continue;
                    if ((y3 - y) * (w1 - w3) - (w3 - -pz) * (y1 - y3) > 0.0) continue;
                } else {
                    if ((y1 - y) * (w2 - w1) - (w1 - -pz) * (y2 - y1) < 0.0) continue;
                    if ((y2 - y) * (w3 - w2) - (w2 - -pz) * (y3 - y2) < 0.0) continue;
                    if ((y3 - y) * (w1 - w3) - (w3 - -pz) * (y1 - y3) < 0.0) continue;
                }
            } else {
                const w1 = surf.vertex1[0], w2 = surf.vertex2[0], w3 = surf.vertex3[0];
                const y1 = surf.vertex1[1], y2 = surf.vertex2[1], y3 = surf.vertex3[1];

                if (surf.normal.z > 0.0) {
                    if ((y1 - y) * (w2 - w1) - (w1 - px) * (y2 - y1) > 0.0) continue;
                    if ((y2 - y) * (w3 - w2) - (w2 - px) * (y3 - y2) > 0.0) continue;
                    if ((y3 - y) * (w1 - w3) - (w3 - px) * (y1 - y3) > 0.0) continue;
                } else {
                    if ((y1 - y) * (w2 - w1) - (w1 - px) * (y2 - y1) < 0.0) continue;
                    if ((y2 - y) * (w3 - w2) - (w2 - px) * (y3 - y2) < 0.0) continue;
                    if ((y3 - y) * (w1 - w3) - (w3 - px) * (y1 - y3) < 0.0) continue;
                }
            }

            // Determine if checking for the camera or not.
            if (this.checkingForCamera) {
                if (surf.flags & SURFACE_FLAG_NO_CAM_COLLISION) {
                    continue;
                }
            } else {
                // Ignore camera only surfaces.
                if (surf.type === SURFACE_CAMERA_BOUNDARY) {
                    continue;
                }
                // (SURFACE_VANISH_CAP_WALLS pass-through omitted: no vanish cap / objects.)
            }

            //! (Wall Overlaps) Because this doesn't update the x and z local variables,
            //  multiple walls can push mario more than is required.
            data.x += surf.normal.x * (radius - offset);
            data.z += surf.normal.z * (radius - offset);

            //! (Unreferenced Walls) Since this only returns the first four walls,
            //  this can lead to wall interaction being missed.
            if (data.numWalls < 4) {
                data.walls[data.numWalls++] = surf;
            }

            numCols++;
        }

        return numCols;
    }

    /**
     * find_wall_collisions(struct WallCollisionData *colData).
     * `data` = { x, y, z, offsetY, radius, numWalls, walls[4] } (see createWallCollisionData).
     * Updates data.x / data.z with the wall push. Returns the number of collisions.
     */
    find_wall_collisions(data) {
        let numCollisions = 0;
        const x = s16(data.x);
        const z = s16(data.z);

        data.numWalls = 0;
        if (!data.walls) data.walls = [null, null, null, null];

        if (x <= -LEVEL_BOUNDARY_MAX || x >= LEVEL_BOUNDARY_MAX) {
            return numCollisions;
        }
        if (z <= -LEVEL_BOUNDARY_MAX || z >= LEVEL_BOUNDARY_MAX) {
            return numCollisions;
        }

        const cellX = ((x + LEVEL_BOUNDARY_MAX) / CELL_SIZE) & NUM_CELLS_INDEX;
        const cellZ = ((z + LEVEL_BOUNDARY_MAX) / CELL_SIZE) & NUM_CELLS_INDEX;

        // (Dynamic surface partition is always empty.)
        numCollisions += this.find_wall_collisions_from_list(this.partition[cellZ][cellX][SPATIAL_PARTITION_WALLS], data);

        return numCollisions;
    }

    /**
     * f32_find_wall_collision: operates on a Vec3f-like array `pos` in place.
     */
    f32_find_wall_collision(pos, offsetY, radius) {
        const collision = createWallCollisionData(pos[0], pos[1], pos[2], offsetY, radius);
        const numCollisions = this.find_wall_collisions(collision);
        pos[0] = collision.x;
        pos[1] = collision.y;
        pos[2] = collision.z;
        return numCollisions;
    }

    // -----------------------------------------------------------------------
    // CEILINGS
    // -----------------------------------------------------------------------

    /** find_ceil_from_list: returns { surface, height } or null. x, y, z are integers. */
    find_ceil_from_list(list, x, y, z) {
        for (let n = 0; n < list.length; n++) {
            const surf = list[n];

            const x1 = surf.vertex1[0];
            const z1 = surf.vertex1[2];
            const z2 = surf.vertex2[2];
            const x2 = surf.vertex2[0];

            // Checking if point is in bounds of the triangle laterally.
            if ((z1 - z) * (x2 - x1) - (x1 - x) * (z2 - z1) > 0) {
                continue;
            }

            const x3 = surf.vertex3[0];
            const z3 = surf.vertex3[2];
            if ((z2 - z) * (x3 - x2) - (x2 - x) * (z3 - z2) > 0) {
                continue;
            }
            if ((z3 - z) * (x1 - x3) - (x3 - x) * (z1 - z3) > 0) {
                continue;
            }

            if (this.checkingForCamera) {
                if (surf.flags & SURFACE_FLAG_NO_CAM_COLLISION) {
                    continue;
                }
            } else if (surf.type === SURFACE_CAMERA_BOUNDARY) {
                continue;
            }

            const nx = surf.normal.x;
            const ny = surf.normal.y;
            const nz = surf.normal.z;
            const oo = surf.originOffset;

            // If a wall, ignore it. Likely a remnant, should never occur.
            if (ny === 0.0) {
                continue;
            }

            // Find the ceil height at the specific point.
            const height = Math.fround(-(x * nx + nz * z + oo) / ny);

            // Checks for ceiling interaction with a 78 unit buffer.
            //! (Exposed Ceilings) Because any point above a ceiling counts
            //  as interacting with a ceiling, ceilings far below can cause
            // "invisible walls" that are really just exposed ceilings.
            if (y - (height - -78.0) > 0.0) {
                continue;
            }

            //! (Surface Cucking) Since only the first ceil is returned and not the lowest,
            //  lower ceilings can be "cucked" by higher ceilings.
            return { surface: surf, height };
        }
        return null;
    }

    /**
     * find_ceil: returns { height, surface } where height = CELL_HEIGHT_LIMIT and
     * surface = null when there is no ceiling.
     */
    find_ceil(posX, posY, posZ) {
        let height = CELL_HEIGHT_LIMIT;

        //! (Parallel Universes) Because position is casted to an s16, reaching higher
        //  float locations can return ceilings despite them not existing there.
        const x = s16(posX);
        const y = s16(posY);
        const z = s16(posZ);

        if (x <= -LEVEL_BOUNDARY_MAX || x >= LEVEL_BOUNDARY_MAX) {
            return { height, surface: null };
        }
        if (z <= -LEVEL_BOUNDARY_MAX || z >= LEVEL_BOUNDARY_MAX) {
            return { height, surface: null };
        }

        const cellX = ((x + LEVEL_BOUNDARY_MAX) / CELL_SIZE) & NUM_CELLS_INDEX;
        const cellZ = ((z + LEVEL_BOUNDARY_MAX) / CELL_SIZE) & NUM_CELLS_INDEX;

        const res = this.find_ceil_from_list(this.partition[cellZ][cellX][SPATIAL_PARTITION_CEILS], x, y, z);
        if (res === null) {
            return { height, surface: null };
        }
        return { height: res.height, surface: res.surface };
    }

    // -----------------------------------------------------------------------
    // FLOORS
    // -----------------------------------------------------------------------

    /** find_floor_from_list: returns { surface, height } or null. x, y, z are integers. */
    find_floor_from_list(list, x, y, z) {
        for (let n = 0; n < list.length; n++) {
            const surf = list[n];

            const x1 = surf.vertex1[0];
            const z1 = surf.vertex1[2];
            const x2 = surf.vertex2[0];
            const z2 = surf.vertex2[2];

            // Check that the point is within the triangle bounds.
            if ((z1 - z) * (x2 - x1) - (x1 - x) * (z2 - z1) < 0) {
                continue;
            }

            const x3 = surf.vertex3[0];
            const z3 = surf.vertex3[2];

            if ((z2 - z) * (x3 - x2) - (x2 - x) * (z3 - z2) < 0) {
                continue;
            }
            if ((z3 - z) * (x1 - x3) - (x3 - x) * (z1 - z3) < 0) {
                continue;
            }

            if (this.checkingForCamera) {
                if (surf.flags & SURFACE_FLAG_NO_CAM_COLLISION) {
                    continue;
                }
            } else if (surf.type === SURFACE_CAMERA_BOUNDARY) {
                continue;
            }

            const nx = surf.normal.x;
            const ny = surf.normal.y;
            const nz = surf.normal.z;
            const oo = surf.originOffset;

            // If a wall, ignore it. Likely a remnant, should never occur.
            if (ny === 0.0) {
                continue;
            }

            // Find the height of the floor at a given location.
            const height = Math.fround(-(x * nx + nz * z + oo) / ny);
            // Checks for floor interaction with a 78 unit buffer.
            if (y - (height + -78.0) < 0.0) {
                continue;
            }

            //! (Surface Cucking) Since only the first floor is returned and not the highest,
            //  higher floors can be "cucked" by lower floors.
            return { surface: surf, height };
        }
        return null;
    }

    /**
     * find_floor: returns { height, surface }; height = FLOOR_LOWER_LIMIT (-11000)
     * and surface = null when there is no floor.
     */
    find_floor(xPos, yPos, zPos) {
        let height = FLOOR_LOWER_LIMIT;

        //! (Parallel Universes) Because position is casted to an s16, reaching higher
        //  float locations can return floors despite them not existing there.
        const x = s16(xPos);
        const y = s16(yPos);
        const z = s16(zPos);

        if (x <= -LEVEL_BOUNDARY_MAX || x >= LEVEL_BOUNDARY_MAX) {
            return { height, surface: null };
        }
        if (z <= -LEVEL_BOUNDARY_MAX || z >= LEVEL_BOUNDARY_MAX) {
            return { height, surface: null };
        }

        const cellX = ((x + LEVEL_BOUNDARY_MAX) / CELL_SIZE) & NUM_CELLS_INDEX;
        const cellZ = ((z + LEVEL_BOUNDARY_MAX) / CELL_SIZE) & NUM_CELLS_INDEX;

        const list = this.partition[cellZ][cellX][SPATIAL_PARTITION_FLOORS];
        let res = this.find_floor_from_list(list, x, y, z);
        let floor = null;
        if (res !== null) {
            floor = res.surface;
            height = res.height;
        }

        // To prevent the Merry-Go-Round room from loading when Mario passes above the hole that leads
        // there, SURFACE_INTANGIBLE is used.
        if (!this.findFloorIncludeSurfaceIntangible) {
            //! (BBH Crash) If this returns a NULL floor, the height of the intangible floor is kept.
            if (floor !== null && floor.type === SURFACE_INTANGIBLE) {
                res = this.find_floor_from_list(list, x, (height - 200.0) | 0, z);
                if (res !== null) {
                    floor = res.surface;
                    height = res.height;
                } else {
                    floor = null;
                }
            }
        } else {
            // To prevent accidentally leaving the floor tangible, stop checking for it.
            this.findFloorIncludeSurfaceIntangible = false;
        }

        return { height, surface: floor };
    }

    /** find_floor_height */
    find_floor_height(x, y, z) {
        return this.find_floor(x, y, z).height;
    }

    /**
     * find_floor_height_and_data: returns { height, floorGeo } where floorGeo is
     * { normalX, normalY, normalZ, originOffset } or null.
     */
    find_floor_height_and_data(xPos, yPos, zPos) {
        const { height, surface } = this.find_floor(xPos, yPos, zPos);
        let floorGeo = null;
        if (surface !== null) {
            floorGeo = {
                normalX: surface.normal.x,
                normalY: surface.normal.y,
                normalZ: surface.normal.z,
                originOffset: surface.originOffset,
            };
        }
        return { height, floorGeo };
    }

    // -----------------------------------------------------------------------
    // ENVIRONMENTAL BOXES
    // -----------------------------------------------------------------------

    /**
     * find_water_level. With no environment regions (the default) this always
     * returns FLOOR_LOWER_LIMIT, so no water transitions can trigger.
     */
    find_water_level(x, z) {
        const regions = this.environmentRegions;
        if (regions) {
            for (const r of regions) {
                if (r.x1 < x && x < r.x2 && r.z1 < z && z < r.z2 && r.type < 50) {
                    return r.y;
                }
            }
        }
        return FLOOR_LOWER_LIMIT;
    }

    /** find_poison_gas_level */
    find_poison_gas_level(x, z) {
        const regions = this.environmentRegions;
        if (regions) {
            for (const r of regions) {
                if (r.type >= 50 && r.x1 < x && x < r.x2 && r.z1 < z && z < r.z2 && r.type % 10 === 0) {
                    return r.y;
                }
            }
        }
        return FLOOR_LOWER_LIMIT;
    }
}
