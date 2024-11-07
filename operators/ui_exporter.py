import math

import numpy as np
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from .patch_tracker import PatchTracker
from .patch_helper import PatchHelper
from .bezier_bspline_converter import BezierBsplineConverter


class IGSExporter(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export.igs"
    bl_label = "Export IGS"

    # ExportHelper mixin class uses this
    filename_ext = ".igs"

    filter_glob: StringProperty(
        default="*.igs",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    patch_names = PatchTracker.patch_names # reference

    def menu_func_export(self, context):
        self.layout.operator(IGSExporter.bl_idname, text="IGES (.igs)")

    def execute(self, context):
        self.__write_igs(context, self.filepath)
        return {'FINISHED'}

    # write knots of bb-form in IGS
    def __knots(self, a_Deg1, a_Bbase, a_Ffctr, f, a_PerLine):
        for i in range(a_Deg1):
            if i%a_PerLine == 0 and i != 0:
                f.write("%8dP%7d\n" % (a_Ffctr, a_Bbase))
                a_Bbase+=1
            f.write("0.00000,")

        for i in range(a_Deg1, 2*a_Deg1):
            if i%a_PerLine==0:
                f.write("%8dP%7d\n" % (a_Ffctr, a_Bbase))
                a_Bbase+=1
            f.write("1.00000,")

        j = (2*a_Deg1) % a_PerLine
        if j != 0:
            j = a_PerLine - j
            for i in range(j):
              f.write("        ")

        f.write("%8dP%7d\n" % (a_Ffctr, a_Bbase))

        a_Bbase += 1

        return a_Bbase

    def __write_igs(self, context, filepath):

        patches = []
        for patch_name in self.patch_names:
            spline = context.scene.objects[patch_name].data.splines[0]
            patch = [list(pt.co)[:3] for pt in list(spline.points)]
            np_patch = BezierBsplineConverter.bspline_to_bezier(np.array(patch), spline.order_v-1, spline.order_u-1)
            np_patch.resize((spline.order_v, spline.order_u, 3))
            patches.append({"coefs": np_patch.tolist(), "deg_u": spline.order_v-1,"deg_v": spline.order_u-1})

        f = open(filepath, 'w', encoding='utf-8')

        # S and G
        f.write("copyright(c)Jorg Peters [jorg.peters@gmail.com]                         S      1\n")
        f.write(",,;                                                                     G      1\n")

        flen = [0 for _ in range(4)]
        t_Bbctr, t_Ffctr = 1, 1

        for patch in patches:
            t_DegU = patch["deg_u"]
            t_DegV = patch["deg_v"]
            k = (t_DegU + 1) + (t_DegV + 1)
            k1 = math.ceil(k / 8) # knots; changed
            w = (t_DegU + 1) * (t_DegV + 1)
            w1 = math.ceil(w / 8) # weights; changed

            # deg-line, knots, weights, xyz location, param
            rows = (1 + 2 * k1 + w1 + w + 1) # size of one block

            f.write("     128%8d       0       1       0       0       0        00000000D%7d\n" % (t_Bbctr, t_Ffctr))
            f.write("     128%8d       8      %d       2                NurbSurf       0D%7d\n" % (0, rows, t_Ffctr+1))

            t_Bbctr += rows
            t_Ffctr += 2

        flen[0] = 1
        flen[1] = 10

        # data entries
        t_Ffctr, t_Bbctr = 1, 1
        for patch in patches:
            t_DegU = patch["deg_u"]
            t_DegV = patch["deg_v"]

            # HEADER
            f.write("128,%7d,%7d,%7d,%7d,0,0,1,0,0,%26dP%7d\n" % (t_DegV, t_DegU, t_DegV, t_DegU, t_Ffctr, t_Bbctr))
            t_Bbctr += 1

            # KNOTS
            w = (t_DegU + 1) * (t_DegV + 1);
            t_Bbctr = self.__knots(t_DegV + 1, t_Bbctr, t_Ffctr, f, 8);
            t_Bbctr = self.__knots(t_DegU + 1, t_Bbctr, t_Ffctr, f, 8);

            cols, col = 8, 0
            for i in range(t_DegU + 1):
                for j in range(t_DegV + 1):
                    if col % cols == 0 and col != 0:
                        f.write("%8dP%7d\n" % (t_Ffctr,t_Bbctr))
                        t_Bbctr += 1
                    h = 1
                    f.write("%7.5f," % h)
                    col += 1

            # finish line
            col = col % cols
            if col != 0:
                col = cols-col
                for i in range(col):
                    f.write("        ")

            f.write("%8dP%7d\n" % (t_Ffctr, t_Bbctr))
            t_Bbctr += 1

            # the XYZ coordinates
            for i in range(t_DegU + 1):
                for j in range(t_DegV + 1):
                    f.write("%20e,%20e,%20e,%9dP%7d\n" % (patch["coefs"][i][j][0], patch["coefs"][i][j][1], patch["coefs"][i][j][2], t_Ffctr,t_Bbctr))
                    t_Bbctr += 1

            f.write("0.00000,1.00000,0.00000,1.00000;%40dP%7d\n" % (t_Ffctr, t_Bbctr))
            t_Bbctr += 1
            t_Ffctr += 2

        flen[2] = t_Ffctr
        flen[3] = t_Bbctr

        # structure of file
        f.write("S%7dG%7dD%7dP%7d%40dT%7d\n" % (flen[0], flen[1], flen[2] - 1, flen[3] - 1, 1, 1))
        f.close()
