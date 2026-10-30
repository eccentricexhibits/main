"""Small geometry helpers shared by the cow scripts."""
import numpy as np, trimesh

SEG = 24        # tube sides


def sweep(C, r, sides=SEG, cap_root=True, cap_tip=True):
    """Closed tube along centreline C (n,3) with radii r (n,). Parallel-transport frames."""
    T = np.gradient(C, axis=0); T /= np.linalg.norm(T, axis=1)[:, None]
    a = np.array([0, 0, 1.0]) if abs(T[0, 2]) < 0.9 else np.array([1.0, 0, 0])
    N = np.cross(T[0], a); N /= np.linalg.norm(N)
    Ns = [N]
    for i in range(1, len(C)):
        v = np.cross(T[i - 1], T[i]); s = np.linalg.norm(v)
        if s > 1e-9:
            v /= s; ang = np.arccos(np.clip(T[i - 1] @ T[i], -1, 1))
            N = N * np.cos(ang) + np.cross(v, N) * np.sin(ang) + v * (v @ N) * (1 - np.cos(ang))
        N -= T[i] * (N @ T[i]); N /= np.linalg.norm(N); Ns.append(N)
    Ns = np.array(Ns); Bs = np.cross(T, Ns)
    th = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    V = (C[:, None, :] + r[:, None, None] * (np.cos(th)[None, :, None] * Ns[:, None, :] + np.sin(th)[None, :, None] * Bs[:, None, :])).reshape(-1, 3)
    F = []
    n = len(C)
    for i in range(n - 1):
        for j in range(sides):
            a0, a1 = i * sides + j, i * sides + (j + 1) % sides
            b0, b1 = a0 + sides, a1 + sides
            F += [[a0, b0, b1], [a0, b1, a1]]
    V = list(V)
    if cap_root:
        V.append(C[0] - T[0] * r[0] * 0.3); c = len(V) - 1
        F += [[c, (j + 1) % sides, j] for j in range(sides)]
    if cap_tip:
        V.append(C[-1] + T[-1] * max(r[-1], 0.2)); c = len(V) - 1
        F += [[c, (n - 1) * sides + j, (n - 1) * sides + (j + 1) % sides] for j in range(sides)]
    return trimesh.Trimesh(np.array(V), np.array(F), process=True)
