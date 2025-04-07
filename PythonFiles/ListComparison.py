#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np

testLib = [[0, [3, 4, 1, 2, 3, 4, 1, 2]], [1, [1, 1, 2, 2, 3, 3, 4, 4]], [2, [1, 1, 2, 2, 1, 3, 4, 4]]]

testCompArr = [2, 2, 4, 4, 1, 1]


# this returns all the lib entries with the highest similarity as well as the similarity
def getSimAndIDsOfLib(arr, lib):
    
    tmpSim = 0
    tmpShifts = 0
    # tmpShiftsShort = 0
    # tmpShiftsLong = 0
    maxSim = 0
    shifts = []
    # shiftsShort = []
    # shiftsLong = []
    simLibIDs = []
    
    for libArr in lib:
        if len(arr) != len(libArr[1]):
            print("Something went wrong")
            print("Arr ", str(arr))
            print("Arr ", str(libArr[1]))

            # should never be reached since the lib array should always be equal
        else:
            # this should be the only case
            tmpSim, tmpShifts = getMaxSimAndShift(libArr[1], arr)

        if tmpSim > maxSim:
            maxSim = tmpSim
            simLibIDs = [libArr[0]]
            shifts = [tmpShifts]
            # shiftsShort = [tmpShiftsShort]
            # shiftsLong = [tmpShiftsLong]
        elif tmpSim == maxSim:
            simLibIDs.append(libArr[0])
            shifts.append(tmpShifts)
            # shiftsShort.append(tmpShiftsShort)
            # shiftsLong.append(tmpShiftsLong)

    return maxSim, simLibIDs, shifts


def getMaxSimAndShift(arr1, arr2):
    maxSim = 0
    shifts = 0
    tmpShifts = 0
    # the arrays should always have same length
    for i in range(0, len(arr1)):

        tmpSim = 0

        for x in range(0, len(arr2)):
            if arr1[x] == arr2[x]:
                tmpSim += 1

        if tmpSim > maxSim:
            maxSim = tmpSim
            shifts = tmpShifts

        tmpShifts += 1
        arr1 = np.roll(arr1, 1)

    return maxSim, shifts


def rollAroundSim(arrShort, arrLong):
    
    maxSim = 0
    shiftsShort = 0
    returnShiftsShort = 0
    returnShiftsLong = 0

    maxSimPossible = len(arrLong) - (len(arrLong) - len(arrShort))

    # roll around short array to get comparisons like:
    # [2, 3, 4, 1, 2, 3, 1] and [3, 4, 1, 2, 3, 4, 1, 2]
    for i in range(0, len(arrShort)):

        shiftsLong = 0
        # roll around long array
        for j in range(0, len(arrLong)):

            tmpSim = 0

            # compare sequence of short array against long array
            for x in range(0, len(arrShort)):
                if arrShort[x] == arrLong[x]:
                    tmpSim += 1

            if tmpSim > maxSim:
                maxSim = tmpSim
                returnShiftsLong = shiftsLong
                returnShiftsShort = shiftsShort

                if maxSim == maxSimPossible:
                    return maxSim, returnShiftsShort, returnShiftsLong

            shiftsLong += 1
            arrLong = np.roll(arrLong, 1)

        shiftsShort += 1
        arrShort = np.roll(arrShort, 1)

    # the lonShifts are the one the long array had to be shifted
    # the shorts shifts are the one the short array had to be shifted (because of possible occlusion
    return maxSim, returnShiftsShort, returnShiftsLong


def getShiftsOfSimilarArray(arr1, arr2, similarity):

    shifts = 0

    if len(arr1) < len(arr2):
        shortArr = arr1
        longArr = arr2
    else:
        shortArr = arr2
        longArr = arr1

    sim = 0

    for i in range(0, len(longArr)):
        for j in range(0, len(shortArr)):
            if shortArr[j] == longArr[j]:
                sim += 1
        if sim == similarity:
            return shifts
        else:
            sim = 0
            shifts += 1
            longArr = np.roll(longArr, 1)
    return -1


def main():
    # print("Array ", testCompArr)
    # print("Sim: ", getSimAndIDsOfLib(testCompArr, testLib))
    return


if __name__ == '__main__':
    main()


# In[ ]:
