"""Step 1: carve the mask out of the voxelized scan (drop box, turntable, scanner blobs) and remesh."""
import sys, numpy as np, trimesh
from scipy import ndimage as ndi
from skimage import measure

vox, out = sys.argv[1], sys.argv[2]
sym = np.load(sys.argv[3]) if len(sys.argv) > 3 else np.array([1., 0, 0, 0])
d = np.load(vox); occ = d['occ']; T = d['T']
ii, jj, kk = np.indices(occ.shape)
X = T[0, 3] + ii * T[0, 0]; Y = T[1, 3] + jj * T[1, 1]; Z = T[2, 3] + kk * T[2, 2]

# everything in front of the box's front face, below the horn bar. The box is square to the
# mask's symmetry plane, so measure depth in that rotated frame.
th = np.arctan2(sym[1], sym[0])
Yr = X * np.sin(-th) + Y * np.cos(-th)
mask = occ & (Yr < -1.0) & (Z < 214)
lab, n = ndi.label(mask)
mask = lab == (np.argmax(ndi.sum(mask, lab, range(1, n + 1))) + 1)

def ball(r):
    g = np.arange(-r, r + 1); a, b, c = np.meshgrid(g, g, g, indexing='ij')
    return a * a + b * b + c * c <= r * r + 0.5

# light opening everywhere removes speckle; the red yarn snout scattered the laser into
# bead-like blobs, so it gets a much stronger opening
gen = ndi.binary_opening(mask, ball(3))
snout_zone = (Y < -66) & (Z < 100)
sn = ndi.binary_opening(mask, ball(7))
w = ndi.gaussian_filter(snout_zone.astype(np.float32), 4)  # feathered blend between the two
f = ndi.gaussian_filter(gen.astype(np.float32), 1.0) * (1 - w) + ndi.gaussian_filter(sn.astype(np.float32), 1.6) * w
np.savez_compressed(out.replace('.ply', '_field.npz'), f=f.astype(np.float16), T=T)
v, fa, _, _ = measure.marching_cubes(np.pad(f, 2), 0.5)
v = (v - 2) * np.diag(T)[:3] + T[:3, 3]
mesh = trimesh.Trimesh(v, fa[:, ::-1])
mesh = max(mesh.split(only_watertight=False), key=lambda c: len(c.faces))
print('faces', len(mesh.faces), 'watertight', mesh.is_watertight)
mesh.export(out)
