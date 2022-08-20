import bpy
from dataclasses import dataclass


@dataclass
class PatchInfo:
    patch_name: str
    central_obj: bpy.types.MeshVertex
    neighbor_vert: list


class PatchTracker:
    patch_names: set = set() # keeps all the spline object name
    vpatch_LUT: dict = {}  # vert to vert-based patch look up table
    fpatch_LUT: dict = {}  # vert to face-based patch look up table

    @classmethod
    def register_patch(cls, central_obj, neighbor_vert, patch_name):
        cls.patch_names.add(patch_name)
        if type(central_obj).__name__ == 'BMVert':
            for nbv in neighbor_vert:
                if nbv.index not in cls.vpatch_LUT:  # if index is not a key in dict
                    cls.vpatch_LUT[nbv.index] = {"PatchObjNames": [], "CentralVertID": []}
                cls.vpatch_LUT[nbv.index]["PatchObjNames"] = cls.vpatch_LUT[nbv.index]["PatchObjNames"] + [patch_name]
                cls.vpatch_LUT[nbv.index]["CentralVertID"] = \
                    cls.vpatch_LUT[nbv.index]["CentralVertID"] + [central_obj.index]
        elif type(central_obj).__name__ == 'BMFace':
            for nbv in neighbor_vert:
                if nbv.index not in cls.fpatch_LUT:  # if index is not a key in dict
                    cls.fpatch_LUT[nbv.index] = {"PatchObjNames": [], "CentralFaceID": []}
                cls.fpatch_LUT[nbv.index]["PatchObjNames"] = cls.fpatch_LUT[nbv.index]["PatchObjNames"] + [patch_name]
                cls.fpatch_LUT[nbv.index]["CentralFaceID"] = \
                    cls.fpatch_LUT[nbv.index]["CentralFaceID"] + [central_obj.index]
        else:
            print("Input type does not match BMVert or BMFace.")

    @classmethod
    def register_multiple_patches(cls, central_obj, neighbor_vert, patch_names):
        for pn in patch_names:
            cls.register_patch(central_obj, neighbor_vert, pn)

    @classmethod
    def get_central_vert_ID(cls, vert) -> list:
        """ Return the belonging central vert for the input vert
        """
        if vert.index in cls.vpatch_LUT:
            return cls.vpatch_LUT[vert.index].get("CentralVertID")
        else:
            return False

    @classmethod
    def get_central_face_ID(cls, vert) -> list:
        """ Return the belonging central face for the input vert
        """
        if vert.index in cls.fpatch_LUT:
            return cls.fpatch_LUT[vert.index].get("CentralFaceID")
        else:
            return False

    @classmethod
    def get_vert_based_patch_obj_name(cls, vert) -> list:
        """ Return the belonging patch obj name for the input vert
        """
        if vert.index in cls.vpatch_LUT:
            return cls.vpatch_LUT[vert.index].get("PatchObjNames")
        else:
            return False

    @classmethod
    def get_face_based_patch_obj_name(cls, vert) -> list:
        """ Return the belonging patch obj name for the input vert
        """
        if vert.index in cls.fpatch_LUT:
            return cls.fpatch_LUT[vert.index].get("PatchObjNames")
        else:
            return False
