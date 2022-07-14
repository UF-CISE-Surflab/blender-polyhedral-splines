from math import degrees
import pprint
from time import time
import numpy as np
import json
import random
def generateCuboid(dimensions = (1,1,1), offsets = (0,0,0), rotations=(0,0,0), degree=2):
    name = f"Cuboid degree:{degree}, offsets:{offsets}, rotations:{rotations}, dimensions:{dimensions}"
    desc = f"Computer Generated cuboid, the attributes of which are described in the name"
    cuboid = {
        "testName": name,
        "testDescription": desc,
        "testVol": (dimensions[0] * dimensions[1] * dimensions[2]),
        "testCOM": [offsets[0], offsets[1], offsets[2]],

    }
    faces = []
    #TODO: Create more complex face generations that generates all faces
    #for i in range(-1,2,2):
    faces = faces + [((-dimensions[0]/2, -dimensions[1]/2, dimensions[2]/2),(dimensions[0]/2, dimensions[1]/2, dimensions[2]/2))]
    faces = faces + [((-dimensions[0]/2, dimensions[1]/2, -dimensions[2]/2), (dimensions[0]/2, -dimensions[1]/2), -dimensions[2]/2)]
    #TODO: Rotate all faces by euler angles or quaternions
    #Create coefficient matrices for each face
    faceMatrices = []
    for face in faces:
        xCoefs = np.zeros((degree+1, degree+1))
        yCoefs = np.zeros((degree+1, degree+1))
        zCoefs = np.zeros((degree+1, degree+1))
        xStep = (face[1][0] - face[0][0]) / (degree)
        yStep = (face[1][1] - face[0][1]) / (degree) 
        offsetZ = face[0][2] + offsets[2]
        offsetY = face[0][1] + offsets[1]
        offsetX = face[0][0] + offsets[0]
        for i in range(0, degree + 1):
            for j in range(0, degree + 1):
                zCoefs[i][j] = offsetZ
                xCoefs[i][j] = offsetX + j * xStep
                yCoefs[i][j] = offsetY + i * yStep
        coefMatrices = {
            "xCoefs": xCoefs.tolist(),
            "yCoefs": yCoefs.tolist(),
            "zCoefs": zCoefs.tolist()
        }
        faceMatrices = faceMatrices + [coefMatrices]
    cuboid["testSurfaces"] = faceMatrices
    return cuboid

#pprint.pprint(generateCuboid(degree=4))
#print(json.dumps(generateCuboid(dimensions=(5,4,3),offsets=(5,4,3)), indent=4))

cuboids = []
#Generate Cuboids made up of surfaces with degrees from 2 to 9
for i in range(2, 12):
    cuboids = cuboids + [generateCuboid(degree=i)]
#Generate Cuboids with offset in each directions from -4 to 4
for i in range(-2, 3):
    for j in range(-2, 3):
        for k in range(-2, 3):
            cuboids = cuboids + [generateCuboid(offsets=(i,j,k))]
#Generate Cuboids with dimensions in each direction from 0.1 to 1 (not inclusive)
for i in np.arange(0.1, 1, 0.1):
    for j in np.arange(0.1, 1, 0.1):
        for k in np.arange(0.1, 1, 0.1):
            cuboids = cuboids + [generateCuboid(dimensions=(i,j,k))]
#Generate Cuboids with dimensions in each direction from 1 to 10
for i in range(1, 5):
    for j in range(1, 5):
        for k in range(1, 5):
            cuboids = cuboids + [generateCuboid(dimensions=(i,j,k))]
#Generate Cuboids with random offsets, dimensions, and degrees from 2 to 9, -100 to 100, and 1 to 1000 
random.seed(time())
for i in range(0, 100):
    deg = random.randrange(2,3)
    offX = random.random() * 200 - 100
    offY = random.random() * 200 - 100
    offZ = random.random() * 200 - 100
    dimX = random.random() * 999 + 1
    dimY = random.random() * 999 + 1
    dimZ = random.random() * 999 + 1
    cuboids = cuboids + [generateCuboid(dimensions=(dimX,dimY,dimZ), offsets=(offX,offY,offZ), degree=deg)]
toPrint = {
    "description": "this file contains computer generated test data for for Unit Tests For the bivariateBBFunctions.py file",
    "testCases": cuboids
}
with open('computedTestData.json', 'w') as outfile:
    json.dump(toPrint, outfile)
