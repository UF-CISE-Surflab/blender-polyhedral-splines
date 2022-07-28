import bpy

class SubdivideMesh(bpy.types.Operator):
    bl_label = "Subdivide Mesh"
    bl_idname = "object.subdivide_mesh"
    bl_description = "Applies 1 iteration of Catmull-Clark subdivision. Use if mesh is not fully supported by polyhedral spline generation"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        selected = context.selected_objects

        if obj in selected and obj.mode == "OBJECT" and obj.type == "MESH":
            return True
        return False

    def execute(self, context):
        obj = context.active_object

        modifierName = "Subdivision"
        subdivMod = obj.modifiers.new(modifierName, "SUBSURF")
        subdivMod.levels = 1
        subdivMod.subdivision_type = "CATMULL_CLARK"

        bpy.ops.object.modifier_apply(modifier=modifierName)
        
        return {'FINISHED'}