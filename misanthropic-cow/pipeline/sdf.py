"""Signed-distance modelling helpers and mesh utilities (marching cubes, smoothing, decimation)."""
import numpy as np
from scipy import sparse


def ellipsoid(p, c, r):
    q = (p - np.asarray(c)) / np.asarray(r)
    k0 = np.linalg.norm(q, axis=-1)
    k1 = np.linalg.norm(q / np.asarray(r), axis=-1)
    return k0 * (k0 - 1) / np.maximum(k1, 1e-9)


def sphere(p, c, r):
    return np.linalg.norm(p - np.asarray(c), axis=-1) - r


def round_cone(p, a, b, r1, r2):
    """Inigo Quilez's exact round cone (tapered capsule) from a (radius r1) to b (radius r2)."""
    a = np.asarray(a, float); b = np.asarray(b, float)
    ba = b - a
    l2 = ba @ ba
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pa = p - a
    y = pa @ ba
    z = y - l2
    xv = pa * l2 - y[..., None] * ba
    x2 = np.einsum('...i,...i->...', xv, xv)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d = np.where(np.sign(z) * a2 * z2 > k, np.sqrt(x2 + z2) * il2 - r2,
                 np.where(np.sign(y) * a2 * y2 < k, np.sqrt(x2 + y2) * il2 - r1,
                          (np.sqrt(x2 * a2 * il2) + y * rr) * il2 - r1))
    return d


def capsule(p, a, b, r):
    return round_cone(p, a, b, r, r)


def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * .25


def smax(a, b, k):
    return -smin(-a, -b, k)


def plane(p, point, normal):
    n = np.asarray(normal, float); n /= np.linalg.norm(n)
    return (p - np.asarray(point)) @ n


# ---------------------------------------------------------------- meshing
def mesh_sdf(fn, lo, hi, step, chunk=40):
    from skimage.measure import marching_cubes
    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    n = np.ceil((hi - lo) / step).astype(int) + 1
    xs, ys, zs = [lo[i] + np.arange(n[i]) * step for i in range(3)]
    vol = np.empty((n[0], n[1], n[2]), np.float32)
    for i0 in range(0, n[0], chunk):
        X, Y, Z = np.meshgrid(xs[i0:i0 + chunk], ys, zs, indexing='ij')
        vol[i0:i0 + chunk] = fn(np.stack([X, Y, Z], -1))
    v, f, _, _ = marching_cubes(vol, 0.0, spacing=(step, step, step))
    v += lo
    f = f.astype(np.int64)
    # orient faces outward using the field gradient at face centroids
    c = v[f].mean(1)
    e = step * .5
    g = np.stack([fn(c + d) - fn(c - d) for d in np.eye(3) * e], -1)
    fnrm = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    if np.sum(np.einsum('ij,ij->i', fnrm, g) < 0) > len(f) / 2:
        f = f[:, ::-1]
    return v, np.ascontiguousarray(f)


def adjacency(nv, f):
    i = np.concatenate([f[:, 0], f[:, 1], f[:, 2], f[:, 1], f[:, 2], f[:, 0]])
    j = np.concatenate([f[:, 1], f[:, 2], f[:, 0], f[:, 0], f[:, 1], f[:, 2]])
    A = sparse.coo_matrix((np.ones(len(i)), (i, j)), shape=(nv, nv)).tocsr()
    A.data[:] = 1
    return A


def taubin(v, f, iters=10, lam=.5, mu=-.53, fixed=None):
    A = adjacency(len(v), f)
    deg = np.asarray(A.sum(1)).ravel()
    deg[deg == 0] = 1
    W = sparse.diags(1 / deg) @ A
    v = v.copy()
    for _ in range(iters):
        for s in (lam, mu):
            d = W @ v - v
            if fixed is not None:
                d[fixed] = 0
            v += s * d
    return v


def vertex_normals(v, f):
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    n = np.zeros_like(v)
    for k in range(3):
        np.add.at(n, f[:, k], fn)
    l = np.linalg.norm(n, axis=1, keepdims=True)
    return n / np.maximum(l, 1e-12)


def decimate(v, f, target_faces):
    import vtk
    from vtk.util import numpy_support as ns
    if len(f) <= target_faces:
        return v, f
    pts = vtk.vtkPoints(); pts.SetData(ns.numpy_to_vtk(np.ascontiguousarray(v, np.float64), deep=True))
    cells = np.hstack([np.full((len(f), 1), 3), f]).astype(np.int64).ravel()
    ca = vtk.vtkCellArray(); ca.SetCells(len(f), ns.numpy_to_vtkIdTypeArray(cells, deep=True))
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(ca)
    q = vtk.vtkQuadricDecimation()
    q.SetInputData(pd)
    q.SetTargetReduction(1 - target_faces / len(f))
    q.VolumePreservationOn()
    q.Update()
    o = q.GetOutput()
    v2 = ns.vtk_to_numpy(o.GetPoints().GetData()).astype(np.float64)
    f2 = ns.vtk_to_numpy(o.GetPolys().GetData()).reshape(-1, 4)[:, 1:].astype(np.int64)
    return v2, f2


def clean(v, f):
    """Remove unreferenced vertices and degenerate faces."""
    f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
    used = np.unique(f)
    remap = -np.ones(len(v), np.int64); remap[used] = np.arange(len(used))
    return v[used], remap[f]


def largest_component(v, f):
    from scipy.sparse.csgraph import connected_components
    A = adjacency(len(v), f)
    n, lab = connected_components(A, directed=False)
    if n == 1:
        return v, f
    big = np.bincount(lab).argmax()
    keep = lab[f[:, 0]] == big
    return clean(v, f[keep])


def remesh(v, f, fn, step, iters=3):
    """Project vertices back onto the SDF zero set (Newton steps) to undo smoothing shrinkage."""
    e = step * .25
    for _ in range(iters):
        d = fn(v)
        g = np.stack([fn(v + dd) - fn(v - dd) for dd in np.eye(3) * e], -1) / (2 * e)
        gn = np.maximum(np.einsum('ij,ij->i', g, g), 1e-12)
        v = v - (d / gn)[:, None] * g
    return v
