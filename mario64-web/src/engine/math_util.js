// Port of the parts of src/engine/math_util.c (and include/trig_tables.inc.c)
// that Mario's physics depend on.

/** Wrap to signed 16-bit like a C (s16) cast (truncates floats toward zero first). */
export function s16(x) {
    return (x << 16) >> 16;
}

/** Wrap to unsigned 16-bit like a C (u16) cast. */
export function u16(x) {
    return x & 0xFFFF;
}

/** Wrap to unsigned 8-bit like a C (u8) cast. */
export function u8(x) {
    return x & 0xFF;
}

/** C (s32) cast of a float: truncation toward zero (with int32 wraparound). */
export function s32(x) {
    return x | 0;
}

export const f32 = Math.fround;

// ---------------------------------------------------------------------------
// Trig tables
//
// gSineTable has 0x400 entries and is immediately followed by gCosineTable
// (0x1000 entries), so the combined table is a sine table of 0x1400 entries
// where gCosineTable[i] == gSineTable[i + 0x400]. The original values are the
// f32 roundings of sin(i * 2pi / 4096); the only differences from
// Math.fround(Math.sin(...)) are exact zeros at multiples of pi, which we
// reproduce here. (Verified against include/trig_tables.inc.c.)
// ---------------------------------------------------------------------------

const SINE_TABLE = new Float32Array(0x1400);
for (let i = 0; i < 0x1400; i++) {
    SINE_TABLE[i] = (i % 2048 === 0) ? 0 : Math.sin(i * 2 * Math.PI / 4096);
}
export const gSineTable = SINE_TABLE;
export const gCosineTable = SINE_TABLE.subarray(0x400);

// gArctanTable[i] == round(atan(i / 1024) * 0x8000 / pi), 0x401 entries (verified).
const ARCTAN_TABLE = new Int16Array(0x401);
for (let i = 0; i <= 0x400; i++) {
    ARCTAN_TABLE[i] = Math.round(Math.atan(i / 1024) * 0x8000 / Math.PI);
}
export const gArctanTable = ARCTAN_TABLE;

/** #define sins(x) gSineTable[(u16) (x) >> 4] */
export function sins(x) {
    return SINE_TABLE[(x & 0xFFFF) >> 4];
}

/** #define coss(x) gCosineTable[(u16) (x) >> 4] */
export function coss(x) {
    return SINE_TABLE[((x & 0xFFFF) >> 4) + 0x400];
}

/**
 * Helper function for atan2s. Does a look up of the arctangent of y/x assuming
 * the resulting angle is in range [0, 0x2000] (1/8 of a circle).
 */
function atan2_lookup(y, x) {
    let ret;
    if (x == 0) {
        ret = ARCTAN_TABLE[0];
    } else {
        // (s32)(y / x * 1024 + 0.5f) in f32 arithmetic
        ret = ARCTAN_TABLE[Math.fround(Math.fround(y / x) * 1024 + 0.5) | 0];
    }
    return ret & 0xFFFF;
}

/**
 * Compute the angle from (0, 0) to (x, y) as a s16. Given that terrain is in
 * the xz-plane, this is commonly called with (z, x) to get a yaw angle.
 */
export function atan2s(y, x) {
    let ret;

    if (x >= 0) {
        if (y >= 0) {
            if (y >= x) {
                ret = atan2_lookup(x, y);
            } else {
                ret = 0x4000 - atan2_lookup(y, x);
            }
        } else {
            y = -y;
            if (y < x) {
                ret = 0x4000 + atan2_lookup(y, x);
            } else {
                ret = 0x8000 - atan2_lookup(x, y);
            }
        }
    } else {
        x = -x;
        if (y < 0) {
            y = -y;
            if (y >= x) {
                ret = 0x8000 + atan2_lookup(x, y);
            } else {
                ret = 0xC000 - atan2_lookup(y, x);
            }
        } else {
            if (y < x) {
                ret = 0xC000 + atan2_lookup(y, x);
            } else {
                ret = -atan2_lookup(x, y);
            }
        }
    }
    // u16 ret, returned as s16
    return s16(ret);
}

/**
 * Return the value 'current' after it tries to approach target, going up at
 * most 'inc' and going down at most 'dec'.
 */
export function approach_s32(current, target, inc, dec) {
    if (current < target) {
        current = (current + inc) | 0;
        if (current > target) {
            current = target;
        }
    } else {
        current = (current - dec) | 0;
        if (current < target) {
            current = target;
        }
    }
    return current;
}

export function approach_f32(current, target, inc, dec) {
    if (current < target) {
        current += inc;
        if (current > target) {
            current = target;
        }
    } else {
        current -= dec;
        if (current < target) {
            current = target;
        }
    }
    return current;
}

