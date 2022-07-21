import numpy
import bpy
import bmesh
from bpy.app.handlers import persistent
from .patch_helper import PatchHelper
from .helper import Helper
from .reg_patch_constructor import RegPatchConstructor
from .extraordinary_patch_constructor import ExtraordinaryPatchConstructor
from .t0_patch_constructor import T0PatchConstructor
from .t1_patch_constructor import T1PatchConstructor
from .t2_patch_constructor import T2PatchConstructor
from .n_gon_patch_constructor import NGonPatchConstructor
from .polar_patch_constructor import PolarPatchConstructor
from .two_triangles_two_quads_patch_constructor import TwoTrianglesTwoQuadsPatchConstructor
from .patch_tracker import PatchTracker
from .patch import PatchOperator
from .bivariateBBFunctions import bbFunctions
from .moments import Moments

import math

# Debug
import time


class PolyhedralSplines(bpy.types.Operator):
    bl_label = "Interactive Modeling"
    bl_idname = "object.polyhedral_splines"

    # The algorithm using face as center
    face_based_patch_constructors: list = [
        T0PatchConstructor,
        T1PatchConstructor,
        T2PatchConstructor,
        NGonPatchConstructor
    ]
    # The algorithm using vert as center
    vert_based_patch_constructors: list = [
        RegPatchConstructor,
        ExtraordinaryPatchConstructor,
        PolarPatchConstructor,
        TwoTrianglesTwoQuadsPatchConstructor
    ]

    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")

    @classmethod
    def poll(cls, context):
        """
        Make the addon only can be found when object is active
        and it is a mesh in edit mode.
        """
        """
        obj = context.active_object
        if obj == None:
            print("No active object.")
            return False
        elif obj.mode != 'EDIT' or obj.type != 'MESH':
            print("Not in edit mode or the object is not mesh.")
            return False
        else:
            return True
        """

        obj = context.active_object
        selected = context.selected_objects

        if obj in selected and obj.mode == "OBJECT" and obj.type == "MESH":
            return True
        return False

    def execute(self, context):
        self.__init_patch_obj__(context)
        bpy.ops.ui.reloadtranslation()
        return {'FINISHED'}

    def __init_patch_obj__(self, context):
        context.object.display_type = 'WIRE'

        # control_mesh is the input obj file
        obj = context.view_layer.objects.active
        control_mesh = obj.data

        bm = bmesh.new()
        bm.from_mesh(control_mesh)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        patchWrappers = PatchHelper.getPatches(bm)
        for patchWrapper in patchWrappers:
            start = time.process_time()

            patchNames = PatchOperator.generate_multiple_patch_obj(patchWrapper.patch)
            PatchTracker.register_multiple_patches(patchWrapper.source, patchWrapper.neighbors, patchNames)
            for patch_name in patchNames:
                bpy.context.scene.objects[patch_name].parent = obj

            print("Generate patch obj time usage (sec): ", time.process_time() - start)

        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        Moments.executeBM(context, bm, obj.name)
        # Finish up, write the bmesh back to the mesh
        if control_mesh.is_editmode:
            bmesh.update_edit_mesh(control_mesh)
        else:
            bm.to_mesh(control_mesh)
            control_mesh.update()


# if previous mode is not edit, switching to edit has no need to update surface
class Mode:
    prev = "OBJECT"


# can't put it in the class
# please see https://developer.blender.org/T73638
prev_mode = 'OBJECT'


@persistent
def edit_object_change_handler(context):
    obj = bpy.context.active_object

    if obj is None:
        return None

    if obj.mode == 'EDIT' and Mode.prev == 'EDIT' and obj.type == 'MESH':
        update_surface(context, obj)

    Mode.prev = obj.mode

    return None


def update_surface(context, obj):
    bm = bmesh.from_edit_mesh(obj.data)
    selected_verts = [v for v in bm.verts if v.select]

    

    for sv in selected_verts:
        bmesh.update_edit_mesh(obj.data)

        # Get the centrol vert that needed to be updated
        central_vert_IDs = PatchTracker.get_central_vert_ID(sv)
        vpatch_names = PatchTracker.get_vert_based_patch_obj_name(sv)
        central_face_IDs = PatchTracker.get_central_face_ID(sv)
        fpatch_names = PatchTracker.get_face_based_patch_obj_name(sv)

        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        if central_face_IDs is not False and fpatch_names is not False:
            i = 0
            while i < len(central_face_IDs):
                for pc in PolyhedralSplines.face_based_patch_constructors:
                    if i >= len(central_face_IDs):
                        break
                    if not pc.is_same_type(bm.faces[central_face_IDs[i]]):
                        continue
                    bspline_patches = pc.get_patch(bm.faces[central_face_IDs[i]])
                    for bc in bspline_patches.bspline_coefs:
                        PatchOperator.update_patch_obj(fpatch_names[i], bc)
                        i = i + 1

        if central_vert_IDs is not False and vpatch_names is not False:
            i = 0
            while i < len(central_vert_IDs):
                for pc in PolyhedralSplines.vert_based_patch_constructors:
                    if i >= len(central_vert_IDs):
                        break
                    if not pc.is_same_type(bm.verts[central_vert_IDs[i]]):
                        continue
                    bspline_patches = pc.get_patch(bm.verts[central_vert_IDs[i]])
                    for bc in bspline_patches.bspline_coefs:
                        PatchOperator.update_patch_obj(vpatch_names[i], bc)
                        i = i + 1

    facePatchList = list(PatchTracker.fpatch_LUT)
    vertexPatchList = list(PatchTracker.vpatch_LUT)

    
bpy.app.handlers.depsgraph_update_post.append(edit_object_change_handler)
