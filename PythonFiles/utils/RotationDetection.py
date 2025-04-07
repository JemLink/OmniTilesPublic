import math
import time

import mpmath
import numpy as np
import cv2
#from imutils import paths
#import imutils
#import math
import collections as coll

from utils import DistanceDetection as dd


def getCornerPositions(shift, angleArray, outlineID, outlineContours, numberCorners):
    corners = getVertices(outlineContours, outlineID, numberCorners)
    centerX, centerY = getCenterCoordinates([outlineID], outlineContours)
    corners = getRotatedCorners(shift, angleArray, corners, [centerX, centerY])
    return corners


def getRotatedCorners(shift, angleArray, corners, center):
    if shift < 0 or len(angleArray) == 0:
        return []
    if shift >= len(angleArray):
        return []

    # This gives us the center of the entry that should be at 0 degree
    print("SHIFT ", str(shift))
    firstEntryAngle = angleArray[shift]
    print("First entry angle ", firstEntryAngle)
    corners = getClockWiseCorners(center[0], center[1], corners)
    minAngle = 360.0
    minCornerID = 0
    for i in range(0, len(corners)):
        angle = getAngleToCenter(center[0], center[1], corners[i])
        # we are looking for the next corner after the zero entry
        # therefore when we subtract the firstEntryAngle from the angles the next one should be positive
        # while the one after should be negative but becoming a larger number by the modulo
        angleDiff = (angle - firstEntryAngle)  # ((firstEntryAngle - angle) + 180) % 360 - 180
        # print("Angle diff ", angleDiff)
        if abs(angleDiff) < minAngle:
            minAngle = abs(angleDiff)
            minCornerID = i
            print("Min Corner ID", minCornerID)
            print("Min angle diff", angleDiff)

    # print("First entry angle: ", firstEntryAngle, "; selected angle: ", minCornerID)
    rotatedCorners = []
    for i in range(0, len(corners)):
        rotatedCorners.append(corners[(minCornerID + i) % len(corners)])

    return rotatedCorners


def getClockWiseCorners(centerX, centerY, corners):
    # print("Corners length ", str(len(corners)))
    angles = []
    for i in range(0, len(corners)):
        # print("Corner ", i, ": ", corners[i])
        angles.append(getAngleToCenter(centerX, centerY, corners[i]))

    sortedCorners = []

    for i in range(0, len(corners)):
        minIdx = angles.index(min(angles))
        # print("Angle ", i, ": ", angles[angles.index(min(angles))])
        angles[minIdx] = 361.0
        sortedCorners.append(corners[minIdx])

    return sortedCorners





"""
XY rotation
"""


def flattenPolygonToXCorners(corners, numberOfCorners):
    tmpCorners = corners.copy()
    tmpCorners = np.array(tmpCorners)

    while len(tmpCorners) > numberOfCorners:
        distanceList = []
        for i in range(0, len(tmpCorners)):
            p = tmpCorners[i][0]
            pp = tmpCorners[(i - 1) % len(tmpCorners)][0]  # previous point
            pn = tmpCorners[(i + 1) % len(tmpCorners)][0]  # next point

            distanceList.append(np.linalg.norm(np.cross(np.subtract(pn, p), np.subtract(p, pp))) / np.linalg.norm(np.subtract(pn, pp)))
        minDist = np.amin(distanceList)
        index = np.where(distanceList == minDist)[0][0]
        tmpCorners = np.delete(tmpCorners, index, axis=0)

    # hullImg = np.zeros((800, 800))
    # cv2.fillPoly(hullImg, [np.array(tmpCorners)], 255)
    # cv2.imshow("Hull image", hullImg)

    return np.array(tmpCorners)


def getSortedCorners(corners):
    # make sure that corner[0]/corner1 is really at bottom right
    #     5----6----7
    #     |         |
    #     4         0
    #     |         |
    #     3----2----1

    roll = 0
    while corners[0][0][0] < corners[1][0][0] or corners[0][0][1] > corners[len(corners) - 1][0][1]:
        #print("corner ", corners)
        roll += 1
        corners = np.roll(np.array(corners), 1)
        if roll > len(corners):
            break
    return corners


def getVertices(contours, contourID, shapeCorners):
    convexHull = cv2.convexHull(contours[contourID])
    convexHull = flattenPolygonToXCorners(convexHull, shapeCorners)
    corners = []
    for x in convexHull:
        corners.append(x[0])
    return corners


