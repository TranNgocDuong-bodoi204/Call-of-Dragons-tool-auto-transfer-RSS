from random import random
import re
import ctypes
import random
import time
import keyboard
from dataconf import dataCof as data

import pytesseract
import cv2 as cv
import numpy as np
import pyautogui
from window_handler import GameWindow
from vision import vision
import pydirectinput as input

# system
import ctypes, sys

pytesseract.pytesseract.tesseract_cmd = r'E:\Apps\tesseract.exe'

def run_as_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Tự restart với quyền admin
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

def ocr(img):
    """
    img: ảnh xám (grayscale), chữ trắng nền tối
    """
    # 1. Upscale x10 với Lanczos — giữ nét hơn CUBIC cho ảnh nhỏ
    up = cv.resize(img, None, fx=10, fy=10, interpolation=cv.INTER_LANCZOS4)

    # 2. Sharpen — làm nét cạnh chữ trước khi threshold
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    sharp = cv.filter2D(up, -1, kernel)

    # 3. Threshold thẳng (KHÔNG invert) — chữ trắng > 200 → giữ lại
    _, th = cv.threshold(sharp, 200, 255, cv.THRESH_BINARY)

    # 4. Tesseract: psm 7 = 1 dòng, whitelist chỉ ký tự số + suffix
    config = "--psm 7 -c tessedit_char_whitelist=0123456789.MKBmkb"
    raw = pytesseract.image_to_string(th, config=config).strip()

    value = parse_value(raw)
    print(f"OCR raw: '{raw}' → value: {value}")
    return value

def parse_value(text: str):
    text = text.upper().strip()
    match = re.search(r"([\d.]+)([MKB]?)", text)
    if not match:
        return None
    number = float(match.group(1))
    suffix = match.group(2)
    multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    return number * multipliers.get(suffix, 1)


def getRect():
    window = GameWindow("Call of Dragons")
    window.setup_window()
    vision = vision("templates")

    # Lấy rect gốc
    rect = window.rect
    print(f"Rect gốc: {rect}")

    # Điều chỉnh rect (ví dụ cộng 10px vào left và top)
    left, top, width, height = rect
    adjusted_rect = (left + 10, top + 10, width, height)
    print(f"Rect đã điều chỉnh: {adjusted_rect}")

    # Chụp ảnh với rect đã điều chỉnh
    img = vision.get_image(adjusted_rect)
    cv.imshow('Captured Image', img)
    cv.waitKey(0)

    print(window.rect)


def loop():
    while True:
        x, y = pyautogui.position()
        print(f"Current mouse position: ({x}, {y})")

def get_mouse_pos():
    cursor = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
    return (cursor.x, cursor.y)

def human_like_move(target_x, target_y, speed=15, delay=0.01):
    print(f"Moving to ({target_x}, {target_y}) with speed {speed} and delay {delay}")

    mouse_pos = get_mouse_pos()

    dx = target_x - mouse_pos[0]
    dy = target_y - mouse_pos[1]
    distance = distanceTo(target_x, target_y, mouse_pos)

    step_x = int((dx / distance) * speed)
    step_y = int((dy / distance) * speed)

    input.moveRel(step_x, step_y)
    #time.sleep(delay)

            #move 
def distanceTo(target_x, target_y, mouse_position=None):
    if mouse_position is None:
        mouse_position = get_mouse_pos()
    distance = np.sqrt(np.power(target_x - mouse_position[0], 2) + np.power(target_y - mouse_position[1], 2))
    return distance

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def learp(a, b, t):
    return a + (b - a) * t

def bezier(a, neo, b, t):
    x = learp(learp(a[0], neo[0], t), learp(neo[0], b[0], t), t)
    y = learp(learp(a[1], neo[1], t), learp(neo[1], b[1], t), t)
    return x, y

def move_human_like(startx, starty, target_x, target_y, neo, delta_time, t = 0, range = 5):
    if distanceTo(target_x, target_y, (startx, starty)) <= range:
        return
    t += delta_time
    t = min(t, 1)
    x,y = bezier((startx, starty), neo, (target_x, target_y), t=t)
    input.moveTo(int(x), int(y))
 

def get_neo(startPosition):
    angle = random.uniform(0, 2 * np.pi)
    distance = random.uniform(50,100)
    neo_x = startPosition[0] + distance * np.cos(angle)
    neo_y = startPosition[1] + distance * np.sin(angle)
    return [neo_x, neo_y]
if __name__ == "__main__":
    ctypes.windll.user32.SetProcessDPIAware()
    #run_as_admin()
    gamewindow = GameWindow("Call of Dragons")
    gamewindow.setup_window()
    vision = vision("templates")

    print(gamewindow.rect)
    data = data(gamewindow.rect)

    com = "txt_time"
    rect = data.get_template_rect("tax")
    #rect = (0,0,1920,1080)
    img = vision.get_image(rect=rect)
    cv.imshow(f"{com}",img)
    value = vision.ocr(img= img)
    print(value)
    cv.waitKey(0)

