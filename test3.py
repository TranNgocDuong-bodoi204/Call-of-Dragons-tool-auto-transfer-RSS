from states.find_target import Find_And_Click_Target as find
from vision import Vision
from  window_handler import GameWindow
from dataconf import dataCof as data
import time
import ctypes
import cv2 as cv
import keyboard
def testFInd():
    window = GameWindow("Call of Dragons")
    window.setup_window()
    vs = Vision("templates")
    print(f"rect {window.rect}")
    dt = data(window.rect)
    f = find(vision=vs,windows=window,dt=dt)
    flag = False
    while True:
        f.find_target_update(0.01)
        if keyboard.is_pressed("k"):
            action = [
                "btn_open_gold_num_pad",
                "btn_1",
                "btn_2",
                "btn_3",
                "btn_4",
                "btn_5",
                "btn_6",
                "btn_copy",
                "btn_confirm",
                "btn_transport"
            ]
            f.set_action(action=action, need_scan=False)
        if keyboard.is_pressed("h"):
            break
        if not flag:
            f.set_action(["target","btn_assistance"], True)
            flag = True
        time.sleep(.01)

def testData():
    window = GameWindow("Call of Dragons")
    window.setup_window()
    vs = Vision("templates")
    dt = data(window.rect)
    time.sleep(.3)

    rect = dt.get_template_rect("tax")
    img = vs.get_image_by_rect(rect=rect)
    cv.imshow("test rect" , img)
    value = vs.ocr(img=img)
    print(value)

def testMatch():
    window = GameWindow("Call of Dragons")
    window.setup_window()
    vs = Vision("templates")
    dt = data(window.rect)

    # lấy rect target
    t_r = vs.get_template_rect(window.rect,"target")
    
    testImg = vs.get_image_by_rect(t_r)
    #(875, 737, 214, 157)
    cv.imshow("tst",testImg)
    print(window.rect)
    print(t_r)

    #vs.get_template_rect(window.rect,"target")


if __name__ == "__main__":
    ctypes.windll.user32.SetProcessDPIAware()
    testFInd()
    #testData()
    #testMatch()
    cv.waitKey(0)