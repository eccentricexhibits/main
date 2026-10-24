"""Step 4: export the head as GLB (metres, Y up, facing +Z, pivot at the base of the neck) and OBJ."""
import sys, os, numpy as np, trimesh
from PIL import Image
from trimesh.visual.material import PBRMaterial
from trimesh.visual import TextureVisuals

baked, parts, out_dir = sys.argv[1:4]
os.makedirs(out_dir, exist_ok=True)
NECK_Y = -24.0                                   # flat neck opening from step 2
def to_m(v): return (np.asarray(v) - [0, NECK_Y, 0]) / 1000.0

d = np.load(f'{baked}/head_uvmesh.npz')
tex = Image.open(f'{baked}/head_basecolor.png')
head = trimesh.Trimesh(to_m(d['V']), d['F'], vertex_normals=d['N'], process=False,
                       visual=TextureVisuals(uv=d['UV'], material=PBRMaterial(
                           name='MaskAndHood', baseColorTexture=tex, roughnessFactor=0.85, metallicFactor=0.0)))

def coloured(path, name, rough, metal=0.0):
    m = trimesh.load(path, process=False); m.vertices = to_m(m.vertices)
    vc = m.visual.vertex_colors.astype(float)
    vc[:, :3] = 255 * (vc[:, :3] / 255) ** 2.2   # glTF vertex colours are linear
    vc = vc.round().astype(np.uint8)
    m.visual = trimesh.visual.ColorVisuals(m, vertex_colors=vc)
    mat = PBRMaterial(name=name, baseColorFactor=[255, 255, 255, 255], roughnessFactor=rough, metallicFactor=metal)
    return m, mat

scene = trimesh.Scene()
scene.add_geometry(head, node_name='MaskAndHood', geom_name='MaskAndHood')
for path, name, rough in ((f'{baked}/hornbar_col.ply', 'HornBar', 0.95), (f'{baked}/horn_L_col.ply', 'Horn.L', 0.55),
                          (f'{baked}/horn_R_col.ply', 'Horn.R', 0.55)):
    m, mat = coloured(path, name, rough)
    m.visual.material = mat
    scene.add_geometry(m, node_name=name, geom_name=name)
wire = trimesh.load(f'{parts}/wire_R.ply', process=False); wire.vertices = to_m(wire.vertices)
wire.visual = TextureVisuals(material=PBRMaterial(name='Wire', baseColorFactor=[0.25, 0.24, 0.23, 1], roughnessFactor=0.4, metallicFactor=0.9))
scene.add_geometry(wire, node_name='HornWire.R', geom_name='HornWire.R')

scene.export(f'{out_dir}/misanthropic_cow_head.glb')
head.export(f'{out_dir}/misanthropic_cow_head_mask_hood.obj')  # writes .mtl + texture alongside
print('exported', {k: len(g.faces) for k, g in scene.geometry.items()})
print('bounds (m)', scene.bounds.round(3).tolist())
