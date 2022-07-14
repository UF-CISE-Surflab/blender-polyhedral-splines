from .patch_constructor import PatchConstructor
from .halfedge import Halfedge
from .bezier_bspline_converter import BezierBsplineConverter
from .patch import BsplinePatch
from .helper import Helper
from .csv_reader import Reader


class NGonPatchConstructor(PatchConstructor):
    name: str = "n-gon"
    mask_file_names = ["ngonSct3", "ngonSct5", "ngonSct6", "ngonSct7", "ngonSct8"]
    masks = Reader.csv_to_masks(mask_file_names)

    @classmethod
    def is_same_type(cls, face) -> bool:
        # The face should have 3 5 6 7 8 edges
        face_valence = Helper.edges_number_of_face(face)
        if face_valence < 3 or face_valence > 8 or face_valence == 4:
            return False

        # All the vertices of central face should be 4-valent
        for he in face.loops:
            if len(he.vert.link_edges) != 4:
                return False

        # get one ring face surround triangle
        neighbor_faces = Helper.init_neighbor_faces(face)

        # The 2*n faces surround central face should all be quad
        if not Helper.are_faces_all_quad(neighbor_faces):
            return False

        print("n-gon found!")

        return True

    @classmethod
    def get_neighbor_verts(cls, face) -> list:
        """
        Return the neighbor verts (including central vert). The bezier coef.
        can be obtained by multiplying the matrix of neighbor vert with mask.

        Here we take 3-gon as example:

                   8
                /    \
              9 - 11- 10
             /   / \   \
            2 - 3 - 7 - 5
            |   |   |   |
            0 - 1 - 6 - 4

        """
        # Get valent of face
        face_valence = Helper.edges_number_of_face(face)

        # Get the halfedge 3->7
        halfedge = face.loops[0]

        # Command for getting 4 vertices in one corner
        one_corner_commands = [3, 1, 4, 3, 4, 2, 4, 2, 4, 2, 2, 3, 2, 3, 1]

        # Repeat commands n times
        repeat_times = face_valence

        # Order for getting all vertices from all wings
        get_vert_order = []
        for i in range(face_valence):
            k = 4 * i  # get 4 vertices in each corner
            get_vert_order += [3 + k, 1 + k, 0 + k, 2 + k]

        # How many vertices we are going to obtain
        num_verts_reserved = face_valence * 4

        # Get vertices corner by corner (0 1 2 3 is a corner)
        return Halfedge.get_verts_repeat_n_times(halfedge,
                                                 one_corner_commands,
                                                 repeat_times,
                                                 get_vert_order,
                                                 num_verts_reserved)

    @classmethod
    def get_patch(cls, face) -> list:
        deg_u = 3
        deg_v = 3
        nb_verts = cls.get_neighbor_verts(face)

        # Get valent of vert and apply the corresponding mask
        valence = Helper.edges_number_of_face(face)
        bezier_coefs = Helper.apply_mask_on_neighbor_verts(cls.masks["ngonSct{}".format(valence)], nb_verts)
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
