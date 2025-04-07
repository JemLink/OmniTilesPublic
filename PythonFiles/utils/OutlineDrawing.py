import cv2


def DrawContours(contours, img):
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, (0, 0, 255), 3)


def DrawContours(contours, img, color):
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, color, 3)


def DrawContoursWithText(contours, img, text):
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, (0, 0, 255), 3)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))


def DrawContoursWithTextInCenter(contourIDs, contours, img, text, color):
    for contourID in contourIDs:
        contour = contours[contourID]
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, color, 3)

        # compute center of contour
        M = cv2.moments(contour)
        area = float(M["m00"])

        cX = 0
        cY = 0
        if area > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        cv2.putText(img, text, (cX, cY), cv2.FONT_HERSHEY_COMPLEX, 0.5, color)


def DrawContoursFromIDWithText(contourIDs, contours, img, text):
    for contourID in contourIDs:
        approx = cv2.approxPolyDP(contours[contourID], 0.01 * cv2.arcLength(contours[contourID], True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, (0, 0, 255), 3)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))


def DrawContoursFromIDWithTextInCenter(contourIDs, contours, img, text):
    if len(contourIDs) > 0:
        allX = 0
        allY = 0

        for contourID in contourIDs:
            approx = cv2.approxPolyDP(contours[contourID], 0.01 * cv2.arcLength(contours[contourID], True), True)

            # if too few curves skip this contour
            if len(approx) < 3:
                continue

            cv2.drawContours(img, [approx], 0, (0, 0, 255), 3)
            x = approx.ravel()[0]
            y = approx.ravel()[1]
            allX = allX + x
            allY = allY + y

        x = int(allX / len(contourIDs))
        y = int(allY / len(contourIDs))
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))


def DrawContoursFromID(contourIDs, contours, img, color):
    for contourID in contourIDs:
        approx = cv2.approxPolyDP(contours[contourID], 0.01 * cv2.arcLength(contours[contourID], True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, color, 3)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        cv2.putText(img, str(contourID), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, color)


def DrawContoursConvexHullFromID(contourIDs, contours, img, color):
    for contourID in contourIDs:
        convexHull = cv2.convexHull(contours[contourID])
        approx = cv2.approxPolyDP(convexHull, 0.01 * cv2.arcLength(convexHull, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, color, 3)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        cv2.putText(img, str(contourID), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, color)


def DrawContoursConvexWithText(contourIDs, contours, img, text, color):
    for contourID in contourIDs:
        convexHull = cv2.convexHull(contours[contourID])
        approx = cv2.approxPolyDP(convexHull, 0.01 * cv2.arcLength(convexHull, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, color, 3)
        x = approx.ravel()[0]
        y = approx.ravel()[1]
        cv2.putText(img, str(text), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, color)


def DrawGroupedContoursFromID(contourIDsList, contours, img):
    for group in contourIDsList:
        DrawContoursFromIDWithTextInCenter(group, contours, img, str(len(group)))


def DrawGroupedBlobsFromCenter(centers, img):
    for center in centers:
        cX, cY = GetCenterOf(center)
        for point in center:
            pp = (round(point[0]), round(point[1]))
            cv2.circle(img, pp, 5, (0, 255, 0), 1)
            txt = str(len(center))
        cv2.putText(img, txt, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1, 2)


def DrawGroupedBlobsFromCenter(centers, img, color):
    for center in centers:
        cX, cY = GetCenterOf(center)
        for point in center:
            pp = (round(point[0]), round(point[1]))
            cv2.circle(img, pp, 5, color, 1)
            txt = str(len(center))
        cv2.putText(img, txt, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, 2)


def GetCenterOf(center):
    cX = 0
    cY = 0
    for point in center:
        x = point[0]
        y = point[1]
        cX = cX + x
        cY = cY + y
    cX = round(cX / len(center))
    cY = round(cY / len(center))
    return cX, cY



def DrawContoursWithArea(contours, hierarchy, img, minArea, maxArea):
    for component in zip(contours, hierarchy):
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

        if area < minArea:
            continue
        elif area > maxArea:
            continue

        # drawContours(imageToDrawOnto, contourOrApproximate,
        #    indexOfContour (here always 0 since we are iterating over the contours via for), lineColor, lineThickness )
        cv2.drawContours(img, [approx], 0, (0, 0, 255), 3)
        x = approx.ravel()[0]
        y = approx.ravel()[1]

        # this gives innermost children since there are no child nodes
        if conHier[2] < 0:
            cv2.putText(img, str(len(conHier)), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))

        # this gives outermost parent since there are no child nodes
        if conHier[3] < 0:
            cv2.putText(img, str(0), (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))

        # cv2.putText(img, conHier[2], (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
        # if we have three polygonal curves it is triangle


#         if len(approx) == 3:
#             cv2.putText(img, "Triangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
#         # Square
#         if len(approx) == 4:
#     #         # for checking if it is square or rectangle
#     #         x, y, w, h = cv2.boundingRect(approx)
#     #         aspectRatio = float(w)/h
#     #         print(aspectRatio)
#     #         if aspectRatio >= 0.95 and aspectRatio <= 1.05:

#             cv2.putText(img, "Square", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
#         # Pentagon
#         if len(approx) == 5:
#             cv2.putText(img, "Pentagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))