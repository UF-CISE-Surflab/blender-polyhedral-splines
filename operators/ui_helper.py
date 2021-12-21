import bpy


bl_info = {
    "name": "Toggle Faces",
    "blender": (2, 80, 0),
    "category": "Object",
    "description": "Adds a button to the view tab to toggle visibilty \
    of mesh faces when in edit mode"
}


class ToggleFaces(bpy.types.Operator):
    """Toggle Faces"""
    bl_idname = "view.toggle_faces"
    bl_label = "Toggle Mesh Faces"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.show_faces = not space.overlay.show_faces
                        break
        return {'FINISHED'}

    def menu_func(self, context):
        self.layout.operator(ToggleFaces.bl_idname)

    bpy.types.VIEW3D_MT_view.append(menu_func)


class ToggleSurfPatchCollection(bpy.types.Operator):
    """Toggle SurfPatch Collection"""
    bl_idname = "view.toggle_surfpatch_collection"
    bl_label = "Toggle SurfPatch Collection"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for area in bpy.context.screen.areas:
            if area.type == 'OUTLINER':
                for space in area.spaces:
                    if space.type == 'OUTLINER':
                        space.use_filter_object_others = not space.use_filter_object_others
                        break
        return {'FINISHED'}

    def menu_func(self, context):
        self.layout.operator(ToggleSurfPatchCollection.bl_idname)

    bpy.types.VIEW3D_MT_view.append(menu_func)
