from typing import List, Any

import cv2
#import numpy as np

## should have the form List[int(ID), int(sim), contour
"""should have the form List[int(ID), int(sim), contour]"""
# formerIDsSimContours: List[Any] = []
formerTriIDsSimContours: List[Any] = []
formerSquIDsSimContours: List[Any] = []
formerPenIDsSimContours: List[Any] = []
#formerShortAndLongShifts = []
formerShifts = []


def getMostLikelyTileOfShape(outline, foundSim, foundIDs, foundShifts, numberCorners):
    if numberCorners == 3:
        return getMostLikelyTile(outline, foundSim, foundIDs, foundShifts, formerTriIDsSimContours)
    elif numberCorners == 4:
        return getMostLikelyTile(outline, foundSim, foundIDs, foundShifts, formerSquIDsSimContours)
    elif numberCorners == 5:
        return getMostLikelyTile(outline, foundSim, foundIDs, foundShifts, formerPenIDsSimContours)


def getMostLikelyTile(outline, foundSim, foundIDs, foundShifts, formerIDsSimContours):
    """
    This function needs the found ids with the highest similarity and compares it to a list of previously found ids.
    It checks if the similarity is higher than the previously found one and whether the position of the outline is around the same position.
    :param outline: the contour that was found
    :param foundSim: the found similarity of the outline array and the library array
    :param foundIDs: the potential ids from the library with the similarity
    :param foundShifts: the shifts for the array
    :param formerIDsSimContours: This is the list of former ids, it should be given the fitting triangle, square or pentagon list
    :return: [Sim], [ID], [foundShortArrayShifts], [foundLongArrayShifts]
    """

    # check for outline if there is tile around similar position in formerIDsSimContours
    formerOutlineID = ComparePosition(outline, formerIDsSimContours)
    if formerOutlineID == -1:
        print("No former contour found nearby")
        # add the outline to the formerIDsSimContours
        formerIDsSimContours.append([foundIDs[0], foundSim, outline])
        formerShifts.append([foundShifts[0]])
    else:
        # if found: check if sim is higher and take ID accordingly
        formerSim = formerIDsSimContours[formerOutlineID][1]
        if formerSim >= foundSim:
            # sim is higher so we want to update the former contour and send back the former sim and id
            # the shifts should be the found shifts of the id
            formerID = formerIDsSimContours[formerOutlineID][0]
            formerIDsSimContours[formerOutlineID][2] = outline

            # if id is in found list: return shifts of list
            if formerID in foundIDs and foundSim:
                shifts = foundShifts[foundIDs.index(formerID)]
                print("new shifts ", str(shifts))
                return formerSim, [formerID], [shifts]

            # otherwise return old shifts
            return formerSim, [formerID], [formerShifts[formerOutlineID][0]]
        else:
            # sim is lower so we want to keep the found sim and id and overwrite the former one
            # since we do not know which of the found ids is more likely, we will just take the first one
            formerIDsSimContours[formerOutlineID][0] = foundIDs[0]
            formerIDsSimContours[formerOutlineID][1] = foundSim
            formerIDsSimContours[formerOutlineID][2] = outline

            formerShifts[formerOutlineID][0] = foundShifts[0]
    # for tile in formerIDsSimContours:
    #     print("Former ids ", tile[0])
    #     print("Former sim ", tile[1])
    return foundSim, foundIDs, foundShifts


def ComparePosition(outline, formerIDsSimContours):
    for i in range(0, len(formerIDsSimContours)):
        formerContour = formerIDsSimContours[i][2]

        M = cv2.moments(outline)
        area = float(M["m00"])
        if area > 0:
            cX = float(M["m10"] / M["m00"])
            cY = float(M["m01"] / M["m00"])

        if cv2.pointPolygonTest(formerContour, (cX, cY), True) >= -0.5:
            return i

    return -1


## this should update the list of previously tracked tiles with higher similarity
def updateFormerListOfShape(contours, numberCorners):

    if numberCorners == 3:
        global formerTriIDsSimContours
        formerTriIDsSimContours = updateFormerList(contours, formerTriIDsSimContours)
    elif numberCorners == 4:
        global formerSquIDsSimContours
        formerSquIDsSimContours = updateFormerList(contours, formerSquIDsSimContours)
    elif numberCorners == 5:
        global formerPenIDsSimContours
        formerPenIDsSimContours = updateFormerList(contours, formerPenIDsSimContours)


