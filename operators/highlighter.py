import bpy
import bmesh
from .polyhedral_splines import PolyhedralSplines
from .color import Color


class Highlighter(bpy.types.Operator):
    bl_label = "highlighter"
    bl_idname = "object.highlighter"

    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")

    def execute(self, context):
        self.__highlight__(context)
        return {'FINISHED'}

    def __highlight__(self, context):

        # control_mesh is the input obj file
        obj = context.view_layer.objects.active
        control_mesh = obj.data

        bpy.data.materials.new(name="Red")
        mat = bpy.data.materials['Red']
        mat.diffuse_color = Color.red
        if len(control_mesh.materials) == 0:
            control_mesh.materials.append(bpy.data.materials[0])
        control_mesh.materials.append(mat)

        bm = bmesh.new()
        bm.from_mesh(control_mesh)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # Highlight faces that are not supported

        Highlighter.mark_unsupported_structure(bm,
                                               PolyhedralSplines.face_based_patch_constructors,
                                               PolyhedralSplines.vert_based_patch_constructors)

        show_message_box("The faces highlighted as RED represent the "
                         + "mesh configuration is not supported by the "
                         + "algorithms (will leave holes on spline surface)", "WARNING", 'ERROR')

        # Finish up, write the bmesh back to the mesh
        if control_mesh.is_editmode:
            bmesh.update_edit_mesh(control_mesh)
        else:
            bm.to_mesh(control_mesh)
            control_mesh.update()

    @classmethod
    def inspect_single_vert(cls, vert_based_patch_constructors, vert):
        """ Return true if vert matches on of the patch structure in the list
        """
        for vpc in vert_based_patch_constructors:
            if vpc.is_same_type(vert):
                return True
        return False

    @classmethod
    def inspect_single_face(cls, face_based_patch_constructors, face):
        """ Return true if face matches on of the patch structure in the list
        """
        for fpc in face_based_patch_constructors:
            if fpc.is_same_type(face):
                return True
        return False

    @classmethod
    def inspect_faces(cls, bmesh, face_based_patch_constructors):
        """ Mark face matches any patch structure as gray
        """
        for f in bmesh.faces:
            if cls.inspect_single_face(face_based_patch_constructors, f):
                f.material_index = 0

    @classmethod
    def inspect_verts(cls, bmesh, vert_based_patch_constructors):
        """ Mark face matches any patch structure as gray
        """
        for v in bmesh.verts:
            if cls.inspect_single_vert(vert_based_patch_constructors, v):
                for vf in v.link_faces:
                    vf.material_index = 0

    @classmethod
    def mark_unsupported_structure(cls,
                                   bmesh,
                                   face_based_patch_constructors,
                                   vert_based_patch_constructors):
        """ Change the color of face
        """
        for f in bmesh.faces:
            f.material_index = 1
        cls.inspect_faces(bmesh, face_based_patch_constructors)
        cls.inspect_verts(bmesh, vert_based_patch_constructors)

    @classmethod
    def highlight_faces_around_vert(vert, color):
        pass


def show_message_box(message="", title="Message Box", icon="INFO"):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
