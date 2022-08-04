from dataclasses import dataclass

from .patch import BezierPatch, BsplinePatch
from .extraordinary_patch_constructor import ExtraordinaryPatchConstructor
from .n_gon_patch_constructor import NGonPatchConstructor
from .polar_patch_constructor import PolarPatchConstructor
from .reg_patch_constructor import RegPatchConstructor
from .t0_patch_constructor import T0PatchConstructor
from .t1_patch_constructor import T1PatchConstructor
from .t2_patch_constructor import T2PatchConstructor
from .two_triangles_two_quads_patch_constructor import TwoTrianglesTwoQuadsPatchConstructor

@dataclass
class PatchWrapper:
    patch: BsplinePatch | BezierPatch = None
    isBSpline = False
    source = None   #The source vert/face the patch is based on
    neighbors = []

    def __init__(self, patch, isBSpline, source, neighbors):
        self.patch = patch
        self.isBSpline = isBSpline
        self.source = source
        self.neighbors = neighbors

class PatchHelper:
    # The algorithm using vert as center
    vert_based_patch_constructors: list = [
        RegPatchConstructor,
        ExtraordinaryPatchConstructor,
        PolarPatchConstructor,
        TwoTrianglesTwoQuadsPatchConstructor
    ]
    # The algorithm using face as center
    face_based_patch_constructors: list = [
        T0PatchConstructor,
        T1PatchConstructor,
        T2PatchConstructor,
        NGonPatchConstructor
    ]

    @staticmethod
    def getPatches(bMesh, isBSpline = True) -> list[PatchWrapper]:
        patchWrappers = []

        vertPatches = PatchHelper.getVertPatches(bMesh, isBSpline)
        facePatches = PatchHelper.getFacePatches(bMesh, isBSpline)

        patchWrappers.extend(vertPatches)
        patchWrappers.extend(facePatches)

        return patchWrappers

    @staticmethod 
    def getVertPatches(bMesh, isBSpline = True) -> list[PatchWrapper]:
        bsplinePatches = []
        # Iterate through each vert of the mesh
        for v in bMesh.verts:
            # Iterate throgh different type of patch constructors
            for pc in PatchHelper.vert_based_patch_constructors:
                if pc.is_same_type(v):
                    patch: BsplinePatch = pc.get_patch(v, isBSpline)
                    neighborVerts: list = pc.get_neighbor_verts(v)
                    patchWrapper = PatchWrapper(patch, isBSpline, v, neighborVerts)
                    bsplinePatches.append(patchWrapper)
        return bsplinePatches

    @staticmethod
    def getFacePatches(bMesh, isBSpline = True) -> list[PatchWrapper]:
        bsplinePatches = []
        # Iterate through each face of the mesh
        for f in bMesh.faces:
            # Iterate throgh different type of patch constructors
            for pc in PatchHelper.face_based_patch_constructors:
                if pc.is_same_type(f):
                    patch: BsplinePatch = pc.get_patch(f, isBSpline)
                    neighborVerts: list = pc.get_neighbor_verts(f)
                    patchWrapper = PatchWrapper(patch, isBSpline, f, neighborVerts)
                    bsplinePatches.append(patchWrapper)
        return bsplinePatches