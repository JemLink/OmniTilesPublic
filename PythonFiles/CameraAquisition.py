import time

import cv2
import numpy as np



if __name__ == '__main__':
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_SETTINGS, 1)

    startTime = time.time()
    i = 0
    while True:
        ret, frame = cap.read()

        cv2.imshow('Camera Image', frame)

        grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, threshBin = cv2.threshold(grey, 30, 255, cv2.THRESH_BINARY)
        thresh = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 9, 2)
        cv2.imshow('Threshold adaptive', thresh)
        cv2.imshow('Threshold binary', threshBin)

        if time.time() > startTime + 5:
            startTime = time.time()
            thresholdName = 'Graphics3/Threshold ' + str(i) + '.png'
            frameName = 'Graphics3/Frame ' + str(i) + '.png'
            cv2.imwrite(thresholdName, threshBin)
            cv2.imwrite(frameName, frame)
            i += 1

        key = cv2.waitKey(1)
        if key == 27:  # ESC
            break

    cv2.destroyAllWindows()