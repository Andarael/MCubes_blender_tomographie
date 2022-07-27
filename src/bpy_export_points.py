import bpy
import numpy as np

C = bpy.context
D = bpy.data

bpy.ops.object.duplicate()

selected_object = C.selected_objects[0]

selected_object.name = "Point Cloud"


geo_node_mod_name = 'Distribute Points Modifier'

geo_node_mod = selected_object.modifiers.new(geo_node_mod_name, 'NODES')

selected_object.modifiers[geo_node_mod_name].node_group = bpy.data.node_groups['Distribute Points']

bpy.ops.object.modifier_apply(modifier=geo_node_mod_name)


verts = selected_object.data.vertices

npverts = np.array(verts)
print(npverts.shape)

output = []

for v in verts:
    radius = np.random.rand()*0.1
    v.co += v.normal*radius
    data = (v.co[0], v.co[1], v.co[2], radius)
    output.append(data)

output = np.array(output)
np.reshape(output, (len(verts), 4))

print(output)
print(output.shape)

path = "G:/Mon Drive/Scolaire/M1_Limoges/stage M1/Work/test.txt"

np.savetxt(path, output, fmt="%10.5f", delimiter=" ", newline=",\n", header="  pos[0]     pos[1]      pos[2]    radius")