def updateFormerList(contours, formerIDsSimContours):

    if len(contours) == 0:
        return []

    ## this should delete tiles which are not in the tracking anymore
    contoursToKeep = []

    for contour in contours:
        # if the contour is within the former contour we keep it
        contourIDToKeep = ComparePosition(contour, formerIDsSimContours)
        if contourIDToKeep != -1:
            contoursToKeep.append(formerIDsSimContours[contourIDToKeep])

    index = 0
    for former in formerIDsSimContours:
        if len(contoursToKeep) > 0:
            if not idAndSimInList(former, contoursToKeep):
                # formerShortAndLongShifts.pop(formerIDsSimContours.index(former))
                #print("Former ", former)
                #print("Pop ", str(formerIDsSimContours[index]))
                formerShifts.pop(index)
                formerIDsSimContours.pop(index)
        index += 1

    formerString = ""
    for former in formerIDsSimContours:
        formerString = formerString + str(former[0])
    return formerIDsSimContours


def resetList(numberCorners):
    if numberCorners == 3:
        formerTriIDsSimContours = []
    elif numberCorners == 4:
        formerSquIDsSimContours = []
    elif numberCorners == 5:
        formerPenIDsSimContours = []


def idAndSimInList(idSimCon, contourList):
    for entry in contourList:
        if idSimCon[0] == entry[0] and idSimCon[1] == entry[1]:
            # print("Returned true ", str(idSimCon[0]), str(entry[0]))
            return True
    return False


#
# def getMostLikelyTile(outline, foundSim, foundIDs, foundShortArrayShifts, foundLongArrayShifts):
#     """
#     This function needs the found ids with the highest similarity and compares it to a list of previously found ids.
#     It checks if the similarity is higher than the previously found one and whether the position of the outline is around the same position.
#     :param outline: the contour that was found
#     :param foundSim: the found similarity of the outline array and the library array
#     :param foundIDs: the potential ids from the library with the similarity
#     :param foundShortArrayShifts: the shifts for the short array
#     :param foundLongArrayShifts: the shifts for the long array
#     :return: [Sim], [ID], [foundShortArrayShifts], [foundLongArrayShifts]
#     """
#
#     # check for outline if there is tile around similar position in formerIDsSimContours
#     formerOutlineID = ComparePosition(outline)
#     if formerOutlineID == -1:
#         print("No former contour found nearby")
#         # add the outline to the formerIDsSimContours
#         formerIDsSimContours.append([foundIDs[0], foundSim, outline])
#         formerShortAndLongShifts.append([foundShortArrayShifts[0], foundLongArrayShifts[0]])
#     else:
#         # if found: check if sim is higher and take ID accordingly
#         formerSim = formerIDsSimContours[formerOutlineID][1]
#         if formerSim > foundSim:
#             # sim is higher so we want to update the former contour and send back the former sim and id
#             # the shifts should be the found shifts of the id
#             formerID = formerIDsSimContours[formerOutlineID][0]
#             formerIDsSimContours[formerOutlineID][2] = outline
#
#             # if id is in found list: return shifts of list
#             if formerID in foundIDs:
#                 shortShifts = foundShortArrayShifts[foundIDs.index(formerID)]
#                 longShifts = foundLongArrayShifts[foundIDs.index(formerID)]
#                 return formerSim, [formerID], [shortShifts], [longShifts]
#
#             # otherwise return old shifts
#             return formerSim, [formerID], [formerShortAndLongShifts[formerOutlineID][0]], [formerShortAndLongShifts[formerOutlineID][1]]
#         else:
#             # sim is lower so we want to keep the found sim and id and overwrite the former one
#             # since we do not know which of the found ids is more likely, we will just take the first one
#             formerIDsSimContours[formerOutlineID][0] = foundIDs[0]
#             formerIDsSimContours[formerOutlineID][1] = foundSim
#             formerIDsSimContours[formerOutlineID][2] = outline
#
#             formerShortAndLongShifts[formerOutlineID][0] = foundShortArrayShifts[0]
#             formerShortAndLongShifts[formerOutlineID][1] = foundLongArrayShifts[0]
#     # for tile in formerIDsSimContours:
#     #     print("Former ids ", tile[0])
#     #     print("Former sim ", tile[1])
#     return foundSim, foundIDs, foundShortArrayShifts, foundLongArrayShifts
