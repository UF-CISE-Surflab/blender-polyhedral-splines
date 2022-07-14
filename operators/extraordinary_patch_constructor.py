from .patch_constructor import PatchConstructor
from .halfedge import Halfedge
from .bezier_bspline_converter import BezierBsplineConverter
from .patch import BezierPatch, BsplinePatch
from .helper import Helper
from .csv_reader import Reader


class ExtraordinaryPatchConstructor(PatchConstructor):
    name: str = "EOP"
    mask_file_names = ["eopSct3", "eopSct5", "eopSct6", "eopSct7", "eopSct8"]
    masks = Reader.csv_to_masks(mask_file_names)

    @classmethod
    def is_same_type(cls, vert) -> bool:
        # The extraordinary point should be 3, 5, 6, 7, 8 valent
        if len(vert.link_edges) not in (3, 5, 6, 7, 8):
            return False

        # The point should not be on the boundary
        if vert.is_boundary:
            return False

        # All neighbor faces should be quad (with four verts)
        for f in vert.link_faces:
            if not Helper.is_quad(f):
                return False

        return True

    @classmethod
    def get_neighbor_verts(cls, vert) -> list:
        """
        Return the neighbor verts (including central vert). The bezier coef.
        can be obtained by multiplying the matrix of neighbor vert with mask.

        Here we take 3 valent as example:
              0
            / | \    Get neighbor vert order 0 1 -> 2 3 -> 4 5 -> 6
           /  |  \
          1   6   5
           \  / \ /
            2    4
             \  /
              3
        """
        # Get valent of vert
        valence = len(vert.link_edges)

        commands = [1, 4, 1, 4, 1, 3]  # get vert in one wing ex: 0 1
        num_of_ring_vert = valence * 2
        index_of_ring_vert = list(range(num_of_ring_vert))
        nb_verts = Halfedge.get_verts_repeat_n_times(
            vert.link_loops[0], commands, valence, index_of_ring_vert, num_of_ring_vert)

        # Last neighbor vert is the central vert
        nb_verts.append(vert)

        return nb_verts

    @classmethod
    def get_patch(cls, vert, isBspline = True) -> list:
        deg_u = 3
        deg_v = 3
        order_u = deg_u + 1
        order_v = deg_v + 1
        nb_verts = cls.get_neighbor_verts(vert)

        # Get valent of vert and apply the corresponding mask
        valence = len(vert.link_edges)
        bezier_coefs = Helper.apply_mask_on_neighbor_verts(cls.masks["eopSct{}".format(valence)], nb_verts)
        bspline_coefs = BezierBsplineConverter.bezier_to_bspline(bezier_coefs, deg_u, deg_v)
        bspline_coefs = Helper.convert_verts_from_matrix_to_list(bspline_coefs)

        # The table output coef for multiple patches so we need to figure out
        # how many patches are generated.
        # The number of patches = # of rows / # of coef per patch
        num_of_coef_per_patch = (deg_u + 1) * (deg_v + 1)
        num_of_patches = len(bspline_coefs) / num_of_coef_per_patch
        if(isBspline):
            return BsplinePatch(
                order_u=order_u,
                order_v=order_v,
                struct_name=cls.name,
                bspline_coefs=Helper.split_list(bspline_coefs, int(num_of_patches))
            )
        else:
            return BezierPatch(
                order_u=order_u,
                order_v=order_v,
                struct_name=cls.name,
                bezier_coefs=Helper.split_list(bezier_coefs, int(num_of_patches))
            )
