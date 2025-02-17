import bpy
import numpy as np
import time

# Script options
mesh_name = "//../output/KPP_Brut_AHPCS_dilue_TT_1000.obj"
output_path = "//../output/points.txt"

density = 100
radius_min = 0.1
radius_max = 1.0

duplicate = True  # keep a copy of the mesh
apply_all_modifiers = True  # apply all modifier before generating point cloud

# ==============================================================================

C = bpy.context
D = bpy.data

# modifier & node names
geo_node_name = 'Distribute Points'
geo_node_mod_name = 'Distribute Points Modifier'
scale_attribute_name = "scale"


def generate_points():
    if C.selected_objects == []:
        print("ERROR! : No object selected")
        return

    if (duplicate):
        bpy.ops.object.duplicate()

    selected_object = C.selected_objects[0]
    selected_object.name = "Point Cloud"

    if (apply_all_modifiers):
        print("Info: Apply all modifiers ...")
        for mod in selected_object.modifiers:
            bpy.ops.object.modifier_apply(modifier=mod.name)

    # generate point cloud
    print("Info: Generate Point Cloud ...")
    geo_node_mod = selected_object.modifiers.new(geo_node_mod_name, 'NODES')
    geo_node_mod.node_group = bpy.data.node_groups[geo_node_name]
    geo_node_mod["Input_3"] = float(density)
    geo_node_mod["Input_4"] = float(radius_min)
    geo_node_mod["Input_5"] = float(radius_max)
    geo_node_mod["Output_6_attribute_name"] = scale_attribute_name
    bpy.ops.object.modifier_apply(modifier=geo_node_mod_name)

    # create vert + raidus array
    print("Info: Fill Array ...")
    verts = selected_object.data.vertices
    output = []
    for i, v in enumerate(verts):
        radius = selected_object.data.attributes['scale'].data[i].value
        data = (v.co[0], v.co[1], v.co[2], radius)
        output.append(data)

    # conversion to numpy array & export
    print("Info: Export to txt ...")
    output = np.array(output)
    np.reshape(output, (len(verts), 4))
    np.savetxt(bpy.path.abspath(output_path), output, fmt="%10.5f", delimiter=" ", newline="\n", header="  pos[0]     pos[1]      pos[2]    radius")


if __name__ == "__main__":

    start_time = time.time()
    print("\n\n==========================================================")
    print("Info: Start point script ...\n")
    generate_points()
    print("\nInfo: Script finished in {:.2f} seconds".format(time.time() - start_time))
    print("==========================================================\n")
