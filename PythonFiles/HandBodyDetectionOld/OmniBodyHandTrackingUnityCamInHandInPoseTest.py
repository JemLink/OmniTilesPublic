#!/usr/bin/env python
# coding: utf-8

# In[ ]:


## another cam aquisition
## so far it is way faster :D


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

import os
from pyspin import PySpin
import matplotlib.pyplot as plt
import sys
import keyboard
import time



# Mediapipe hand tracking and OpenCV and Pillow
import cv2

from PIL import Image
import numpy as np

import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


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


# Unity python communication
#import time #already imported above
import zmq
import random

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
unity_output = "-1"


# insert the output of fisheye calibration step
Img_DIM=(800, 800)
dim1=(800, 800)
dim2=(800, 800)
dim3=(800, 800)
balance = 1.0
K=np.array([[351.6318033232932, 0.0, 450.4607527123814], [0.0, 351.7439651791754, 391.2576486450391], [0.0, 0.0, 1.0]])
D=np.array([[-0.170592708935433], [0.5324235902617314], [-1.5452235955907878], [1.4793950832426657]])


ROI_y = 850
ROI_x = 550
ROI_height = 800
ROI_width = 800



global continue_recording
continue_recording = True


BG_COLOR = (0, 0, 0) # black


def handle_close(evt):
    """
    This function will close the GUI when close event happens.

    :param evt: Event that occurs when the figure closes.
    :type evt: Event
    """

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

    # Change bufferhandling mode to NewestOnly
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
        ## gesture recognition
        result = True
        use_brect = True
        
        ## media pipe
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
        device_serial_number = ''
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
        
        print('Waiting for Unity3D to start communication')
        
        ## this is for the pose aquisition
        with mp_pose.Pose(
            enable_segmentation=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        

            # Retrieve and display images
            with mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:

                ## for gesture recognition
                keypoint_classifier = KeyPointClassifier()

                point_history_classifier = PointHistoryClassifier()

                # Read labels ###########################################################
                with open('../model/keypoint_classifier/keypoint_classifier_label.csv', encoding='utf-8-sig') as f:
                    keypoint_classifier_labels = csv.reader(f)
                    keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels]
                with open('../model/point_history_classifier/point_history_classifier_label.csv', encoding='utf-8-sig') as f:
                    point_history_classifier_labels = csv.reader(f)
                    point_history_classifier_labels = [row[0] for row in point_history_classifier_labels]

                # FPS Measurement ########################################################
                cvFpsCalc = CvFpsCalc(buffer_len=10)

                # Coordinate history #################################################################
                history_length = 16
                point_history = deque(maxlen=history_length)

                # Finger gesture history ################################################
                finger_gesture_history = deque(maxlen=history_length)

                #  ########################################################################

                mode = 0

                while(continue_recording):
                    try:


                        fps = cvFpsCalc.get()
                        # Process Key (ESC: end) #################################################
                        key = cv2.waitKey(1)
                        if key == 27:  # ESC
                            break
                        number, mode = select_mode(key, mode)


                        
                            




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

                        image_result = cam.GetNextImage()

                        #  Ensure image completion
                        if image_result.IsIncomplete():
                            print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                        else:

                            ## This is 2048x2048 so we need to crop it to the ROI from the lense
                            width = image_result.GetWidth()
                            height = image_result.GetHeight()


                            ## This converts it to GreyScale
                            #image_converted = image_result.Convert(spin.PixelFormat_Mono8, spin.HQ_LINEAR)
                            ## This converts it to RGB
                            image_converted = image_result.Convert(PySpin.PixelFormat_BGR8)
                            rgb_array = image_converted.GetData()
                            rgb_array = rgb_array.reshape(height, width, 3)


                            ## process mediapipe on image
                            #image_rgb = cv2.cvtColor(cv2.flip(rgb_array, 1), cv2.COLOR_BGR2RGB)
                            image_rgb = cv2.flip(rgb_array, 1)
                            
                            
                            ## unity communication
                            message = socket.recv()
                            print("Received request: %s" % message)
                            unity_output = "-1" # when no gesture/pose is detected -1 will be returned

                            stringMessage = message.decode("utf-8")
                            stringMessage = stringMessage.strip()
                            ## this is to stop the running program
                            if stringMessage == "END":
                                print("Should END")
                                ## create the data that contains a string for the gesture etc and an iamge of the pose
