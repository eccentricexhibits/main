"""Scan frame (mm, Z up, face toward -Y, box behind) <-> model frame (mm, Y up, face toward +Z, X = character's left)."""
import numpy as np

def scan_to_model_matrix(sym):
    n, off = sym[:3], sym[3]
    th = np.arctan2(n[1], n[0])          # yaw of the symmetry-plane normal
    c, s = np.cos(-th), np.sin(-th)
    Rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    swap = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])  # (x, y, z) -> (x, z, -y)
    A = np.eye(4); A[:3, :3] = swap @ Rz; A[:3, 3] = swap @ np.array([-off, 0, 0])
    return A

def apply(A, P):
    return P @ A[:3, :3].T + A[:3, 3]
