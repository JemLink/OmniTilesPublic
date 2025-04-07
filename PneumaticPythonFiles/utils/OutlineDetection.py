import cv2
import numpy as np
import math

#import os
#import keyboard


"""
Finding the outer contour of markers
"""


def getContourIDsWithArea(contours, hierarchy, minArea, maxArea):
    returnContours = []
    returnHierarchy = []

    i = -1
    for component in zip(contours, hierarchy):
        i += 1
        contour = component[0]
        conHier = component[1]

        # approximate the number of polygonal curves
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        # compute center of contour
        M = cv2.moments(contour)
        area = float(M["m00"])

        if area == 0:
            continue
        elif area < minArea:
            continue
        elif area > maxArea:
            continue
        else:
            returnContours.append(i)
            returnHierarchy.append(conHier)
            #cY = int(M["m01"] / M["m00"])

    return returnContours, returnHierarchy


def getContourIDsWithConvexHullArea(contours, hierarchy, minArea, maxArea):
    returnContours = []
    returnHierarchy = []

    i = -1
    for component in zip(contours, hierarchy):
        i += 1
        contour = component[0]
        conHier = component[1]
        convexHull = cv2.convexHull(contour)

        # approximate the number of polygonal curves
        approx = cv2.approxPolyDP(convexHull, 0.01 * cv2.arcLength(convexHull, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        # compute center of contour
        M = cv2.moments(convexHull)
        area = float(M["m00"])

        if area == 0:
            continue
        elif area < minArea:
            continue
        elif area > maxArea:
            continue
        else:
            returnContours.append(i)
            returnHierarchy.append(conHier)
            #hullImg = np.zeros((800, 800))
            #cv2.fillPoly(hullImg, [convexHull], (255, 255, 255))
            #cv2.imshow("Hull image", hullImg)

    return returnContours, returnHierarchy


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


"""
Find the shape of the outer contour
"""


def getShapesOfContourIDs(contourIDs, contours):
    """
    This function returns 3 arrays with the contour ids in them

    :param contourIDs: this should be a list of all the found contourIDs with a certain area
    :param contours: this should be all contours, so that the contourIDs can be found in here

    :return: triangleIDs[], squareIDs[], pentagonIDs[]
    """

    triangleIDs = []
    squareIDs = []
    pentagonIDs = []

    for ID in contourIDs:
        # get convex hull of id
        contour = contours[ID]
        convexHull = cv2.convexHull(contour)
        # convexHull = flattenPolygonToXCorners(convexHull, 5)

        # approximate the number of polygonal curves
        approx = cv2.approxPolyDP(convexHull, 0.01 * cv2.arcLength(convexHull, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        # compute area of convex hull
        M = cv2.moments(convexHull)
        area = float(M["m00"])

        #compute perimeter of convex hull
        perimeter = cv2.arcLength(convexHull, True)

        # find circularity
        circularity = (4 * np.pi * area) / (perimeter * perimeter)
        #print("\nCircularity: ", circularity)

        # shape classification

        squareCirc = cv2.getTrackbarPos("Square", "Circularity Track Bar") * 0.001
        penCirc = cv2.getTrackbarPos("Pentagon", "Circularity Track Bar") * 0.001

        if circularity > penCirc:
            # pentagon
            # print("Pentagon was detected")
            pentagonIDs.append(ID)
        elif circularity > squareCirc:
            # square
            # print("Square was detected")
            squareIDs.append(ID)
        else:
            # triangle
            # print("Triangle was detected")
            triangleIDs.append(ID)
        # elif circularity > 0.65:
        #     # triangle
        #     print("Triangle was detected")
        #     triangleIDs.append(ID)
        # else:
        #     # no match
        #     print("No specific shape detected. Contour will be discarded")

    return triangleIDs, squareIDs, pentagonIDs


"""
Finding the inner contour / dot contours of the marker
"""


def getBlobCentersInConvexHull(outlineConID, outlineContours, blobs):
    returnBlobs = []

    if outlineConID > len(outlineContours):
        # print("ID is bigger than contours. -1 will be returned")
        # returnContours.append(-1)
        return returnBlobs

    convexHull = cv2.convexHull(outlineContours[outlineConID])

    # minDistanceToOutline = cv2.getTrackbarPos("MinDistanceToOutline", "Blob Track Bar") * -1.0
    # maxDistanceToOutline = cv2.getTrackbarPos("MaxDistanceToOutline", "Blob Track Bar") * -1.0
    # print("Min Distance " + str(minDistanceToOutline))

    for blob in blobs:
        centerDot = blob.pt[0], blob.pt[1]
        distanceToContour = cv2.pointPolygonTest(convexHull, centerDot, True)
        # print("Blob Distance: " + str(distanceToContour))
        # negative values hence min >= value >= max
        #if minDistanceToOutline >= distanceToContour >= maxDistanceToOutline:
        if distanceToContour >= 0.5:
            #print("Blob in boundaries found")
            returnBlobs.append([blob.pt[0], blob.pt[1]])

    return returnBlobs


def getBlobsCenterWithBlobDetector(image, trackbarName, shouldCapture):
    """
        This function detects the blobs at different threshold in the image
        :param image: This is the image the blobs are detected in, it needs to be dark blobs on white/bright background
        :param trackbarName: the name of the trackbar the values are in
        :param distance: the distance of the outline the blobs are in
        :param shouldCapture: whether the camera should capture and save the image

        :return: Will return a string that contains the ID, position and rotation of every found contour.
        Form: [[ID, (x, y, z), (xRot, yRot, zRot)], [...]]
        """

    # Setup SimpleBlobDetector parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = cv2.getTrackbarPos("minThresh", trackbarName)
    params.maxThreshold = cv2.getTrackbarPos("maxThresh", trackbarName)
    params.thresholdStep = cv2.getTrackbarPos("threshStep", trackbarName)

    params.filterByColor = True
    params.blobColor = cv2.getTrackbarPos("color", trackbarName)

    # Filter by Area.
    params.filterByArea = True
    params.minArea = (cv2.getTrackbarPos("minArea", trackbarName))
    params.maxArea = (cv2.getTrackbarPos("maxArea", trackbarName))

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = (cv2.getTrackbarPos("circularity", trackbarName) / 1000.0)

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = (cv2.getTrackbarPos("minConvexity", trackbarName) / 100.0)
    params.minConvexity = (cv2.getTrackbarPos("maxConvexity", trackbarName) / 100.0)

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = (cv2.getTrackbarPos("inertia", trackbarName) / 100.0)

    # Filter by distance
    params.minDistBetweenBlobs = cv2.getTrackbarPos("minDistBetweenBlobs", trackbarName)

    # Create a detector with the parameters
    ver = cv2.__version__.split('.')
    if int(ver[0]) < 3:
        detector = cv2.SimpleBlobDetector(params)
    else:
        detector = cv2.SimpleBlobDetector_create(params)

    #detect blobs
    keypoints = detector.detect(image)
    # Draw detected blobs as green circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(image, keypoints, np.array([]), (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # Show keypoints
    cv2.imshow("Keypoints", im_with_keypoints)
    ### Taking pictures ###
    # this is to find the focal length, it is not needed for the actual program
    if shouldCapture:
        imagePath = 'Images/Captures/'
        print("Saved image to: ", imagePath)
        #path, dirs, files = next(os.walk(imagePath))
        cv2.imwrite(imagePath + 'BlobImg.jpg', im_with_keypoints)

    return keypoints


"""
Finding the array of the number of dots
"""


def getGroupedDotsFromCenters(centers, maxDist):
    """
    This function returns the centers that are close enough together

    :param centers: list of all centers found in an outline
    :param maxDist: max distance between grouped dots
    :return: returns an aray of center arrays that are grouped together
    """
    # control that there are enough entries
    if len(centers) < 2:
        return [centers]

    # copy contourIDs into seperate list which will then be emptied over time
    cen = centers.copy()
    returnCenters = []

    # this is to keep track if all entires have been sorted into buckets
    #addedIDs = []
    # while len(addedIDs) < len(contourIDs):
    while cen:
        if len(cen) < 1:
            break

        visited = []
        # queue = []

        # get all contours whose center is within maxDist
        queue = getCentersOfMaxDistance(cen[0], cen, maxDist)

        # stop if there are no contours
        if len(queue) < 1:
            break

        # while there are still contours to check the distance
        while queue:
            # get first entry and add it to the visited list
            # then control for next one if it also has close nodes in list
            p = queue.pop(0)
            idx = centers.index(p)
            visited.append(idx)
            #addedIDs.append(p)

            # remove popped entry from IDs so that it wont be visited again
            if p in cen:
                cen.remove(p)

            # remove other closest entries from IDs since they are already in the queue
            for deleteCenter in queue:
                if deleteCenter in cen:
                    cen.remove(deleteCenter)

            if len(queue) > 0:
                queue.extend(getCentersOfMaxDistance(queue[0], cen, maxDist))

        # set(x) removes double entries
        visited = list(set(visited))
        visitedGroup = []
        for v in visited:
            visitedGroup.append(centers[v])
        returnCenters.append(visitedGroup)
    return returnCenters


def getCentersOfMaxDistance(currentCenter, centers, maxDist):
    returnCenters = []

    for center in centers:
        dist = getDistance(currentCenter[0], currentCenter[1], center[0], center[1])
        if dist > maxDist:
            continue
        else:
            returnCenters.append(center)

    return returnCenters


def getDistance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    # print("Dist ", str(dist))
    return dist


def getDistanceOfIDs(id1, id2, contours):
    con1 = contours[id1]
    con2 = contours[id2]

    # compute the center of the contour
    M1 = cv2.moments(con1)
    M2 = cv2.moments(con2)

    # float(M["m00"]) is area
    if float(M1["m00"]) > 0 and float(M2["m00"]) > 0:
        cX1 = float(M1["m10"] / M1["m00"])
        cY1 = float(M1["m01"] / M1["m00"])

        cX2 = float(M2["m10"] / M2["m00"])
        cY2 = float(M2["m01"] / M2["m00"])

        dist = getDistance(cX1, cY1, cX2, cY2)
        return dist

    return -1


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


def getDotIDsInConvexHullWithEcc(outlineConID, outlineContours, dotsIDs, contours, minDotSize, maxDotSize, dotMinEcc, dotMaxEcc):
    returnDotIDs = []

    if outlineConID > len(outlineContours):
        # print("ID is bigger than contours. -1 will be returned")
        # returnContours.append(-1)
        return returnDotIDs

    convexHull = cv2.convexHull(outlineContours[outlineConID])

    for dot in dotsIDs:
        centerDot = getCenterCoordinates([dot], contours)
        if cv2.pointPolygonTest(convexHull, centerDot, False) >= -0.5:
            M = cv2.moments(contours[dot])
            dotArea = float(M["m00"])
            if minDotSize < dotArea < maxDotSize:

                # need at least 5 points for ellipse
                if len(contours[dot]) < 5:
                    return returnDotIDs
                ellipse = cv2.fitEllipse(contours[dot])
                width = ellipse[1][0]
                height = ellipse[1][1]
                #ecc = 0
                if width < height:
                    ecc = math.sqrt(1 - width ** 2 / height ** 2)
                else:
                    ecc = math.sqrt(1 - height ** 2 / width ** 2)

                if ecc < dotMinEcc or ecc > dotMaxEcc:
                    continue
                else:
                    returnDotIDs.append(dot)

    return returnDotIDs


# commented out section
# def getInnermostConvexHullContours(contourIDs, contours):
#     returnContourIDs = contourIDs.copy()
#     for ID in contourIDs:
#         convexHull = cv2.convexHull(contours[ID])
#         M = cv2.moments(convexHull)
#         area = float(M["m00"])
#         for i in range(0, len(returnContourIDs)):
#             print("Current return ", returnContourIDs)
#             convexHullReturnCon = cv2.convexHull(contours[returnContourIDs[i]])
#             MR = cv2.moments(convexHullReturnCon)
#             areaRID = float(MR["m00"])
#
#             if area < areaRID:
#                 if float(M["m00"]) > 0:
#                     cX = float(M["m10"] / M["m00"])
#                     cY = float(M["m01"] / M["m00"])
#                     # this means the center of the new outline is located in the area and the area is smaller than the previously saved one
#                     if cv2.pointPolygonTest(convexHullReturnCon, [cX, cY], False) >= 0:
#                         returnContourIDs[i] = ID
#
#     returnContourIDs = list(set(returnContourIDs))
#     print("return ids ", returnContourIDs)
#     return returnContourIDs


# def getContoursWithArea(contours, hierarchy, minArea, maxArea):
#     returnContours = []
#     returnHierarchy = []
#
#     for component in zip(contours, hierarchy):
#         contour = component[0]
#         conHier = component[1]
#
#         # approximate the number of polygonal curves
#         approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
#
#         # if too few curves skip this contour
#         if len(approx) < 3:
#             continue
#
#         # compute center of contour
#         M = cv2.moments(contour)
#         area = float(M["m00"])
#
#         if area == 0:
#             continue
#         elif area < minArea:
#             continue
#         elif area > maxArea:
#             continue
#         else:
#             returnContours.append(contour)
#             returnHierarchy.append(conHier)
#     return returnContours, returnHierarchy
# this returns only child Contours, so contours that have no other contour in them
# def getChildContours(contours, hierarchy):
#     returnContours = []
#     returnHierarchy = []
#
#     for component in zip(contours, hierarchy):
#         contour = component[0]
#         conHier = component[1]
#         # approximate the number of polygonal curves
#         approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
#
#         # if too few curves skip this contour
#         if len(approx) < 3:
#             continue
#
#         # this gives innermost children since there are no child nodes
#         if conHier[2] < 0:
#             returnContours.append(contour)
#             returnHierarchy.append(conHier)
#
#     return returnContours, returnHierarchy


# def getAllContoursOfSameHierarchy(contourID, contours, hierarchies):
#     returnContours = []
#     returnHierarchies = []
#
#     # append the given contour
#     returnContours.append(contours[contourID])
#     returnHierarchies.append(hierarchies[contourID])
#
#     # get the next contour from the given
#     nextContourID = contourID
#
#     # while there is a next contour, get next and add the one to returnContours
#     while hierarchies[nextContourID][0] > 0:
#         nextContourID = hierarchies[nextContourID][0]
#
#         returnContours.append(contours[nextContourID])
#         returnHierarchies.append(hierarchies[nextContourID])
#
#     return returnContours, returnHierarchies

# def getDotsInOutline(outlineID, contours, hierarchy, minAreaDot, maxAreaDot):
#     # print("Outline ID ", outlineID)
#
#     # this returns a list of size contours where every contour id that is not a dot will be set to -1
#     dotIDs = getDotIDsInOutline(outlineID, contours, hierarchy, minAreaDot, maxAreaDot)
#     # print("IDs: ", dotIDs)
#     returnDotCon = []
#     for i in range(0, len(dotIDs)):
#         if dotIDs[i] > 0:
#             returnDotCon.append(contours[dotIDs[i]])
#
#     return returnDotCon


# def getAllContourIDsOfSameHierarchy(contourID, contours, hierarchies):
#     # append the given contour
#     returnContourIDs = [contourID]
#
#     # get the next contour from the given
#     nextContourID = contourID
#
#     # while there is a next contour, get next and add the one to returnContours
#     while hierarchies[nextContourID][0] > 0:
#         nextContourID = hierarchies[nextContourID][0]
#
#         returnContourIDs.append(nextContourID)
#
#     return returnContourIDs


# def getDotIDsInOutlineWithEccentricity(contourID, contours, hierarchy, minDotSize, maxDotSize, dotMinEcc, dotMaxEcc):
#     print("This isnt working")
#     returnContours = []
#     skippedOutlineContourIDs = []
#
#     if contourID > len(contours) or contourID > len(hierarchy):
#         # print("ID is bigger than contours. -1 will be returned")
#         # returnContours.append(-1)
#         return returnContours, skippedOutlineContourIDs
#
#     # get child contour of outline
#     # return outline contour if there is no child contour -> this is recursive
#     if hierarchy[contourID][2] > 0:
#
#         skippedOutlineContourIDs.append(contourID)
#         # get all children IDs
#         childContourIDs = getAllContourIDsOfSameHierarchy(hierarchy[contourID][2], contours, hierarchy)
#         # print("ChildContourIDS ", childContourIDs)
#
#         # add children ids to return ids and return them
#         for i in range(0, len(childContourIDs)):
#             tmpRet, tmpOut = getDotIDsInOutlineWithEccentricity(childContourIDs[i], contours, hierarchy, minDotSize,
#                                                                 maxDotSize, dotMinEcc, dotMaxEcc)
#             returnContours.extend(tmpRet)
#             skippedOutlineContourIDs.extend(tmpOut)
#         return returnContours, skippedOutlineContourIDs
#
#     else:
#         # compute area of contour
#         M = cv2.moments(contours[contourID])
#         area = float(M["m00"])
#
#         # return empty if area is too big or small for dot
#         # return outline contour otherwise
#         if area > maxDotSize:
#             # print("Area is bigger")
#             # returnContours.append(-1)
#             return returnContours, skippedOutlineContourIDs
#         elif area < minDotSize:
#             # print("Area is smaller")
#             # returnContours.append(-1)
#             return returnContours, skippedOutlineContourIDs
#         else:
#             # need at least 5 points for ellipse
#             if len(contours[contourID]) < 5:
#                 return returnContours, skippedOutlineContourIDs
#             ellipse = cv2.fitEllipse(contours[contourID])
#             width = ellipse[1][0]
#             height = ellipse[1][1]
#             ecc = 0
#             if width < height:
#                 ecc = math.sqrt(1 - width ** 2 / height ** 2)
#             else:
#                 ecc = math.sqrt(1 - height ** 2 / width ** 2)
#
#             if ecc < dotMinEcc or ecc > dotMaxEcc:
#                 return returnContours, skippedOutlineContourIDs
#             else:
#                 returnContours.append(contourID)
#                 return returnContours, skippedOutlineContourIDs
#
#
# def getDotIDsInOutline(contourID, contours, hierarchy, minDotSize, maxDotSize):
#     returnContours = []
#     skippedOutlineContourIDs = []
#
#     if contourID > len(contours) or contourID > len(hierarchy):
#         # print("ID is bigger than contours. -1 will be returned")
#         # returnContours.append(-1)
#         return returnContours, skippedOutlineContourIDs
#
#     # get child contour of outline
#     # return outline contour if there is no child contour -> make this recursive
#     if hierarchy[contourID][2] > 0:
#
#         skippedOutlineContourIDs.append(contourID)
#         # get all children IDs
#         childContourIDs = getAllContourIDsOfSameHierarchy(hierarchy[contourID][2], contours, hierarchy)
#         # print("ChildContourIDS ", childContourIDs)
#
#         # add children ids to return ids and return them
#         for i in range(0, len(childContourIDs)):
#             tmpRet, tmpOut = getDotIDsInOutline(childContourIDs[i], contours, hierarchy, minDotSize, maxDotSize)
#             returnContours.extend(tmpRet)
#             skippedOutlineContourIDs.extend(tmpOut)
#         return returnContours, skippedOutlineContourIDs
#
#     else:
#         # compute area of contour
#         M = cv2.moments(contours[contourID])
#         area = float(M["m00"])
#
#         # return empty if area is too big or small for dot
#         # return outline contour otherwise
#         if area > maxDotSize:
#             # print("Area is bigger")
#             # returnContours.append(-1)
#             return returnContours, skippedOutlineContourIDs
#         elif area < minDotSize:
#             # print("Area is smaller")
#             # returnContours.append(-1)
#             return returnContours, skippedOutlineContourIDs
#         else:
#             # print("Should return 0 contour")
#             returnContours.append(contourID)
#             return returnContours, skippedOutlineContourIDs


# def getDotIDsInConvexHull(contourID, dotsIDs, contours, hierarchy, minDotSize, maxDotSize, dotMinEcc, dotMaxEcc):
#     returnDotIDs = []
#     alreadyVisitedCon = []
#
#     if contourID > len(contours) or contourID > len(hierarchy):
#         # print("ID is bigger than contours. -1 will be returned")
#         # returnContours.append(-1)
#         return returnDotIDs, alreadyVisitedCon
#
#     if hierarchy[contourID][2] > 0:
#         return getDotIDsInOutlineWithEccentricity(contourID, contours, hierarchy, minDotSize, maxDotSize, dotMinEcc,
#                                                   dotMaxEcc)
#     else:
#         convexHull = cv2.convexHull(contours[contourID])
#
#         for dot in dotsIDs:
#             centerDot = getCenterCoordinates([dot], contours)
#             if cv2.pointPolygonTest(convexHull, centerDot, False) >= 0:
#                 M = cv2.moments(contours[dot])
#                 dotArea = float(M["m00"])
#                 if minDotSize < dotArea < maxDotSize:
#                     returnDotIDs.append(dot)
#
#     return returnDotIDs, alreadyVisitedCon
#
#


# def getMaxDotIDsInConvexHullWithEcc(outlineConID, outlineContours, dotsIDs, contours, minDotSize, maxDotSize, dotMinEcc, dotMaxEcc, maxNumberDots):
#     returnDotIDs = []
#     alreadyVisitedCon = []
#
#     if outlineConID > len(outlineContours):
#         # print("ID is bigger than contours. -1 will be returned")
#         # returnContours.append(-1)
#         return returnDotIDs, alreadyVisitedCon
#
#     convexHull = cv2.convexHull(outlineContours[outlineConID])
#
#     for dot in dotsIDs:
#         centerDot = getCenterCoordinates([dot], contours)
#         if cv2.pointPolygonTest(convexHull, centerDot, False) >= -0.5:
#             M = cv2.moments(contours[dot])
#             dotArea = float(M["m00"])
#             if minDotSize < dotArea < maxDotSize:
#
#                 # need at least 5 points for ellipse
#                 if len(contours[dot]) < 5:
#                     return returnDotIDs, alreadyVisitedCon
#                 ellipse = cv2.fitEllipse(contours[dot])
#                 width = ellipse[1][0]
#                 height = ellipse[1][1]
#                 ecc = 0
#                 if width < height:
#                     ecc = math.sqrt(1 - width ** 2 / height ** 2)
#                 else:
#                     ecc = math.sqrt(1 - height ** 2 / width ** 2)
#
#                 if ecc < dotMinEcc or ecc > dotMaxEcc:
#                     continue
#                 else:
#                     # only append max X dots
#                     if len(returnDotIDs) < maxNumberDots:
#                         returnDotIDs.append(dot)
#                     else:
#                         for x in range(0, len(returnDotIDs)):
#                             MRetDot = cv2.moments(contours[returnDotIDs[x]])
#                             retDotArea = float(MRetDot["m00"])
#                             if retDotArea < dotArea:
#                                 returnDotIDs[x] = dot
#                                 break
#
#     return returnDotIDs, alreadyVisitedCon

# this should return an array which contains subarrays which are the dots close to each other
# Example Form: [[0,1,2],[3,4],[5,8,9,10],[7]]
# def getGroupedDotsIDs(contourIDs, contours, maxDist):
#     # control that there are enough entries
#     if len(contourIDs) < 2:
#         return [contourIDs]
#
#     # copy contourIDs into seperate list which will then be emptied over time
#     IDs = contourIDs.copy()
#     returnIDs = []
#
#     # this is to keep track if all entires have been sorted into buckets
#     addedIDs = []
#     # while len(addedIDs) < len(contourIDs):
#     while IDs:
#         if len(IDs) < 1:
#             break
#
#         visited = []
#         queue = []
#
#         # get all contours whose center is within maxDIst
#         queue = getIDsOfMaxDistance(IDs[0], IDs, contours, maxDist)
#
#         # stop if there are no contours
#         if len(queue) < 1:
#             break
#
#         # while there are still contours to check the distance
#         while queue:
#             # get first entry and add it to the visited list
#             # then control for next one if it also has close nodes in list
#             p = queue.pop(0)
#             visited.append(p)
#             addedIDs.append(p)
#
#             # remove popped entry from IDs so that it wont be visited again
#             if p in IDs:
#                 IDs.remove(p)
#
#             # remove other closest entries from IDs since they are already in the queue
#             for deleteID in queue:
#                 if deleteID in IDs:
#                     IDs.remove(deleteID)
#
#             if len(queue) > 0:
#                 queue.extend(getIDsOfMaxDistance(queue[0], IDs, contours, maxDist))
#
#         # set(x) removes double entries
#         visited = list(set(visited))
#         returnIDs.append(visited)
#
#     return returnIDs

# def getIDsOfMaxDistance(currentID, IDs, contours, maxDist):
#     returnIDs = []
#
#     currentCon = contours[currentID]
#
#     # compute the center of the contour
#     M = cv2.moments(currentCon)
#
#     # float(M["m00"]) is area
#     if float(M["m00"]) > 0:
#         cX = float(M["m10"] / M["m00"])
#         cY = float(M["m01"] / M["m00"])
#
#         for ID in IDs:
#             idContour = contours[ID]
#             # compute the center of the contour
#             idM = cv2.moments(idContour)
#             if float(idM["m00"]) > 0:
#                 idCX = int(idM["m10"] / idM["m00"])
#                 idCY = int(idM["m01"] / idM["m00"])
#
#                 dist = getDistance(cX, cY, idCX, idCY)
#                 # print("Compared: ", str(currentCon), str(ID))
#
#                 if dist > maxDist:
#                     continue
#                 else:
#                     # print("Added: ", str(ID))
#                     returnIDs.append(ID)
#
#     return returnIDs
