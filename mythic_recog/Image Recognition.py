import time
import cv2
import numpy as np
import mss
import pyautogui as pag  # Mouse
import pydirectinput as pdi  # Keyboard


class LootFinder:
    def __init__(self):
        sct = mss.mss()
        # Screenshots the chest window
        self.left = 0
        self.top = 40
        scr = sct.grab({'left': self.left, 'top': self.top, 'width': 1960, 'height': 1000})
        # Get raw pixels from screen and save to numpy array
        self.window = np.array(scr)
        self.target = cv2.imread('smol_mythic.png', cv2.IMREAD_UNCHANGED)
        cv2.imshow('',self.window)
        result = cv2.matchTemplate(self.window, self.target,
                                   cv2.TM_CCORR_NORMED)  # Searches of matches | it rates them from 0 to 1
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)  # takes the min/max value and location of the results
        print(max_val, min_val)
        # Object dimensions
        width = self.target.shape[1]
        height = self.target.shape[0]

        threshold = 0.98
        yloc, xloc = np.where(result >= threshold)  # Only takes matches which have results above 0.92
        print(len(yloc))
        match = []
        for (x, y) in zip(xloc, yloc):  # Highlight the match
            match += [[int(x), int(y), int(width), int(height)]]
            match += [[int(x), int(y), int(width), int(height)]]
        matches, weights = cv2.groupRectangles(match, 1, 0.2)

        for (x, y, w, h) in matches:
            cv2.rectangle(self.window, (x, y), (x + width, y + height), (0, 255, 255), 1)
        cv2.imshow('', self.window)
        cv2.waitKey()

    def mythic_checker(self):
        # Import self.target images | numpy image array
        self.target = cv2.imread('mythic.png', cv2.IMREAD_UNCHANGED)
        self.filter()

    def legendary_checker(self):
        # Import self.target images | numpy image array
        self.target = cv2.imread('legendary.png', cv2.IMREAD_UNCHANGED)
        self.filter()

    def filter(self):
        result = cv2.matchTemplate(self.window, self.target, cv2.TM_CCORR_NORMED)  # Searches of matches | it rates them from 0 to 1

        # Object dimensions
        self.width = self.target.shape[1]
        self.height = self.target.shape[0]

        threshold = 0.99
        self.yloc, self.xloc = np.where(result >= threshold)  # Only takes matches which have results above 'threshold'
        match = []
        for (x, y) in zip(self.xloc, self.yloc):  # Highlight the match
            match += [[int(x), int(y), int(self.width), int(self.height)]]
            match += [[int(x), int(y), int(self.width), int(self.height)]]

        matches, weights = cv2.groupRectangles(match, 1, 0.2)  # Filters similar results - by 0.2

        x = []
        y = []
        for coords in matches:
            x += [coords[0]]
            y += [coords[1]]

        try:
            for (x, y) in zip(x, y):
                pag.moveTo(self.left + x + 10, self.top + y + 10)
                pdi.keyDown('shift')
                pag.mouseDown(button='left')
                pag.mouseUp(button='left')
                pdi.keyUp('shift')
        except NameError:
            return 'nope'
        finally:
            pass


time.sleep(2)
lootfinder = LootFinder()
lootfinder.mythic_checker()
lootfinder.legendary_checker()
