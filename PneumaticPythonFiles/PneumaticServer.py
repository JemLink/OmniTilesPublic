#!/usr/bin/env python
# coding: utf-8

# In[1]:

import numpy as np
import cv2

import os
from pyspin import PySpin
import matplotlib.pyplot as plt
import sys
import keyboard

#from PIL import Image
import time

# Unity python communication
import zmq
#import random

import LightDetection as ld
from utils import GestureDetection as gd

## gesture recognition
from utils import CvFpsCalc
from model import KeyPointClassifier
from model import PointHistoryClassifier

import csv
import copy
import argparse
import itertools
from collections import Counter
from collections import deque

import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

cropped = True


"""
Unity communication parameters
"""
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
unity_output = "-1"

UnityCommunication_ON = True

"""
Image preprocessing 
"""

backgroundSubtraction_ON = False
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

K = np.array([[347.85784929000965, 0.0, 401.4146339449159], [0.0, 347.73344257233083, 448.147582198276], [0.0, 0.0, 1.0]])
D = np.array([[-0.06900876503944645], [0.15906407154587035], [-0.2972276889568439], [0.14036265519404062]])


formerMessage = "END"
lastFrame = np.zeros((800, 800, 1), np.uint8)

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


def trackChanged(x):
    pass


"""
Trackbar creation and handling
"""


def createBlurTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Blur Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("FV", "Blur Track Bar", 18, 50, trackChanged)
    cv2.createTrackbar("SV", "Blur Track Bar", 5, 30, trackChanged)
    cv2.createTrackbar("TV", "Blur Track Bar", 5, 30, trackChanged)


def createImageTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Image Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("roi_x", "Image Track Bar", 605, 1000, trackChanged)
    cv2.createTrackbar("roi_y", "Image Track Bar", 949, 1500, trackChanged)


def createLightDetectionTrackbar():
    # creating trackbar to change contour size
    cv2.namedWindow('Detection Track Bar', cv2.WINDOW_NORMAL)

    cv2.createTrackbar("ThreshWithoutSub", "Detection Track Bar", 195, 255, trackChanged)
    cv2.createTrackbar("ThreshWithSub", "Detection Track Bar", 35, 255, trackChanged)
    cv2.createTrackbar("Blur", "Detection Track Bar", 5, 50, trackChanged)
    cv2.createTrackbar("StructElem", "Detection Track Bar", 15, 50, trackChanged)
    cv2.createTrackbar("maxArea", "Detection Track Bar", 4000, 5000, trackChanged)


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
    createBlurTrackbar()
    createImageTrackbar()
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

        # with mp_pose.Pose(enable_segmentation=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        # Retrieve and display images
        with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            ## for gesture recognition
            keypoint_classifier = KeyPointClassifier()

            point_history_classifier = PointHistoryClassifier()

            # Read labels ###########################################################
            with open('model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
                keypoint_classifier_labels = csv.reader(f)
                keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels]
            with open('model/point_history_classifier/point_history_classifier_label.csv', encoding='utf-8-sig') as f:
                point_history_classifier_labels = csv.reader(f)
                point_history_classifier_labels = [row[0] for row in point_history_classifier_labels]

            history_length = 16
            mode = 0

            # FPS Measurement ########################################################
            cvFpsCalc = CvFpsCalc(buffer_len=10)

            # Coordinate history #################################################################
            point_history = deque(maxlen=history_length)

            # Finger gesture history ################################################
            finger_gesture_history = deque(maxlen=history_length)
            use_brect = True
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
                            elif stringMessage == "GESTURE":
                                print("Should DETECT GESTURE")
                                data = gd.getGestureData(image_rgb, hands, mp_drawing, mp_hands, finger_gesture_history,
                                                  point_history, point_history_classifier, point_history_classifier_labels,
                                                  keypoint_classifier, keypoint_classifier_labels, mode, key)
                                formerMessage = "GESTURE"
                            else:
                                print("Should END")
                                output_byte = str.encode("END")
                                socket.send(b"%s" % output_byte)
                                break
                        else:
                            data = gd.getGestureData(image_rgb, hands, mp_drawing, mp_hands, finger_gesture_history,
                                                  point_history, point_history_classifier, point_history_classifier_labels,
                                                  keypoint_classifier, keypoint_classifier_labels, mode, key)
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
