"""Studio render of the glove pair .blend: left glove's finger pairs spread, right glove closed.
usage: python3 bl_render_pair.py <Glove_pair.blend> <out.png> [spread_deg=15] [samples=32]"""
import sys, math, bpy
from mathutils import Vector
B, OUT = sys.argv[1:3]; SP = float(sys.argv[3]) if len(sys.argv) > 3 else 15; SA = int(sys.argv[4]) if len(sys.argv) > 4 else 32
bpy.ops.wm.open_mainfile(filepath=B)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = SA
sc.render.resolution_x, sc.render.resolution_y = 1600, 1000
bpy.data.objects["Glove_L_Toe_IndexMiddle"].rotation_euler.y += math.radians(SP)    # +X toe tips outward
bpy.data.objects["Glove_L_Toe_RingLittle"].rotation_euler.y -= math.radians(SP)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.93, 0.93, 0.95, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.55
for rot, e in (((50, 10, -35), 3.0), ((70, 0, 140), 1.0)):
    l = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); l.data.energy = e; sc.collection.objects.link(l)
    l.rotation_euler = tuple(math.radians(a) for a in rot)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 85; tgt = Vector((0, 0, 0.125)); d = Vector((0.15, -1, 0.25)).normalized()
cam.location = tgt + d * 1.15; cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = OUT; bpy.ops.render.render(write_still=True); print("saved", OUT)