#                                 data = {
#                                     'messageString': 'END',
#                                     'image': cv2.imencode('.jpg', image_rgb)[1].ravel().tolist()
#                                 }
                                output_byte = str.encode("END") #this was just for gesture
                                socket.send_json(output_byte)
                                break


                            ## **** Resizing / Croping *****

                            ## RESIZING the image since it would be 2048x2048 otherwise (kind of too big for the window)

                            ## we might have to size this further down for mediapipe to run fast
                            image_rgb = cv2.resize(image_rgb, (800, 800))
                            # scale = 800/2048   
                            ## this is to display potential cropping region in the downscaled image
                            # cv2.rectangle(image_rgb, (int(650*scale), int(580*scale)), (int(1450*scale), int(1380*scale)), (0, 255, 0), 3)

                            ## CROPPPING the region of the lense (should be around 800 to fit with the setup so far...)
                            ## This is the cropping
                            ## These values are taken from the unity config
                            ## They might change...
                            #array_cropped = image_rgb[ROI_y:(ROI_y + ROI_height), ROI_x:(ROI_x + ROI_width)]
                            #image_rgb = array_cropped.copy() # needed to get the correct data format for further processing




                            ## **** un-distort image

                            #undistorted_img = cv2.remap(image_rgb, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
                            image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)  
                            
                            
                            
                            ## **** Mediapipe Pose Detection ****
                            poseResults = pose.process(image_rgb)


                            ## **** Mediapipe hand detection ****
                            image_rgb.flags.writeable = False
                            results = hands.process(image_rgb)
                            image_rgb.flags.writeable = True

                            
                            ## convert image back to bgr for outputting it in rgb with the cam (python is confusing...)
                            image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)



                            #gesture recongition output and pose recognition output
                            debug_image = copy.deepcopy(image_rgb)
                            pose_image = copy.deepcopy(image_rgb)
                            
                            
                            output_image = np.zeros(pose_image.shape, dtype=np.uint8)
                            output_image[:] = BG_COLOR
                            if poseResults.pose_landmarks:
                                ## Draw the pose annotations on the image
