#!/usr/bin/env python
# coding: utf-8

# In[1]:

import numpy as np
import cv2
#from imutils import paths
#import imutils
#import math
#import collections as coll

import os
from pyspin import PySpin
import matplotlib.pyplot as plt
import sys
import keyboard
#import argparse

#from PIL import Image
import time

# Unity python communication
import zmq
#import random

# own files/utils
import ListComparison as lc
from utils import OutlineDetection as od
from utils import OutlineDrawing as odraw
from utils import RotationDetection as rotDet
from utils import CSVReader as csvR
from utils import DistanceDetection as dd
from utils import ShapeID
from utils import PrevTileComparison as ptc
from utils import ChangedAreaDetection as chad
import LightDetection as ld

cropped = True


"""
Unity communication parameters
"""
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
unity_output = "-1"

UnityCommunication_ON = False

"""
Image preprocessing 
"""

backgroundSubtraction_ON = True
use_BIG_Tiles = False
USE_CLAHE = False
DISTORT = False

fgbg = cv2.bgsegm.createBackgroundSubtractorCNT(1)
resetBG = True

# insert the output of fisheye calibration step
Img_DIM = (800, 800)
dim1 = (800, 800)
dim2 = (800, 800)
dim3 = (800, 800)
balance = 1.0
#K = np.array([[351.6318033232932, 0.0, 450.4607527123814], [0.0, 351.7439651791754, 391.2576486450391], [0.0, 0.0, 1.0]])
#D = np.array([[-0.170592708935433], [0.5324235902617314], [-1.5452235955907878], [1.4793950832426657]])

#K = np.array([[382.2014871088083, 0.0, 416.9994991920387], [0.0, 383.57160317378157, 404.66646795694476], [0.0, 0.0, 1.0]])
#D = np.array([[-0.05172022218296033], [-0.06241081918898781], [0.1127643910012391], [-0.08088999845624256]])

#K = np.array([[380.9819171587433, 0.0, 419.1255603857164], [0.0, 382.47328344299814, 393.1569388113894], [0.0, 0.0, 1.0]])
#D = np.array([[-0.024558481049299842], [-0.025316902502382683], [-0.14455312496009526], [0.18782965184370032]])

#K=np.array([[348.7786669913665, 0.0, 394.31078715254756], [0.0, 349.7208111119022, 446.4043008386129], [0.0, 0.0, 1.0]])
#D=np.array([[-0.11688144853327687], [0.5560359579947118], [-1.7340707225876424], [1.6426608377773764]])

K = np.array([[347.85784929000965, 0.0, 401.4146339449159], [0.0, 347.73344257233083, 448.147582198276], [0.0, 0.0, 1.0]])
D = np.array([[-0.06900876503944645], [0.15906407154587035], [-0.2972276889568439], [0.14036265519404062]])


formerMessage = "END"
triangles = []
squares = []
pentagons = []
lastFrame = np.zeros((800, 800, 1), np.uint8)

triOutlines = []
squOutlines = []
penOutlines = []

BACKGROUND = np.zeros((800, 800, 1), np.uint8)

global distortedImg


def GetBlurredGrayScaleImage(imagePath):
    img = cv2.imread(imagePath)
    #img = ~img
    # img = cv2.imread('TriangleWithDot.jpg')
    img = cv2.resize(img, (800, 800))
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgGray = cv2.GaussianBlur(imgGray, (25, 25), 0)
    return imgGray


def GetBlurredGrayScaleImageFromImage(img):
    if len(img.shape) == 3:
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        imgGray = img.copy()
    if cropped:
        blur = int(cv2.getTrackbarPos("Blur", "Outline Track Bar"))
        if blur % 2 == 0:
            blur = blur + 1

        imgGray = cv2.GaussianBlur(imgGray, (blur, blur), 0)
        # cl = int(cv2.getTrackbarPos("ClipLimit", "Outline Track Bar"))
        # tgs = int(cv2.getTrackbarPos("TileGridSize", "Outline Track Bar"))
        # clahe = cv2.createCLAHE(clipLimit=cl, tileGridSize=(9, 9))
        # imgGrayEqualized = clahe.apply(imgGray)
        #imgGray = cv2.bilateralFilter(imgGray, FV, SV, TV)
        #imgGray = cv2.medianBlur(imgGray, 5)
    else:
        imgGray = cv2.GaussianBlur(imgGray, (25, 25), 0)
    return imgGray


def GetBlurredBlobsGrayScaleImageFromImage(img):
    if len(img.shape) == 3:
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        imgGray = img.copy()
    if cropped:
        FV = cv2.getTrackbarPos("FV", "Blob Track Bar")
        SV = cv2.getTrackbarPos("SV", "Blob Track Bar")
        TV = cv2.getTrackbarPos("TV", "Blob Track Bar")

        if USE_CLAHE:
            cl = int(cv2.getTrackbarPos("ClipLimit", "Outline Track Bar"))
            tgs = int(cv2.getTrackbarPos("TileGridSize", "Outline Track Bar"))
            clahe = cv2.createCLAHE(clipLimit=cl, tileGridSize=(8, 8))
            imgGray = clahe.apply(imgGray)
            if SV % 2 == 0:
                SV += 1
            imgGray = cv2.GaussianBlur(imgGray, (SV, SV), 0)
        else:
            imgGray = cv2.GaussianBlur(imgGray, (3, 3), 0)
            imgGray = cv2.bilateralFilter(imgGray, FV, SV, TV)
            #imgGray = cv2.medianBlur(imgGray, 5)
    else:
        imgGray = cv2.GaussianBlur(imgGray, (25, 25), 0)
    return imgGray


def trackChanged(x):
    pass

#
# def rotate_image(image, angle):
#     image_center = tuple(np.array(image.shape[1::-1]) / 2)
#     rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
#     result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
#     return result


