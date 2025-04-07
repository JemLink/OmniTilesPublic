import numpy as np
import cv2


def getChangedAreas(img_grey, fgbg, minArea):
    """
    This is detecting changes in the foreground and returns all convex hulls that are big enough to be a tile
    :param img_grey: the grayscale image of the camera
    :param fgbg: the opencv background subtraction odel
    :param minArea: minum area of a tile
    :return: array of convex hulls that are big enough to be a tile. Use this to compare which tiles have to be changed
    """
    mask = fgbg.apply(img_grey, 1)
    # get contours
    conts, hier = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    hull = []
    # only take contours of area
    for c in conts:
        M = cv2.moments(c)
        area = M["m00"]
        if area > minArea:
            hull.append(cv2.convexHull(c))

    # this is just for debugging
    out = np.zeros_like(img_grey)
    for i in range(0, len(hull)):
        cv2.drawContours(out, hull, i, 255, -1)

    ret = cv2.bitwise_and(img_grey, img_grey, mask = out)
    cv2.imshow("Grey", img_grey)
    cv2.imshow("Mask", ret)
    return hull


def getBGMask(img_grey, fgbg, minArea):
    """
    This is detecting changes in the foreground and returns all convex hulls that are big enough to be a tile
    :param img_grey: the grayscale image of the camera
    :param fgbg: the opencv background subtraction odel
    :param minArea: minum area of a tile
    :return: array of convex hulls that are big enough to be a tile. Use this to compare which tiles have to be changed
    """
    mask = fgbg.apply(img_grey, 1)
    # get contours
    conts, hier = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    hull = []
    # only take contours of area
    for c in conts:
        M = cv2.moments(c)
        area = M["m00"]
        if area > minArea:
            hull.append(cv2.convexHull(c))

    # this is just for debugging
    out = np.zeros_like(img_grey)
    for i in range(0, len(hull)):
        cv2.drawContours(out, hull, i, 255, -1)

    ret = cv2.bitwise_and(img_grey, img_grey, mask = out)
    cv2.imshow("Grey", img_grey)
    cv2.imshow("Mask", ret)
    return ret


def getDetectionImage(imgGray, triOutlines, squOutlines, penOutlines, changedAreas):

    if len(changedAreas) == 0:
        return imgGray

    if len(changedAreas) == 1:
        # check if area is the same as imgGray
        M = cv2.moments(changedAreas[0])
        area = M["m00"]
        h, w = imgGray.shape
        print("H and W ", str(h), str(w))
        # should be around the same as the image
        if (area / (w * h)) > 0.9:
            return imgGray

    newMask = np.zeros_like(imgGray)
    # check in which outlines the changed areas are
    for c in changedAreas:
        oldTriOutline = popOutline(triOutlines, c)
        if oldTriOutline is not None:
            cv2.drawContours(newMask, [cv2.convexHull(oldTriOutline)], 0, 255, -1)

        oldSquOutline = popOutline(squOutlines, c)
        if oldSquOutline is not None:
            cv2.drawContours(newMask, [cv2.convexHull(oldSquOutline)], 0, 255, -1)

        oldPenOutline = popOutline(penOutlines, c)
        if oldPenOutline is not None:
            cv2.drawContours(newMask, [cv2.convexHull(oldPenOutline)], 0, 255, -1)

    retImg = cv2.bitwise_and(imgGray, imgGray, mask = newMask)

    return retImg


def getConvexHullOfFormerOutline(imgGray, shapes, changedArea):

    retMask = np.zeros_like(imgGray)
    if len(shapes) > 0:
        cornersOfAllTiles = shapes[2]
        oldOutline = getOutlineIfInArea(cornersOfAllTiles, changedArea)
        if oldOutline is not None:
            cv2.drawContours(retMask, [cv2.convexHull(oldOutline)], 0, 255, -1)
            return retMask
    return


def getMaskOfSingleArea(imgGray, triangles, squares, pentagons, changedArea):

    ret = getConvexHullOfFormerOutline(imgGray, triangles, changedArea)
    if ret is not None:
        return ret

    ret = getConvexHullOfFormerOutline(imgGray, squares, changedArea)
    if ret is not None:
        return ret

    ret = getConvexHullOfFormerOutline(imgGray, pentagons, changedArea)
    if ret is not None:
        return ret

    return imgGray


def checkIfEntireImageWasUpdated(imgGray, changedAreas):
    if len(changedAreas) == 0:
        return False

    if len(changedAreas) == 1:
        # check if area is the same as imgGray
        M = cv2.moments(changedAreas[0])
        area = M["m00"]
        h, w = imgGray.shape
        print("H and W ", str(h), str(w))
        # should be around the same as the image
        if (area / (w * h)) > 0.9:
            return True
    return False


