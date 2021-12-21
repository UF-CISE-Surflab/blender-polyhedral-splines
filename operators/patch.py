import bpy
from dataclasses import dataclass, field
from bpy_extras.io_utils import unpack_list
from .helper import Helper
from collections import defaultdict


@dataclass
class BezierPatch:
    order_u: int = 3
    order_v: int = 3
    struct_name: str = "None"
    bezier_coefs: list = field(default_factory=lambda: [])


@dataclass
class BsplinePatch:
    order_u: int = 3
    order_v: int = 3
    struct_name: str = "None"
    bspline_coefs: list = field(default_factory=lambda: [])


class PatchOperator:
    # Create patch with same order_u and order_u only once
    # The following patch with same size with copy the first one as template
    # patch_template[order_u][order_v] = "name of patch obj"
    patch_templates: dict = defaultdict(dict)

    @classmethod
    def generate_single_patch_obj(cls, bspline_coefs, order_u, order_v, struct_name):

        bpy.ops.object.mode_set(mode='OBJECT')

        template_patch_name = PatchOperator.get_patch_template_name(order_u, order_v)
        patch_obj = 0

        if not template_patch_name:  # no template with wanted u v order
            patch_obj = PatchOperator.init_patch_template(order_u, order_v)
            PatchOperator.add_patch_name_to_dict(order_u, order_v, patch_obj.name)
        else:
            template_patch_obj = bpy.data.objects[template_patch_name]
            patch_obj = template_patch_obj.copy()
            patch_obj.data = template_patch_obj.data.copy()
            bpy.context.collection.objects.link(patch_obj)

        # Set different color for different structure
        mat = bpy.data.materials.get(struct_name)
        if mat is None:
            mat = bpy.data.materials.new(name=struct_name)
        patch_obj.active_material = mat

        # Spline coef need an extra dimension "weighting"
        bspline_coefs_4D = Helper.convert_3d_vectors_to_4d_coords(vecs=bspline_coefs, weighting=1)

        # Assign the position of each control points of bspline
        patch_obj.data.splines[0].points.foreach_set("co", unpack_list(bspline_coefs_4D))

        return patch_obj.name

    def generate_multiple_patch_obj(patch) -> list:
        """
        Input list of bezier coefs then generate multiple patche objects
        Return list of names for patch objects
        """
        obj_names = []
        for bc in patch.bspline_coefs:
            obj_names.append(PatchOperator.generate_single_patch_obj(bc, patch.order_u,
                                                                     patch.order_v, patch.struct_name))
        return obj_names

    @staticmethod
    def update_patch_obj(patch_name, bspline_coefs):  # call after running get patch
        bspline_coefs_4D = Helper.convert_3d_vectors_to_4d_coords(vecs=bspline_coefs, weighting=1)
        bpy.data.objects[patch_name].data.splines[0].points.foreach_set("co", unpack_list(bspline_coefs_4D))

        # for update purpose.. haven't found better function..
        for i in range(len(bspline_coefs)):
            bpy.data.objects[patch_name].data.splines[0].points[i].co = \
                bpy.data.objects[patch_name].data.splines[0].points[i].co

    @staticmethod
    def init_patch_template(order_u, order_v):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.surface.primitive_nurbs_surface_surface_add(radius=1, enter_editmode=True, location=(0, 0, 0))

        patch_obj = bpy.context.active_object

        for p in patch_obj.data.splines[0].points:
            p.select = False

        if order_u == 3 and order_v == 3:
            patch_obj.data.splines[0].points[3].select = True
            patch_obj.data.splines[0].points[7].select = True
            patch_obj.data.splines[0].points[11].select = True
            patch_obj.data.splines[0].points[15].select = True
            bpy.ops.curve.delete(type='VERT')
            patch_obj.data.splines[0].points[0].select = True
            patch_obj.data.splines[0].points[1].select = True
            patch_obj.data.splines[0].points[2].select = True
            bpy.ops.curve.delete(type='VERT')
            patch_obj.data.splines[0].order_u = 3
            patch_obj.data.splines[0].order_v = 3
        elif order_u == 5 and order_v == 5:
            patch_obj.data.splines[0].points[0].select = True
            patch_obj.data.splines[0].points[1].select = True
            patch_obj.data.splines[0].points[2].select = True
            patch_obj.data.splines[0].points[3].select = True
            bpy.ops.curve.extrude_move(CURVE_OT_extrude=None, TRANSFORM_OT_translate=None)
            for p in patch_obj.data.splines[0].points:
                p.select = False
            patch_obj.data.splines[0].points[3].select = True
            patch_obj.data.splines[0].points[7].select = True
            patch_obj.data.splines[0].points[11].select = True
            patch_obj.data.splines[0].points[15].select = True
            patch_obj.data.splines[0].points[19].select = True
            bpy.ops.curve.extrude_move(CURVE_OT_extrude=None, TRANSFORM_OT_translate=None)
            patch_obj.data.splines[0].order_u = 5
            patch_obj.data.splines[0].order_v = 5
        elif order_u == 4 and order_v == 4:
            patch_obj.data.splines[0].order_u = 4
            patch_obj.data.splines[0].order_v = 4
        elif order_u == 4 and order_v == 3:
            patch_obj.data.splines[0].points[3].select = True
            patch_obj.data.splines[0].points[7].select = True
            patch_obj.data.splines[0].points[11].select = True
            patch_obj.data.splines[0].points[15].select = True
            bpy.ops.curve.delete(type='VERT')
            patch_obj.data.splines[0].order_u = 3  # TODO: u v reflected problem here need to be fixed.
            patch_obj.data.splines[0].order_v = 4
        else:
            print("patch order has not supported yet")

        return patch_obj

    @classmethod
    def get_patch_template_name(cls, order_u, order_v):
        if order_u not in cls.patch_templates:
            return False
        if order_v not in cls.patch_templates[order_u]:
            return False
        return cls.patch_templates[order_u][order_v]

    @classmethod
    def add_patch_name_to_dict(cls, order_u, order_v, patch_name):
        cls.patch_templates[order_u][order_v] = patch_name