export function vec3f_copy(dest, src) {
    dest[0] = src[0];
    dest[1] = src[1];
    dest[2] = src[2];
    return dest;
}

export function vec3f_set(dest, x, y, z) {
    dest[0] = x;
    dest[1] = y;
    dest[2] = z;
    return dest;
}

export function vec3s_set(dest, x, y, z) {
    dest[0] = s16(x);
    dest[1] = s16(y);
    dest[2] = s16(z);
    return dest;
}

export function vec3s_copy(dest, src) {
    dest[0] = src[0];
    dest[1] = src[1];
    dest[2] = src[2];
    return dest;
}

export function find_vector_perpendicular_to_plane(dest, a, b, c) {
    dest[0] = (b[1] - a[1]) * (c[2] - b[2]) - (c[1] - b[1]) * (b[2] - a[2]);
    dest[1] = (b[2] - a[2]) * (c[0] - b[0]) - (c[2] - b[2]) * (b[0] - a[0]);
    dest[2] = (b[0] - a[0]) * (c[1] - b[1]) - (c[0] - b[0]) * (b[1] - a[1]);
    return dest;
}

export function vec3f_cross(dest, a, b) {
    const x = a[1] * b[2] - b[1] * a[2];
    const y = a[2] * b[0] - b[2] * a[0];
    const z = a[0] * b[1] - b[0] * a[1];
    dest[0] = x;
    dest[1] = y;
    dest[2] = z;
    return dest;
}

export function vec3f_normalize(dest) {
    //! Possible division by zero
    const invsqrt = 1.0 / Math.sqrt(dest[0] * dest[0] + dest[1] * dest[1] + dest[2] * dest[2]);
    dest[0] *= invsqrt;
    dest[1] *= invsqrt;
    dest[2] *= invsqrt;
    return dest;
}

/** Create a 4x4 matrix (Mat4, indexed [row][col] like the original). */
export function mtxf_new() {
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]];
}

/**
 * Set 'mtx' to a transformation matrix that aligns an object with the terrain
 * based on 3 height samples in an equilateral triangle around the object.
 * Used for Mario when crawling or sliding. `findFloor(x, y, z)` returns a height.
 */
export function mtxf_align_terrain_triangle(mtx, pos, yaw, radius, findFloorHeight) {
    const point0 = [0, 0, 0];
    const point1 = [0, 0, 0];
    const point2 = [0, 0, 0];
    const forward = [0, 0, 0];
    const xColumn = [0, 0, 0];
    const yColumn = [0, 0, 0];
    const zColumn = [0, 0, 0];
    const minY = -radius * 3;

    point0[0] = pos[0] + radius * sins(yaw + 0x2AAA);
    point0[2] = pos[2] + radius * coss(yaw + 0x2AAA);
    point1[0] = pos[0] + radius * sins(yaw + 0x8000);
    point1[2] = pos[2] + radius * coss(yaw + 0x8000);
    point2[0] = pos[0] + radius * sins(yaw + 0xD555);
    point2[2] = pos[2] + radius * coss(yaw + 0xD555);

    point0[1] = findFloorHeight(point0[0], pos[1] + 150, point0[2]);
    point1[1] = findFloorHeight(point1[0], pos[1] + 150, point1[2]);
    point2[1] = findFloorHeight(point2[0], pos[1] + 150, point2[2]);

    if (point0[1] - pos[1] < minY) {
        point0[1] = pos[1];
    }
    if (point1[1] - pos[1] < minY) {
        point1[1] = pos[1];
    }
    if (point2[1] - pos[1] < minY) {
        point2[1] = pos[1];
    }

    const avgY = (point0[1] + point1[1] + point2[1]) / 3;

    vec3f_set(forward, sins(yaw), 0, coss(yaw));
    find_vector_perpendicular_to_plane(yColumn, point0, point1, point2);
    vec3f_normalize(yColumn);
    vec3f_cross(xColumn, yColumn, forward);
    vec3f_normalize(xColumn);
    vec3f_cross(zColumn, xColumn, yColumn);
    vec3f_normalize(zColumn);

    mtx[0][0] = xColumn[0];
    mtx[0][1] = xColumn[1];
    mtx[0][2] = xColumn[2];
    mtx[3][0] = pos[0];

    mtx[1][0] = yColumn[0];
    mtx[1][1] = yColumn[1];
    mtx[1][2] = yColumn[2];
    mtx[3][1] = (avgY < pos[1]) ? pos[1] : avgY;

    mtx[2][0] = zColumn[0];
    mtx[2][1] = zColumn[1];
    mtx[2][2] = zColumn[2];
    mtx[3][2] = pos[2];

    mtx[0][3] = 0;
    mtx[1][3] = 0;
    mtx[2][3] = 0;
    mtx[3][3] = 1;
    return mtx;
}
