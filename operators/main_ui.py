from .highlighter import Highlighter
from .polyhedral_splines import PolyhedralSplines
from .ui_color import COLOR_OT_TemplateOperator
import bpy


class MainUI(bpy.types.Panel):
    bl_label = "Polyhedral Splines"
    bl_category = "Polyhedral Splines"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.operator(operator=Highlighter.bl_idname, text="Inspect Mesh")
        layout.operator(operator=PolyhedralSplines.bl_idname, text="Generate Bspline Patches")
        layout.operator(operator=COLOR_OT_TemplateOperator.bl_idname, text="Patch Color")
