# Unity python communication
import zmq
import numpy as np
import cv2
import os
from pyspin import PySpin
import matplotlib.pyplot as plt
import sys
import keyboard


"""
Unity communication parameters
"""
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
unity_output = "-1"


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


tri = ""  # "[30,(80,80,0),(v20,20v20,90v90,90)]"
squ = "[0,(320,320,0),(v400,300v550,300v550,550v300,550)]"
pen = ""  # "[50,(80,80,0),(v20,20v20,90v90,90v90,20v55,55)]"

continue_recording = True


def main():
    #
    # print("Triangle: ", str(len(trianglesVal)))
    # tri = ShapesToString(trianglesVal)
    # print("Square", str(len(squaresVal)))
    # squ = ShapesToString(squaresVal)
    # print("Pentagon", str(len(pentagonsVal)))
    # pen = ShapesToString(pentagonsVal)

    while continue_recording:

        print("Waiting for unity")
        message = socket.recv()
        print("Received request: %s" % message)
        # unity_output = "-1"  # when no gesture is detected -1 will be returned

        stringMessage = message.decode("utf-8")
        stringMessage = stringMessage.strip()
        if stringMessage == "END":
            print("Should END")
            output_byte = str.encode("END")
            socket.send(b"%s" % output_byte)
            break

        image_rgb = np.zeros((800, 800, 1), np.uint8)

        if stringMessage == "DRAWING":
            data = {
                'messageString': "Running",
                'centerMessage': "NotDrawing",
                'image': cv2.imencode('.jpg', image_rgb)[1].ravel().tolist()
            }
            
        elif stringMessage == "TILES":
            ## the first part needs to be the same name as in the unity data
            data = {
                'messageString': "TILES",
                'trianglesMessage': tri,
                'squaresMessage': squ,
                'pentagonsMessage': pen,
                'image': cv2.imencode('.jpg', image_rgb)[1].ravel().tolist()
            }

        socket.send_json(data)


if __name__ == '__main__':
    if main():
        sys.exit(0)
    else:
        sys.exit(1)