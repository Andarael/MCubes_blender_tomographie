import bpy
import numpy as np

# Script options
output_path = "G:/Mon Drive/Scolaire/M1_Limoges/stage M1/Work/test.txt"

density = 100
radius_min = 0.01
radius_max = 0.05

duplicate = True # keep a copy of the mesh
apply_all = True # apply all modifier before generating point cloud

# ==============================================================================

C = bpy.context
D = bpy.data

# modifier & node names
geo_node_name = 'Distribute Points'
geo_node_mod_name = 'Distribute Points Modifier'

if (duplicate):
    bpy.ops.object.duplicate()

selected_object = C.selected_objects[0]
selected_object.name = "Point Cloud"

if (apply_all):
    for mod in selected_object.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)

# generate point cloud
geo_node_mod = selected_object.modifiers.new(geo_node_mod_name, 'NODES')
geo_node_mod.node_group = bpy.data.node_groups[geo_node_name]
geo_node_mod["Input_3"] = float(density)
bpy.ops.object.modifier_apply(modifier=geo_node_mod_name)

# move the points cloud above the surface according to particle radius
verts = selected_object.data.vertices
output = []
for v in verts:
    radius = np.random.uniform(radius_min, radius_max)
    v.co += v.normal*radius
    data = (v.co[0], v.co[1], v.co[2], radius)
    output.append(data)

# conversion to numpy array & export
output = np.array(output)
np.reshape(output, (len(verts), 4))
np.savetxt(output_path, output, fmt="%10.5f", delimiter=" ", newline=",\n", header="  pos[0]     pos[1]      pos[2]    radius")