def getDistanceBetweenPoints(point1, point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return dist


# def getCorners(hullImg, detPixel):
#     dst = cv2.cornerHarris(hullImg.astype(np.uint8), detPixel, 3, 0.04)
#
#     retCorners = []
#     ret, dst = cv2.threshold(dst, 0.1 * dst.max(), 255, 0)
#     dst = np.uint8(dst)
#     ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
#     criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
#     gray = np.float32(hullImg)
#     corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria)
#
#     for i in range(1, len(corners)):
#         retCorners.append(corners[i])
#         #print(corners[i])
#
#     return retCorners


def mapRange(x, valueMin, valueMax, targetMin, targetMax):
    if x > valueMax:
        x = valueMax
    if x < valueMin:
        x = valueMin

    x = x - valueMin
    x = x / (valueMax - valueMin)
    x = x * (targetMax - targetMin)
    x = x + targetMin
    return x


## returns the distance to a line defined by the points p1 and p2
def getDistanceToLine(self, p1, p2):

    p1 = p1[0]
    p2 = p2[0]
    self = self[0]
    xDiff = p2[0] - p1[0]
    yDiff = p2[1] - p1[1]
    num = abs(yDiff * self[0] - xDiff * self[1] + p2[0] * p1[1] - p2[1] * p1[0])
    den = math.sqrt(yDiff**2 + xDiff**2)
    #print("Dist ", num / den)
    return num / den


def getDiffOfPoints(point1, point2):
    diffVec = np.array([point1[0] - point2[0], point1[1] - point2[1]])
    return np.linalg.norm(diffVec)


def getMiddlePoint(p1, p2):
    return [(p1[0] + p2[0]) * 0.5, (p1[1] + p2[1]) * 0.5]


def getSortedCountAndCenterArray(groupedCenterArray, outlineID, outlineContours, numberOfIdealEntries):
    countArray = []
    angleArray = []
    centerArray = []

    if outlineID > len(outlineContours):
        return []

    outlineX, outlineY = getCenterCoordinates([outlineID], outlineContours)

    for group in groupedCenterArray:
        dotsX, dotsY = getCenterCoordinatesOfGroup(group)
        index, angleArray = getSortedAngleArrayAndInsertID(outlineX, outlineY, dotsX, dotsY, angleArray)
        countArray.insert(index, len(group))
        centerArray.insert(index, [dotsX, dotsY])

    if len(angleArray) > numberOfIdealEntries:
        countArray, centerArray, angleArray = ReduceArraysTo(countArray, centerArray, angleArray, numberOfIdealEntries)

    elif len(angleArray) < numberOfIdealEntries:
        countArray, centerArray, angleArray = ExtendArraysTo(countArray, centerArray, angleArray, numberOfIdealEntries)
    # print("angle array ", angleArray)
    # print("sorted count array ", countArray)
    # print("sorted center array ", centerArray)
    return countArray, centerArray, angleArray


def ReduceArraysTo(countArray, centerArray, angleArray, idealNumber):
    # find the entries that have the smallest distance to each other (those are the ones most likely to be wrongly detected)
    angleDiffs = []
    if len(angleArray) > idealNumber:
        for i in range(0, len(angleArray)):
            # take the average angle difference to following and previous entry since that should still be less
            diff_fol = (angleArray[(i + 1) % len(angleArray)] - angleArray[i]) % 360
            diff_prev = (angleArray[i] - angleArray[(i - 1) % len(angleArray)]) % 360
            angleDiffs.append((diff_fol + diff_prev) * 0.5)

        over = len(angleArray) - idealNumber

        for i in range(0, over):
            idx = angleDiffs.index(min(angleDiffs))
            angleDiffs.pop(idx)
            angleArray.pop(idx)
            countArray.pop(idx)
            centerArray.pop(idx)
    return countArray, centerArray, angleArray


def ExtendArraysTo(countArray, centerArray, angleArray, idealNumber):
    """
    This will extend the angle and count array with -1 but leaves the center array the same so far

    :param countArray:
    :param centerArray:
    :param angleArray:
    :param idealNumber:
    :return:
    """
    angleDiffs = []
    if len(angleArray) < idealNumber:
        for i in range(0, len(angleArray)):
            # take the average angle difference to following and previous entry since that should still be less
            diff_fol = (angleArray[(i + 1) % len(angleArray)] - angleArray[i]) % 360
            diff_prev = (angleArray[i] - angleArray[(i - 1) % len(angleArray)]) % 360
            angleDiffs.append((diff_fol + diff_prev) * 0.5)

        less = idealNumber - len(angleArray)

        for i in range(0, less):
            # we need the maximum distance. But we have to keep in mind that more than on entry might be missing
            idxMax = angleDiffs.index(max(angleDiffs))
            # check if former or previous group is further away
            angle = 360 / idealNumber
            if angleDiffs[(idxMax + 1) % len(angleDiffs)] > angleDiffs[(idxMax - 1) % len(angleDiffs)]:
                # insert the new group after the max idx
                angleDiffs[idxMax] = angleDiffs[idxMax] + angle * 0.5
                angleDiffs.insert((idxMax + 1) % len(angleDiffs), angle)
                angleArray.insert((idxMax + 1) % len(angleDiffs), angleArray[idxMax] + angle)
                countArray.insert((idxMax + 1) % len(angleDiffs), -1)

            else:
                # insert new group before the max idx
                angleDiffs[idxMax] = angleDiffs[idxMax] - angle * 0.5
                angleDiffs.insert((idxMax - 1) % len(angleDiffs), angle)
                angleArray.insert((idxMax - 1) % len(angleDiffs), angleArray[idxMax] - angle)
                countArray.insert((idxMax - 1) % len(angleDiffs), -1)

    return countArray, centerArray, angleArray


# this will return the id and the sorted array after cosine values
# outlineX and outlineY are the center coordinates of the outline
def getSortedAngleArrayAndInsertID(outlineX, outlineY, dotsX, dotsY, angleArray):
    vec = [dotsX - outlineX, dotsY - outlineY]  # cv2.normalize(dotsC) - cv2.normalize(outlineC)

    angle = getAngle(vec)

    if len(angleArray) < 1:
        angleArray.append(angle)
        return 0, angleArray
    else:
        for i in range(0, len(angleArray)):
            if angle < angleArray[i]:
                angleArray.insert(i, angle)
                return i, angleArray
        angleArray.append(angle)
        return len(angleArray) - 1, angleArray


def getAngle(vec):
    # print("Vector before norm ", vec)
    # norm = np.linalg.norm(vec)
    # vec = vec / norm
    #print("Vector ", vec)
    arctan = np.arctan2(vec[1], vec[0])
    angle = (np.degrees(arctan)) % 360
    return angle


def getAngleToCenter(centerX, centerY, vec):
    angleVec = [vec[0] - centerX, vec[1] - centerY]
    return getAngle(angleVec)


def getCenterCoordinates(ids, contours):
    if len(ids) > 0:
        cX = 0
        cY = 0

        for ID in ids:
            M = cv2.moments(contours[ID])
            if float(M["m00"]) > 0:
                x = float(M["m10"] / M["m00"])
                y = float(M["m01"] / M["m00"])
                cX = cX + x
                cY = cY + y

        cX = int(cX / len(ids))
        cY = int(cY / len(ids))

        return cX, cY


def getCenterCoordinatesOfGroup(groupCenters):
    if len(groupCenters) > 0:
        cX = 0
        cY = 0

        for center in groupCenters:
            x = center[0]
            y = center[1]
            cX = cX + x
            cY = cY + y

        cX = int(cX / len(groupCenters))
        cY = int(cY / len(groupCenters))

        return cX, cY

# commented out section
## this should return the ID and the image rotation from the array that contains the counts of dots
##
# def getTileIDAndShiftsFromGroupedArray(array, library):
#     # this return -1 i the array is not found in the library
#     ID, shifts = getArrayIDAndShift(array, library)
#
#     return ID, shifts  # later: compare length of array against library to determine if something is occluded


# def getArrayIDAndShift(array, library):
#     # library is in form: [[id0, [x,x,x,x,x,x,x,x]], [id1,[y,y,y,y,y,y,y,y]], ...]
#     # the id hereby should be the index of the entry
#
#     for entry in library:
#         if checkIfArraysAreEqualWoOrder(array, entry[1]):
#             shifts = getShiftsOfArray(array, entry[1])
#             if shifts < len(array):
#                 return entry[0], shifts
#
#     print("No array found. -1 will be returned")
#     return -1, -1

# go over entries in array and compare/check if they are in the entries (of entries) of the library
# select the entry from the library that contains most entries from the array as best choice
# return its ID


# def checkIfArraysAreEqualWoOrder(array1, array2):
#     if len(array1) != len(array2):
#         return False
#     else:
#         return coll.Counter(array1) == coll.Counter(array2)


# def getShiftsOfArray(array, targetArray):
#     shifts = 0
#
#     # shift the array until it matches the targetArray
#     for i in range(0, len(array)):
#         if (np.array(array) == np.array(targetArray)).all():
#             break
#         # count the shifts
#
#         shifts += 1
#         array = np.roll(array, 1)
#
#     # return shifts
#     return shifts


# def getRotation(shortShifts, longShifts, centerArray, outlineID, outlineContours, detPixel, numberCorners):
#     zRot = getZRotationFromShiftsAndSim(shortShifts, longShifts, centerArray, outlineID, outlineContours)
#     xRot, yRot = getXYRotationFromCorners(outlineContours, outlineID, detPixel, numberCorners)
#     return xRot, yRot, zRot


# def getRotation(shift, angleArray, outlineID, outlineContours, detPixel, numberCorners):
#     corners = getVertices(outlineContours, outlineID, detPixel, numberCorners)
#     zRot = getZRotationFromShiftsAndSim(shift, angleArray, outlineID, outlineContours)
#     xRot, yRot = getXYRotationFromCorners(outlineContours, outlineID, detPixel, numberCorners)
#     return xRot, yRot, zRot


# def getZRotationFromShiftsAndSim(shortShifts, longShifts, centerArray, outlineID, outlineContours):
#     if longShifts < 0:
#         return -1
#     if longShifts > len(centerArray):
#         return -1
#
#     # get the centers coordinates
#     outlineCenter = getCenterCoordinates([outlineID], outlineContours)
#
#     # This gives us the center of the entry that should be at 0 degree
#     firstEntryCenter = centerArray[(len(centerArray) + longShifts) % len(centerArray)]
#
#     centerToZeroVec = [firstEntryCenter[0] - outlineCenter[0], firstEntryCenter[1] - outlineCenter[1]]
#     # need to calculate out the shifts since first entry might not be the zero entry since it might be omitted
#
#     # if angleArray[0] < 45:
#     #     return ((getAngle(centerToZeroVec) - shortShifts * 45)) % 360
#     # else:
#     return ((getAngle(centerToZeroVec) - shortShifts * 45)) % 360


# def getZRotationFromShiftsAndSim(shift, angleArray):
#     if shift < 0:
#         return -1
#     if shift > len(angleArray):
#         return -1
#
#     # This gives us the center of the entry that should be at 0 degree
#     firstEntryAngle = angleArray[shift]
#     return firstEntryAngle
# def getZRotationFromShiftsAndSim(shift, angleArray, outlineID, outlineContours):
#     if shift < 0:
#         return -1
#     if shift > len(angleArray):
#         return -1
#
#     # get the centers coordinates
#     outlineCenter = getCenterCoordinates([outlineID], outlineContours)
#
#     # This gives us the center of the entry that should be at 0 degree
#     print("Angles ", str(angleArray))
#     print("First entry ", str(angleArray[shift]))
#     print("Shift ", shift)
#     firstEntryAngle = angleArray[shift]
#
#     #centerToZeroVec = [firstEntryCenter[0] - outlineCenter[0], firstEntryCenter[1] - outlineCenter[1]]
#     # need to calculate out the shifts since first entry might not be the zero entry since it might be omitted
#
#     # if angleArray[0] < 45:
#     #     return ((getAngle(centerToZeroVec) - shortShifts * 45)) % 360
#     # else:
#     return firstEntryAngle # ((getAngle(centerToZeroVec) - shortShifts * 45)) % 360


# def getZRotationFromShifts(shifts, centerArray, outlineID, contours):
#     if shifts < 0:
#         return -1
#     if shifts > len(centerArray):
#         return -1
#
#     # get the centers coordinates
#     outlineCenter = getCenterCoordinates([outlineID], contours)
#     #print("Outline center ", outlineCenter)
#
#     # This gives us the center of the entry that should be at 0 degree
#     zeroEntryCenter = centerArray[(len(centerArray) - shifts) % len(centerArray)]
#     #print("zero center ", zeroEntryCenter)
#
#     centerToZeroVec = [zeroEntryCenter[0] - outlineCenter[0], zeroEntryCenter[1] - outlineCenter[1]]
#     #print("center to zero vector ", centerToZeroVec)
#     #print("zero angle ", getAngle(centerToZeroVec))
#     return getAngle(centerToZeroVec)

#
# # this one is with suppression so that only the strongest 4 corners are taken in
# def getXYRotationFromConvexHullWithCorners(contourID, contours, numberOfCorners, realWidth):
#     convexHull = cv2.convexHull(contours[contourID])
#     corners = flattenPolygonToXCorners(convexHull, numberOfCorners)
#     #hullImg = np.zeros((800, 800))
#     #cv2.fillPoly(hullImg, [corners], (255, 255, 255))
#     #cv2.imshow("Hull image", hullImg)
#
#     return getXYRotationOfSquare(corners, realWidth)


# corners should be in the form of four entries in a matrix
# def getXYRotationOfSquare(corners):
#     # Y rotation should be the same just for other corners comparison
#
#     # get corners and compare front and back distance
#     #     5----6----7
#     #     |         |
#     #     4         0
#     #     |         |
#     #     3----2----1
#     if len(corners) > 0:
#
#         print("Corners ", corners)
#         #corners = getSortedCorners(corners)
#         corner1 = corners[0]
#         corner3 = corners[1]
#         corner5 = corners[2]
#         corner7 = corners[3]
#         point0 = getMiddlePoint(corner7[0], corner1[0])
#         point2 = getMiddlePoint(corner1[0], corner3[0])
#         point4 = getMiddlePoint(corner3[0], corner5[0])
#         point6 = getMiddlePoint(corner5[0], corner7[0])
#         print("Middle points ", point0, point2, point4, point6)
#
#         height = getDiffOfPoints(point2, point6)
#         width = getDiffOfPoints(point0, point4)
#
#         diff13 = getDiffOfPoints(corner1[0], corner3[0])
#         diff57 = getDiffOfPoints(corner5[0], corner7[0])
#         diff17 = getDiffOfPoints(corner1[0], corner7[0])
#         diff35 = getDiffOfPoints(corner3[0], corner5[0])
#         # width = getDistanceToLine(corner7, corner1, corner3)
#         print("Width ", width)
#         # height = getDistanceToLine(corner1, corner3, corner5)
#         print("Height", height)
#
#         # xRot = getRotationFromDifference(diff13, diff57, height)
#         # yRot = getRotationFromDifference(diff17, diff35, width)
#         xRot = getRotationFromDiff(height, width)
#         yRot = getRotationFromDiff(width, height)
#         return xRot, yRot
#     else:
#         return 0, 0


# def getXYRotationFromDistanceAndSize(distance, width, height):
#     imageWidth = (dd.KNOWN_WIDTH * dd.FOCAL_LENGTH) / distance
#     print("Image Width")
#
#     if width > imageWidth:
#         tmp = width
#         width = imageWidth
#         imageWidth = tmp
#
#     if height > imageWidth:
#         tmp = height
#         height = imageWidth
#         imageWidth = tmp
#
#     xAngle = 90.0 - math.degrees((math.asin(width / imageWidth)))
#     yAngle = 90.0 - math.degrees((math.asin(height / imageWidth)))
#
#     return xAngle, yAngle



# def getXYRotationFromCorners(contours, contourID, detPixel, shapeCorners):
#     convexHull = cv2.convexHull(contours[contourID])
#     convexHull = flattenPolygonToXCorners(convexHull, shapeCorners)
#     hullImg = np.zeros((800, 800))
#     cv2.fillPoly(hullImg, [convexHull], 255)
#     cv2.imshow("Hull image", hullImg)
#     corners = getCorners(hullImg, detPixel)
#
#     if shapeCorners == 3:
#         # get rotation of triangle
#         print("\nReturn Triangle")
#         getXYRotationTriangle()
#         return 0, 0
#     elif shapeCorners == 4:
#         if len(corners) != shapeCorners:
#             print("Something went wrong")
#             return 0, 0
#         else:
#             # get square rotation
#             print("\nReturn square")
#             return getXYRotationSquare(corners)
#     elif shapeCorners == 5:
#         # get pentagon
#         print("\nReturn Pentagon")
#         getXYRotationPentagon()
#         return 0, 0
#     else:
#         print("\nReturn Unclear")
#         print("Not implemented yet")


# def getXYRotationSquare(corners):
#
#     bottomLeftCorner, topLeftCorner, topRightCorner, bottomRightCorner = getSortedSquareCorners(corners)
#
#     xSign = 1
#     ySign = 1
#
#     bottomWidth = getDistanceBetweenPoints(bottomRightCorner,  bottomLeftCorner)
#     topWidth = getDistanceBetweenPoints(topRightCorner, topLeftCorner)
#     leftHeight = getDistanceBetweenPoints(bottomLeftCorner, topLeftCorner)
#     rightHeight = getDistanceBetweenPoints(bottomRightCorner, topRightCorner)
#
#     if bottomWidth < topWidth:
#         xSign = -1
#         xgk = 0.5 * (topWidth - bottomWidth)
#         xHypo = max(leftHeight, rightHeight)
#     else:
#         xgk = 0.5 * (bottomWidth - topWidth)
#         xHypo = max(leftHeight, rightHeight)
#
#     if leftHeight < rightHeight:
#         ySign = -1
#         ygk = 0.5 * (rightHeight - leftHeight)
#         yHypo = max(topWidth, bottomWidth)
#     else:
#         ygk = 0.5 * (leftHeight - rightHeight)
#         yHypo = max(topWidth, bottomWidth)
#
#     scale = 5
#     # xAngle = (math.degrees((math.asin(xgk / xHypo)))) * xSign * scale
#     # yAngle = (math.degrees((math.asin(ygk / yHypo)))) * ySign * scale
#
#     xAngle = (math.degrees((math.atan(xgk / xHypo)))) * xSign * scale
#     yAngle = (math.degrees((math.atan(ygk / yHypo)))) * ySign * scale
#
#     print("xgk, xhypo, angle ", xgk, xHypo, xAngle)
#     print("ygk, yhypo, angle ", ygk, yHypo, yAngle)
#
#     return xAngle, yAngle


# def getSortedSquareCorners(corners):
#     # corners are sorted after y value
#     # coord sys
#     # ----->
#     # |
#     # \/
#     # bottom corners (smallest y value)
#     x = []
#     y = []
#     for corner in corners:
#         x.append(corner[0])
#         y.append(corner[1])
#
#     # right side
#     maxX = x.index(max(x))
#     rightSide = [x.pop(maxX), y.pop(maxX)]
#
#     maxX = x.index(max(x))
#     rightSide2 = [x.pop(maxX), y.pop(maxX)]
#
#     if rightSide[1] < rightSide2[1]:
#         topRightCorner = rightSide2
#         bottomRightCorner = rightSide
#     else:
#         topRightCorner = rightSide
#         bottomRightCorner = rightSide2
#
#     minX = x.index(min(x))
#     leftSide = [x.pop(minX), y.pop(minX)]
#     leftSide2 = [x.pop(0), y.pop(0)]
#
#     if leftSide[1] < leftSide2[1]:
#         topLeftCorner = leftSide2
#         bottomLeftCorner = leftSide
#     else:
#         topLeftCorner = leftSide
#         bottomLeftCorner = leftSide2
#
#     return bottomLeftCorner, topLeftCorner, topRightCorner, bottomRightCorner

#
# def getSortedCountAndCenterArray(groupedArray, outlineID, outlineContours, contours):
#     countArray = []
#     angleArray = []
#     centerArray = []
#
#     if outlineID > len(outlineContours):
#         return []
#
#     outlineX, outlineY = getCenterCoordinates([outlineID], outlineContours)
#
#     for group in groupedArray:
#         dotsX, dotsY = getCenterCoordinates(group, contours)
#         index, angleArray = getSortedAngleArrayAndInsertID(outlineX, outlineY, dotsX, dotsY, angleArray)
#         countArray.insert(index, len(group))
#         centerArray.insert(index, [dotsX, dotsY])
#     # print("angle array ", angleArray)
#     # print("sorted count array ", countArray)
#     # print("sorted center array ", centerArray)
#     return countArray, centerArray
