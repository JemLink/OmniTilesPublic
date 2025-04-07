#!/usr/bin/env python
# coding: utf-8

# In[1]:
import math

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

cropped = True


"""
Unity communication parameters
"""
# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind("tcp://*:5555")
# unity_output = "-1"

UnityCommunication_ON = True

"""
Image preprocessing
"""

backgroundSubtraction_ON = True

# insert the output of fisheye calibration step
Img_DIM = (800, 800)
dim1 = (800, 800)
dim2 = (800, 800)
dim3 = (800, 800)
balance = 1.0
K = np.array([[351.6318033232932, 0.0, 450.4607527123814], [0.0, 351.7439651791754, 391.2576486450391], [0.0, 0.0, 1.0]])
D = np.array([[-0.170592708935433], [0.5324235902617314], [-1.5452235955907878], [1.4793950832426657]])


lightPos = [0,0,0]
#lastFrame = np.zeros((800, 800, 1), np.uint8)
BACKGROUND = np.zeros((800, 800, 1), np.uint8)


def GetBlurredGrayScaleImageFromImage(img, blur):
    #blur = cv2.getTrackbarPos("Blur", "Detection Track Bar")
    if blur <= 0 or (blur % 2) == 0:
        blur = blur + 1
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgGray = cv2.GaussianBlur(imgGray, (blur, blur), 0)
    return imgGray


def trackChanged():
    pass


"""
Trackbar creation and handling
"""


def createImageTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Image Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("roi_x", "Image Track Bar", 500, 1000, trackChanged)
    cv2.createTrackbar("roi_y", "Image Track Bar", 1110, 1500, trackChanged)


def createDetectionTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Detection Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("Thresh", "Detection Track Bar", 70, 255, trackChanged)
    cv2.createTrackbar("Blur", "Detection Track Bar", 25, 50, trackChanged)


def getBinarizedImage(imgGray, thresh):
    th, imgThresh = cv2.threshold(imgGray, thresh, 255, cv2.THRESH_BINARY)
    return imgThresh


def lightTracking(camImg, blur, thresh):
    img = camImg
    imgGray = GetBlurredGrayScaleImageFromImage(img, blur)
    cv2.imshow("GrayScale image", imgGray)

    if backgroundSubtraction_ON:
        global BACKGROUND
        diffFrames = cv2.absdiff(BACKGROUND, imgGray)
        # BACKGROUND = imgGray
        cv2.imshow("Background Difference", diffFrames)
        print("DiffFrames ", str(cv2.countNonZero(diffFrames)))
        # if cv2.countNonZero(diffFrames) > 500000:
        #     setBackgroundImageTo(img, blur)
        imgThresh = getBinarizedImage(diffFrames, thresh)
    else:
        diffFrames = cv2.absdiff(BACKGROUND, imgGray)
        # if cv2.countNonZero(diffFrames) > 400:
        #     setBackgroundImageTo(imgGray, blur)
        imgThresh = getBinarizedImage(imgGray, thresh)

    structElem = cv2.getTrackbarPos("StructElem", "Detection Track Bar")
    detImg = cv2.morphologyEx(imgThresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (structElem, structElem)))
    imgThresh = cv2.morphologyEx(detImg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (structElem, structElem)))

    cv2.imshow("Threshold image", imgThresh)

    cX, cY = getCentroid(imgThresh)
    circleImage = imgGray.copy()
    circleImage = cv2.circle(circleImage, (cX, cY), 20, (255, 0, 0), 2)
    cv2.imshow("Detected Center", circleImage)
    return cX, cY


