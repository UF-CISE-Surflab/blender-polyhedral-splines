from .patch import BezierPatch
from .patch_helper import PatchHelper
from .helper import Helper
from .bivariateBBFunctions import bbFunctions
from random import randint
#from unittest.loader import VALID_MODULE_NAME
import bpy
import bmesh
import time
import math
from math import factorial
import numpy as np
import mathutils
from bpy.app.handlers import persistent


class Moments(bpy.types.Operator):
    bl_label = "Calculate Moments"
    bl_idname = "object.moments"
    bl_description = "Calculates moment inertia values for the active object. Values are displayed on the bottom of the panel"
    
    Volume = 0                       # display volume in UI
    CoM = [[], [], []]                        # put point at center of mass
    InertiaTens = [[[],[],[]],[[],[],[]],[[],[],[]]]        # and arrows at each direction of inertia tensor

    CurrentSelection: None              #Type: Blender Object
    ControlMeshNames: list[str] = []
    CenterOfMassObj = None              #Type: Blender Object
    ArrowObjs = []                      #Type: List of Blender Objects

    def __init__(self):
        print("Start")

    def __del__(self):
        print("End")

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        selected = context.selected_objects

        if obj in selected and obj.name in Moments.ControlMeshNames:
            return True
        return False

    # TODO: variable size based on madnitude of vector                                                                                                
    # calculate rotation from vector
    def execute(self, context):
        Moments.CurrentSelection = context.view_layer.objects.active
        Moments.cleanupObjects()

        Moments.calculateMoments(context, Moments.CurrentSelection.name)
        Moments.createCenterOfMass(context, Moments.CoM)
        Moments.createArrows(context)

        return {'FINISHED'}

    def cleanupObjects():
        #Delete arrow objects
        for arrow in Moments.ArrowObjs:
            objs = bpy.data.objects
            objs.remove(objs[arrow.name])
        Moments.ArrowObjs.clear()

        #Delete old center of mass object
        if Moments.CenterOfMassObj is not None:
            objs = bpy.data.objects
            objs.remove(objs[Moments.CenterOfMassObj.name])
            Moments.CenterOfMassObj = None

    def createArrows(context):
        Moments.createArrow(context, np.linalg.norm(Moments.InertiaTens[0])/5, (1, 0, 0, 1), Moments.InertiaTens[0])     #context, location, size, color(RGBA), rotation
        Moments.createArrow(context, np.linalg.norm(Moments.InertiaTens[1])/5, (0, 1, 0, 1), Moments.InertiaTens[1])     #context, location, size, color(RGBA), rotation
        Moments.createArrow(context, np.linalg.norm(Moments.InertiaTens[2])/5, (0, 0, 1, 1), Moments.InertiaTens[2])     #context, location, size, color(RGBA), rotation

    def calculateMoments(context, controlMeshName):
        mesh = Moments.CurrentSelection.data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        if controlMeshName not in Moments.ControlMeshNames:
            Moments.ControlMeshNames.append(controlMeshName)

        sourceObj = bpy.context.scene.objects[controlMeshName]

        runningSum = 0.000
        centerOfMass = np.zeros(3)
        momentOfInertia = np.zeros((3,3))

        #Center of mass calculation
        comPatches = PatchHelper.getPatches(bm, False)
        for patch in comPatches:
            bezierPatch: BezierPatch = patch.patch
            for bp in bezierPatch.bezier_coefs:
                xCoefs, yCoefs, zCoefs = Helper.list_to_npmatrices(bp, bezierPatch.order_u, bezierPatch.order_v)
                #TODO: allMoments incorrectly states what is being calculating, only the first two moments are being calculating
                pieceVol, pieceCOM = bbFunctions.allMoments(xCoefs, yCoefs, zCoefs)
                runningSum = runningSum + pieceVol
                centerOfMass = centerOfMass + pieceCOM
        #Center of Mass needs to be normalized by volume
        centerOfMass = centerOfMass / runningSum
        centerOfMass = centerOfMass + np.array(sourceObj.location)

        #Moment of Inertia calculation needs to be done after calculating center of mass
        inertiaPatches = PatchHelper.getPatches(bm, False)      #Can't reuse the patches up there for some reason, so grab a new set here for intertia calculations
        for patch in inertiaPatches:
            bezierPatch: BezierPatch = patch.patch
            for bp in bezierPatch.bezier_coefs:
                xCoefs, yCoefs, zCoefs = Helper.list_to_npmatrices(bp, bezierPatch.order_u, bezierPatch.order_v)
                pieceMOI = bbFunctions.secondMoment(xCoefs, yCoefs, zCoefs, offset=centerOfMass)
                momentOfInertia = momentOfInertia + pieceMOI

        #To display the moment of inertia, the eigen values and eigenvectors of the matrix needs to be calculated                
        eigenVectors = np.linalg.eig(momentOfInertia)
        eigenScalers = np.abs(eigenVectors[0])
        eigenScalers = eigenScalers / np.amax(eigenScalers) 
        momentOfInertia = eigenVectors[1]
        for i in range(0,3):
            momentOfInertia[:,i] = momentOfInertia[:,i] * eigenScalers[i]
        print(f"TOTAL SUM = {runningSum}\nCENTER OF MASS = {centerOfMass}\nMOMENT OF INTERTIA = {momentOfInertia}\nEIGENVALUES = {eigenVectors}")
        momentOfInertia = eigenVectors[1]
        
        Moments.Volume = runningSum
        Moments.CoM = np.around(centerOfMass, decimals=3).tolist()
        momentOfInertia = np.around(momentOfInertia, decimals=3)
        for i in range(0, 3):
            for j in range(0,3):
                Moments.InertiaTens[i][j] = momentOfInertia[j,i]
        
    def createCenterOfMass(context, CoM):
        mesh = bpy.data.meshes.new("Point")
        obj = bpy.data.objects.new("CenterOfMass", mesh)

        obj.location = CoM
        bpy.context.collection.objects.link(obj)

        # Construct the bmesh sphere and assign it to the blender mesh.
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=0.1)
        bm.to_mesh(mesh)
        bm.free()

        Moments.CenterOfMassObj = obj


    i = 0
    def createArrow(context, size, color, rotation):

        verts = [(0*2, 0.0221108*2, -2.38419e-07*2), (1.50453e-09*2, 6.7131e-09*2, 2.2895+size),
                 (0.00431361*2, 0.021686*2, -2.38419e-07*2), (0.00846145*2, 0.0204277*2, -2.38419e-07*2),
                 (0.0122841*2, 0.0183845*2, -2.38419e-07*2), (0.0156347*2, 0.0156347*2, -2.38419e-07*2),
                 (0.0183845*2, 0.0122841*2, -2.38419e-07*2), (0.0204277*2, 0.00846145*2, -2.38419e-07*2),
                 (0.021686*2, 0.00431361*2, -2.38419e-07*2), (0.0221108*2, 1.66932e-09*2, -2.38419e-07*2),
                 (0.021686*2, -0.00431361*2, -2.38419e-07*2), (0.0204277*2, -0.00846145*2, -2.38419e-07*2),
                 (0.0183845*2, -0.0122841*2, -2.38419e-07*2), (0.0156347*2, -0.0156347*2, -2.38419e-07*2),
                 (0.0122841*2, -0.0183845*2, -2.38419e-07*2), (0.00846145*2, -0.0204277*2, -2.38419e-07*2),
                 (0.0043136*2, -0.021686*2, -2.38419e-07*2), (-7.20462e-09*2, -0.0221108*2, -2.38419e-07*2),
                 (-0.00431362*2, -0.021686*2, -2.38419e-07*2), (-0.00846146*2, -0.0204277*2, -2.38419e-07*2),
                 (-0.0122841*2, -0.0183845*2, -2.38419e-07*2), (-0.0156347*2, -0.0156347*2, -2.38419e-07*2),
                 (-0.0183845*2, -0.0122841*2, -2.38419e-07*2), (-0.0204278*2, -0.00846143*2, -2.38419e-07*2),
                 (-0.021686*2, -0.00431359*2, -2.38419e-07*2), (-0.0221108*2, 2.13502e-08*2, -2.38419e-07*2),
                 (-0.021686*2, 0.00431363*2, -2.38419e-07*2), (-0.0204277*2, 0.00846147*2, -2.38419e-07*2),
                 (-0.0183845*2, 0.0122841*2, -2.38419e-07*2), (-0.0156347*2, 0.0156347*2, -2.38419e-07*2),
                 (-0.0122841*2, 0.0183845*2, -2.38419e-07*2), (-0.00846142*2, 0.0204278*2, -2.38419e-07*2),
                 (-0.00431358*2, 0.021686*2, -2.38419e-07*2), (0*2, 0.0221108*2, 1.97731+size),
                 (0.00431361*2, 0.021686*2, 1.97731+size), (0.00846145*2, 0.0204277*2, 1.97731+size),
                 (0.0122841*2, 0.0183845*2, 1.97731+size), (0.0156347*2, 0.0156347*2, 1.97731+size),
                 (0.0183845*2, 0.0122841*2, 1.97731+size), (0.0204277*2, 0.00846145*2, 1.97731+size),
                 (0.021686*2, 0.00431361*2, 1.97731+size), (0.0221108*2, 1.66932e-09*2, 1.97731+size),
                 (0.021686*2, -0.00431361*2, 1.97731+size), (0.0204277*2, -0.00846145*2, 1.97731+size),
                 (0.0183845*2, -0.0122841*2, 1.97731+size), (0.0156347*2, -0.0156347*2, 1.97731+size),
                 (0.0122841*2, -0.0183845*2, 1.97731+size), (0.00846145*2, -0.0204277*2, 1.97731+size),
                 (0.0043136*2, -0.021686*2, 1.97731+size), (-7.20462e-09*2, -0.0221108*2, 1.97731+size),
                 (-0.00431362*2, -0.021686*2, 1.97731+size), (-0.00846146*2, -0.0204277*2, 1.97731+size),
                 (-0.0122841*2, -0.0183845*2, 1.97731+size), (-0.0156347*2, -0.0156347*2, 1.97731+size),
                 (-0.0183845*2, -0.0122841*2, 1.97731+size), (-0.0204278*2, -0.00846143*2, 1.97731+size),
                 (-0.021686*2, -0.00431359*2, 1.97731+size), (-0.0221108*2, 2.13502e-08*2, 1.97731+size),
                 (-0.021686*2, 0.00431363*2, 1.97731+size), (-0.0204277*2, 0.00846147*2, 1.97731+size),
                 (-0.0183845*2, 0.0122841*2, 1.97731+size), (-0.0156347*2, 0.0156347*2, 1.97731+size),
                 (-0.0122841*2, 0.0183845*2, 1.97731+size), (-0.00846142*2, 0.0204278*2, 1.97731+size),
                 (-0.00431358*2, 0.021686*2, 1.97731+size), (-1.14042e-08*2, 0.142162*2, 1.98456+size),
                 (0.0277344*2, 0.13943*2, 1.98456+size), (0.0544029*2, 0.13134*2, 1.98456+size),
                 (0.0789808*2, 0.118203*2, 1.98456+size), (0.100523*2, 0.100523*2, 1.98456+size),
                 (0.118203*2, 0.0789808*2, 1.98456+size), (0.13134*2, 0.0544029*2, 1.98456+size),
                 (0.13943*2, 0.0277343*2, 1.98456+size), (0.142162*2, -2.70575e-08*2, 1.98456+size),
                 (0.13943*2, -0.0277344*2, 1.98456+size), (0.13134*2, -0.0544029*2, 1.98456+size),
                 (0.118203*2, -0.0789808*2, 1.98456+size), (0.100523*2, -0.100524*2, 1.98456+size),
                 (0.0789808*2, -0.118203*2, 1.98456+size), (0.0544029*2, -0.13134*2, 1.98456+size),
                 (0.0277343*2, -0.13943*2, 1.98456+size), (-5.77264e-08*2, -0.142162*2, 1.98456+size),
                 (-0.0277344*2, -0.13943*2, 1.98456+size), (-0.054403*2, -0.13134*2, 1.98456+size),
                 (-0.0789809*2, -0.118203*2, 1.98456+size), (-0.100524*2, -0.100523*2, 1.98456+size),
                 (-0.118203*2, -0.0789808*2, 1.98456+size), (-0.13134*2, -0.0544029*2, 1.98456+size),
                 (-0.13943*2, -0.0277343*2, 1.98456+size), (-0.142162*2, 9.94808e-08*2, 1.98456+size),
                 (-0.13943*2, 0.0277345*2, 1.98456+size), (-0.13134*2, 0.054403*2, 1.98456+size),
                 (-0.118203*2, 0.0789809*2, 1.98456+size), (-0.100523*2, 0.100524*2, 1.98456+size),
                 (-0.0789807*2, 0.118203*2, 1.98456+size), (-0.0544027*2, 0.13134*2, 1.98456+size),
                 (-0.0277342*2, 0.13943*2, 1.98456+size), ]
        edges = [(0, 2), (65, 1), (34, 2), (2, 3), (35, 3), (3, 4), (36, 4), (4, 5), (37, 5), (5, 6),
                 (38, 6), (6, 7), (39, 7), (7, 8), (40, 8), (8, 9), (41, 9), (9, 10), (42, 10), (10, 11),
                 (43, 11), (11, 12), (44, 12), (12, 13), (45, 13), (13, 14), (46, 14), (14, 15), (47, 15), (15, 16),
                 (48, 16), (16, 17), (49, 17), (17, 18), (50, 18), (18, 19), (51, 19), (19, 20), (52, 20), (20, 21),
                 (53, 21), (21, 22), (54, 22), (22, 23), (55, 23), (23, 24), (56, 24), (24, 25), (57, 25), (25, 26),
                 (58, 26), (26, 27), (59, 27), (27, 28), (60, 28), (28, 29), (61, 29), (29, 30), (62, 30), (30, 31),
                 (63, 31), (31, 32), (64, 32), (32, 0), (0, 33), (66, 34), (67, 35), (68, 36), (69, 37), (70, 38),
                 (71, 39), (72, 40), (73, 41), (74, 42), (75, 43), (76, 44), (77, 45), (78, 46), (79, 47), (80, 48),
                 (81, 49), (82, 50), (83, 51), (84, 52), (85, 53), (86, 54), (87, 55), (88, 56), (89, 57), (90, 58),
                 (91, 59), (92, 60), (93, 61), (94, 62), (95, 63), (96, 64), (64, 33), (63, 64), (62, 63), (61, 62),
                 (60, 61), (59, 60), (58, 59), (57, 58), (56, 57), (55, 56), (54, 55), (53, 54), (52, 53), (51, 52),
                 (50, 51), (49, 50), (48, 49), (47, 48), (46, 47), (45, 46), (44, 45), (43, 44), (42, 43), (41, 42),
                 (40, 41), (39, 40), (38, 39), (37, 38), (36, 37), (35, 36), (34, 35), (33, 34), (33, 65), (96, 65),
                 (95, 96), (94, 95), (93, 94), (92, 93), (91, 92), (90, 91), (89, 90), (88, 89), (87, 88), (86, 87),
                 (85, 86), (84, 85), (83, 84), (82, 83), (81, 82), (80, 81), (79, 80), (78, 79), (77, 78), (76, 77),
                 (75, 76), (74, 75), (73, 74), (72, 73), (71, 72), (70, 71), (69, 70), (68, 69), (67, 68), (66, 67),
                 (65, 66), (1, 66), (1, 67), (1, 68), (1, 69), (1, 70), (1, 71), (1, 72), (1, 73), (1, 74),
                 (1, 75), (1, 76), (1, 77), (1, 78), (1, 79), (1, 80), (1, 81), (1, 82), (1, 83), (1, 84),
                 (1, 85), (1, 86), (1, 87), (1, 88), (1, 89), (1, 90), (1, 91), (1, 92), (1, 93), (1, 94),
                 (1, 95), (1, 96), ]
        faces = [(65, 1, 66, ), (66, 1, 67, ), (67, 1, 68, ), (68, 1, 69, ), (69, 1, 70, ), (70, 1, 71, ), (71, 1, 72, ), (72, 1, 73, ), (73, 1, 74, ), (74, 1, 75, ),
                 (75, 1, 76, ), (76, 1, 77, ), (77, 1, 78, ), (78, 1, 79, ), (79, 1, 80, ), (80, 1, 81, ), (81, 1, 82, ), (82, 1, 83, ), (83, 1, 84, ), (84, 1, 85, ),
                 (85, 1, 86, ), (86, 1, 87, ), (87, 1, 88, ), (88, 1, 89, ), (89, 1, 90, ), (90, 1, 91, ), (91, 1, 92, ), (92, 1, 93, ), (93, 1, 94, ), (94, 1, 95, ),
                 (95, 1, 96, ), (96, 1, 65, ), (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, ), (32, 64, 33, 0, ), (31, 63, 64, 32, ), (30, 62, 63, 31, ), (29, 61, 62, 30, ), (28, 60, 61, 29, ), (27, 59, 60, 28, ), (26, 58, 59, 27, ),
                 (25, 57, 58, 26, ), (24, 56, 57, 25, ), (23, 55, 56, 24, ), (22, 54, 55, 23, ), (21, 53, 54, 22, ), (20, 52, 53, 21, ), (19, 51, 52, 20, ), (18, 50, 51, 19, ), (17, 49, 50, 18, ), (16, 48, 49, 17, ),
                 (15, 47, 48, 16, ), (14, 46, 47, 15, ), (13, 45, 46, 14, ), (12, 44, 45, 13, ), (11, 43, 44, 12, ), (10, 42, 43, 11, ), (9, 41, 42, 10, ), (8, 40, 41, 9, ), (7, 39, 40, 8, ), (6, 38, 39, 7, ),
                 (5, 37, 38, 6, ), (4, 36, 37, 5, ), (3, 35, 36, 4, ), (2, 34, 35, 3, ), (0, 33, 34, 2, ), (64, 96, 65, 33, ), (63, 95, 96, 64, ), (62, 94, 95, 63, ), (61, 93, 94, 62, ), (60, 92, 93, 61, ),
                 (59, 91, 92, 60, ), (58, 90, 91, 59, ), (57, 89, 90, 58, ), (56, 88, 89, 57, ), (55, 87, 88, 56, ), (54, 86, 87, 55, ), (53, 85, 86, 54, ), (52, 84, 85, 53, ), (51, 83, 84, 52, ), (50, 82, 83, 51, ),
                 (49, 81, 82, 50, ), (48, 80, 81, 49, ), (47, 79, 80, 48, ), (46, 78, 79, 47, ), (45, 77, 78, 46, ), (44, 76, 77, 45, ), (43, 75, 76, 44, ), (42, 74, 75, 43, ), (41, 73, 74, 42, ), (40, 72, 73, 41, ),
                 (39, 71, 72, 40, ), (38, 70, 71, 39, ), (37, 69, 70, 38, ), (36, 68, 69, 37, ), (35, 67, 68, 36, ), (34, 66, 67, 35, ), (33, 65, 66, 34, ), ]
        mesh = bpy.data.meshes.new("arrow")
        obj = bpy.data.objects.new("arrow", mesh)
        obj.parent = Moments.CenterOfMassObj

        bpy.context.collection.objects.link(obj)

        mat = bpy.data.materials.new(name="ArrowMat"+str(Moments.i))
        if(bpy.data.materials.get('ArrowMat'+str(Moments.i)) != None):
            obj.data.materials.append(mat)
        obj.data.materials['ArrowMat'+str(Moments.i)].diffuse_color = color
        Moments.i+=1

        """
        tempRot = [[],[],[]]
        tempRot[0] = rotation[0][0]/np.linalg.norm(rotation)
        tempRot[1] = rotation[1]/np.linalg.norm(rotation)
        tempRot[2] = rotation[2]/np.linalg.norm(rotation)

        
        # rotation
        obj.rotation_euler.x = rotation[0]
        obj.rotation_euler.y = rotation[1]
        obj.rotation_euler.z = rotation[2]

        """
        vector = mathutils.Vector([rotation[0], rotation[1], rotation[2]])

        up_axis = mathutils.Vector([0.0, 0.0, 1.0])
        angle = vector.angle(up_axis, 0)
        axis = up_axis.cross(vector)
        euler = mathutils.Matrix.Rotation(angle, 4, axis).to_euler()

        obj.rotation_euler = euler


        mesh.from_pydata(verts, edges, faces)
        mesh.update()

        Moments.ArrowObjs.append(obj)
        

#Remove arrows when deselecting object
@persistent
def objectHandler(context):
    selected = bpy.context.selected_objects

    if Moments.CurrentSelection not in selected:
        Moments.cleanupObjects()
        Moments.CurrentSelection = None

    return None

bpy.app.handlers.depsgraph_update_post.append(objectHandler)

#Clean up member variables on scene change
@persistent
def sceneLoadHandler(context):
    Moments.Volume = 0
    Moments.CoM = [[], [], []]
    Moments.InertiaTens = [[[],[],[]],[[],[],[]],[[],[],[]]]
    Moments.CurrentSelection = None
    Moments.ControlMeshNames = []
    Moments.CenterOfMassObj = None
    Moments.ArrowObjs = []

bpy.app.handlers.load_post.append(sceneLoadHandler)