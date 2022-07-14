import numpy as np


class Helper:
    @staticmethod
    def add_a_dimesion_to_vector(vec, val):
        return vec + (val,)

    @staticmethod
    def convert_3d_vector_to_4d_coord(vec, weighting):
        return Helper.add_a_dimesion_to_vector(vec, weighting)

    @staticmethod
    def convert_3d_vectors_to_4d_coords(vecs, weighting):
        return [Helper.convert_3d_vector_to_4d_coord(v, weighting) for v in vecs]

    @staticmethod
    def get_verts_id(verts):
        return [v.index for v in verts]

    @staticmethod
    def convert_verts_from_list_to_matrix(verts):
        mat = ()  # Number by 3(xyz)
        for v in verts:
            mat = mat + (list(v.co),)
        return mat

    @staticmethod
    def split_list(list, numb_of_pieces):
        if numb_of_pieces <= 0:
            print("Cannot split by zero")
            return False
        num_of_element_per_chunk = int(len(list) / numb_of_pieces)
        for i in range(0, len(list), num_of_element_per_chunk):
            yield list[i:i + num_of_element_per_chunk]

    @staticmethod
    def list_to_npmatrices(vlist, u, v):
        xCoefs = np.empty((v,u))
        yCoefs = np.empty((v,u))
        zCoefs = np.empty((v,u))
        for i in range(0, v):
            for j in range(0, u):
                xCoefs[i][j] = vlist[i*u+j][0]
                yCoefs[i][j] = vlist[i*u+j][1]
                zCoefs[i][j] = vlist[i*u+j][2]
        return xCoefs, yCoefs, zCoefs

    @staticmethod
    def convert_verts_from_matrix_to_list(mat) -> list:
        vlist = []
        for row in mat:
            vlist = vlist + [tuple(row)]
        return vlist

    @staticmethod
    def normalize_each_row(mat):
        row_sums = np.array(mat).sum(axis=1)
        return mat / row_sums[:, np.newaxis]

    @staticmethod
    def apply_mask_on_neighbor_verts(mask, nbverts) -> list:
        nbmat = Helper.convert_verts_from_list_to_matrix(nbverts)  # vector
        mask = Helper.normalize_each_row(mask)
        return np.dot(mask, nbmat)

    @staticmethod
    def edges_number_of_face(face) -> int:
        return len(face.verts)

    @staticmethod
    def is_pentagon(face) -> bool:
        if Helper.edges_number_of_face(face) == 5:
            return True
        else:
            return False

    @staticmethod
    def is_quad(face) -> bool:
        if Helper.edges_number_of_face(face) == 4:
            return True
        else:
            return False

    @staticmethod
    def is_triangle(face) -> bool:
        if Helper.edges_number_of_face(face) == 3:
            return True
        else:
            return False

    @staticmethod
    def is_hexagon(face) -> bool:
        if Helper.edges_number_of_face(face) == 6:
            return True
        else:
            return False

    @staticmethod
    def reorder_list(list, order, num_of_elements) -> list:
        """
        Reorder list using input order. The size of output list is equal to
        num_of_elements. The element of output list doesn't in list will be none
        """
        ordered_list = [0] * num_of_elements
        for i in range(len(order)):
            ordered_list[order[i]] = list[i]
        return ordered_list

    @staticmethod
    def init_neighbor_faces(face) -> list:
        """ Get one ring faces of input face
        """
        one_ring_faces = []
        # Get faces around each verts
        for v in face.verts:
            for f in v.link_faces:
                one_ring_faces.append(f)

        # Remove the duplicated faces from list
        one_ring_faces = list(dict.fromkeys(one_ring_faces))
        one_ring_faces.remove(face)

        # Remove centrol face from list
        return one_ring_faces

    @staticmethod
    def are_faces_all_quad(faces) -> list:
        """ Check if faces in the list are all quad
        """
        for f in faces:
            if not Helper.is_quad(f):
                return False
        return True
