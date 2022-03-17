from math import factorial
import math
import numpy as np

"""
    SCALER MATRICES ARE DEFINED PRIOR TO COMPUTATION FOR BETTER PERFORMANCE
"""
matrixLUT = {
	"33": np.array([
		[1,2,1,],
		[2,4,2,],
		[1,2,1,],
	]),
	"23": np.array([
		[1,2,1,],
		[1,2,1,],
	]),
	"32": np.array([
		[1,1,],
		[2,2,],
		[1,1,],
	]),
	"44": np.array([
		[1,3,3,1,],
		[3,9,9,3,],
		[3,9,9,3,],
		[1,3,3,1,],
	]),
	"34": np.array([
		[1,3,3,1,],
		[2,6,6,2,],
		[1,3,3,1,],
	]),
	"43": np.array([
		[1,2,1,],
		[3,6,3,],
		[3,6,3,],
		[1,2,1,],
	]),
	"55": np.array([
		[1,4,6,4,1,],
		[4,16,24,16,4,],
		[6,24,36,24,6,],
		[4,16,24,16,4,],
		[1,4,6,4,1,],
	]),
	"45": np.array([
		[1,4,6,4,1,],
		[3,12,18,12,3,],
		[3,12,18,12,3,],
		[1,4,6,4,1,],
	]),
	"54": np.array([
		[1,3,3,1,],
		[4,12,12,4,],
		[6,18,18,6,],
		[4,12,12,4,],
		[1,3,3,1,],
	]),
	"66": np.array([
		[1,5,10,10,5,1,],
		[5,25,50,50,25,5,],
		[10,50,100,100,50,10,],
		[10,50,100,100,50,10,],
		[5,25,50,50,25,5,],
		[1,5,10,10,5,1,],
	]),
	"56": np.array([
		[1,5,10,10,5,1,],
		[4,20,40,40,20,4,],
		[6,30,60,60,30,6,],
		[4,20,40,40,20,4,],
		[1,5,10,10,5,1,],
	]),
	"65": np.array([
		[1,4,6,4,1,],
		[5,20,30,20,5,],
		[10,40,60,40,10,],
		[10,40,60,40,10,],
		[5,20,30,20,5,],
		[1,4,6,4,1,],
	]),
	"77": np.array([
		[1,6,15,20,15,6,1,],
		[6,36,90,120,90,36,6,],
		[15,90,225,300,225,90,15,],
		[20,120,300,400,300,120,20,],
		[15,90,225,300,225,90,15,],
		[6,36,90,120,90,36,6,],
		[1,6,15,20,15,6,1,],
	]),
	"67": np.array([
		[1,6,15,20,15,6,1,],
		[5,30,75,100,75,30,5,],
		[10,60,150,200,150,60,10,],
		[10,60,150,200,150,60,10,],
		[5,30,75,100,75,30,5,],
		[1,6,15,20,15,6,1,],
	]),
	"76": np.array([
		[1,5,10,10,5,1,],
		[6,30,60,60,30,6,],
		[15,75,150,150,75,15,],
		[20,100,200,200,100,20,],
		[15,75,150,150,75,15,],
		[6,30,60,60,30,6,],
		[1,5,10,10,5,1,],
	]),
	"88": np.array([
		[1,7,21,35,35,21,7,1,],
		[7,49,147,245,245,147,49,7,],
		[21,147,441,735,735,441,147,21,],
		[35,245,735,1225,1225,735,245,35,],
		[35,245,735,1225,1225,735,245,35,],
		[21,147,441,735,735,441,147,21,],
		[7,49,147,245,245,147,49,7,],
		[1,7,21,35,35,21,7,1,],
	]),
	"78": np.array([
		[1,7,21,35,35,21,7,1,],
		[6,42,126,210,210,126,42,6,],
		[15,105,315,525,525,315,105,15,],
		[20,140,420,700,700,420,140,20,],
		[15,105,315,525,525,315,105,15,],
		[6,42,126,210,210,126,42,6,],
		[1,7,21,35,35,21,7,1,],
	]),
	"87": np.array([
		[1,6,15,20,15,6,1,],
		[7,42,105,140,105,42,7,],
		[21,126,315,420,315,126,21,],
		[35,210,525,700,525,210,35,],
		[35,210,525,700,525,210,35,],
		[21,126,315,420,315,126,21,],
		[7,42,105,140,105,42,7,],
		[1,6,15,20,15,6,1,],
	]),
	"99": np.array([
		[1,8,28,56,70,56,28,8,1,],
		[8,64,224,448,560,448,224,64,8,],
		[28,224,784,1568,1960,1568,784,224,28,],
		[56,448,1568,3136,3920,3136,1568,448,56,],
		[70,560,1960,3920,4900,3920,1960,560,70,],
		[56,448,1568,3136,3920,3136,1568,448,56,],
		[28,224,784,1568,1960,1568,784,224,28,],
		[8,64,224,448,560,448,224,64,8,],
		[1,8,28,56,70,56,28,8,1,],
	]),
	"89": np.array([
		[1,8,28,56,70,56,28,8,1,],
		[7,56,196,392,490,392,196,56,7,],
		[21,168,588,1176,1470,1176,588,168,21,],
		[35,280,980,1960,2450,1960,980,280,35,],
		[35,280,980,1960,2450,1960,980,280,35,],
		[21,168,588,1176,1470,1176,588,168,21,],
		[7,56,196,392,490,392,196,56,7,],
		[1,8,28,56,70,56,28,8,1,],
	]),
	"98": np.array([
		[1,7,21,35,35,21,7,1,],
		[8,56,168,280,280,168,56,8,],
		[28,196,588,980,980,588,196,28,],
		[56,392,1176,1960,1960,1176,392,56,],
		[70,490,1470,2450,2450,1470,490,70,],
		[56,392,1176,1960,1960,1176,392,56,],
		[28,196,588,980,980,588,196,28,],
		[8,56,168,280,280,168,56,8,],
		[1,7,21,35,35,21,7,1,],
	])
}

