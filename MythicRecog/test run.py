import time
import cv2
import numpy as np
import win32api
import win32con
import mss


def image_recog(window):
    # Import images | numpy image array
    target = cv2.imread('mythic box.png', cv2.IMREAD_UNCHANGED)

    result = cv2.matchTemplate(window, target, cv2.TM_CCORR_NORMED)  # Searches of matches | it rates them from 0 to 1
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)  # takes the min/max value and location of the results
    print(max_val, min_val)
    # Object dimensions
    width = target.shape[1]
    height = target.shape[0]

    threshold = 0.94
    yloc, xloc = np.where(result >= threshold)  # Only takes matches which have results above 0.92

    match = []
    for (x, y) in zip(xloc, yloc):  # Highlight the match
        match += [[int(x), int(y), int(width), int(height)]]
        match += [[int(x), int(y), int(width), int(height)]]
    matches, weights = cv2.groupRectangles(match, 1, 0.2)

    for (x, y, w, h) in matches:
        cv2.rectangle(window, (x, y), (x + width, y + height), (0, 255, 255), 1)

    cv2.imshow('Window', window)
    cv2.waitKey()
    cv2.destroyAllWindows()


window1 = cv2.imread('mythic boxes.png', cv2.IMREAD_UNCHANGED)
window2 = cv2.imread('small mythic box.png', cv2.IMREAD_UNCHANGED)
window3 = cv2.imread('weird mythic boxes.png', cv2.IMREAD_UNCHANGED)

image_recog(window1)
image_recog(window2)
image_recog(window3)
