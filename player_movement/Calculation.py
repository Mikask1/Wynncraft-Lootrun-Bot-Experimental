import concurrent.futures
import time
import re
import mss
import cv2
import pytesseract
import numpy as np
from timeit import default_timer as timer
import pyautogui as pag
import pydirectinput as pdi
import math

LIST_OF_COORDINATES = [(-46, 239), (-38, 235), (-42, 222), (-36, 222), (-36, 225), (-27, 228), (100, 100)]
LIST_OF_SPECIAL = [4, 5]

# 143 pixels = 90
# 286 = 180
# 571 = 360
def round(num):  # Rounds the number the way most people are educated with
    if num % 1 >= 0.5:
        return math.ceil(num)
    return math.floor(num)


def convert_positive(value):  # Converts negative value degrees to positive (2 pi)
    if value < 0:
        return 360 + value
    return value


class PlayerMovement:
    def __init__(self):
        self.sct = mss.mss()  # Initialize mss class
        pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Tesseract executable location
        self.counter = 0

        # Screenshot start points (Coordinated and Rotation)
        self.left_coordinate = 0
        self.top_coordinate = 225
        self.left_rotation = 0
        self.top_rotation = 307

        # Player sneaking speed
        self.speed = 1.31

        # Regex for finding numbers
        self.regex = r'((?:[\+-]?[0-9]*[\.,][0-9]+)|(?:[\+-]?[0-9]+))'

    def get_coordinates(self):  # Gets coordinates off screen
        # Screenshots the chest window
        scr = self.sct.grab({'left': self.left_coordinate, 'top': self.top_coordinate, 'width': 350, 'height': 58})

        # Get raw pixels from screen and save to numpy array
        coordinate_img = np.array(scr)
        coordinate_img = cv2.cvtColor(coordinate_img, cv2.COLOR_RGB2GRAY)

        # OCR
        coordinates_raw = pytesseract.image_to_string(coordinate_img).lower()
        split = coordinates_raw.split('\n')

        try:  # Coordinates are located on index 1 or 3
            coordinates_dirty = split[3]
            reResult = re.findall(self.regex, coordinates_dirty)
            if len(reResult) == 3:  # Usually OCR returns combined coordinates - e.g. 123 60127 (123 60 127)
                return int(reResult[0]), int(reResult[1]), int(reResult[2])  # x, y, z
            else:
                return 'None', 'None', 'None'
        except IndexError:
            try:
                coordinates_dirty = split[1]
                reResult = re.findall(self.regex, coordinates_dirty)
                if len(reResult) == 3:  # Usually OCR returns combined coordinates - e.g. 123 60127 (123 60 127)
                    return int(reResult[0]), int(reResult[1]), int(reResult[2])
                else:
                    return 'None', 'None', 'None'
            except IndexError or ValueError:  # if OCR returns nothing
                return 'None', 'None', 'None'

    def get_rotation(self):  # Gets rotation off screen
        # Screenshots the chest window
        scr = self.sct.grab({'left': self.left_rotation, 'top': self.top_rotation, 'width': 613, 'height': 30})

        # Get raw pixels from screen and save to numpy array
        rotation_img = np.array(scr)
        rotation_img = cv2.cvtColor(rotation_img, cv2.COLOR_RGB2GRAY)

        # OCR
        rotation_raw = pytesseract.image_to_string(rotation_img).lower()
        split = rotation_raw.split('\n')[0]

        for i in range(len(split) - 1, 0, -1):  # Checks for { or ( since that's where the rotation is located
            if split[i] == '{' or split[i] == '(':
                rotation_dirty = split[i:]
                break
        else:
            return 'None'

        try:
            # Rotation is decimals so 127. 8, it takes 127 and 8 then joins them with '.' so rotation = 127.8
            reResult = re.findall(self.regex, rotation_dirty)[:2]
            rotation = float('.'.join(reResult))
            if rotation < 180 or rotation > -180:  # Sometimes OCR returns a number not in the 360 degree spectrum
                return float(rotation)
            else:
                return 'None'
        except ValueError:  # if regex finds a weird number that is not a float
            return 'None'

    def slow_down(self):  # Basically like main, but more accurate | Did not put the same stuff into functions since it's slower
        error = 0
        while True:
            # Stops
            pdi.keyUp('w')
            pdi.keyUp('r')
            pdi.keyDown('shift')

            # Get player properties
            with concurrent.futures.ThreadPoolExecutor() as executor:
                coords_func = executor.submit(self.get_coordinates)
                rotate_func = executor.submit(self.get_rotation)
                x, y, z = coords_func.result()
                raw_rotation = rotate_func.result()
                player_posAccurate = (x, z)
            if 'None' in player_posAccurate or raw_rotation == 'None':  # If OCR fails to get necessary data. Run again.
                error += 1
                if error > 10:
                    error = 0
                    pdi.keyDown('w')
                    pdi.keyDown('r')
                    time.sleep(0.5)
                    pdi.keyUp('w')
                    pdi.keyUp('r')
                    pag.moveRel(30, 0, 0.5)
                continue

            selisihx = abs(player_posAccurate[0] - self.destination[0])
            selisihz = abs(player_posAccurate[1] - self.destination[1])
            if selisihx <= 1 and selisihz <= 1:  # If Arrived
                pdi.keyUp('w')
                pdi.keyUp('space')
                pdi.keyUp('r')
                pdi.keyDown('s')
                time.sleep(0.1)
                pdi.keyUp('s')
                pdi.keyUp('shift')
                print('Arrived')
                if self.counter in LIST_OF_SPECIAL:
                    self.special()
                self.counter += 1
                break

            # Calculation
            distance = math.hypot(abs(player_posAccurate[0] - self.destination[0]),
                                  abs(player_posAccurate[1] - self.destination[1]))
            #  Calculates how many pixels the player has to rotate
            degree = (180 / 3.14) * math.atan2(self.destination[1] - player_posAccurate[1],
                                               self.destination[0] - player_posAccurate[0]) - 90
            degree = convert_positive(degree)
            raw_rotation = convert_positive(raw_rotation)
            rotate = degree - raw_rotation
            rotate_pixels = round(rotate / 90.1 * 143)
            duration = distance / self.speed

            # Rotate
            pag.moveRel(rotate_pixels, 0, 1)

            # Move
            pdi.keyDown('r')
            pdi.keyDown('w')
            pdi.keyDown('shift')
            time.sleep(duration - 0.03)
            print(duration)
            pdi.keyUp('w')
            pdi.keyUp('r')

            selisihx = abs(player_posAccurate[0] - self.destination[0])
            selisihz = abs(player_posAccurate[1] - self.destination[1])
            if selisihx <= 1 and selisihz <= 1:
                pdi.keyUp('w')
                pdi.keyUp('space')
                pdi.keyUp('r')
                pdi.keyDown('s')
                time.sleep(0.1)
                pdi.keyUp('s')
                pdi.keyUp('shift')
                print('Arrived')
                if self.counter in LIST_OF_SPECIAL:
                    self.special()
                self.counter += 1
                break

    def degree_calc(self, player_pos):
        degree = (180 / 3.14) * math.atan2(self.destination[1] - player_pos[1],
                                           self.destination[0] - player_pos[0]) - 90
        degree = convert_positive(degree)
        return degree

    def get_PP(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            coords_func = executor.submit(self.get_coordinates)
            rotate_func = executor.submit(self.get_rotation)
            x, y, z = coords_func.result()
            raw_rotation = rotate_func.result()
            player_pos = (x, z)
        return player_pos, raw_rotation

    def calc_destination_rotation(self, degree):
        raw_rotation = self.get_rotation()
        if raw_rotation == 'None':  # If OCR fails to get necessary data. Run again.
            self.calc_destination_rotation(degree)
            return 'None'
        rotate = degree - raw_rotation
        rotate_pixels = round(rotate / 90.1 * 143)
        pag.moveRel(rotate_pixels, 0, 1)

    def look_at_chest(self):
        pag.moveRel(0, 140, 0.5)
        pag.mouseDown(button='right')
        pag.mouseUp(button='right')
        print('Searching for mythics...')
        time.sleep(3)
        pag.keyDown('esc')
        pag.keyUp('esc')
        pag.moveRel(0, -140, 0.5)

    def special(self):
        if self.counter == 4:
            degree = 0
            self.calc_destination_rotation(degree)
            self.look_at_chest()
        elif self.counter == 5:
            degree = -90
            self.calc_destination_rotation(degree)
            time.sleep(0.1)
            self.look_at_chest()

    def main(self):
        error = 0
        while True:
            start = timer()
            # Destination
            self.destination = LIST_OF_COORDINATES[self.counter]

            # Get player properties
            player_pos, raw_rotation = self.get_PP()
            print(timer() - start)

            if 'None' in player_pos or raw_rotation == 'None':  # If OCR fails to get necessary data. Run again.
                error += 1
                if error > 10:
                    error = 0
                    pdi.keyDown('w')
                    pdi.keyDown('r')
                    time.sleep(0.5)
                    pdi.keyUp('w')
                    pdi.keyUp('r')
                    pag.moveRel(30, 0, 0.5)
                continue

            selisihx = abs(player_pos[0] - self.destination[0])
            selisihz = abs(player_pos[1] - self.destination[1])
            if selisihx <= 1 and selisihz <= 1:  # If Arrived
                pdi.keyUp('w')
                pdi.keyUp('r')
                pdi.keyDown('s')
                time.sleep(0.1)
                pdi.keyUp('s')
                pdi.keyUp('shift')
                print('Arrived')
                if self.counter in LIST_OF_SPECIAL:
                    self.special()
                self.counter += 1
                continue

            # If player is in a 6 radius area | More like 2-3
            if selisihx <= 7 and selisihz <= 7:
                self.slow_down()
                continue

            #  Calculates how many pixels the player has to rotate
            with concurrent.futures.ThreadPoolExecutor() as executor:
                conversion1 = executor.submit(convert_positive, raw_rotation)
                conversion2 = executor.submit(self.degree_calc, player_pos)
                self.degree = conversion2.result()
                self.raw_rotation = conversion1.result()

            rotate = self.degree - self.raw_rotation
            rotate_pixels = round(rotate / 90.1 * 143)

            #  Move based on calculation
            pag.moveRel(rotate_pixels, 0, 1)
            pdi.keyDown('r')
            pdi.keyDown('w')


player_movement = PlayerMovement()
time.sleep(2)
player_movement.main()
