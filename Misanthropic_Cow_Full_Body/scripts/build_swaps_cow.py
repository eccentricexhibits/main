"""Stage 6b geometry swaps on the Tripo cow, at real size (metres).

python3 -I build_swaps_cow.py <cowMask.obj> <tripo_blender_frame.npz> <tripo_vcol.npy> <fit.json> <horns_dir> <slippers.glb> <out_dir> [face=tripo|scan]

Blender frame throughout: Z up, front -Y, the costume's own left +X. Tripo units x S = metres.
1. Mask. face=tripo (the user's choice after seeing both): Tripo's own face stays; the scan, moved onto the head
   with the fit from fit_mask_scan_cow.py, only gives the mask's outline (mask_footprint.npz) for the region map.
   face=scan (the first version): the scan's relief replaces the face; its rim gets a skirt running backward into
   the hood, and Tripo's face (in front of the mask's back plane, inside its outline, a little below the chin) is
   deleted and the hole capped behind the mask.
2. Horns: Tripo's horns and wire (yellow/dark texels beyond the bolster ends) are deleted. The scan-guided
   horns (horns_from_scan_cow.py) are moved with the same fit and then shifted so each root sits on its
   bolster end; their 12 mm root extension plugs into the bolster.
3. Feet: everything below the ankle cut is deleted; a black-sock foot (loft from the leg's cut ring down to
   a foot outline on the slipper's footbed) is added per leg; the slipper pair is placed at real size (27 cm),
   each centred under its leg, toes on Tripo's toes.
4. Tail: a 4 mm white cord from the bottom of the gold bow, draped down over the seat to knee height.
Writes body.npz (v in metres, f, uv, deleted-hole info), mask_shell.ply, horn_*.ply, socks.ply, tail.ply,
swaps.json (scale, slipper placement, horn shifts, all landmarks).
"""
import sys, os, json
import numpy as np, trimesh, networkx as nx
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geom_cow import sweep  # noqa: E402

SCAN, NPZ, VCOL, FIT, HORNS, SLIPPERS, OUT = sys.argv[1:8]
FACE = sys.argv[8] if len(sys.argv) > 8 else "tripo"
os.makedirs(OUT, exist_ok=True)
fit = json.load(open(FIT))
S = fit["mm_per_tripo_unit_used"] / 1000.0          # metres per Tripo unit
F = fit["scan_mm_to_tripo_units"]; FR, Fs, Ft = np.array(F["R"]), F["s"], np.array(F["t"])
to_cow = lambda X: S * (Fs * np.asarray(X) @ FR.T + Ft)       # scan mm -> cow metres
info = {"metres_per_tripo_unit": S}

d = np.load(NPZ); v = d["v"].astype(np.float64) * S; f = d["f"].astype(np.int64); uv = d["uv"]
col = np.load(VCOL).astype(int); r_, g_, b_ = col.T; L = (r_ + g_ + b_) / 3
print(f"body: {len(v):,} verts, {len(f):,} faces, height {v[:, 2].max():.3f} m")
U = lambda x: x * S                                          # Tripo units -> metres for thresholds


def boundary_loops(faces):
    e = np.sort(np.r_[faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]], axis=1)
    u, c = np.unique(e, axis=0, return_counts=True)
    g = nx.Graph(); g.add_edges_from(u[c == 1])
    loops = []
    for comp in nx.connected_components(g):
        sg = g.subgraph(comp)
        try: loops.append([a for a, _ in nx.find_cycle(sg)])
        except nx.NetworkXNoCycle: pass
    return sorted(loops, key=len, reverse=True)


