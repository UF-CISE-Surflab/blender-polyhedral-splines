import bpy
import os

from .color import Color
from .reg_patch_constructor import RegPatchConstructor
from .extraordinary_patch_constructor import ExtraordinaryPatchConstructor
from .t0_patch_constructor import T0PatchConstructor
from .t1_patch_constructor import T1PatchConstructor
from .t2_patch_constructor import T2PatchConstructor
from .n_gon_patch_constructor import NGonPatchConstructor
from .polar_patch_constructor import PolarPatchConstructor
from .two_triangles_two_quads_patch_constructor import TwoTrianglesTwoQuadsPatchConstructor


class COLOR_OT_TemplateOperator(bpy.types.Operator):

    dir = os.getcwdb()
    bl_label = "Patch Colors"
    bl_idname = "wm.template_operator"
    config_names = ["Extraordinary", "Polar", "Regular", "T0", "T1", "T2", "n-gon", "twoTQ"]
    text = "Select a color"
    options = [
        ('OPTIONGR', "Gray", "Add gray color"),
        ('OPTIONG', "Green", "Add green color"),
        ('OPTIONL', "Lime", "Add gold color"),
        ('OPTIONC', "Cyan", "Add cyan color"),
        ('OPTIONY', "Yellow", "Add yellow color"),
        ('OPTIONB', "Blue", "Add blue color"),
        ('OPTIONO', "Orange", "Add orange color"),
        ('OPTIONP', "Pink", "Add pink color")
    ]

    extra_enum: bpy.props.EnumProperty(name=config_names[0], description=text, items=options)
    polar_enum: bpy.props.EnumProperty(name=config_names[1], description=text, items=options)
    reg_enum: bpy.props.EnumProperty(name=config_names[2], description=text, items=options)
    T0_enum: bpy.props.EnumProperty(name=config_names[3], description=text, items=options)
    T1_enum: bpy.props.EnumProperty(name=config_names[4], description=text, items=options)
    T2_enum: bpy.props.EnumProperty(name=config_names[5], description=text, items=options)
    nGon_enum: bpy.props.EnumProperty(name=config_names[6], description=text, items=options)
    twottwoq_enum: bpy.props.EnumProperty(name=config_names[7], description=text, items=options)

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "extra_enum")
        layout.prop(self, "polar_enum")
        layout.prop(self, "reg_enum")
        layout.prop(self, "T0_enum")
        layout.prop(self, "T1_enum")
        layout.prop(self, "T2_enum")
        layout.prop(self, "nGon_enum")
        layout.prop(self, "twottwoq_enum")

    def execute(self, context):
        matEOP = bpy.data.materials.get(ExtraordinaryPatchConstructor.name)
        matPolar = bpy.data.materials.get(PolarPatchConstructor.name)
        matReg = bpy.data.materials.get(RegPatchConstructor.name)
        matTO = bpy.data.materials.get(T0PatchConstructor.name)
        matT1 = bpy.data.materials.get(T1PatchConstructor.name)
        matT2 = bpy.data.materials.get(T2PatchConstructor.name)
        matNGon = bpy.data.materials.get(NGonPatchConstructor.name)
        matTTTQ = bpy.data.materials.get(TwoTrianglesTwoQuadsPatchConstructor.name)

        mats = [matEOP, matPolar, matReg, matTO, matT1, matT2, matNGon, matTTTQ]
        mats_enum = [self.extra_enum,
                     self.polar_enum,
                     self.reg_enum,
                     self.T0_enum,
                     self.T1_enum,
                     self.T2_enum,
                     self.nGon_enum,
                     self.twottwoq_enum]

        for i in range(len(mats)):
            if mats[i] is None:
                continue
            elif mats_enum[i] == 'OPTIONGR':
                mats[i].diffuse_color = Color.default
            elif mats_enum[i] == 'OPTIONG':
                mats[i].diffuse_color = Color.green
            elif mats_enum[i] == 'OPTIONL':
                mats[i].diffuse_color = Color.lime
            elif mats_enum[i] == 'OPTIONC':
                mats[i].diffuse_color = Color.cyan
            elif mats_enum[i] == 'OPTIONY':
                mats[i].diffuse_color = Color.yellow
            elif mats_enum[i] == 'OPTIONB':
                mats[i].diffuse_color = Color.blue
            elif mats_enum[i] == 'OPTIONO':
                mats[i].diffuse_color = Color.orange
            elif mats_enum[i] == 'OPTIONP':
                mats[i].diffuse_color = Color.pink

        return {'FINISHED'}
