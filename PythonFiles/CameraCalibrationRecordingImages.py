## This is for capturing the images from the cam and safe it at location
## capture images with c and quit program with q


# Spinnaker SDK
import os
from pyspin import PySpin as spin
import sys
import keyboard
import cv2

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
# Acquisition.py shows how to acquire images. It relies on
# information provided in the Enumeration example. Also, check out the
# ExceptionHandling and NodeMapInfo examples if you haven't already.
# ExceptionHandling shows the handling of standard and Spinnaker exceptions
# while NodeMapInfo explores retrieving information from various node types.
#
# This example touches on the preparation and cleanup of a camera just before
# and just after the acquisition of images. Image retrieval and conversion,
# grabbing image data, and saving images are all covered as well.
#
# Once comfortable with Acquisition, we suggest checking out
# AcquisitionMultipleCamera, NodeMapCallback, or SaveToAvi.
# AcquisitionMultipleCamera demonstrates simultaneously acquiring images from
# a number of cameras, NodeMapCallback serves as a good introduction to
# programming with callbacks and events, and SaveToAvi exhibits video creation.


## parameters

calibPictureFilename = "Test"
ROI_y = 949
ROI_x = 633
ROI_height = 800
ROI_width = 800


def acquire_images(cam, nodemap, nodemap_tldevice):
    """
    This function acquires and saves 10 images from a device.

    :param cam: Camera to acquire images from.
    :param nodemap: Device nodemap.
    :param nodemap_tldevice: Transport layer device nodemap.
    :type cam: CameraPtr
    :type nodemap: INodeMap
    :type nodemap_tldevice: INodeMap
    :return: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** IMAGE ACQUISITION ***\n')
    try:
        result = True

        # Set acquisition mode to continuous
        #
        #  *** NOTES ***
        #  Because the example acquires and saves 10 images, setting acquisition
        #  mode to continuous lets the example finish. If set to single frame
        #  or multiframe (at a lower number of images), the example would just
        #  hang. This would happen because the example has been written to
        #  acquire 10 images while the camera would have been programmed to
        #  retrieve less than that.
        #
        #  Setting the value of an enumeration node is slightly more complicated
        #  than other node types. Two nodes must be retrieved: first, the
        #  enumeration node is retrieved from the nodemap; and second, the entry
        #  node is retrieved from the enumeration node. The integer value of the
        #  entry node is then set as the new value of the enumeration node.
        #
        #  Notice that both the enumeration and the entry nodes are checked for
        #  availability and readability/writability. Enumeration nodes are
        #  generally readable and writable whereas their entry nodes are only
        #  ever readable.
        #
        #  Retrieve enumeration node from nodemap

        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        node_acquisition_mode = spin.CEnumerationPtr(nodemap.GetNode('AcquisitionMode'))
        if not spin.IsAvailable(node_acquisition_mode) or not spin.IsWritable(node_acquisition_mode):
            print('Unable to set acquisition mode to continuous (enum retrieval). Aborting...')
            return False

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName('Continuous')
        if not spin.IsAvailable(node_acquisition_mode_continuous) or not spin.IsReadable(
                node_acquisition_mode_continuous):
            print('Unable to set acquisition mode to continuous (entry retrieval). Aborting...')
            return False

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        print('Acquisition mode set to continuous...')

        #  Begin acquiring images
        #
        #  *** NOTES ***
        #  What happens when the camera begins acquiring images depends on the
        #  acquisition mode. Single frame captures only a single image, multi
        #  frame catures a set number of images, and continuous captures a
        #  continuous stream of images. Because the example calls for the
        #  retrieval of 10 images, continuous mode has been set.
        #
        #  *** LATER ***
        #  Image acquisition must be ended when no more images are needed.
        # cam.PixelFormat.SetValue(spin.PixelFormat_BGR8)
        cam.BeginAcquisition()

        print('Acquiring images...')

        #  Retrieve device serial number for filename
        #
        #  *** NOTES ***
        #  The device serial number is retrieved in order to keep cameras from
        #  overwriting one another. Grabbing image IDs could also accomplish
        #  this.
        device_serial_number = ''
        node_device_serial_number = spin.CStringPtr(nodemap_tldevice.GetNode('DeviceSerialNumber'))
        if spin.IsAvailable(node_device_serial_number) and spin.IsReadable(node_device_serial_number):
            device_serial_number = node_device_serial_number.GetValue()
            print('Device serial number retrieved as %s...' % device_serial_number)

        # Retrieve, convert, and save images
        ## for continous tream: change this into while true?
        i = 0
        while not keyboard.is_pressed('q'):
            try:
                if keyboard.is_pressed('c'):  # if key 'c' is pressed
                    print('You Pressed A Key!')
                    i = i + 1

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
                    #
                    #  *** NOTES ***
                    #  Images can easily be checked for completion. This should be
                    #  done whenever a complete image is expected or required.
                    #  Further, check image status for a little more insight into
                    #  why an image is incomplete.
                    if image_result.IsIncomplete():
                        print('Image incomplete with image status %d ...' % image_result.GetImageStatus())

                    else:

                        #  Print image information; height and width recorded in pixels
                        #
                        #  *** NOTES ***
                        #  Images have quite a bit of available metadata including
                        #  things such as CRC, image status, and offset values, to
                        #  name a few.
                        width = image_result.GetWidth()
                        height = image_result.GetHeight()
                        print('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

                        #  Convert image to mono 8
                        #
                        #  *** NOTES ***
                        #  Images can be converted between pixel formats by using
                        #  the appropriate enumeration value. Unlike the original
                        #  image, the converted one does not need to be released as
                        #  it does not affect the camera buffer.
                        #
                        #  When converting images, color processing algorithm is an
                        #  optional parameter.

                        ## This converts it to GreyScale
                        # image_converted = image_result.Convert(spin.PixelFormat_Mono8, spin.HQ_LINEAR)
                        ## This converts it to RGB
                        # image_converted = image_result.Convert(spin.PixelFormat_BGR8)

                        image_converted = image_result.Convert(spin.PixelFormat_BGR8)
                        rgb_array = image_converted.GetData()
                        rgb_array = rgb_array.reshape(height, width, 3)

                        ## process mediapipe on image
                        image_rgb = cv2.cvtColor(cv2.flip(rgb_array, 1), cv2.COLOR_BGR2RGB)

                        ## **** Resizing / Cropping *****

                        ## RESIZING the image since it would be 2048x2048 otherwise (kind of too big for the window)
                        # image_rgb = cv2.resize(image_rgb, (800, 800))
                        ## this is to display potential cropping region in the downscaled image
                        # scale = 800/2048
                        # cv2.rectangle(image_rgb, (int(650*scale), int(580*scale)), (int(1450*scale), int(1380*scale)), (0, 255, 0), 3)

                        ## CROPPPING the region of the lens (should be around 800 to fit with the setup so far...)
                        ## This is the cropping
                        ## These values are taken from the unity config
                        ## They might change... [y:y+h, x:x+h]
                        array_cropped = image_rgb[ROI_y:(ROI_y + ROI_height), ROI_x:(ROI_x + ROI_width)]
                        image_rgb = array_cropped.copy()  # needed to get the correct data format for further processing

                        image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                        ## Saving the image to a folder
                        # Create a unique filename
                        if calibPictureFilename:
                            filename = 'CameraFeed\%s-%d.jpg' % (calibPictureFilename, i)
                        else:
                            if device_serial_number:
                                filename = 'CameraFeed\Acquisition-%s-%d.jpg' % (device_serial_number, i)
                            else:  # if serial number is empty
                                filename = 'CameraFeed\Acquisition-%d.jpg' % i

                        #  Save image
                        #
                        #  *** NOTES ***
                        #  The standard practice of the examples is to use device
                        #  serial numbers to keep images of one device from
                        #  overwriting those of another.
                        # image_converted.Save(filename)
                        cv2.imwrite(filename, image_rgb)
                        print('Image saved at %s' % filename)

                        #  Release image
                        #
                        #  *** NOTES ***
                        #  Images retrieved directly from the camera (i.e. non-converted
                        #  images) need to be released in order to keep from filling the
                        #  buffer.
                        image_result.Release()
                        print('')
                else:
                    ## when no capturing key is pressed the image still needs to be loaded, otherwise the images will pile up in the buffer
                    image_result = cam.GetNextImage(1000)
                    image_result.Release()

            except spin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False

        #  End acquisition
        #
        #  *** NOTES ***
        #  Ending acquisition appropriately helps ensure that devices clean up
        #  properly and do not need to be power-cycled to maintain integrity.
        cam.EndAcquisition()

    except spin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer; please see NodeMapInfo example for more in-depth comments on printing
    device information from the nodemap.

    :param nodemap: Transport layer device nodemap.
    :type nodemap: INodeMap
    :returns: True if successful, False otherwise.
    :rtype: bool
    """

    print('*** DEVICE INFORMATION ***\n')

    try:
        result = True
        node_device_information = spin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if spin.IsAvailable(node_device_information) and spin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = spin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if spin.IsReadable(node_feature) else 'Node not readable'))

        else:
            print('Device control information not available.')

    except spin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

    return result


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

        # Retrieve TL device nodemap and print device information
        nodemap_tldevice = cam.GetTLDeviceNodeMap()

        result &= print_device_info(nodemap_tldevice)

        # Initialize camera
        cam.Init()

        # Retrieve GenICam nodemap
        nodemap = cam.GetNodeMap()

        # Acquire images
        result &= acquire_images(cam, nodemap, nodemap_tldevice)

        # Deinitialize camera
        cam.DeInit()

    except spin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

    return result


def main():
    """
    Example entry point; please see Enumeration example for more in-depth
    comments on preparing and cleaning up the system.

    :return: True if successful, False otherwise.
    :rtype: bool
    """

    # Since this application saves images in the current folder
    # we must ensure that we have permission to write to this folder.
    # If we do not have permission, fail right away.
    try:
        test_file = open('test.txt', 'w+')
    except IOError:
        print('Unable to write to current directory. Please check permissions.')
        input('Press Enter to exit...')
        return False

    test_file.close()
    os.remove(test_file.name)

    result = True

    # Retrieve singleton reference to system object
    system = spin.System.GetInstance()

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
    return result


if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)