from .patch_constructor import PatchConstructor
from .halfedge import Halfedge
from .bezier_bspline_converter import BezierBsplineConverter
from .patch import BezierPatch, BsplinePatch
from .helper import Helper
from .polar_patch_constructor import PolarPatchConstructor


class TwoTrianglesTwoQuadsPatchConstructor(PatchConstructor):
    name: str = "2T2Q"
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

        # The four neighbor faces should be two quads and two triangles
        num_of_quads = 0
        num_of_triangles = 0
        for f in vert.link_faces:
            if Helper.is_quad(f):
                num_of_quads = num_of_quads + 1
            elif Helper.is_triangle(f):
                num_of_triangles = num_of_triangles + 1
        if num_of_quads != 2 or num_of_triangles != 2:
            return False

        # Make sure two consecutive faces should both be quad or triangle
        if vert.link_faces[0] == vert.link_faces[2]:
            return False

        # One of the connected vert should be polar
        is_any_polar_vert = False
        for ve in vert.link_edges:
            ev = ve.other_vert(vert)
            if PolarPatchConstructor.is_same_type(ev):
                is_any_polar_vert = True
                break

        if not is_any_polar_vert:
            return False

        return True

    @classmethod
    def get_neighbor_verts(cls, vert) -> list:
        """
                     1 --- 2     0 3 6 are the vertices in the same position
                   / |     |
                  /  |     |
          (0,3,6) -- 4 --- 5
                  \  |     |
                   \ |     |
                     7 --- 8
        """
        # Get halfedge 4 -> 5
        halfedge = 0
        for he in vert.link_loops:
            if Helper.is_quad(he.face) and Helper.is_quad(he.link_loop_radial_next.face):
                halfedge = he
                break

        commands = [4, 1, 4, 1, 4, 1, 4, 3, 1, 1, 4, 4, 3, 1, 4, 1, 4, 3, 1, 1, 4]
        get_vert_order = [4, 5, 2, 1, 0, 3, 6, 7, 8]
        nb_verts = Halfedge.get_verts_repeat_n_times(halfedge, commands, 4, get_vert_order, 9)

        return nb_verts

    @classmethod
    def get_patch(cls, vert, isBspline = True) -> list:
        # Mask * nb_Verts = bezier coefs for single or multiple patches
        nb_verts = cls.get_neighbor_verts(vert)
        bezier_coefs = Helper.apply_mask_on_neighbor_verts(cls.mask, nb_verts)
        bspline_coefs = BezierBsplineConverter.bezier_to_bspline(bezier_coefs, cls.deg_u, cls.deg_v)
        bspline_coefs = Helper.convert_verts_from_matrix_to_list(bspline_coefs)

        # The table output coef for multiple patches so we need to figure out
        # how many patches are generated.
        # The number of patches = # of rows / # of coef per patch
        num_of_coef_per_patch = (cls.deg_u + 1) * (cls.deg_v + 1)
        num_of_patches = len(bspline_coefs) / num_of_coef_per_patch
        if(isBspline):
            return BsplinePatch(
                order_u=3,
                order_v=3,
                struct_name=cls.name,
                bspline_coefs=Helper.split_list(bspline_coefs, int(num_of_patches))
            )
        else:
            return BezierPatch(
                order_u=3,
                order_v=3,
                struct_name=cls.name,
                bezier_coefs=Helper.split_list(bezier_coefs, int(num_of_patches))
            )
