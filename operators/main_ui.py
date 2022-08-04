from .subdivide_mesh import SubdivideMesh
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

        calculationBox = layout.box()
        calculationBox.label(text="Calculations")
        calculationBox.operator(operator=PolyhedralSplines.bl_idname, text="Generate Bspline Patches")
        calculationBox.operator(operator=SubdivideMesh.bl_idname, text="Subdivide Mesh")
        calculationBox.operator(operator=Moments.bl_idname, text="Calculate Moments")

        viewBox = layout.box()
        viewBox.label(text="View")
        viewBox.operator(operator=Highlighter.bl_idname, text="Inspect Mesh")
        viewBox.operator(operator=COLOR_OT_TemplateOperator.bl_idname, text="Patch Color")
        viewBox.operator(operator=ToggleFaces.bl_idname, text="Toggle Mesh Faces")
        viewBox.operator(operator=ToggleSurfPatchCollection.bl_idname, text="Toggle SurfPatch Collection")

        valuesBox = layout.box()
        valuesBox.label(text="Values")
        valuesBox.label(text="Volume: " + str(Moments.Volume))
        valuesBox.label(text="Center of Mass: " + str(Moments.CoM))
        valuesBox.label(text="Inertia Tensors: ")
        valuesBox.label(text="     X: " + str(Moments.InertiaTens[0]))
        valuesBox.label(text="     Y: " + str(Moments.InertiaTens[1]))
        valuesBox.label(text="     Z: " + str(Moments.InertiaTens[2]))
