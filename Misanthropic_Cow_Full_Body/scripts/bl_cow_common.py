"""Shared Blender helpers for the cow's delivery scripts."""
import bpy


def gltf_output_group():
    """The node group the glTF exporter reads extra channels from (occlusion)."""
    g = bpy.data.node_groups.get("glTF Material Output")
    if g: return g
    g = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
    g.interface.new_socket("Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
    g.nodes.new("NodeGroupInput")
    return g


def baked_material(name, maps):
    """Principled material from baked maps: maps = {basecolor, roughness, normal, ao} -> bpy images.
    Metallic 0. AO goes to the glTF occlusion slot only (not into the colour)."""
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    bs = N["Principled BSDF"]; bs.inputs["Metallic"].default_value = 0.0
    def tex(img, loc, data):
        n = N.new("ShaderNodeTexImage"); n.image = img; n.location = loc
        if data: img.colorspace_settings.name = "Non-Color"
        return n
    c = tex(maps["basecolor"], (-700, 300), False); L.new(c.outputs["Color"], bs.inputs["Base Color"])
    r = tex(maps["roughness"], (-700, 0), True); L.new(r.outputs["Color"], bs.inputs["Roughness"])
    n = tex(maps["normal"], (-700, -300), True)
    nm = N.new("ShaderNodeNormalMap"); nm.location = (-400, -300); L.new(n.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], bs.inputs["Normal"])
    if maps.get("ao"):
        a = tex(maps["ao"], (-700, -600), True)
        sep = N.new("ShaderNodeSeparateColor"); sep.location = (-400, -600); L.new(a.outputs["Color"], sep.inputs["Color"])
        gn = N.new("ShaderNodeGroup"); gn.node_tree = gltf_output_group(); gn.location = (0, -600)
        L.new(sep.outputs[0], gn.inputs["Occlusion"])
    return m
