from .patch_constructor import PatchConstructor
from .halfedge import Halfedge
from .bezier_bspline_converter import BezierBsplineConverter
from .patch import BezierPatch, BsplinePatch
from .helper import Helper


class RegPatchConstructor(PatchConstructor):
    name: str = "Regular"
    deg_u: int = 2
    deg_v: int = 2

    mask: tuple = (
        [1, 1, 0, 1, 1, 0, 0, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 0, 0],
        [0, 1, 1, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 1, 1, 0],
        [0, 0, 0, 0, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 1, 1]
    )

    @classmethod
    def is_same_type(cls, vert) -> bool:

        # The vert should be 4-valent
        if len(vert.link_edges) != 4:
            return False

        # All four neighbor faces should be quad (with four verts)
        for f in vert.link_faces:
            if not Helper.is_quad(f):
                return False

        return True

    @classmethod
    def get_neighbor_verts(cls, vert) -> list:
        """
        Return the neighbor verts (including central vert) which will
        be the input of mask (then output bezier coef).
        """
        he = vert.link_loops[0]
        commands = [1, 4, 1, 4, 1, 3]
        get_vert_order = [1, 0, 3, 6, 7, 8, 5, 2]
        nb_verts = Halfedge.get_verts_repeat_n_times(he, commands, 4, get_vert_order, 9)
        nb_verts[4] = vert
        print(nb_verts)
        return nb_verts

    @classmethod
    def get_bezier_patch(cls, vert) -> list:
        nb_verts = cls.get_neighbor_verts(vert)
        bezier_coefs = Helper.apply_mask_on_neighbor_verts(cls.mask, nb_verts)
        num_of_coef_per_patch = (cls.deg_u + 1) * (cls.deg_v + 1)
        num_of_patches = len(bezier_coefs) / num_of_coef_per_patch
        return BezierPatch(
            order_u=cls.deg_u + 1,
            order_v=cls.deg_v + 1, 
            struct_name=cls.name,
            bezier_coefs=Helper.split_list(bezier_coefs, int(num_of_patches))
        )

    @classmethod
    def get_patch(cls, vert) -> list:
        # Mask * nb_Verts = bezier coefs for single or multiple patches
        nb_verts = cls.get_neighbor_verts(vert)
        bezier_coefs = Helper.apply_mask_on_neighbor_verts(cls.mask, nb_verts)
        #print(bezier_coefs)
        #print("break")
        bspline_coefs = BezierBsplineConverter.bezier_to_bspline(bezier_coefs, cls.deg_u, cls.deg_v)
        bspline_coefs = Helper.convert_verts_from_matrix_to_list(bspline_coefs)
        # The table output coef for multiple patches so we need to figure out
        # how many patches are generated.
        # The number of patches = # of rows / # of coef per patch
        num_of_coef_per_patch = (cls.deg_u + 1) * (cls.deg_v + 1)
        num_of_patches = len(bspline_coefs) / num_of_coef_per_patch

        return BsplinePatch(
            order_u=cls.deg_u + 1,
            order_v=cls.deg_v + 1,
            struct_name=cls.name,
            bspline_coefs=Helper.split_list(bspline_coefs, int(num_of_patches))
        )
