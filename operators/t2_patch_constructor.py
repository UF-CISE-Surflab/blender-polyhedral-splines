from .patch_constructor import PatchConstructor
from .halfedge import Halfedge
from .bezier_bspline_converter import BezierBsplineConverter
from .patch import BezierPatch, BsplinePatch
from .helper import Helper
from .csv_reader import Reader


class T2PatchConstructor(PatchConstructor):
    name: str = "T2"
    mask_file_names = ["T2"]
    masks = Reader.csv_to_masks(mask_file_names)

    @classmethod
    def is_same_type(cls, face) -> bool:

        # The face belongs to T2 structure should be hexagon
        if not Helper.is_hexagon(face):
            return False

        # Get vert 13 6 5 9 11 12 (counter or clockwise) and store them to vector
        vert_valences = []
        for v in face.verts:
            vert_valences += [len(v.link_edges)]

        # Rotate until first element is 3 (valent)
        for i in range(len(vert_valences)):
            if vert_valences[0] == 3:
                break
            # Left rotate by 1 element
            vert_valences = vert_valences[1:] + vert_valences[:1]

        print(vert_valences)

        # After rotation the order of valence should be 3 4 4 4 3 4 or 3 4 3 4 4 4
        correct_order0 = [3, 4, 4, 4, 3, 4]
        correct_order1 = [3, 4, 3, 4, 4, 4]
        if(vert_valences != correct_order0 and vert_valences != correct_order1):
            return False

        # Get surrounding faces
        neighbor_faces = Helper.init_neighbor_faces(face)

        # Check 10 surrounding faces are all quad
        if not Helper.are_faces_all_quad(neighbor_faces):
            return False
        print("T2 found!")

        return True

    @classmethod
    def get_neighbor_verts(cls, face) -> list:
        """
            0 - 1 -------- 2 - 3
            |   |          |   |
            4 - 5 -------- 6 - 7
            |   |          |   |
            8 - 9          |   |
            |   |          |   |
           10 - 11 - 12 - 13 - 14
            |   |    |     |   |
           15 - 16 - 17 - 18 - 19
        """
        # Get halfedge pointing from 11 -> 12
        halfedge = 0
        for he in face.loops:
            if len(he.vert.link_edges) == 4:
                v_prev = Halfedge.get_single_vert(he, [2, 4])
                v_next = Halfedge.get_single_vert(he, [1, 4])
                if len(v_prev.link_edges) == 3 and len(v_next.link_edges) == 3:
                    halfedge = he
                    break

        commands = [
            4, 3, 4, 2, 4, 2, 4,  # Get 11 12 17 16
            2, 3, 2, 4, 2, 4,     # Get 15 10
            2, 3, 2, 4, 2, 4,     # Get  8  9
            3, 2, 4, 2, 4,        # Get  4  5
            3, 2, 4, 2, 4,        # Get  0  1
            2, 3, 2, 4, 2, 4,     # Get  2  6
            3, 2, 4, 2, 4,        # Get  3  7
            2, 3, 2, 4, 2, 4,     # Get 14 13
            3, 2, 4, 2, 4         # Get 19 18
        ]
        get_vert_order = [11, 12, 17, 16, 15, 10, 8, 9, 4, 5, 0, 1, 2, 6, 3, 7, 14, 13, 19, 18]
        return Halfedge.get_verts_repeat_n_times(halfedge, commands, 1, get_vert_order, 20)



    @classmethod
    def get_patch(cls, face, isBspline = True ) -> list:

        deg_u = 3
        deg_v = 3
        order_u = deg_u + 1
        order_v = deg_v + 1

        nb_verts = cls.get_neighbor_verts(face)

        bezier_coefs = Helper.apply_mask_on_neighbor_verts(cls.masks[cls.name], nb_verts)
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