#                                 mp_drawing.draw_landmarks(
#                                     pose_image,
#                                     poseResults.pose_landmarks,
#                                     mp_pose.POSE_CONNECTIONS,
#                                     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()) 

                                #annotated_image = pose_image.copy()
                                # Draw segmentation on the image.
                                # To improve segmentation around boundaries, consider applying a joint
                                # bilateral filter to "results.segmentation_mask" with "image".
                                 condition = np.stack((poseResults.segmentation_mask,) * 3, axis=-1) > 0.1
                                 bg_image = np.zeros(pose_image.shape, dtype=np.uint8)
                                 bg_image[:] = BG_COLOR
                                 output_image = np.where(condition, pose_image, bg_image)
                            

                            # Draw the hand annotations on the image.
                            if results.multi_hand_landmarks:

                                # need to overwrite unity_output so that it will not start with -1
                                unity_output = ""

                                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,results.multi_handedness):
                                    mp_drawing.draw_landmarks(image_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                                    ## gesture recognition

                                    # Bounding box calculation
                                    brect = calc_bounding_rect(debug_image, hand_landmarks)
                                    # Landmark calculation
                                    landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                                    ## Landmark calcualtion with 3 coordinates
                                    hand_landmarks_list = get_hand_landmarks_list(debug_image, hand_landmarks)

                                    # Conversion to relative coordinates / normalized coordinates
                                    pre_processed_landmark_list = pre_process_landmark(landmark_list)
                                    pre_processed_point_history_list = pre_process_point_history(debug_image, point_history)
                                    # Write to the dataset file
                                    logging_csv(number, mode, pre_processed_landmark_list, pre_processed_point_history_list)

                                    # Hand sign classification
                                    hand_sign_id = keypoint_classifier(pre_processed_landmark_list)
                                    if hand_sign_id == 2:  # Point gesture
                                        point_history.append(landmark_list[8])
                                    else:
                                        point_history.append([0, 0])

                                    # Finger gesture classification
                                    finger_gesture_id = 0
                                    point_history_len = len(pre_processed_point_history_list)
                                    if point_history_len == (history_length * 2):
                                        finger_gesture_id = point_history_classifier(pre_processed_point_history_list)

                                    # Calculates the gesture IDs in the latest detection
                                    finger_gesture_history.append(finger_gesture_id)
                                    most_common_fg_id = Counter(finger_gesture_history).most_common()

                                    # Drawing part
                                    debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                                    debug_image = draw_landmarks(debug_image, landmark_list)
                                    debug_image = draw_info_text(
                                        debug_image,
                                        brect,
                                        handedness,
                                        keypoint_classifier_labels[hand_sign_id],
                                        point_history_classifier_labels[most_common_fg_id[0][0]],
                                    )

                                    # writing hand_sign to unity output
                                    unity_output = unity_output + str(hand_sign_id)

                                    ## Landmark calcualtion with 3 coordinates
                                    hand_landmarks_list = get_hand_landmarks_list(debug_image, hand_landmarks)
                                    ## convert hand_landmarks_list to string
                                    string_list = ";".join(str(x) for x in hand_landmarks_list)
                                    #print("normalized hand_landmarks: " + string_list)

                                    # add an "h" for showing that one hand is finished
                                    unity_output = unity_output + ":" + string_list + "h"





                            cv2.imshow('Hand Gesture Recognition', debug_image)    
                            cv2.imshow('MediaPipe Hands', image_rgb)
                            cv2.imshow('MediaPipe Pose Segmentation mask', output_image) 
                            if cv2.waitKey(5) & 0xFF == 27:
                                break


                            ## write gesture output to send to unity
                            output_byte = str.encode(unity_output)
#                             data = {
#                                     'messageString': output_byte,
#                                     'image': cv2.imencode('.jpg', output_image)[1].ravel().tolist()
#                                 }
                            

                            #  Send reply back to client
                            #  In the real world usage, after you finish your work, send your output here
                            socket.send(output_byte)




                        #image_result.Release()

                        # Getting the image data as a numpy array
                        #image_data = image_result.GetNDArray()

                        # Draws an image on the current figure
                        #plt.imshow(image_data, cmap='gray')

                        # Interval in plt.pause(interval) determines how fast the images are displayed in a GUI
                        # Interval is in seconds.
                        #plt.pause(0.001)

                        # Clear current reference of a figure. This will improve display speed significantly
                        #plt.clf()

                        # If user presses enter, close the program
                        if keyboard.is_pressed('ENTER'):
                            print('Program is closing...')

                            # Close figure
                            plt.close('all')             
                            input('Done! Press Enter to exit...')
                            continue_recording=False                        

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
        cam.EndAcquisition()

    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return True






## gesture recognition

## converting hand_landmarks to sendable vector3 string list?
## returns a list of all handmarks and their 3 coordinates (normalized)
def get_hand_landmarks_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = landmark.x
        landmark_y = landmark.y
        landmark_z = landmark.z
        #landmark_x = min(int(landmark.x * image_width), image_width - 1)
        #landmark_y = min(int(landmark.y * image_height), image_height - 1)
        #landmark_z = landmark.z

        
        ## need the brackets for this function
        landmark_point.append([landmark_x, landmark_y, landmark_z])

    return landmark_point







## gesture recognition functions

def select_mode(key, mode):
    number = -1
    if 48 <= key <= 57:  # 0 ~ 9
        number = key - 48
    if key == 110:  # n
        mode = 0
    if key == 107:  # k
        mode = 1
    if key == 104:  # h
        mode = 2
    return number, mode

def calc_bounding_rect(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_array = np.empty((0, 2), int)

    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)

        landmark_point = [np.array((landmark_x, landmark_y))]

        landmark_array = np.append(landmark_array, landmark_point, axis=0)

    x, y, w, h = cv2.boundingRect(landmark_array)

    return [x, y, x + w, y + h]


def calc_landmark_list(image, landmarks):
    image_width, image_height = image.shape[1], image.shape[0]

    landmark_point = []

    # Keypoint
    for _, landmark in enumerate(landmarks.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        # landmark_z = landmark.z

        landmark_point.append([landmark_x, landmark_y])

    return landmark_point


def pre_process_landmark(landmark_list):
    temp_landmark_list = copy.deepcopy(landmark_list)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, landmark_point in enumerate(temp_landmark_list):
        if index == 0:
            base_x, base_y = landmark_point[0], landmark_point[1]

        temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
        temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

    # Convert to a one-dimensional list
    temp_landmark_list = list(
        itertools.chain.from_iterable(temp_landmark_list))

    # Normalization
    max_value = max(list(map(abs, temp_landmark_list)))

    def normalize_(n):
        return n / max_value

    temp_landmark_list = list(map(normalize_, temp_landmark_list))

    return temp_landmark_list


def pre_process_point_history(image, point_history):
    image_width, image_height = image.shape[1], image.shape[0]

    temp_point_history = copy.deepcopy(point_history)

    # Convert to relative coordinates
    base_x, base_y = 0, 0
    for index, point in enumerate(temp_point_history):
        if index == 0:
            base_x, base_y = point[0], point[1]

        temp_point_history[index][0] = (temp_point_history[index][0] -
                                        base_x) / image_width
        temp_point_history[index][1] = (temp_point_history[index][1] -
                                        base_y) / image_height

    # Convert to a one-dimensional list
    temp_point_history = list(
        itertools.chain.from_iterable(temp_point_history))

    return temp_point_history


def logging_csv(number, mode, landmark_list, point_history_list):
    if mode == 0:
        pass
    if mode == 1 and (0 <= number <= 9):
        csv_path = '../model/keypoint_classifier/keypoint.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *landmark_list])
    if mode == 2 and (0 <= number <= 9):
        csv_path = '../model/point_history_classifier/point_history.csv'
        with open(csv_path, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, *point_history_list])
    return

def draw_landmarks(image, landmark_point):
    if len(landmark_point) > 0:
        # Thumb
        cv2.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[2]), tuple(landmark_point[3]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[3]), tuple(landmark_point[4]),
                (255, 255, 255), 2)

        # Index finger
        cv2.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[5]), tuple(landmark_point[6]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[6]), tuple(landmark_point[7]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[7]), tuple(landmark_point[8]),
                (255, 255, 255), 2)

        # Middle finger
        cv2.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[9]), tuple(landmark_point[10]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[10]), tuple(landmark_point[11]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[11]), tuple(landmark_point[12]),
                (255, 255, 255), 2)

        # Ring finger
        cv2.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[13]), tuple(landmark_point[14]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[14]), tuple(landmark_point[15]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[15]), tuple(landmark_point[16]),
                (255, 255, 255), 2)

        # Little finger
        cv2.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[17]), tuple(landmark_point[18]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[18]), tuple(landmark_point[19]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[19]), tuple(landmark_point[20]),
                (255, 255, 255), 2)

        # Palm
        cv2.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[0]), tuple(landmark_point[1]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[1]), tuple(landmark_point[2]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[2]), tuple(landmark_point[5]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[5]), tuple(landmark_point[9]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[9]), tuple(landmark_point[13]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[13]), tuple(landmark_point[17]),
                (255, 255, 255), 2)
        cv2.line(image, tuple(landmark_point[17]), tuple(landmark_point[0]),
                (0, 0, 0), 6)
        cv2.line(image, tuple(landmark_point[17]), tuple(landmark_point[0]),
                (255, 255, 255), 2)

    # Key Points
    for index, landmark in enumerate(landmark_point):
        if index == 0:  # 手首1
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 1:  # 手首2
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 2:  # 親指：付け根
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 3:  # 親指：第1関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 4:  # 親指：指先
            cv2.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
        if index == 5:  # 人差指：付け根
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 6:  # 人差指：第2関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 7:  # 人差指：第1関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 8:  # 人差指：指先
            cv2.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
        if index == 9:  # 中指：付け根
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 10:  # 中指：第2関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 11:  # 中指：第1関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 12:  # 中指：指先
            cv2.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
        if index == 13:  # 薬指：付け根
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 14:  # 薬指：第2関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 15:  # 薬指：第1関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 16:  # 薬指：指先
            cv2.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)
        if index == 17:  # 小指：付け根
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 18:  # 小指：第2関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 19:  # 小指：第1関節
            cv2.circle(image, (landmark[0], landmark[1]), 5, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 5, (0, 0, 0), 1)
        if index == 20:  # 小指：指先
            cv2.circle(image, (landmark[0], landmark[1]), 8, (255, 255, 255),
                      -1)
            cv2.circle(image, (landmark[0], landmark[1]), 8, (0, 0, 0), 1)

    return image