# ---------------- 1. mask shell ----------------
scan = trimesh.load(SCAN, force="mesh", process=False)
sv, sf = np.asarray(scan.vertices), np.asarray(scan.faces)
keep = (sv[sf][:, :, 1].max(1) < -2.0) & (sv[sf][:, :, 2].max(1) < 212.0)
# (the scanner's flat strips in the last ~2 cm before the rim stay: removing them breaks the rim into many holes)
rel = trimesh.Trimesh(sv, sf[keep], process=False); rel.remove_unreferenced_vertices(); rel.merge_vertices()
rel = sorted(rel.split(only_watertight=False), key=lambda p: -len(p.faces))[0]
loops = boundary_loops(np.asarray(rel.faces))
outer = np.array(loops[0])
print(f"mask relief: {len(rel.faces):,} faces, {len(loops)} boundary loops (outer {len(outer)} verts; the rest {[len(l) for l in loops[1:6]]})")
rv = np.asarray(rel.vertices); rf = np.asarray(rel.faces)
# skirt: the outer rim runs 20 mm back (+Y in the scan) and 10 mm in toward the face centre, so it tucks into the hood
ring = rv[outer]; cen = ring.mean(0)
inward = cen - ring; inward[:, 1] = 0; inward /= np.linalg.norm(inward, axis=1)[:, None] + 1e-9
ring2 = ring + np.array([0, 20.0, 0]) + inward * 10.0
n0 = len(rv); n = len(outer)
sk = [[outer[i], outer[(i + 1) % n], n0 + (i + 1) % n] for i in range(n)] + [[outer[i], n0 + (i + 1) % n, n0 + i] for i in range(n)]
shell = trimesh.Trimesh(np.r_[rv, ring2], np.r_[rf, np.array(sk)], process=False)
trimesh.repair.fix_normals(shell, multibody=False)
if shell.face_normals[:len(rf)][:, 1].mean() > 0: shell.invert()        # face the front (-Y)
shell.vertices = to_cow(shell.vertices)
if FACE == "scan": shell.export(f"{OUT}/mask_shell.ply")
elif os.path.exists(f"{OUT}/mask_shell.ply"): os.remove(f"{OUT}/mask_shell.ply")
info["mask"] = {"faces": int(len(shell.faces)), "bounds_m": shell.bounds.round(4).tolist(), "relief_faces": int(len(rf))}
print("mask shell bounds (m)", shell.bounds.round(3).tolist())

# Tripo's own face: everything in front of the mask's back plane inside the mask's front outline (dilated 6 mm,
# and carried 24 mm below the chin so Tripo's bigger snout goes too) is deleted; the hole gets a recessed cap.
# Tripo's forehead fur above the mask's top edge stays: the hood closes over the top of the mask.
from scipy.ndimage import binary_closing, binary_fill_holes, binary_dilation
relv = np.asarray(shell.vertices)[:len(rv)]
GR = 0.002; x0_, z0_ = relv[:, 0].min() - 0.05, relv[:, 2].min() - 0.06
nx_, nz_ = int((relv[:, 0].max() + 0.05 - x0_) / GR) + 1, int((relv[:, 2].max() + 0.02 - z0_) / GR) + 1
fp = np.zeros((nz_, nx_), bool)
ii = ((relv[:, 2] - z0_) / GR).astype(int); jj = ((relv[:, 0] - x0_) / GR).astype(int); fp[ii, jj] = True
fp = binary_fill_holes(binary_closing(fp, iterations=3))
zb = int((relv[:, 2].min() - z0_) / GR)
cols = fp[zb:zb + 10].any(0)
fp[max(zb - 12, 0):zb, :] |= cols[None, :]
fp = binary_dilation(fp, iterations=3)
Y_BACK = float(np.percentile(relv[outer, 1], 50))
def in_fp(p):
    i = ((p[:, 2] - z0_) / GR).astype(int); j = ((p[:, 0] - x0_) / GR).astype(int)
    ok = (i >= 0) & (i < nz_) & (j >= 0) & (j < nx_)
    out = np.zeros(len(p), bool); out[ok] = fp[i[ok], j[ok]]; return out
np.savez(f"{OUT}/mask_footprint.npz", fp=fp, x0=x0_, z0=z0_, grid=GR, y_back=Y_BACK, zmin=relv[:, 2].min(), zmax=relv[:, 2].max())
if FACE == "scan":
    facev = (v[:, 2] > relv[:, 2].min() - 0.04) & (v[:, 2] < relv[:, 2].max() - 0.004) & (v[:, 1] < Y_BACK) & in_fp(v)
    print(f"Tripo face: {facev.sum():,} verts in front of the mask's back plane (y < {Y_BACK:.3f} m) inside its outline -> deleted")
