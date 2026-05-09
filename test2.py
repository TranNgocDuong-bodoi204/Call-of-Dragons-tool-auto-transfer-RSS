
import random

import cv2 as cv
import pytesseract
import numpy as np
import pyautogui
from window_handler import GameWindow
from vision import Vision
import action as action
from window_handler import GameWindow
import time
import pos_define as region_tool
def human_move(mouse_pos,neo,target,t):
        x,y = action.bezier(mouse_pos,neo,target,t)
        if t >= 1:
            print("Finish")
            return "done"
        print(f"t: {t}, x: {x}, y: {y}")
        action.move_step(((int)(x), (int)(y)))

def moveTest(window, vision):
    finish = False
    start = True
    while finish == False:
        if start:
            t = 0
            screenshot = vision.get_image(window.rect)
            template_loc = vision.get_template_location(window.rect, screenshot, "target", threshold=0.5)
            random_pos = action.random_position_around(template_loc, radius=10)
            target = random_pos
            mouse_pos = action.get_mouse_pos()
            neo = action.get_neo(target)
            step = random.uniform(0.01, 0.03)
            start = False
        t += step
        t = min(t, 1)
        rs = action.human_like_move(mouse_pos, neo, target, t)
        if rs == "done":
            finish = True

if __name__ == "__main__":
    
    vision = Vision("templates")
    window = GameWindow("Call of Dragons")
    window.setup_window()
    time.sleep(.5)
    #moveTest(window, vision)

    screenshot = vision.get_image_by_rect(window.rect)
    #cv.imshow("screenshot", screenshot)
    region_tool.region_tool(screenshot)
    cv.waitKey(0)
