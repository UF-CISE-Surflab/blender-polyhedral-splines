from .patch_constructor import PatchConstructor
from .halfedge import Halfedge
from .bezier_bspline_converter import BezierBsplineConverter
from .patch import BezierPatch, BsplinePatch
from .helper import Helper
from .csv_reader import Reader


class T1PatchConstructor(PatchConstructor):
    name: str = "T1"
    mask_file_names = ["T1"]
    masks = Reader.csv_to_masks(mask_file_names)

    @classmethod
    def is_same_type(cls, face) -> bool:

        # The face belongs to T1 structure should be pentagon
        if not Helper.is_pentagon(face):
            return False

        # The verts of pentagon should be one 3 valences and four 4 valences
        if not cls.__is_pentagon_t_junction__(face):
            return False

        # get one ring face surround pentagon
        neighbor_faces = Helper.init_neighbor_faces(face)

        # The 9 faces surround pentagon should all be quad
        if not Helper.are_faces_all_quad(neighbor_faces):
            return False

        print("T1 found!")

        return True

    @classmethod
    def __is_pentagon_t_junction__(cls, face):
        num_of_4_valent_vert = 0
        num_of_3_valent_vert = 0
        for v in face.verts:
            if len(v.link_edges) == 4:
                num_of_4_valent_vert = num_of_4_valent_vert + 1
            elif len(v.link_edges) == 3:
                num_of_3_valent_vert = num_of_3_valent_vert + 1

        print("# 3 valent = ", num_of_3_valent_vert, "# 4 valent = ", num_of_4_valent_vert)
        if num_of_4_valent_vert != 4 or num_of_3_valent_vert != 1:
            return False
        else:
            return True

    @classmethod
    def get_neighbor_verts(cls, face) -> list:
        """
              0 - 1 - 2 - 3
              |   |   |   |
              4 - 5 - 6 - 7
             /   /     \   \
            8 - 9 -10- 11 - 12
            |   |   |   |   |
           13 -14 -15- 16 - 17
        """
        # Get halfedge pointing from 10 -> 11
        halfedge = 0
        for he in face.loops:
            if len(he.vert.link_edges) == 3:
                halfedge = he

        commands = [
            4, 3, 4, 2, 4, 3, 1, 1, 4,
            1, 4, 3, 1, 1, 4, 3, 4, 1, 1, 4,
            1, 4, 3, 1, 1, 4, 3, 4, 1, 1, 4,
            1, 4, 3, 1, 1, 4, 3, 4, 1, 1, 4,
            1, 4, 3, 1, 1, 4
        ]
        get_vert_order = [10, 11, 16, 17, 12, 7, 6, 3, 2, 1, 5, 0, 4, 8, 9, 13, 14, 15]
        return Halfedge.get_verts_repeat_n_times(halfedge, commands, 1, get_vert_order, 18)

    @classmethod
    def get_bezier_patch(cls, face) -> list:
        deg_u = 3
        deg_v = 3
        order_u = deg_u + 1
        order_v = deg_v + 1
        nb_verts = cls.get_neighbor_verts(face)
        bezier_coefs = Helper.apply_mask_on_neighbor_verts(cls.masks[cls.name], nb_verts)
        num_of_coef_per_patch = (deg_u + 1) * (deg_v + 1)
        num_of_patches = len(bezier_coefs) / num_of_coef_per_patch
        return BezierPatch(
            order_u=order_u,
            order_v=order_v,
            struct_name=cls.name,
            bezier_coefs=Helper.split_list(bezier_coefs, int(num_of_patches))
        )

    @classmethod
    def get_patch(cls, face) -> list:
        deg_u = 3
        deg_v = 3

        nb_verts = cls.get_neighbor_verts(face)

        bezier_coefs = Helper.apply_mask_on_neighbor_verts(cls.masks[cls.name], nb_verts)
        bspline_coefs = BezierBsplineConverter.bezier_to_bspline(bezier_coefs, deg_u, deg_v)
        bspline_coefs = Helper.convert_verts_from_matrix_to_list(bspline_coefs)

        # The table output coef for multiple patches so we need to figure out
        # how many patches are generated.
        # The number of patches = # of rows / # of coef per patch
        num_of_coef_per_patch = (deg_u + 1) * (deg_v + 1)
        num_of_patches = len(bspline_coefs) / num_of_coef_per_patch

        return BsplinePatch(
            order_u=deg_u + 1,
            order_v=deg_v + 1,
            struct_name=cls.name,
            bspline_coefs=Helper.split_list(bspline_coefs, int(num_of_patches))
        )