else:
    facev = np.zeros(len(v), bool)
    print("Tripo face kept; the scan's outline is saved for the region map")
info["face"] = FACE
info["mask"]["back_plane_y_m"] = Y_BACK

# ---------------- 2. horns ----------------
yellow = (r_ > 140) & (g_ > 100) & (b_ < 0.7 * g_) & (r_ - b_ > 60)
dark = L < 70
zone = (v[:, 2] > U(0.915)) & (v[:, 1] < U(0.005))
end_p, end_n = U(0.032), U(-0.036)                         # bolster ends (texels change from white fur to horn)
hornv = zone & (yellow | dark) & ((v[:, 0] > end_p - U(0.001)) | (v[:, 0] < end_n + U(0.001)))
# grow into the horn's untextured/odd texels: neighbours beyond the bolster ends, 6 rings
e = np.r_[f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]
beyond = zone & ((v[:, 0] > end_p - U(0.002)) | (v[:, 0] < end_n + U(0.002)))
for _ in range(6):
    m = hornv[e[:, 0]] & beyond[e[:, 1]]; hornv[e[m, 1]] = True
    m = hornv[e[:, 1]] & beyond[e[:, 0]]; hornv[e[m, 0]] = True
# bolster end centres = centroid of the deleted horn verts right at each end
ends = {}
for side, xe in (("L", end_p), ("R", end_n)):
    sel = hornv & (np.abs(v[:, 0] - xe) < U(0.006))
    ends[side] = np.array([xe, v[sel, 1].mean(), v[sel, 2].mean()])
print("bolster ends (m):", {k: v_.round(4).tolist() for k, v_ in ends.items()})
info["bolster_ends_m"] = {k: v_.tolist() for k, v_ in ends.items()}

H = json.load(open(f"{HORNS}/horns.json"))
shift = {}
for name, side, key in (("horn_long", "L", "long_horn"), ("horn_short", "R", "short_horn")):
    m = trimesh.load(f"{HORNS}/{name}.ply", process=False)
    m.vertices = to_cow(m.vertices)
    root = to_cow(np.array(H[key]["root"])[None])[0]
    sh = ends[side] - root; shift[side] = sh
    m.vertices = m.vertices + sh
    m.export(f"{OUT}/{name}.ply")
    print(f"{name}: root moved {np.linalg.norm(sh) * 1000:.0f} mm onto the bolster end {sh.round(4).tolist()}")
w = trimesh.load(f"{HORNS}/horn_wires.ply", process=False); w.vertices = to_cow(w.vertices) + shift["R"]; w.export(f"{OUT}/horn_wires.ply")
info["horn_shift_m"] = {k: s_.tolist() for k, s_ in shift.items()}

# ---------------- 3. feet ----------------
Z_CUT = U(0.105)
feetv = v[:, 2] < Z_CUT

# ---------------- delete faces ----------------
dead = hornv | feetv | facev
fk = ~dead[f].any(1)
info["faces_deleted"] = {"horns": int(hornv[f].any(1).sum()), "feet": int(feetv[f].any(1).sum()), "face": int(facev[f].any(1).sum())}
f2 = f[fk]
used = np.unique(f2); remap = -np.ones(len(v), int); remap[used] = np.arange(len(used))
v2, uv2, f2 = v[used], uv[used], remap[f2]
print(f"deleted {(~fk).sum():,} faces {info['faces_deleted']} -> {len(f2):,} faces")

