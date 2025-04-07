import math

# import numpy as np
# import imutils
import cv2
#import os

# known distance for initializing the focal length
KNOWN_DISTANCE = 40.0
# known size of the enclosing rectangular of th marker: the white area in the middle for a square is 53 mm
KNOWN_WIDTH_TRI = 4.3
KNOWN_WIDTH_SQU = 5.3
KNOWN_WIDTH_PEN = 7.0
KNOWN_PIXEL_WIDTH = 86.12117767333984  # this is in pixel from the lab set up
#KNOWN_PIXEL_WIDTH = 237.0530242919922 # this is in pixel from the home set up

FOCAL_LENGTH = 324.9855761258107  # lab set up
#FOCAL_LENGTH = 1789.079428618809 # home set up


def getDistance(knownWidth, focalLength, imgWidth):
    # print("Width ", imgWidth)
    return (knownWidth * focalLength) / imgWidth


def getFocalLengthFromKnownDistance(image, numberCorners):
    markerWidth = getMarkerFromImage(image)[1][0]

    if numberCorners == 3:
        focalLength = (markerWidth * KNOWN_DISTANCE) / KNOWN_WIDTH_TRI
    elif numberCorners == 4:
        focalLength = (markerWidth * KNOWN_DISTANCE) / KNOWN_WIDTH_SQU
    else:
        focalLength = (markerWidth * KNOWN_DISTANCE) / KNOWN_WIDTH_PEN
    print("Marker Width: ", markerWidth)
    print("Focal length: ", focalLength)


def getMarkerFromImage(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (25, 25), 0)
    gray = ~gray
    adaptInvThresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 45, 5)
    edged = cv2.Canny(adaptInvThresh, 35, 125)

    contours, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # contours = imutils.grab_contours(contours)
    c = max(contours, key=cv2.contourArea)
    DrawContours([c], image)

    print("This is only for square so far")

    return cv2.minAreaRect(c)


def DrawContours(contours, img):
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

        # if too few curves skip this contour
        if len(approx) < 3:
            continue

        cv2.drawContours(img, [approx], 0, (0, 0, 255), 3)
    #cv2.imshow("contours", img)
    cv2.waitKey(0)


#todo add stuff for pentagon and triangle
def getDistanceAndWidthHeightFromOutlineID(outlineID, contours, numberCorners):
    marker = cv2.minAreaRect(contours[outlineID])
    width = marker[1][0]
    height = marker[1][1]

    # x, y, maxWidth, maxHeight = cv2.boundingRect(contours[outlineID])
    # diagonal = maxWidth * maxWidth + maxHeight * maxHeight
    # sideLength = math.sqrt(width * height)

    diagonalSqu = width * width + height * height
    sideLength = math.sqrt(diagonalSqu * 0.5)

    if numberCorners == 3:
        knownWidth = KNOWN_WIDTH_TRI
    elif numberCorners == 4:
        knownWidth = KNOWN_WIDTH_SQU
    else:
        knownWidth = KNOWN_WIDTH_PEN

    # print("Width ", width)
    # print("Height ", height)
    if width > height:
        cm = getDistance(knownWidth, FOCAL_LENGTH, sideLength)
    else:
        cm = getDistance(knownWidth, FOCAL_LENGTH, sideLength)
    return cm, width, height


def main():
    image = cv2.imread('../Images/image9.jpg')
    getFocalLengthFromKnownDistance(image)

    return


if __name__ == '__main__':
    main()


# commented out section

# def testDistanceDetection():
#     path, dirs, files = next(os.walk('../Images/'))
#     for i in range(0, len(files) - 1): # -1 since one of them is the calibration image
#         path = '../Images/image' + str(i) + '.jpg'
#         image = cv2.imread(path)
#         marker = getMarkerFromImage(image)
#         width = marker[1][0]
#         cm = getDistance(KNOWN_WIDTH, FOCAL_LENGTH, width)
#
#         # draw a bounding box around the image and display it
#         box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
#         box = np.int0(box)
#         cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
#         cv2.putText(image, "%.2fcm" % (cm / 12),
#                     (image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
#                     2.0, (0, 255, 0), 3)
#         cv2.imshow("image", image)
#         cv2.waitKey(0)


# def getDistanceFromCorners(corners, image):
#     marker = cv2.minAreaRect(corners)
#     width = marker[1][0]
#     feet = getDistance(KNOWN_WIDTH, FOCAL_LENGTH, width)
#     box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
#     box = np.int0(box)
#
#     cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
#     cv2.putText(image, "%.2fft" % (feet / 12),
#                 (image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
#                 2.0, (0, 255, 0), 3)
#     cv2.imshow("image", image)


# def getDistanceFromOutlineID(outlineID, contours, image):
#     marker = cv2.minAreaRect(contours[outlineID])
#     width = marker[1][0]
#     cm = getDistance(KNOWN_WIDTH, FOCAL_LENGTH, width)
#     #print("Still need to improve this")
#     return cm

    # box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
    # box = np.int0(box)
    #
    # cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
    # cv2.putText(image, "%.2fcm" % (cm * 2.0),
    #             (image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
    #             2.0, (0, 255, 0), 3)
    # cv2.imshow("image", image)
