from .reg_patch_constructor import RegPatchConstructor
from .t0_patch_constructor import T0PatchConstructor
from .t1_patch_constructor import T1PatchConstructor
from .t2_patch_constructor import T2PatchConstructor
from .n_gon_patch_constructor import NGonPatchConstructor
from .polar_patch_constructor import PolarPatchConstructor
from .extraordinary_patch_constructor import ExtraordinaryPatchConstructor
from .two_triangles_two_quads_patch_constructor import TwoTrianglesTwoQuadsPatchConstructor

class Algorithms:
    # The algorithm using face as center
    face_patch_constructors: list = [
        T0PatchConstructor,
        T1PatchConstructor,
        T2PatchConstructor,
        NGonPatchConstructor
    ]
    # The algorithm using vert as center
    vert_patch_constructors: list = [
        RegPatchConstructor,
        ExtraordinaryPatchConstructor,
        PolarPatchConstructor,
        TwoTrianglesTwoQuadsPatchConstructor
    ]