# ankle centres (just above the cut): each slipper is centred under its leg. Tripo's legs come down about 2.7 cm
# closer to the middle than Tripo's own slippers, so centring on those let the ankle overhang the slipper's inner edge
ank = {sd: v[(np.abs(v[:, 2] - Z_CUT - 0.012) < 0.008) & (sg_ * v[:, 0] > 0.03)][:, :2].mean(0) for sd, sg_ in (("L", 1), ("R", -1))}
info["ankle_centres_xy_m"] = {k: a.tolist() for k, a in ank.items()}
# slippers: real size (1 GLB unit = 27.5 cm), toes on Tripo's toes, A on the costume's own left (+X)
sl = list(trimesh.load(SLIPPERS).geometry.values())[0]
sv0 = np.asarray(sl.vertices); sv0 = np.c_[sv0[:, 0], -sv0[:, 2], sv0[:, 1]] * 0.275
slip = {}
for side, sg in (("L", 1), ("R", -1)):
    p = sv0.copy(); p[:, 0] *= sg
    off = np.array([ank[side][0] - (p[:, 0].max() + p[:, 0].min()) / 2, U(-0.074) - p[:, 1].min(), -p[:, 2].min()])
    slip[side] = {"mirror_x": sg < 0, "scale": 0.275, "offset_m": off.tolist(),
                  "length_m": float(np.ptp(p[:, 1])), "toe_y": float(U(-0.074)), "heel_y": float(U(-0.074) + np.ptp(p[:, 1]))}
    pm = trimesh.Trimesh(p + off, sl.faces if sg > 0 else sl.faces[:, ::-1], process=False)
    hy = U(-0.074) + np.ptp(p[:, 1]) * 0.80              # footbed probe: 80 % back along the slipper
    loc, _, _ = pm.ray.intersects_location([[ank[side][0], hy, 0.5]], [[0, 0, -1.0]], multiple_hits=False)
    slip[side]["footbed_z"] = float(loc[0, 2]) if len(loc) else 0.02
info["slippers"] = slip
print("slipper footbed z (m):", {k: round(s_["footbed_z"], 4) for k, s_ in slip.items()})

# weld by position for topology (the mesh is split at UV seams, so raw boundary edges include every seam)
_, wid = np.unique(np.round(v2, 7), axis=0, return_inverse=True); wid = wid.ravel()
rep = np.zeros(wid.max() + 1, int); rep[wid] = np.arange(len(v2))
wloops = boundary_loops(wid[f2])

# socks: loft from the leg's cut ring to a foot outline on the footbed
socks = []
for side, sg in (("L", 1), ("R", -1)):
    lp = [l for l in wloops if np.all(np.abs(v2[rep[l], 2] - Z_CUT) < 0.02) and np.mean(v2[rep[l], 0]) * sg > 0]
    lp = max(lp, key=len); ring = v2[rep[lp]]
    c0 = ring.mean(0)
    ang = np.arctan2(ring[:, 1] - c0[1], ring[:, 0] - c0[0]); o_ = np.argsort(ang)
    th = np.linspace(-np.pi, np.pi, 48, endpoint=False)
    rr = np.interp(th, ang[o_], np.linalg.norm(ring[o_, :2] - c0[:2], axis=1), period=2 * np.pi) * 1.04
    top_z = Z_CUT + 0.015
    # foot outline: 15 x 7 cm, centred on the slipper (and so under the leg), heel 2 cm in front of its heel end; the toes reach only
    # about 4 cm under the slipper's head (its foot opening is shallow), so nothing breaks through its sides
    fb = slip[side]["footbed_z"] + 0.004; heel = slip[side]["heel_y"] - 0.02; flen, fw = 0.15, 0.07
    fc = np.array([ank[side][0], heel - flen / 2])
    a, b = fw / 2, flen / 2
    rf_ = (np.abs(np.cos(th)) ** 2.5 / a ** 2.5 + np.abs(np.sin(th)) ** 2.5 / b ** 2.5) ** (-1 / 2.5)
    K = 14; V, Fc = [], []
    for k in range(K + 1):
        # the ankle keeps its section down to ~5 cm above the sole, then the foot runs forward (low instep)
        t = k / K; z = top_z + (fb - top_z) * t
        s_ = np.clip((0.055 - (z - fb)) / 0.055, 0, 1); s_ = s_ * s_ * (3 - 2 * s_)
        cxy = (1 - s_) * c0[:2] + s_ * fc
        rad = (1 - s_) * rr + s_ * rf_
        V += list(np.c_[cxy[0] + rad * np.cos(th), cxy[1] + rad * np.sin(th), np.full(48, z)])
    for k in range(K):
        for j in range(48):
            a0, a1 = k * 48 + j, k * 48 + (j + 1) % 48
            Fc += [[a0, a1 + 48, a0 + 48], [a0, a1, a1 + 48]]
    V.append([fc[0], fc[1], fb]); c = len(V) - 1
    Fc += [[c, K * 48 + (j + 1) % 48, K * 48 + j] for j in range(48)]
    sm = trimesh.Trimesh(np.array(V), np.array(Fc), process=True); trimesh.repair.fix_normals(sm)
    socks.append(sm)
