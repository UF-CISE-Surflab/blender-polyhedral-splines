from .highlighter import Highlighter
from .semi_structure_spline import SemiStructureSpline
from .ui_color import COLOR_OT_TemplateOperator
import bpy


class MainUI(bpy.types.Panel):
    bl_label = "Semi-structured Spline"
    bl_category = "Semi-structured Spline"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.operator(operator=Highlighter.bl_idname, text="Inspect Mesh")
        layout.operator(operator=SemiStructureSpline.bl_idname, text="Generate Bspline Patches")
        layout.operator(operator=COLOR_OT_TemplateOperator.bl_idname, text="Patch Color")