def draw_bounding_rect(use_brect, image, brect):
    if use_brect:
        # Outer rectangle
        cv2.rectangle(image, (brect[0], brect[1]), (brect[2], brect[3]),
                     (0, 0, 0), 1)

    return image


def draw_info_text(image, brect, handedness, hand_sign_text,
                   finger_gesture_text):
    cv2.rectangle(image, (brect[0], brect[1]), (brect[2], brect[1] - 22),
                 (0, 0, 0), -1)

    info_text = handedness.classification[0].label[0:]
    if hand_sign_text != "":
        info_text = info_text + ':' + hand_sign_text
    cv2.putText(image, info_text, (brect[0] + 5, brect[1] - 4),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

    if finger_gesture_text != "":
        cv2.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(image, "Finger Gesture:" + finger_gesture_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2,
                   cv2.LINE_AA)

    return image


def draw_point_history(image, point_history):
    for index, point in enumerate(point_history):
        if point[0] != 0 and point[1] != 0:
            cv2.circle(image, (point[0], point[1]), 1 + int(index / 2),
                      (152, 251, 152), 2)

    return image


def draw_info(image, fps, mode, number):
    cv2.putText(image, "FPS:" + str(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
               1.0, (0, 0, 0), 4, cv2.LINE_AA)
    cv2.putText(image, "FPS:" + str(fps), (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
               1.0, (255, 255, 255), 2, cv2.LINE_AA)

    mode_string = ['Logging Key Point', 'Logging Point History']
    if 1 <= mode <= 2:
        cv2.putText(image, "MODE:" + mode_string[mode - 1], (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                   cv2.LINE_AA)
        if 0 <= number <= 9:
            cv2.putText(image, "NUM:" + str(number), (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1,
                       cv2.LINE_AA)
    return image


















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