"""
    ALGORITHMS FOR MANIPULATING BERNSTEIN BEZIER POLYNOMIALS
"""
#Take the derivative of a bernstein polynomial in the u direction
def bbUDir(poly): 
    #matrix math
    leftCols = poly[:, :len(poly[0]) - 1]
    rightCols = poly[:, 1:]
    colDirs = rightCols - leftCols
    return colDirs * (len(poly[0]) - 1)
    #Take the derivative of a bernstein polynomial in the v direction
def bbVDir(poly):
    upRows = poly[:len(poly)-1,:]
    botRows = poly[1:,:]
    rowDirs = botRows - upRows
    return rowDirs * (len(poly)-1)
#multiply two bernstein polynomials
#TODO: maybe have a dictionary of scalerMatrices and have the function determine which scalar matrix to use based on the dimensions of the two bernstein polynomials
def bbMult(poly1, poly2):
    scalerKey1 = str(len(poly1)) + str(len(poly1[0]))
    scalerKey2 = str(len(poly2)) + str(len(poly2[0]))
    descalerKey = str(len(poly1)+len(poly2)-1) * 2
    scaledPoly1 = poly1 * matrixLUT[scalerKey1]
    scaledPoly2 = poly2 * matrixLUT[scalerKey2]
    newScaledPoly = np.zeros((len(scaledPoly1)+len(scaledPoly2)-1, len(scaledPoly1[0]) + len(scaledPoly2[0]) - 1))
    for vi in range(0, len(poly1)):
        for ui in range(0, len(poly1[0])):
            for vj in range(0, len(poly2)):
                for uj in range(0, len(poly2[0])):
                    newScaledPoly[vi+vj][ui+uj] = newScaledPoly[vi+vj][ui+uj] + scaledPoly1[vi][ui] * scaledPoly2[vj][uj]
    return newScaledPoly / matrixLUT[descalerKey]

def bbDefIntegral(poly):
    return np.sum(poly) / (len(poly) * len(poly[0]))

class bbFunctions:

    @staticmethod
    def firstMoment(xCoefs, yCoefs, zCoefs):
        dxdu = bbUDir(xCoefs)
        dydv = bbVDir(yCoefs)
        xuyv = bbMult(dxdu, dydv)
        dxdv = bbVDir(xCoefs)
        dydu = bbUDir(yCoefs)
        xvyu = bbMult(dxdv, dydu)
        n3 = xuyv - xvyu
        zn = bbMult(n3, zCoefs)
        return(bbDefIntegral(zn))
