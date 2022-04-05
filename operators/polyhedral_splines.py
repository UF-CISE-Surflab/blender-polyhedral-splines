import numpy
import bpy
import bmesh
from bpy.app.handlers import persistent
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
        return True

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

        # Iterate through each vert of the mesh
        runningSum = 0.000
        centerOfMass = numpy.zeros(3)
        momentOfInertia = numpy.zeros((3,3))
        for v in bm.verts:
            # Iterate throgh different type of patch constructors
            for pc in self.vert_based_patch_constructors:
                if pc.is_same_type(v):
                    start = time.process_time()
                    bspline_patches = pc.get_patch(v)
                    patch_names = PatchOperator.generate_multiple_patch_obj(bspline_patches)
                    nb_verts = pc.get_neighbor_verts(v)
                    PatchTracker.register_multiple_patches(v, nb_verts, patch_names)
                    bezier_patches = pc.get_bezier_patch(v)
                    for bp in bezier_patches.bezier_coefs:
                        xCoefs, yCoefs, zCoefs = Helper.list_to_npmatrices(bp, bezier_patches.order_u, bezier_patches.order_v)
                        pieceVolume, pieceCOM, pieceMOI = bbFunctions.allMoments(xCoefs, yCoefs, zCoefs)
                        runningSum = runningSum + pieceVolume
                        centerOfMass = centerOfMass + pieceCOM
                        momentOfInertia = momentOfInertia + pieceMOI
                    print("Generate patch obj time usage (sec): ", time.process_time() - start)
        
        centerOfMass /= runningSum
        
        Moments.CoM[0] = round(centerOfMass[0], 2)
        Moments.CoM[1] = round(centerOfMass[1], 2)
        Moments.CoM[2] = round(centerOfMass[2], 2)

        Moments.Volume = abs(round(runningSum, 2))

        Moments.InertiaTens[0][0] = round(momentOfInertia[0][0], 2)
        Moments.InertiaTens[0][1] = round(momentOfInertia[0][1], 2)
        Moments.InertiaTens[0][2] = round(momentOfInertia[0][2], 2)
        Moments.InertiaTens[1][0] = round(momentOfInertia[1][0], 2)
        Moments.InertiaTens[1][1] = round(momentOfInertia[1][1], 2)
        Moments.InertiaTens[1][2] = round(momentOfInertia[1][2], 2)
        Moments.InertiaTens[2][0] = round(momentOfInertia[2][0], 2)
        Moments.InertiaTens[2][1] = round(momentOfInertia[2][1], 2)
        Moments.InertiaTens[2][2] = round(momentOfInertia[2][2], 2)

        Moments.execute(self = self, context= context)

        # Iterate through each face of the mesh
        for f in bm.faces:
            for pc in self.face_based_patch_constructors:
                if pc.is_same_type(f):
                    bspline_patches = pc.get_patch(f)
                    patch_names = PatchOperator.generate_multiple_patch_obj(bspline_patches)
                    nb_verts = pc.get_neighbor_verts(f)
                    PatchTracker.register_multiple_patches(f, nb_verts, patch_names)

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


bpy.app.handlers.depsgraph_update_post.append(edit_object_change_handler)