def updateShapes(locTri, locSqu, locPen, tris, squs, pens):
    if len(locTri) > 0:
        tris = updateSingleShape(locTri, tris)

    if len(locSqu) > 0:
        squs = updateSingleShape(locSqu, squs)

    if len(locPen) > 0:
        pens = updateSingleShape(locPen, pens)

    return tris, squs, pens


def updateSingleShape(locShape, shape):
    if len(locShape) == 0:
        return shape

    if len(shape) == 0:
        return locShape

    locID = locShape[0]
    locCen = locShape[1]
    locCorn = locShape[2]

    # it might happen that no id was detected since the tile was taken out
    if len(locID) == 0:
        return shape
    if len(locCen) == 0:
        return shape
    if len(locCorn) == 0:
        return shape

    IDs = shape[0]
    centers = shape[1]
    cornersOfAllTiles = shape[2]

    for i in range(0, len(cornersOfAllTiles)):
        cornersOfOneTile = cornersOfAllTiles[i]
        if len(cornersOfOneTile) < 3:
            continue
        print("corners of one tile ", cornersOfOneTile[1])
        test = cv2.convexHull(np.asarray(cornersOfOneTile))
        res = cv2.pointPolygonTest(test, locCen[0], False)
        if res >= 0:
            IDs[i] = locID[0]
            centers[i] = locCen[0]
            cornersOfAllTiles[i] = locCorn[0]
            print("Updated shape ", str(locID[0]))

    shape = IDs, centers, cornersOfAllTiles
    return shape



#
#
#
# def getConvexHullsOfFormerOutline(imgGray, triangles, squares, pentagons, changedAreas):
#     if len(changedAreas) == 0:
#         return triangles, squares, pentagons
#
#     if len(changedAreas) == 1:
#         # check if area is the same as imgGray
#         M = cv2.moments(changedAreas[0])
#         area = M["m00"]
#         h, w = imgGray.shape
#         print("H and W ", str(h), str(w))
#         # should be around the same as the image
#         if (area / (w * h)) > 0.9:
#             return triangles, squares, pentagons
#
#     newMask = np.zeros_like(imgGray)
#     # check in which outlines the changed areas are
#     for c in changedAreas:
#         oldTriOutline = popOutline(triOutlines, c)
#         if oldTriOutline is not None:
#             cv2.drawContours(newMask, [cv2.convexHull(oldTriOutline)], 0, 255, -1)
#
#         oldSquOutline = popOutline(squOutlines, c)
#         if oldSquOutline is not None:
#             cv2.drawContours(newMask, [cv2.convexHull(oldSquOutline)], 0, 255, -1)
#
#         oldPenOutline = popOutline(penOutlines, c)
#         if oldPenOutline is not None:
#             cv2.drawContours(newMask, [cv2.convexHull(oldPenOutline)], 0, 255, -1)
#
#     retImg = cv2.bitwise_and(imgGray, imgGray, mask = newMask)
#
#     return retImg




#
#
#
# def combineShapes(locTris, locSqus, locPens, triangles, squares, pentagons):
#
#
# # shapes have the form: IDs, centers, corners
# def combineSingleShapes(localShapes, globalShapes):
#     if len(globalShapes) == 0:
#         return localShapes
#
#     IDs = globalShapes[0]
#     centers = globalShapes[1]
#     corners = globalShapes[2]
#
#
#
#     if len(shapes) == 0:
#         shapes = localShapes
#         shapeOutlines = localShapeOutlines
#         shapeIDs = localIDs
#     else:






#
#
# def getMessage(imgGray, triOutlines, squOutlines, penOutlines, changedAreas):
#     # check in which outlines the changed areas are
#     for c in changedAreas:
#         oldTriOutline = popOutline(triOutlines, c)
#         if oldTriOutline.isNull():
#             print("No triangle")
#
#         oldSquOutline = popOutline(squOutlines, c)
#         if oldSquOutline.isNull():
#             print("No square")
#
#         oldPenOutline = popOutline(penOutlines, c)
#         if oldPenOutline.isNull():
#             print("No pentagon")


def getOutlineIfInArea(cornersOfAllTiles, changedArea):

    for i in range(0, len(cornersOfAllTiles)):
        corners = cornersOfAllTiles[i]
        for c in corners:
            print("Corners ", str(c[0]))
            if len(c) < 3:
                return
            o = cv2.convexHull(corners)
            M = cv2.moments(o)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            res = cv2.pointPolygonTest(changedArea, (cX,cY), False)
            if res >= 0:
                # update the outlines with new area info
                return o

    return


def popOutline(outlines, changedArea):
    for o in outlines:
        M = cv2.moments(o)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        res = cv2.pointPolygonTest(changedArea, (cX,cY), False)
        if res >= 0:
            # update the outlines with new area info
            return outlines.pop(outlines.index(o))

    return

