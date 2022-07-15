from .highlighter import Highlighter
from .polyhedral_splines import PolyhedralSplines
from .ui_color import COLOR_OT_TemplateOperator
from .moments import Moments
from .ui_helper import ToggleFaces, ToggleSurfPatchCollection
import bpy



class MainUI(bpy.types.Panel):
    bl_label = "Polyhedral Splines"
    bl_category = "Polyhedral Splines"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_info = ""


    def modal(self, context, event):
        if event.type == 'TIMER':
            self.draw(context)

    def draw(self, context):
        layout = self.layout
        layout.operator(operator=Highlighter.bl_idname, text="Inspect Mesh")
        layout.operator(operator=PolyhedralSplines.bl_idname, text="Generate Bspline Patches")
        layout.operator(operator=COLOR_OT_TemplateOperator.bl_idname, text="Patch Color")
        layout.operator(operator=ToggleFaces.bl_idname, text="Toggle Mesh Faces")
        layout.operator(operator=ToggleSurfPatchCollection.bl_idname, text="Toggle SurfPatch Collection")

        layout.label(text="Volume: " + str(Moments.Volume))
        layout.label(text="Center of Mass: " + str(Moments.CoM))
        layout.label(text="Inertia Tensors: ")
        layout.label(text="     X: " + str(Moments.InertiaTens[0]))
        layout.label(text="     Y: " + str(Moments.InertiaTens[1]))
        layout.label(text="     Z: " + str(Moments.InertiaTens[2]))
