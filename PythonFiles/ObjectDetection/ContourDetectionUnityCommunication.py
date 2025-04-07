#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import time
import zmq
import random

import numpy as np
import cv2
from imutils import paths
import imutils

img = cv2.imread('MagformersWithOutline.jpg')
img = cv2.resize(img, (800, 800))
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgGray = cv2.GaussianBlur(imgGray, (15, 15), 0)
#edged = cv2.Canny(imgGray, 25, 225)
imgHSV = cv2.GaussianBlur(img, (25,25), 0)
imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


while True:
    #  Wait for next request from client
    message = socket.recv()
    print("Received request: %s" % message)

    
    
    # find contours
    dark = cv2.inRange(imgHSV, (0, 0, 0), (100, 100, 100))
    _, thrash = cv2.threshold(imgGray, 160, 255, cv2.THRESH_BINARY)
    #edged = cv2.Canny(thrash, 25, 325)



    # opening and closing
    kernelSizes = [(3, 3)]
    morphedImage = thrash.copy()

    i = 0
    iterations = 0

    while i < iterations:
        i += 1
        # opening
        for kernelSize in kernelSizes:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
            morphedImage = cv2.morphologyEx(morphedImage, cv2.MORPH_OPEN, kernel)
            #cv2.imshow("Opening: ({}, {})".format(kernelSize[0], kernelSize[1]), morphedImage)
            #cv2.waitKey(0)

        # loop over the kernels sizes ag)ain
        for kernelSize in kernelSizes:
            # construct a rectangular kernel form the current size, but this
            # time apply a "closing" operation
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernelSize)
            morphedImage = cv2.morphologyEx(morphedImage, cv2.MORPH_CLOSE, kernel)
            #cv2.imshow("Closing: ({}, {})".format(kernelSize[0], kernelSize[1]), morphedImage)
            #cv2.waitKey(0)




    # grab longest contour
    edged = cv2.Canny(morphedImage, 25, 325)
    contours, _ = cv2.findContours(morphedImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #contours = imutils.grab_contours(contours)
    #c = max(contours, key = cv2.contourArea)

    
    output = ""
    
    for contour in contours:
        
        #approximate the number of polygonal curves
        approx = cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour, True), True)
        
        
        # if too few curves skip this contour
        if len(approx) < 3:
            continue
        
        # compute center of contour
        M = cv2.moments(contour)
        area = float(M["m00"])
        
        threshold = 3000
        
        if area < threshold:
            continue
        else:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        
        output = output + "c"
        # a for area
        # m for middle since c for center is already used
        # v for vertices
        output = output + "a" + str(area) + "m" + str(cX) + "," + str(cY) + "v"
        
        
        
        
        # get coordinates of vertices and safe them as string
        n = approx.ravel()
        i = 0
        
        for j in n:
            if(i % 2 == 0):
                x = n[i]
                y = n[i+1]
                
                output = output + str(x) + "," + str(y) + ";"
            i = i + 1
        
        
        
        
#         # drawContours(imageToDrawOnto, contourOrApproximate, 
#         #         indexOfContour (here always 0 since we are iterating over the contoursvia for), lineColor, lineThickness )
#         cv2.drawContours(img, [approx], 0, (0, 0, 255), 3)
#         x = approx.ravel()[0]
#         y = approx.ravel()[1]
#         # if we have three polygonal curves it is triangle
#         if len(approx) == 3:
#             cv2.putText(img, "Triangle", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
#         # Square
#         if len(approx) == 4:
#     #         # for checking if it square or rectangle
#     #         x, y, w, h = cv2.boundingRect(approx)
#     #         aspectRatio = float(w)/h
#     #         print(aspectRatio)
#     #         if aspectRatio >= 0.95 and aspectRatio <= 1.05:

#             cv2.putText(img, "Square", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))
#         # Pentagon
#         if len(approx) == 5:
#             cv2.putText(img, "Pentagon", (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255))

    
    data = {
        'gestureString': "",
        'contourString': output,
        'image': cv2.imencode('.jpg', edged)[1].ravel().tolist()
    }


    #  Send reply back to client
    #  In the real world usage, after you finish your work, send your output here
    socket.send_json(data)
    
    
    
    
    #  Do some 'work'.
    #  Try reducing sleep time to 0.01 to see how blazingly fast it communicates
    #  In the real world usage, you just need to replace time.sleep() with
    #  whatever work you want python to do, maybe a machine learning task?
    #time.sleep(1)
    
#     x = random.random()
#     y = random.random()
#     z = random.random()
    
#     output = str(x) + "," + str(y) + "," + str(z)
    output_byte = str.encode(output)

    #  Send reply back to client
    #  In the real world usage, after you finish your work, send your output here
    socket.send(b"%s" % output_byte)

