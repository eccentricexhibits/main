#!/usr/bin/env python3
"""Register each fixed event map to its venue blueprint.

Model: event = s * R(v) + t, with R fixed to the known 90-deg turn:
R(x, y) = (y, -x)  (venue page-right/north -> event page-up/north).
Solve (s, tx, ty) per floor by minimizing robust point-cloud distance
between transformed venue wall geometry and event map geometry.
"""
import pymupdf as fitz, math, json
import numpy as np
from scipy.spatial import cKDTree
from scipy.optimize import minimize

UP = "/root/.claude/uploads/8646fd97-4ad3-5951-b0bc-d4bea048f46f"
SP = "/tmp/claude-0/-home-user-main/8646fd97-4ad3-5951-b0bc-d4bea048f46f/scratchpad"
VENUE = {1: f"{UP}/6187c370-Venue_Supplied_Plans__Level_1__From_Blueprints.pdf",
         2: f"{UP}/3e70b7e6-Venue_Supplied_Plans__Level_2__From_Blueprints.pdf",
         3: f"{UP}/2bb18f85-Venue_Supplied_Plans__Level_3__From_Blueprints.pdf"}
EVENT = {1: f"{SP}/Event_Map_Level_1_Lobby_v2.pdf",
         2: f"{SP}/Event_Map_Level_2_Trading_Floor_v2.pdf",
         3: f"{SP}/Event_Map_Level_3_Gallery_v2.pdf"}
PTFT = {1: 4.533, 2: 4.533, 3: 5.022}
BIGX = {1: (104.4, 411.9), 2: (106.6, 419.9), 3: (465.1, 442.8)}
SMALLX = {1: (104.4, 504.7), 2: (106.6, 512.7), 3: (465.1, 545.6)}
CORNX = {1: (492.4, 609.7), 2: (494.7, 613.7)}
E_CORNX = {1: (679.9, 204.5), 2: (667.2, 210.9)}

def sample_seg(p1, p2, step=3.0):
    L = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
    n = max(2, int(L/step))
    return [(p1[0]+(p2[0]-p1[0])*i/(n-1), p1[1]+(p2[1]-p1[1])*i/(n-1)) for i in range(n)]

def cloud(path, keep, bbox=None, step=3.0):
    doc = fitz.open(path); page = doc[0]
    pts = []
    for d in page.get_drawings():
        if not keep(d): continue
        for it in d["items"]:
            if it[0] in ("l", "c"):
                p1, p2 = it[1], it[-1]
                segs = [((p1.x, p1.y), (p2.x, p2.y))]
            elif it[0] == "re":
                r = it[1]
                segs = [((r.x0,r.y0),(r.x1,r.y0)),((r.x1,r.y0),(r.x1,r.y1)),
                        ((r.x1,r.y1),(r.x0,r.y1)),((r.x0,r.y1),(r.x0,r.y0))]
            elif it[0] == "qu":
                q = it[1]; c4 = [q.ul, q.ur, q.lr, q.ll]
                segs = [((a.x,a.y),(b.x,b.y)) for a,b in zip(c4, c4[1:]+c4[:1])]
            else:
                continue
            for a, b in segs:
                for p in sample_seg(a, b, step):
                    if bbox is None or (bbox[0]<=p[0]<=bbox[2] and bbox[1]<=p[1]<=bbox[3]):
                        pts.append(p)
    doc.close()
    return np.array(pts)

def is_grayish(c, vmax=0.95):
    if c is None: return False
    r, g, b = c
    return max(r,g,b)-min(r,g,b) < 0.06 and max(r,g,b) <= vmax

def venue_keep(d):
    c, f = d.get("color"), d.get("fill")
    if c and c[0] > 0.7 and c[1] < 0.45: return False   # red clearances
    return is_grayish(c) or is_grayish(f)

def event_keep(d):
    c, f = d.get("color"), d.get("fill")
    ok = lambda col: col is not None and is_grayish(col, 0.9)
    return ok(c) or ok(f)

def R(pts):
    return np.column_stack([pts[:,1], -pts[:,0]])

results = {}
for lvl in (1, 2, 3):
    vb = (60, 140, 590, 770) if lvl < 3 else (60, 150, 600, 780)
    vpts = cloud(VENUE[lvl], venue_keep, vb)
    epts = cloud(EVENT[lvl], event_keep, (40, 160, 960, 800))
    tree = cKDTree(epts)
    vr = R(vpts)
    def score(params):
        s, tx, ty = params
        q = vr * s + np.array([tx, ty])
        dd, _ = tree.query(q, distance_upper_bound=8.0)
        dd = np.where(np.isinf(dd), 8.0, dd)
        return float(np.mean(dd))
    best = None
    if lvl in CORNX:
        vx = np.array(CORNX[lvl]); ex = np.array(E_CORNX[lvl])
        vxr = np.array([vx[1], -vx[0]])
        for s0 in np.arange(1.15, 1.95, 0.02):
            t0 = ex - vxr * s0
            sc = score((s0, t0[0], t0[1]))
            if best is None or sc < best[0]:
                best = (sc, (s0, t0[0], t0[1]))
    else:
        # seed from boardroom text centres
        vd = fitz.open(VENUE[lvl])
        vh = vd[0].search_for("Gallery Boardroom") or vd[0].search_for("Gallery")
        vc = vh[0]; vcen = np.array([(vc.x0+vc.x1)/2, (vc.y0+vc.y1)/2])
        vd.close()
        ecen = np.array([(98.1+214.5)/2, (401.5+439.7)/2])  # GALLERY/BOARDROOM block
        vcr = np.array([vcen[1], -vcen[0]])
        for s0 in np.arange(1.0, 1.9, 0.02):
            t0 = ecen - vcr * s0
            for dx in (-20, 0, 20):
                for dy in (-20, 0, 20):
                    sc = score((s0, t0[0]+dx, t0[1]+dy))
                    if best is None or sc < best[0]:
                        best = (sc, (s0, t0[0]+dx, t0[1]+dy))
    res = minimize(score, best[1], method="Nelder-Mead",
                   options={"xatol":1e-3, "fatol":1e-5, "maxiter":2000})
    s, tx, ty = res.x
    T = lambda p, s=s, tx=tx, ty=ty: (p[1]*s + tx, -p[0]*s + ty)
    k = s * PTFT[lvl]
    info = {"s": s, "t": [tx, ty], "score": res.fun, "k_event_pt_per_ft": k,
            "bigx_event": T(BIGX[lvl]), "smallx_event": T(SMALLX[lvl])}
    if lvl in CORNX:
        pred = T(CORNX[lvl])
        info["cornx_residual_pt"] = math.hypot(pred[0]-E_CORNX[lvl][0], pred[1]-E_CORNX[lvl][1])
    results[lvl] = info
    print(f"L{lvl}: s={s:.4f} t=({tx:.1f},{ty:.1f}) meanDist={res.fun:.2f}pt "
          f"k={k:.3f} pt/ft bigX_e=({info['bigx_event'][0]:.1f},{info['bigx_event'][1]:.1f})"
          + (f" cornerX resid={info.get('cornx_residual_pt',0):.2f}pt" if lvl in CORNX else ""))

# cross-floor sanity: small shaft offset from big shaft, in feet, per floor
for lvl in (1, 2, 3):
    i = results[lvl]
    dx = (i["smallx_event"][0]-i["bigx_event"][0]) / i["k_event_pt_per_ft"]
    dy = (i["smallx_event"][1]-i["bigx_event"][1]) / i["k_event_pt_per_ft"]
    print(f"L{lvl}: small shaft offset from big shaft = ({dx:+.2f}, {dy:+.2f}) ft")

json.dump(results, open(f"{SP}/registration.json", "w"), indent=1)
print("saved registration.json")