def getCentroid(binaryImg):
    contours, hierarchy = cv2.findContours(binaryImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #maxArea = cv2.getTrackbarPos("maxArea", "Detection Track Bar")
    totalArea = 0
    cX = 0
    cY = 0

    if len(contours) > 0:
        maxCont = contours[0]
        for c in contours:
            M = cv2.moments(c)
            area = float(M["m00"])
            # if 0 < area < maxArea:
            #     print("Area: ", str(area))
            totalArea = totalArea + area

        #minArea = 0.2 * totalArea
        for c in contours:
            M = cv2.moments(c)
            # if 0 < float(M["m00"]) < maxArea:
            x = float(M["m10"] / M["m00"])
            y = float(M["m01"] / M["m00"])
            cX = cX + x * (M["m00"] / totalArea)
            cY = cY + y * (M["m00"] / totalArea)

        #cX = int(cX / len(contours))
        #cY = int(cY / len(contours))

    return int(cX), int(cY)


def setBackgroundImageTo(image_rgb):
    global BACKGROUND
    blur = cv2.getTrackbarPos("Blur", "Detection Track Bar")
    BACKGROUND = GetBlurredGrayScaleImageFromImage(image_rgb, blur)
    #cv2.imshow("Background", BACKGROUND)


def setBackgroundImage(cam, map1, map2, blur):
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

        if cropped:
            ROI_y = cv2.getTrackbarPos("roi_y", "Image Track Bar")
            ROI_x = cv2.getTrackbarPos("roi_x", "Image Track Bar")
            array_cropped = image_rgb[ROI_y:(ROI_y + ROI_height), ROI_x:(ROI_x + ROI_width)]
            image_rgb = array_cropped.copy()  # needed to get the correct data format for further processing

        ## **** un-distort image
        if cropped:
            image_rgb = cv2.remap(image_rgb, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        ## media pipe works better on rgb image
        image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
        image_rgb = cv2.resize(image_rgb, (800, 800))
    global BACKGROUND
    BACKGROUND = GetBlurredGrayScaleImageFromImage(image_rgb, blur)
    #cv2.imshow("Background", BACKGROUND)



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

        createImageTrackbar()
        createDetectionTrackbar()

        blur = cv2.getTrackbarPos("Blur", "Detection Track Bar")
        setBackgroundImage(cam, map1, map2, blur)

        while continue_recording:
            try:

                # Process Key (ESC: end) #################################################
                key = cv2.waitKey(1)
                if key == 27:  # ESC
                    break

                ## unity communication
                if UnityCommunication_ON:
                    print("Waiting for unity")
                    #message = socket.recv()
                    #print("Received request: %s" % message)

                    #stringMessage = message.decode("utf-8")
                    #stringMessage = stringMessage.strip()
                    if stringMessage == "END":
                        print("Should END")
                        output_byte = str.encode("END")
                        #socket.send(b"%s" % output_byte)
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
                    image_rgb = cv2.flip(rgb_array, 1)

                    ## **** Resizing / Cropping *****
                    ## RESIZING the image since it would be 2048x2048 otherwise (kind of too big for the window)

                    ## we might have to size this further down for mediapipe to run fast

                    if cropped:

                        ROI_y = cv2.getTrackbarPos("roi_y", "Image Track Bar")
                        ROI_x = cv2.getTrackbarPos("roi_x", "Image Track Bar")
                        array_cropped = image_rgb[ROI_y:(ROI_y + ROI_height), ROI_x:(ROI_x + ROI_width)]
                        image_rgb = array_cropped.copy()  # needed to get the correct data format for further processing

                    ## **** un-distort image
                    if cropped:
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

                    thresh = cv2.getTrackbarPos("Thresh", "Detection Track Bar")
                    blur = cv2.getTrackbarPos("Blur", "Detection Track Bar")
                    center = lightTracking(image_rgb, blur, thresh)
                    if center == (0,0):
                        centerMessage = "NotDrawing"
                    else:
                        centerMessage = str(center[0]) + "," + str(center[1])

                    end = time.time()
                    print("Time ", end - start)

                    # cv2.imshow('Camera Image', image_rgb)
                    if cv2.waitKey(5) & 0xFF == 27:
                        continue_recording = False
                        break

                    #### Unity communication end ####

                    if UnityCommunication_ON:
                        # need to flip the image before sending it unity
                        image_rgb = cv2.flip(image_rgb, 1)

                        ## the first part needs to be the same name as in the unity data
                        data = {
                            'messageString': "Running",
                            'centerMessage': centerMessage,
                            'image': cv2.imencode('.jpg', image_rgb)[1].ravel().tolist()
                        }

                        #  Send reply to client
                        #  In the real world usage, after you finish your work, send your output here
                        #socket.send_json(data)

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
