import sys
sys.path.append('../operators')
from colorama import Fore
from bivariateBBFunctions import bbFunctions
import json
import numpy
import time
with open("./computedTestData.json") as f:
    testData = json.loads(f.read())
    arrTimes = []
    testsPassed = 0
    for testCase in testData["testCases"]:
        testCaseStartTime = time.process_time()
        #Initialize running sums of all moments
        runningVolume = 0
        runningCOM = numpy.array([0,0,0])
        runningMOI = numpy.array([
            [0,0,0],
            [0,0,0],
            [0,0,0]
        ])
        totalCalcTime = 0
        #Iterate through each surface and add its moments to our running moments
        for surface in testCase["testSurfaces"]:
            
            xCoefs = numpy.array(surface["xCoefs"])
            yCoefs = numpy.array(surface["yCoefs"])
            zCoefs = numpy.array(surface["zCoefs"])
            individualMomentCalcStartTime = time.process_time()
            vol, com = bbFunctions.allMoments(xCoefs, yCoefs, zCoefs)
            individualMomentCalcTime = time.process_time() - individualMomentCalcStartTime
            runningVolume = runningVolume + vol
            runningCOM = runningCOM + com
            totalCalcTime = totalCalcTime + individualMomentCalcTime
        #Normalize Center of Mass
        runningCOM = runningCOM / runningVolume
        for surface in testCase["testSurfaces"]:
            xCoefs = numpy.array(surface["xCoefs"])
            yCoefs = numpy.array(surface["yCoefs"])
            zCoefs = numpy.array(surface["zCoefs"])
            individualMomentCalcTime = time.process_time() - individualMomentCalcStartTime
            moi = bbFunctions.secondMoment(xCoefs, yCoefs, zCoefs, runningCOM)
            runningMOI = runningMOI + moi
            totalCalcTime = totalCalcTime + individualMomentCalcTime
        
            
        #TODO: perform EIGEN decomposition on the moment of inertia
        if not numpy.allclose(runningVolume,testCase["testVol"]) or not numpy.allclose(runningCOM, numpy.array(testCase["testCOM"])):
            print(Fore.RED +"test: ", testCase["testName"],  ": Failed")
            print(Fore.YELLOW + "Calculated Volume: ", runningVolume)
            print("Expected Volume: ",testCase["testVol"])
            print("Calculated Center of Mass: ", runningCOM)
            print("Expected Center of Mass: ", testCase["testCOM"])
            print("Calculated Moment of Inertia: ", runningMOI)
        else:
            print(Fore.GREEN +"Test: ", testCase["testName"],  ": Passed")
            testsPassed = testsPassed + 1
        print(Fore.RESET + "Average Surface Moment Calculation Time: ", totalCalcTime / len(testCase["testSurfaces"]))
        testTime = time.process_time() - testCaseStartTime
        print("Test Time: ", testTime , "\n\n")
        arrTimes = arrTimes + [str(testTime)]
    #TODO: add command line options for this file to output to csv, have testing be verbose, print without color, etc...
    print("Passed ", testsPassed, " out of ", len(testData["testCases"]))

    

        