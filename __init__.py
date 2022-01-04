import bpy

from .operators.polyhedral_splines import PolyhedralSplines
from .operators.highlighter import Highlighter
from .operators.main_ui import MainUI
from .operators.ui_helper import ToggleFaces, ToggleSurfPatchCollection
from .operators.ui_color import COLOR_OT_TemplateOperator

bl_info = {
    "name": "polyhedral_splines",
    "description": "An interactive spline generation addon",
    "version": (1, 0, 0),
    "blender": (2, 80, 2),
    "category": "Modeling"
}

classes = (
    PolyhedralSplines,
    Highlighter,
    ToggleFaces,
    ToggleSurfPatchCollection,
    MainUI,
    COLOR_OT_TemplateOperator
)

register, unregister = bpy.utils.register_classes_factory(classes)
