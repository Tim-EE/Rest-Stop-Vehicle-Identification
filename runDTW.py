
import numpy as np
import matplotlib.pyplot as plt
from dtw import *
import math, random
from real_car_data import realCarData
from rc_car_data import rcCarData

def normalize(v):
    """Perform vector normalization on a vector.

    See: http://mathworld.wolfram.com/NormalizedVector.html

    :math:`\\hat{X} \\equiv \\frac{X}{\\norm{X}`
    """
    norm = max(np.absolute(np.min(v)),np.absolute(np.max(v)))
    if norm == 0:
       return v
    return v / norm

def runForNTimes(dataSet,n, verbose,doLog, normalizeSignals):

    errors = []
    logStr = ""


    for iteration in range(n):
        if verbose:
            print(("-" * 10) + " Iteration: " + str(iteration) + " " + ("-" * 20))
        if doLog:
            logStr += ("-" * 10) + " Iteration: " + str(iteration) + " " + ("-" * 20) + "\n"

        # get a list of the available types/categories/vehicles/etc.
        categoryList = list(dataSet.keys())


        # create index->name mapping
        nameMap = {}
        sampleNumberMap = {}

        # Step 1: Randomly pick one reference signal
        referenceSignalType = random.choice(categoryList)
        referenceSignalSampleNumber = random.randint(0,len(dataSet[referenceSignalType])-1)
        referenceSignal = dataSet[referenceSignalType][referenceSignalSampleNumber]
        if normalizeSignals:
            referenceSignal = normalize(referenceSignal)


        if verbose:
            print("reference signal: " + referenceSignalType + " using sample " + str(referenceSignalSampleNumber))
        if doLog:
            logStr += "reference signal: " + referenceSignalType + " using sample " + str(referenceSignalSampleNumber) + "\n"


        # Step 2: Randomly select one signal from each of the categories/types
        inputSignals = []
        costs = np.zeros(len(categoryList))
        minCost = (-1,float('inf'))
        for i in range(len(categoryList)):
            categoryName = categoryList[i]
            nameMap[i] = categoryName
            categoryDataStr = str(i) + ": " + categoryName + " using sample "

            sampleNumber = random.randint(0,len(dataSet[categoryName])-1)
            sampleSignal = dataSet[categoryName][sampleNumber]
            if normalizeSignals:
                sampleSignal = normalize(sampleSignal)

            sampleNumberMap[i] = sampleNumber

            categoryDataStr += str(sampleNumber)

        # Step 3: Add the selected signal to an array
            inputSignals.append(sampleSignal)

            dtwComparison = DTW(referenceSignal,sampleSignal)
            dtwComparison.run()
            comparisonCost = dtwComparison.cost
            costs[i] = comparisonCost

            # if verbose:
            #     print(categoryDataStr)
            # if doLog:
            #     logStr += categoryDataStr + "\n"

            if verbose:
                # print("    cost (" + str(i) + "): " + str(comparisonCost))
                print("    " + categoryName + "[{:2d}]: ".format(sampleNumber) + str(comparisonCost))
            if doLog:
                # logStr += "    cost (" + str(i) + "): " + str(comparisonCost) + "\n"
                logStr += "    " + categoryName + "[{:2d}]: ".format(sampleNumber) + str(comparisonCost) + "\n"

            if comparisonCost < minCost[1]:
                minCost = (i,comparisonCost)

        if (referenceSignalType != nameMap[minCost[0]]):
            # errors.append("Iteration " + str(iteration) + " identified the signal incorrectly.")
            errors.append("Iteration " + str(iteration) + " identified the signal (" + referenceSignalType + "[" + str(referenceSignalSampleNumber) + "]" + ") incorrectly as " +
            nameMap[minCost[0]] + "[" + str(sampleNumberMap[minCost[0]]) + "]."
            )


    return errors,logStr


if __name__ == '__main__':
    import sys
    import argparse
    import os

    availableDataSets = {'real':realCarData,'rc':rcCarData}



    parser = argparse.ArgumentParser()
    parser.add_argument("numRuns", type=int,help="the number of times to run DTW on the dataset")
    parser.add_argument("-v", "--verbose", help="print the results of each operation",action="store_true")
    parser.add_argument("-log", "--log", help="create a log of the results",action="store_true")
    parser.add_argument("-n", "--normalize", help="use normalized signals during evaluation",action="store_true")

    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument('-dataset', help='dataset to use',choices=availableDataSets.keys(), required=True)
    args = parser.parse_args()

    n = args.numRuns
    dataSet = availableDataSets[args.dataset]
    errors,logStr = runForNTimes(dataSet,n,args.verbose,args.log, args.normalize)


    resultsStr = ("-" * 40) + "\n""FINISHED\n" + ("-" * 40) + "\n"


    resultsStr += "    There were " + str(len(errors)) + " errors\n"
    if len(errors) > 0:
        for error in errors:
            resultsStr += "        " + error + "\n"

    accuracyRate = ((n - len(errors)) / n) * 100
    resultsStr += "    Accuracy: {:.2f}%".format(accuracyRate) + "\n"
    resultsStr += ("-" * 40) + "\n"

    print(resultsStr)

    if args.log:
        logStr += resultsStr

        with open('log.txt', 'w') as logFile:
            logFile.write(logStr)