"""
Trackbar creation and handling
"""


def getCircularityTrackbar():
    cv2.namedWindow('Circularity Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("Square", "Circularity Track Bar", 760, 1000, trackChanged)
    cv2.createTrackbar("Pentagon", "Circularity Track Bar", 870, 1000, trackChanged)


def createOutlineTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Outline Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("SurPix", "Outline Track Bar", 130, 200, trackChanged)
    cv2.createTrackbar("SubtrPix", "Outline Track Bar", 4, 10, trackChanged)
    cv2.createTrackbar("AbsThreshold", "Outline Track Bar", 100, 255, trackChanged)
    cv2.createTrackbar("MaxOutline", "Outline Track Bar", 75000, 100000, trackChanged)
    cv2.createTrackbar("MinOutline", "Outline Track Bar", 750, 15000, trackChanged)
    cv2.createTrackbar("StructElemX", "Outline Track Bar", 1, 20, trackChanged)
    cv2.createTrackbar("StructElemY", "Outline Track Bar", 1, 20, trackChanged)
    cv2.createTrackbar("Blur", "Outline Track Bar", 5, 50, trackChanged)
    cv2.createTrackbar("ClipLimit", "Outline Track Bar", 5, 50, trackChanged)


# def createDotTrackbar():
#     # creating trackbar to change contour size
#     cv2.namedWindow('Dot Track Bar', cv2.WINDOW_NORMAL)
#
#     cv2.createTrackbar("SurPix", "Dot Track Bar", 15, 100, trackChanged)
#     cv2.createTrackbar("SubtrPix", "Dot Track Bar", 9, 100, trackChanged)
#     cv2.createTrackbar("MaxDot", "Dot Track Bar", 700, 1000, trackChanged)
#     cv2.createTrackbar("MinDot", "Dot Track Bar", 5, 100, trackChanged)
#     cv2.createTrackbar("StructDotElemX", "Dot Track Bar", 2, 10, trackChanged)
#     cv2.createTrackbar("StructDotElemY", "Dot Track Bar", 2, 10, trackChanged)
#     cv2.createTrackbar("MinEcc", "Dot Track Bar", 0, 100, trackChanged)
#     cv2.createTrackbar("MaxEcc", "Dot Track Bar", 95, 100, trackChanged)
#     cv2.createTrackbar("MaxDist", "Dot Track Bar", 19, 100, trackChanged)


def createBlurTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Blur Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("FV", "Blur Track Bar", 18, 50, trackChanged)
    cv2.createTrackbar("SV", "Blur Track Bar", 5, 30, trackChanged)
    cv2.createTrackbar("TV", "Blur Track Bar", 5, 30, trackChanged)


def createBlobTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Blob Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("minThresh", "Blob Track Bar", 10, 255, trackChanged)
    cv2.createTrackbar("maxThresh", "Blob Track Bar", 200, 255, trackChanged)
    cv2.createTrackbar("colorThresh", "Blob Track Bar", 70, 255, trackChanged)
    cv2.createTrackbar("threshStep", "Blob Track Bar", 3, 100, trackChanged)
    cv2.createTrackbar("color", "Blob Track Bar", 0, 255, trackChanged)
    cv2.createTrackbar("minArea", "Blob Track Bar", 3, 100, trackChanged)
    cv2.createTrackbar("maxArea", "Blob Track Bar", 446, 700, trackChanged)
    cv2.createTrackbar("circularity", "Blob Track Bar", 150, 1000, trackChanged)
    cv2.createTrackbar("minConvexity", "Blob Track Bar", 0, 100, trackChanged)
    cv2.createTrackbar("maxConvexity", "Blob Track Bar", 95, 100, trackChanged)
    cv2.createTrackbar("inertia", "Blob Track Bar", 26, 100, trackChanged)
    cv2.createTrackbar("minDistBetweenBlobs", "Blob Track Bar", 2, 100, trackChanged)
    cv2.createTrackbar("groupMultiplier", "Blob Track Bar", 16, 20, trackChanged)
    cv2.createTrackbar("MinDistanceToOutline", "Blob Track Bar", 0, 500, trackChanged)
    cv2.createTrackbar("MaxDistanceToOutline", "Blob Track Bar", 100, 500, trackChanged)
    cv2.createTrackbar("MinEcc", "Blob Track Bar", 0, 100, trackChanged)
    cv2.createTrackbar("MaxEcc", "Blob Track Bar", 95, 100, trackChanged)
    cv2.createTrackbar("MaxDistForGroup", "Blob Track Bar", 18, 100, trackChanged)
    cv2.createTrackbar("FV", "Blob Track Bar", 35, 100, trackChanged)
    cv2.createTrackbar("SV", "Blob Track Bar", 9, 30, trackChanged)
    cv2.createTrackbar("TV", "Blob Track Bar", 9, 30, trackChanged)


def createImageTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Image Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("roi_x", "Image Track Bar", 605, 1000, trackChanged)
    cv2.createTrackbar("roi_y", "Image Track Bar", 949, 1500, trackChanged)


def createSimilarityTrackbar():
    cv2.namedWindow('Similarity Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("TriSim", "Similarity Track Bar", 4, 6, trackChanged)
    cv2.createTrackbar("SquSim", "Similarity Track Bar", 6, 8, trackChanged)
    cv2.createTrackbar("PenSim", "Similarity Track Bar", 8, 10, trackChanged)


def createCornerDetectionTrackbar():
    cv2.namedWindow('Corner Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("minDistPercentage", "Corner Track Bar", 1, 100, trackChanged)
    cv2.createTrackbar("SquSim", "Corner Track Bar", 3, 8, trackChanged)
    cv2.createTrackbar("PenSim", "Corner Track Bar", 3, 10, trackChanged)


def createLightDetectionTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Detection Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("ThreshWithoutSub", "Detection Track Bar", 195, 255, trackChanged)
    cv2.createTrackbar("ThreshWithSub", "Detection Track Bar", 35, 255, trackChanged)
    cv2.createTrackbar("Blur", "Detection Track Bar", 5, 50, trackChanged)
    cv2.createTrackbar("StructElem", "Detection Track Bar", 15, 50, trackChanged)
    cv2.createTrackbar("maxArea", "Detection Track Bar", 4000, 5000, trackChanged)


def tileTracking(camImg, triLibrary, squLibrary, penLibrary, shouldCapture):
    # reading image
    img = camImg
    imgGray = GetBlurredGrayScaleImageFromImage(img)
    minAreaOutline = cv2.getTrackbarPos("MinOutline", "Outline Track Bar")

    global triangles, squares, pentagons
    # cv2 background subtraction

    # own bg subtraction
    global lastFrame
    diffFrames = cv2.absdiff(lastFrame, imgGray)
    # threshold the diff image so that we get the foreground
    diffFrames = cv2.threshold(diffFrames, 50, 255, cv2.THRESH_BINARY)[1]
    lastFrame = imgGray
    global fgbg
    updatedAreas = chad.getChangedAreas(imgGray, fgbg, minAreaOutline)

    if cv2.countNonZero(diffFrames) < 20 and backgroundSubtraction_ON:
        print("No change in background")
        return triangles, squares, pentagons
    else:
        triangles, squares, pentagons = tileRecognition(img, triLibrary, squLibrary, penLibrary, shouldCapture)
        print("Square IDs in tile tracking: ", str(squares[0]))
        return triangles, squares, pentagons


def tileRecognition(capImg, triLibrary, squLibrary, penLibrary, shouldCapture):
    # reading image
    img = capImg
    imgGray = GetBlurredGrayScaleImageFromImage(img)
    imgBlobs = img.copy()
    imgBlobs = cv2.cvtColor(imgBlobs, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("ColorImage", img)

    # adaptive thresholding
    # surrPixelDot = cv2.getTrackbarPos("SurPix", "Dot Track Bar")
    # subtrPixelDot = cv2.getTrackbarPos("SubtrPix", "Dot Track Bar")
    # surrounding pixel must be odd number
    # if surrPixelDot % 2 == 0:
    #     surrPixelDot += 1

    surrPixelOutline = cv2.getTrackbarPos("SurPix", "Outline Track Bar")
    subtrPixelOutline = cv2.getTrackbarPos("SubtrPix", "Outline Track Bar")
    # surrounding pixel must be odd number
    if surrPixelOutline % 2 == 0:
        surrPixelOutline += 1

    # get track bar values
    minAreaBlob = cv2.getTrackbarPos("minArea", "Blob Track Bar")
    maxAreaBlob = cv2.getTrackbarPos("maxArea", "Blob Track Bar")
    # structDotElemX = cv2.getTrackbarPos("StructDotElemX", "Dot Track Bar")
    # structDotElemY = cv2.getTrackbarPos("StructDotElemX", "Dot Track Bar")
    minBlobEcc = cv2.getTrackbarPos("MinEcc", "Blob Track Bar") * 0.01
    maxBlobEcc = cv2.getTrackbarPos("MaxEcc", "Blob Track Bar") * 0.01
    maxBlobDist = float(cv2.getTrackbarPos("MaxDistForGroup", "Blob Track Bar"))

    minAreaOutline = cv2.getTrackbarPos("MinOutline", "Outline Track Bar")
    maxAreaOutline = cv2.getTrackbarPos("MaxOutline", "Outline Track Bar")
    structElemX = cv2.getTrackbarPos("StructElemX", "Outline Track Bar")
    structElemY = cv2.getTrackbarPos("StructElemY", "Outline Track Bar")

    # mean thresholding
    # adaptiveThreshold(src, dst, 125, Imgproc.ADAPTIVE_THRESH_MEAN_C, Imgproc.THRESH_BINARY, number_of_surrounding_pixels(must be odd), 12)
    #adapMeanThresh = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, surrPixelDot, subtrPixelDot)
    # gaussian thresholding
    # adapGausThresh = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, surrPixelDot, subtrPixelDot)

    imgGray = ~imgGray
    adaptInvThresh = cv2.adaptiveThreshold(imgGray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, surrPixelOutline, subtrPixelOutline)
    #imgGray = ~imgGray

    triSim = int(cv2.getTrackbarPos("TriSim", "Similarity Track Bar"))
    squSim = int(cv2.getTrackbarPos("SquSim", "Similarity Track Bar"))
    penSim = int(cv2.getTrackbarPos("PenSim", "Similarity Track Bar"))

    # detect contour on threshold image
    # detImg = adapGausThresh.copy()

    # preprocess for contours
    outlineDetImg = adaptInvThresh.copy()
    # detImg = cv2.morphologyEx(detImg, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (structDotElemX, structDotElemY)))
    outlineDetImg = cv2.morphologyEx(outlineDetImg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (structElemX, structElemY)))

    # grab longest contour
    outlineContours, outlineHierarchy = cv2.findContours(outlineDetImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    outlineHierarchy = outlineHierarchy[0]

    contourImage = img.copy()

    # get outline contours
    outlineConIDs, outlineHier = od.getContourIDsWithConvexHullArea(outlineContours, outlineHierarchy, minAreaOutline, maxAreaOutline)

    print("\nNew round\n")
    testerStart = time.time()

    if shouldCapture:
        imagePath = 'Images/Captures/'
        print("Saved image to: ", imagePath)
        #path, dirs, files = next(os.walk(imagePath))
        cv2.imwrite(imagePath + 'ContoursInThreshold.jpg', outlineDetImg)

    start = time.time()
    triangleIDs, squareIDs, pentagonIDs = od.getShapesOfContourIDs(outlineConIDs, outlineContours)
    print("Time to detect shapes: ", str(time.time() - start))
    start = time.time()
    outlineDetImg = cv2.cvtColor(outlineDetImg, cv2.COLOR_GRAY2BGR)
    odraw.DrawContoursConvexWithText(squareIDs, outlineContours, outlineDetImg, "SQU", (0, 255, 0))
    odraw.DrawContoursConvexWithText(triangleIDs, outlineContours, outlineDetImg, "TRI", (255, 0, 0))
    odraw.DrawContoursConvexWithText(pentagonIDs, outlineContours, outlineDetImg, "PEN", (0, 0, 255))

    dotParam = ShapeID.DotParameters(minAreaBlob, maxAreaBlob, minBlobEcc, maxBlobEcc, maxBlobDist)
    #imgGray = ~imgGray
    imgBlobs = GetBlurredBlobsGrayScaleImageFromImage(imgBlobs)
    #imgBlobs = imgGray.copy()
    blobs = od.getBlobsCenterWithBlobDetector(imgBlobs, "Blob Track Bar", shouldCapture)
    print("Time to detect blobs and draw stuff: ", str(time.time() - start))

    start = time.time()

    # detect triangles
    locTriangles = tileIDDetection("TRI", triangleIDs, outlineContours, dotParam, triSim, contourImage, blobs, triLibrary, 3, shouldCapture)
    print("Time to detect triangles: ", str(time.time() - start))
    start = time.time()

    # detect square
    locSquares = tileIDDetection("SQU", squareIDs, outlineContours, dotParam, squSim, contourImage, blobs, squLibrary, 4, shouldCapture)
    print("Time to detect squares: ", str(time.time() - start))
    start = time.time()

    # detect pentagon
    locPentagons = tileIDDetection("PEN", pentagonIDs, outlineContours, dotParam, penSim, contourImage, blobs, penLibrary, 5, shouldCapture)
    print("Time to detect pentagons: ", str(time.time() - start))

    testerEnd = time.time()
    print("Time (without image and trackbar acquisition): ", str(testerEnd - testerStart))
    # cv2.imshow("DetectionImage", detImg)
    cv2.imshow("Contour Image", contourImage)
    cv2.imshow("Outline detection Img", outlineDetImg)
    #cv2.imshow("edged", edged)

    ### Taking pictures ###
    # this is to find the focal length, it is not needed for the actual program
    if shouldCapture:
        imagePath = 'Images/Captures/'
        print("Saved image to: ", imagePath)
        #path, dirs, files = next(os.walk(imagePath))
        cv2.imwrite(imagePath + 'CameraImage.jpg', capImg)
        cv2.imwrite(imagePath + 'DistortedImage.jpg', distortedImg)
        imgGray= ~imgGray
        cv2.imwrite(imagePath + 'grayAndBlurred.jpg', imgGray)
        cv2.imwrite(imagePath + 'OutlineDetImg.jpg', outlineDetImg)
        cv2.imwrite(imagePath + 'BlobDetectionImage.jpg', imgBlobs)
        cv2.imwrite(imagePath + 'ContourImage.jpg', contourImage)
        # cv2.imwrite(imagePath + 'DetectionImg.jpg', detImg)

    print("Square IDs in point tracking ", str(locSquares[0]))
    return locTriangles, locSquares, locPentagons


def tileIDDetection(shape, outlineContourIDs, outlineContours, dotParam, similarity, contourImg, blobs, idLibrary, numberCorners, shouldCapture):
    """
    This function detects the specific id of the given contour.
    It should receive the information of the shape and the designated contour params
    :param shape: this should be a string containing the shape of the contour
    :param outlineContourIDs: this is an array of the contour ids with the aforementioned area
    :param outlineContours: this is an array of all the contours from which the contour designated by the outlineID will be found
    :param dotParam: all the dot parameters that are used to decide which dots will be taken in
    :param similarity: this determines how many entries of the id array must be the same as the library to be detected
    :param contourImg: the image the contours should be drawn in
    :param blobImg: this the image the blobs will be detected in
    :param idLibrary: the library with which the idArray will be compared to. This should match the shape; triangle, square or pentagon
    :param numberCorners: the number of corners of the shape
    :param shouldCapture: whether the camera is capturing or not


    :return: Will rturn the ID, center, rotation and outline found
    :return: Will rturn the ID, corners, and outline found
    # Will return a string that contains the ID, position and rotation of every found contour.
    Form: [[ID, (x, y, z), (xRot, yRot, zRot)], [...]]
    """

    """ This will contain the message in form of ID, Position, Rotation"""
    foundIDs = []
    foundOutlines = []
    foundCenters = []
    foundCorners = []

    for outlineID in outlineContourIDs:
        outlineValues = getIdCenterAndCornersOfOutline(outlineID, outlineContours, numberCorners, blobs, contourImg, shape, dotParam, idLibrary, similarity)

        if outlineValues is not None:
            print("OutlineValues ", str(outlineValues[0]))
            foundIDs.append(outlineValues[0])
            foundCenters.append(outlineValues[1])
            foundCorners.append(outlineValues[2])
            foundOutlines.append(outlineContours[outlineID])
        #else:
            #print("Found none")

    ## we need to clear the list of tracked tiles
    ptc.updateFormerListOfShape(foundOutlines, numberCorners)
    print("Found square IDs in tileIDDetection ", str(foundIDs))
    return foundIDs, foundCenters, foundCorners


def getIdCenterAndCornersOfOutline(outlineID, outlineContours, numberCorners, blobs, contourImg, shape, dotParam, idLibrary, similarity):
    start = time.time()
    # first get distance so that dot size can be adapted
    distance, width, height = dd.getDistanceAndWidthHeightFromOutlineID(outlineID, outlineContours, numberCorners)

    # get dots of only one outline
    #blobs = od.getBlobsCenterInConvexHullWithBlobDetector(blobImg, "Blob Track Bar", distance, shouldCapture)

    # Show keypoints
    # cv2.imshow("Keypoints", im_with_keypoints)
    # minArea = (dotParam.minArea / distance * 10)
    # maxArea = (dotParam.maxArea / distance * 10)
    # print("Dot min max ", minArea, maxArea)
    singleBlobCenters = od.getBlobCentersInConvexHull(outlineID, outlineContours, blobs)

    if len(singleBlobCenters) > 0:
        multiplier = cv2.getTrackbarPos("groupMultiplier", "Blob Track Bar")
        groupedCenters = od.getGroupedDotsFromCenters(singleBlobCenters, (dotParam.maxDist / distance) * multiplier)
        #contourImg = odraw.DrawGroupedBlobsFromCenter(groupedCenters, contourImg, (255, 0, 0))
        if len(groupedCenters) > numberCorners - 1:
            # this gives back an array that will have the same length as the library
            # if it was shorter, the entries are filled up with -1
            # if it was longer, the entries were deleted
            countArray, centerArray, angleArray = rotDet.getSortedCountAndCenterArray(groupedCenters, outlineID, outlineContours, numberCorners * 2)

            # now we just need to rotate around the array once to see which shift has the highest similarity
            sim, simLibEntries, shifts = lc.getSimAndIDsOfLib(countArray, idLibrary)

            if sim >= numberCorners - 1:
                sim, simLibEntries, shifts = ptc.getMostLikelyTileOfShape(outlineContours[outlineID], sim, simLibEntries, shifts, numberCorners)

            if sim >= similarity:
                print("Potential IDs: Similarity [ids] ", sim, simLibEntries)

                tileID = simLibEntries[0]
                # just take the first similar entry from the library for now and take second argument of lib since first is the id
                shift = shifts[0]
                center = od.getCenterCoordinates([outlineID], outlineContours)
                corners = rotDet.getCornerPositions(shift, angleArray, outlineID, outlineContours, numberCorners)

                msg = shape + ": ID: " + str(tileID) #+ ": Distance: " + str(distance)  # + ", Corners: " + corners #str(round(xRot, 2)) + ", " + str(round(yRot, 2)) + ", " + str(round(zRot, 2))
                if shape == "Triangle":
                    color = (255, 0, 0)
                elif shape == "Square":
                    color = (0, 255, 0)
                else:
                    color = (0, 0, 255)

                odraw.DrawGroupedBlobsFromCenter(groupedCenters, contourImg, (0, 255, 0))
                odraw.DrawContoursConvexWithText([outlineID], outlineContours, contourImg, msg, color)
                print("Time to detect one tile in total: ", str(time.time() - start))
                print("Returned ID ", str(tileID))
                return tileID, center, corners
                # foundCorners.append(corners)
                # foundIDs.append(tileID)
                # foundCenters.append(center)


## Fast cam acquisition and MediaPipe POSE recognition and gesture recognition


# coding=utf-8
# =============================================================================
# Copyright (c) 2001-2021 FLIR Systems, Inc. All Rights Reserved.
#
# This software is the confidential and proprietary information of FLIR
# Integrated Imaging Solutions, Inc. ("Confidential Information"). You
# shall not disclose such Confidential Information and shall use it only in
# accordance with the terms of the license agreement you entered into
# with FLIR Integrated Imaging Solutions, Inc. (FLIR).
#
# FLIR MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE
# SOFTWARE, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT. FLIR SHALL NOT BE LIABLE FOR ANY DAMAGES
# SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING OR DISTRIBUTING
# THIS SOFTWARE OR ITS DERIVATIVES.
# =============================================================================
#
# This AcquireAndDisplay.py shows how to get the image data, and then display images in a GUI.
# This example relies on information provided in the ImageChannelStatistics.py example.
#
# This example demonstrates how to display images represented as numpy arrays.
# Currently, this program is limited to single camera use.
# NOTE: keyboard and matplotlib must be installed on Python interpreter prior to running this example.


global continue_recording
continue_recording = True

BG_COLOR = (0, 0, 0)  # black

ROI_height = 800
ROI_width = 800


#def handle_close(evt):
def handle_close():
    # """
    # This function will close the GUI when close event happens.
    #
    # :param evt: Event that occurs when the figure closes.
    # :type evt: Event
    # """

    global continue_recording
    continue_recording = False


def drawWithLight(image_rgb):
    if backgroundSubtraction_ON:
        thresh = cv2.getTrackbarPos("ThreshWithSub", "Detection Track Bar")
    else:
        thresh = cv2.getTrackbarPos("ThreshWithoutSub", "Detection Track Bar")
    blur = cv2.getTrackbarPos("Blur", "Detection Track Bar")
    global formerMessage
    # if formerMessage != "DRAWING":
    #     print("Set background")
    #     backgroundImg = cv2.cvtColor(lastFrame, cv2.COLOR_GRAY2BGR)
    #     ld.setBackgroundImageTo(backgroundImg, blur)

    center = ld.lightTracking(image_rgb, blur, thresh)
    if center == (0, 0):
        centerMessage = "NotDrawing"
    else:
        centerMessage = str(center[0]) + "," + str(center[1])

    # need to flip the image before sending it unity
    image_rgb = cv2.flip(image_rgb, 1)
    print("Message: ", centerMessage)
    ## the first part needs to be the same name as in the unity data
    data = {
        'messageString': "Running",
        'centerMessage': centerMessage,
        'image': cv2.imencode('.jpg', image_rgb)[1].ravel().tolist()
    }
    return data


def detectTiles(image_rgb, triIdLibrary, squIdLibrary, penIdLibrary, shouldCapture):
    #global triangles, squares, pentagons
    trianglesVal, squaresVal, pentagonsVal = tileTracking(image_rgb, triIdLibrary, squIdLibrary, penIdLibrary, shouldCapture)

    print("Triangle: ", str(len(trianglesVal)))
    tri = ShapesToString(trianglesVal)
    print("Square", str(len(squaresVal)))
    squ = ShapesToString(squaresVal)
    print("Pentagon", str(len(pentagonsVal)))
    pen = ShapesToString(pentagonsVal)

    global formerMessage, fgbg
    if formerMessage != "TILES":
        fgbg = cv2.bgsegm.createBackgroundSubtractorCNT()
        formerMessage = "TILES"

    # need to flip the image before sending it unity
    image_rgb = cv2.flip(image_rgb, 1)

    ## the first part needs to be the same name as in the unity data
    data = {
        'messageString': "Running",
        'trianglesMessage': tri,
        'squaresMessage': squ,
        'pentagonsMessage': pen,
        'image': cv2.imencode('.jpg', image_rgb)[1].ravel().tolist()
    }

    return data


def ShapesToString(shapes):
    # print("Shape length ", str(len(shapes)))
    if len(shapes) == 0:
        return ""

    returnMessage = ""
    IDs = shapes[0]
    centers = shapes[1]
    corners = shapes[2]

    if len(IDs) == 0:
        return returnMessage
    if len(corners) == 0:
        return returnMessage
    if len(centers) == 0:
        return returnMessage

    for i in range(0, len(IDs)):

        #print("Center ", str(len(centers[i])))
        contourMessage = "[" + str(IDs[i])
        contourMessage = contourMessage + ",(" + str(centers[i][0]) + "," + str(centers[i][1]) + "," + str(0) + ")"
        contourMessage = contourMessage + ",("
        for c in corners[i]:
            contourMessage = contourMessage + "v" + str(c[0]) + "," + str(c[1])
        contourMessage = contourMessage + ")]"

        returnMessage = returnMessage + contourMessage
    return returnMessage


def SelectModeViaLight(imgRGB):
    img = imgRGB.copy()
    blur = cv2.getTrackbarPos("Blur", "Detection Track Bar")
    thresh = cv2.getTrackbarPos("Thresh", "Detection Track Bar")
    imgGray = ld.GetBlurredGrayScaleImageFromImage(img, blur)
    cv2.imshow("GrayScale image", imgGray)

    global lastFrame

    if formerMessage != "DRAWING":
        backgroundImg = cv2.cvtColor(lastFrame, cv2.COLOR_GRAY2BGR)
        ld.setBackgroundImageTo(backgroundImg, blur)

    if backgroundSubtraction_ON:
        diffFrames = cv2.absdiff(lastFrame, imgGray)
        lastFrame = imgGray
        cv2.imshow("Background Difference 2", diffFrames)
        _th, imgThresh = cv2.threshold(diffFrames, thresh, 255, cv2.THRESH_BINARY)
    else:
        _th, imgThresh = cv2.threshold(imgGray, thresh, 255, cv2.THRESH_BINARY)

    structElem = cv2.getTrackbarPos("StructElem", "Detection Track Bar")
    detImg = cv2.morphologyEx(imgThresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (structElem, structElem)))
    imgThresh = cv2.morphologyEx(detImg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (structElem, structElem)))

    cv2.imshow("Mode Threshold image", imgThresh)
    print("Return ", str(_th))
    numbNonZero = cv2.countNonZero(imgThresh)
    print("NumbNonZero ", str(numbNonZero))
    if numbNonZero < 50:
        mode = "TILES"
    else:
        mode = "DRAWING"

    print("Mode ", mode)
    return mode


def initEverything(cam):
    createOutlineTrackbar()
    getCircularityTrackbar()
    # createDotTrackbar()
    createBlurTrackbar()
    createBlobTrackbar()
    createImageTrackbar()
    createSimilarityTrackbar()
    createLightDetectionTrackbar()

    backgroundImg = prepareImg(cam)
    blur = cv2.getTrackbarPos("Blur", "Detection Track Bar")
    ld.setBackgroundImageTo(backgroundImg)


def prepareImg(cam):
    image_result = cam.GetNextImage(1000)

    #  Ensure image completion
    if image_result.IsIncomplete():
        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

    else:

        ## This is 2048x2048, so we need to crop it to the ROI from the lens
        width = image_result.GetWidth()
        height = image_result.GetHeight()

        ## This converts it to RGB
        image_converted = image_result.Convert(PySpin.PixelFormat_BGR8)
        rgb_array = image_converted.GetData()
        rgb_array = rgb_array.reshape(height, width, 3)

        ## process mediapipe on image
        # image_rgb = cv2.cvtColor(cv2.flip(rgb_array, 1), cv2.COLOR_BGR2RGB)
        image_rgb = cv2.flip(rgb_array, 1)

        if cropped:
            ROI_y = cv2.getTrackbarPos("roi_y", "Image Track Bar")
            ROI_x = cv2.getTrackbarPos("roi_x", "Image Track Bar")
            array_cropped = image_rgb[ROI_y:(ROI_y + ROI_height), ROI_x:(ROI_x + ROI_width)]
            image_rgb = array_cropped.copy()  # needed to get the correct data format for further processing

        ## **** un-distort image
        if cropped:
            ## Undistort image parameters
            ## fisheye parameter
            scaled_K = K * dim1[0] / Img_DIM[0]  # The values of K is to scale with image dimension.
            scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0

            # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
            new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3),
                                                                           balance=balance)
            map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)

            image_rgb = cv2.remap(image_rgb, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        ## media pipe works better on rgb image
        image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
        image_rgb = cv2.resize(image_rgb, (800, 800))
        return image_rgb


def acquire_and_display_images(cam, nodemap, nodemap_tldevice):
    """
    This function continuously acquires images from a device and display them in a GUI.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    global continue_recording

    sNodemap = cam.GetTLStreamNodeMap()

    # Change buffer handling mode to NewestOnly
    node_bufferhandling_mode = PySpin.CEnumerationPtr(sNodemap.GetNode('StreamBufferHandlingMode'))
    if not PySpin.IsAvailable(node_bufferhandling_mode) or not PySpin.IsWritable(node_bufferhandling_mode):
        print('Unable to set stream buffer handling mode.. Aborting...')
        return False

    # Retrieve entry node from enumeration node
    node_newestonly = node_bufferhandling_mode.GetEntryByName('NewestOnly')
    if not PySpin.IsAvailable(node_newestonly) or not PySpin.IsReadable(node_newestonly):
        print('Unable to set stream buffer handling mode.. Aborting...')
        return False

    # Retrieve integer value from entry node
    node_newestonly_mode = node_newestonly.GetValue()

    # Set integer value from entry node as new value of enumeration node
    node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

    print('*** IMAGE ACQUISITION ***\n')
    try:

        ## media pipe?
        node_acquisition_mode = PySpin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not PySpin.IsAvailable(node_acquisition_mode_continuous) or not PySpin.IsReadable(
                node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')

        ## Undistort image parameters
        ## fisheye parameter
        scaled_K = K * dim1[0] / Img_DIM[0]  # The values of K is to scale with image dimension.
        scaled_K[2][2] = 1.0  # Except that K[2][2] is always 1.0

        # This is how scaled_K, dim2 and balance are used to determine the final K used to un-distort image. OpenCV document failed to make this clear!
        new_K = cv2.fisheye.estimateNewCameraMatrixForUndistortRectify(scaled_K, D, dim2, np.eye(3), balance=balance)
        map1, map2 = cv2.fisheye.initUndistortRectifyMap(scaled_K, D, np.eye(3), new_K, dim3, cv2.CV_16SC2)

        #  Begin acquiring images
        #
        #  *** NOTES ***
        #  What happens when the camera begins acquiring images depends on the
        #  acquisition mode. Single frame captures only a single image, multi
        #  frame catures a set number of images, and continuous captures a
        #  continuous stream of images.
        #
        #  *** LATER ***
        #  Image acquisition must be ended when no more images are needed.
        cam.BeginAcquisition()

        print('Acquiring images...')

        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        # device_serial_number = ''
        node_device_serial_number = PySpin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if PySpin.IsAvailable(node_device_serial_number) and PySpin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)

        # Close program
        print('Press enter to close the program..')

        # Figure(1) is default so you can omit this line. Figure(0) will create a new window every time program hits this line
        fig = plt.figure(1)

        # Close the GUI when close event happens
        fig.canvas.mpl_connect('close_event', handle_close)

        # Initilization of everything
        initEverything(cam)
        triIdLibrary = csvR.getRowsOfFile('TestTriangle.csv')
        squIdLibrary = csvR.getRowsOfFile('TestSquare.csv')
        penIdLibrary = csvR.getRowsOfFile('TestPentagon.csv')
        print("Lib ", triIdLibrary)
        print("Lib ", squIdLibrary)
        print("Lib ", penIdLibrary)

        while continue_recording:
            try:

                # Process Key (ESC: end) #################################################
                key = cv2.waitKey(1)
                if key == 27:  # ESC
                    break

                ## unity communication
                if UnityCommunication_ON:
                    print("Waiting for unity")
                    message = socket.recv()
                    print("Received request: %s" % message)
                    #unity_output = "-1"  # when no gesture is detected -1 will be returned

                    stringMessage = message.decode("utf-8")
                    stringMessage = stringMessage.strip()
                    if stringMessage == "END":
                        print("Should END")
                        output_byte = str.encode("END")
                        socket.send(b"%s" % output_byte)
                        break

                #  Retrieve next received image
                #
                #  *** NOTES ***
                #  Capturing an image houses images on the camera buffer. Trying
                #  to capture an image that does not exist will hang the camera.
                #
                #  *** LATER ***
                #  Once an image from the buffer is saved and/or no longer
                #  needed, the image must be released in order to keep the
                #  buffer from filling up.

                image_result = cam.GetNextImage(1000)

                #  Ensure image completion
                if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                else:

                    ## This is 2048x2048, so we need to crop it to the ROI from the lens
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()

                    ## This converts it to GreyScale
                    # image_converted = image_result.Convert(spin.PixelFormat_Mono8, spin.HQ_LINEAR)
                    ## This converts it to RGB
                    image_converted = image_result.Convert(PySpin.PixelFormat_BGR8)
                    rgb_array = image_converted.GetData()
                    rgb_array = rgb_array.reshape(height, width, 3)

                    ## process mediapipe on image
                    # image_rgb = cv2.cvtColor(cv2.flip(rgb_array, 1), cv2.COLOR_BGR2RGB)
                    image_rgb = cv2.flip(rgb_array, 1)

                    ## **** Resizing / Croping *****

                    ## RESIZING the image since it would be 2048x2048 otherwise (kind of too big for the window)

                    ## we might have to size this further down for mediapipe to run fast
                    # if scaleImg:
                    #
                    #     image_rgb = cv2.resize(image_rgb, (800, 800))
                    #     scale = 800/2048
                    #     this is to display potential cropping region in the downscaled image
                    #     cv2.rectangle(image_rgb, (int(650*scale), int(580*scale)), (int(1450*scale), int(1380*scale)), (0, 255, 0), 3)

                    ## CROPPING the region of the lens (should be around 800 to fit with the setup so far...)
                    ## This is the cropping
                    ## These values are taken from the unity config
                    ## They might change...
                    if cropped:

                        ROI_y = cv2.getTrackbarPos("roi_y", "Image Track Bar")
                        ROI_x = cv2.getTrackbarPos("roi_x", "Image Track Bar")
                        array_cropped = image_rgb[ROI_y:(ROI_y + ROI_height), ROI_x:(ROI_x + ROI_width)]
                        image_rgb = array_cropped.copy()  # needed to get the correct data format for further processing

                    cv2.imshow("Undistorted image", image_rgb)
                    global distortedImg
                    distortedImg = image_rgb.copy()

                    # **** undistort image
                    if cropped and DISTORT:
                        image_rgb = cv2.remap(image_rgb, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

                    ## media pipe works better on rgb image
                    image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
                    image_rgb = cv2.resize(image_rgb, (800, 800))

                    ### Taking pictures ###
                    # this is to find the focal length, it is not needed for the actual program
                    shouldCapture = False
                    if keyboard.is_pressed('p'):
                        shouldCapture = True
                        imagePath = 'Images/Captures'
                        print("Saved image to: ", imagePath)
                        path, dirs, files = next(os.walk(imagePath))
                        cv2.imwrite(imagePath + 'image' + str(len(files) - 1) + '.jpg', image_rgb)

                    ### tracking ####
                    ## do stuff here
                    start = time.time()
                    global formerMessage
                    if UnityCommunication_ON:
                        ## change behaviour depending on unity message
                        if stringMessage == "DRAWING":
                            if formerMessage != "DRAWING":
                                ld.setBackgroundImageTo(image_rgb, )
                            print("Should DRAW")
                            data = drawWithLight(image_rgb)
                            formerMessage = "DRAWING"
                        elif stringMessage == "TILES":
                            print("Should DETECT TILES")
                            data = detectTiles(image_rgb, triIdLibrary, squIdLibrary, penIdLibrary, shouldCapture)
                            formerMessage = "TILES"
                        else:
                            print("Should END")
                            output_byte = str.encode("END")
                            socket.send(b"%s" % output_byte)
                            break
                    else:
                        # mode = SelectModeViaLight(image_rgb)
                        # if mode == "DRAWING":
                        #     data = drawWithLight(image_rgb)
                        #     formerMessage = "DRAWING"
                        # elif mode == "TILES":
                        data = detectTiles(image_rgb, triIdLibrary, squIdLibrary, penIdLibrary, shouldCapture)

                    if cv2.waitKey(5) & 0xFF == 27:
                        continue_recording = False
                        break

                    end = time.time()
                    print("Time total: ", end - start)

                    #### Unity communication end ####

                    if UnityCommunication_ON:
                        #  Send reply to client
                        #  In the real world usage, after you finish your work, send your output here
                        socket.send_json(data)

                # If user presses enter, close the program
                # if keyboard.is_pressed('ENTER'):
                #     print('Program is closing...')
                #
                #     # Close figure
                #     plt.close('all')
                #     input('Done! Press Enter to exit...')
                #     continue_recording = False

                    #  Release image
                #
                #  *** NOTES ***
                #  Images retrieved directly from the camera (i.e. non-converted
                #  images) need to be released in order to keep from filling the
                #  buffer.
                image_result.Release()

            except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

        #  End acquisition
        #
        #  *** NOTES ***
        #  Ending acquisition appropriately helps ensure that devices clean up
        #  properly and do not need to be power-cycled to maintain integrity.
        print("Ended acquisition")
        cam.EndAcquisition()
        cv2.destroyAllWindows()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return True


# def logging_csv(number, mode, landmark_list, point_history_list):
#     if mode == 0:
#         pass
#     if mode == 1 and (0 <= number <= 9):
#         csv_path = 'model/keypoint_classifier/keypoint.csv'
#         with open(csv_path, 'a', newline="") as f:
#             writer = csv.writer(f)
#             writer.writerow([number, *landmark_list])
#     if mode == 2 and (0 <= number <= 9):
#         csv_path = 'model/point_history_classifier/point_history.csv'
#         with open(csv_path, 'a', newline="") as f:
#             writer = csv.writer(f)
#             writer.writerow([number, *point_history_list])
#     return


def run_single_camera(cam):
    """
    This function acts as the body of the example; please see NodeMapInfo example
    for more in-depth comments on setting up cameras.

    :param cam: Camera to run on.
    :type cam: CameraPtr
    :return: True if successful, False otherwise.
    :rtype: bool
    """
    try:
        result = True

        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        result &= acquire_and_display_images(cam, nodemap, nodemap_tldevice)

        # Deinitialize camera
        cam.DeInit()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():
    """
    Example entry point; notice the volume of data that the logging event handler
    prints out on debug despite the fact that very little really happens in this
    example. Because of this, it may be better to have the logger set to lower
    level in order to provide a more concise, focused log.

    :return: True if successful, False otherwise.
    :rtype: bool
    """
    result = True

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()

    # Get current library version
    version = system.GetLibraryVersion()
    print('Library version: %d.%d.%d.%d' % (version.major, version.minor, version.type, version.build))

    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()

    num_cameras = cam_list.GetSize()

    print('Number of cameras detected: %d' % num_cameras)

    # Finish if there are no cameras
    if num_cameras == 0:
        # Clear camera list before releasing system
        cam_list.Clear()

        # Release system instance
        system.ReleaseInstance()

        print('Not enough cameras!')
        input('Done! Press Enter to exit...')
        return False

    # Run example on each camera
    for i, cam in enumerate(cam_list):
        print('Running example for camera %d...' % i)

        result &= run_single_camera(cam)
        print('Camera %d example complete... \n' % i)

    # Release reference to camera
    # NOTE: Unlike the C++ examples, we cannot rely on pointer objects being automatically
    # cleaned up when going out of scope.
    # The usage of del is preferred to assigning the variable to None.
    del cam

    # Clear camera list before releasing system
    cam_list.Clear()

    # Release system instance
    system.ReleaseInstance()

    input('Done! Press Enter to exit...')
    cv2.destroyAllWindows()
    return result


if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)

# In[ ]:
