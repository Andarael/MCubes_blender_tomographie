import bpy
import time

# IO options
input = "C:/Users/josur/Documents/untitled.obj"
output = "C:/Users/josur/Documents/TT 1000 KPP Prop 7 couches_edit.obj"

# Mesh options
scale = 1.0
scale_z = 1.0  # must correspond to scale factor used in the marching cubes algorithm

# Decimation options
decimation_ratio = 0.1
apply_modifiers = True  # applying modifier is faster for export, but we loose the original geometry

# Loose parts options
separate_by_loose_parts = False
nb_loose_parts_to_merge = 1
min_nb_count = 100000

# clean up options
remove_duplicates = True
remove_degenerate = True


def select_objects_by_vertex_count(count=0, mode='higher'):
    """select objects by vertex count"""
    objlist = []
    for o in bpy.data.objects:
        if isinstance(o.data, bpy.types.Mesh):

            if len(o.data.vertices) < count and mode == 'lower':
                objlist.append(o)

            elif len(o.data.vertices) > count and mode == 'higher':
                objlist.append(o)

            elif len(o.data.vertices) == count and mode == 'equal':
                objlist.append(o)

    if (objlist == []):
        print("ERROR! : No objects found with the given vertex count, using all objects instead")
        for o in bpy.data.objects:
            if isinstance(o.data, bpy.types.Mesh):
                o.select_set(True)

    objlist.sort(key=lambda x: len(x.data.vertices))

    objlist = objlist[:nb_loose_parts_to_merge]
    for o in objlist:
        o.select_set(True)


def set_active(object):
    bpy.context.view_layer.objects.active = object
    object.select_set(True)


def op_edit_mode():
    """Do some cleanup operations in edit mode, and separate loose geometry"""
    print("Info: Enter edit mode ...")
    bpy.ops.object.editmode_toggle()

    bpy.ops.mesh.select_all(action='SELECT')
    print("Info: Select all ...")

    if (remove_duplicates):
        print("Info: Remove duplicates ...")
        bpy.ops.mesh.remove_doubles(use_unselected=True)

    if (remove_degenerate):
        print("Info: Remove degenerate geometry ...")
        bpy.ops.mesh.dissolve_degenerate()

    if (separate_by_loose_parts):
        print("Info: Separate loose parts ...")
        bpy.ops.mesh.separate(type='LOOSE')

    bpy.ops.object.editmode_toggle()
    print("Info: Exit edit mode ...")


def add_decimate_modifiers(objects):
    """Add a decimate modifier to the objects in the list"""
    for object in objects:
        set_active(object)
        mod_name = 'decimate modifier'
        decimate_modifier = object.modifiers.new(mod_name, 'DECIMATE')
        decimate_modifier.decimate_type = 'COLLAPSE'
        decimate_modifier.ratio = decimation_ratio
        # no need to apply modifier, it is applied automatically at export
        if (apply_modifiers):
            print("Info: Apply modifier ...")
            bpy.ops.object.modifier_apply(modifier=mod_name)


def execute_script():
    print("Info: Import mesh ...")
    bpy.ops.wm.obj_import(filepath=input)

    print("Info: Apply scale ...")
    bpy.ops.transform.resize(value=(scale, scale, scale * scale_z), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL')
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    op_edit_mode()

    print("Info: Delete low vertex count objects ...")
    bpy.ops.object.select_all(action='DESELECT')
    select_objects_by_vertex_count(min_nb_count)
    bpy.ops.object.join()
    bpy.ops.object.select_all(action='INVERT')
    bpy.ops.object.delete(use_global=False)

    print("Info: Decimation ...")
    add_decimate_modifiers(bpy.context.selectable_objects)

    print("Info: Export mesh ...")
    bpy.ops.wm.obj_export(filepath=output,
                          forward_axis='NEGATIVE_Z_FORWARD', up_axis='Y_UP',
                          scaling_factor=1, apply_modifiers=True, export_eval_mode='DAG_EVAL_VIEWPORT', export_selected_objects=False, export_uv=False, export_normals=True, export_materials=False, path_mode='AUTO')


if __name__ == '__main__':
    start_time = time.time()
    print("\n\n==========================================================")
    print("Info: Start script ...\n")
    execute_script()
    print("\nInfo: Script finished in {:.2f} seconds".format(time.time() - start_time))
    print("==========================================================\n")


# TODO : cut in the unit cube
# TODO : add option to select all in loose parts