trimesh.util.concatenate(socks).export(f"{OUT}/socks.ply")

# ---------------- 4. tail cord ----------------
gold = (r_ > 120) & (g_ > 80) & (b_ < 0.75 * g_) & (r_ - b_ > 40)
bowv = gold & (v[:, 1] > 0) & (v[:, 2] < U(0.75)) & (v[:, 2] > U(0.35))
bow = v[bowv]; bc = bow.mean(0)
start = np.array([bc[0], np.percentile(bow[:, 1], 70), np.percentile(bow[:, 2], 8)])
body = trimesh.Trimesh(v2, f2, process=False)
zs = np.linspace(start[2], 0.45, 120)
o = np.c_[np.full(len(zs), start[0]), np.full(len(zs), 1.0), zs]
loc, ri, _ = body.ray.intersects_location(o, np.tile([0, -1.0, 0], (len(zs), 1)), multiple_hits=False)
yb = np.full(len(zs), -1.0); yb[ri] = loc[:, 1]
yc = np.maximum.accumulate(np.maximum(yb + 0.002 + 0.006, start[1]))   # hangs, resting on whatever sticks out below
yc = gaussian_filter1d(yc, 3, mode="nearest")
xs = start[0] + 0.004 * np.sin(np.linspace(0, 2.2, len(zs)))
P = np.c_[xs, yc, zs]; P[0] = start
tail = sweep(P, np.full(len(P), 0.002), sides=10)
tail.export(f"{OUT}/tail.ply")
info["tail"] = {"start_m": start.tolist(), "end_m": P[-1].tolist(), "length_m": float(np.linalg.norm(np.diff(P, axis=0), axis=1).sum())}
print(f"tail: from {start.round(3).tolist()} to z {zs[-1]:.2f} m, length {info['tail']['length_m']:.2f} m")

# caps: fan-fill each cut hole (welded topology) from a centre point pushed into the body
# (face hole: 6 cm back; bolster ends: 6 mm toward the centre; ankles: 1 cm up)
caps_v, caps_uv, caps_f = [], [], []
fw_ = wid[f2]; dedges = set(map(tuple, np.r_[fw_[:, [0, 1]], fw_[:, [1, 2]], fw_[:, [2, 0]]].tolist()))
for lp in wloops:
    if len(lp) < 6: continue
    P = v2[rep[lp]]; c = P.mean(0)
    if c[2] > 1.25 and abs(c[0]) < 0.045: c = c + [0, 0.06, 0]; kind = "face"
    elif c[2] > 1.45: c = c + [-np.sign(c[0]) * 0.006, 0, 0]; kind = "bolster end"
    elif c[2] < 0.3: c = c + [0, 0, 0.01]; kind = "ankle"
    else: kind = "other"
    ci = len(v2) + len(caps_v); caps_v.append(c); caps_uv.append(uv2[rep[lp[0]]])
    L_ = [rep[i] for i in lp]
    # wind the fan against the neighbouring faces' boundary edges, so its normals agree with theirs
    if (lp[0], lp[1]) not in dedges: L_ = L_[::-1]
    caps_f += [[ci, L_[(k + 1) % len(L_)], L_[k]] for k in range(len(L_))]
    print(f"cap: {kind:12s} loop {len(lp):4d} verts at {c.round(3).tolist()}")
if caps_v:
    v2 = np.r_[v2, np.array(caps_v)]; uv2 = np.r_[uv2, np.array(caps_uv)]; f2 = np.r_[f2, np.array(caps_f)]
np.savez(f"{OUT}/body.npz", v=v2.astype(np.float32), f=f2.astype(np.int32), uv=uv2.astype(np.float32))
info["body"] = {"verts": int(len(v2)), "faces": int(len(f2)), "height_m": float(v2[:, 2].max())}
json.dump(info, open(f"{OUT}/swaps.json", "w"), indent=1)
print("wrote", OUT)
