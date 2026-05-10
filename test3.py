from states.find_target import Find_And_Click_Target as find
from states.transfer import Transfer
from vision import Vision
from  window_handler import GameWindow
from dataconf import dataCof as data
import time
import ctypes
import cv2 as cv
import keyboard
import win32api
import win32con
def testFInd():
    window = GameWindow("Call of Dragons")
    window.setup_window()
    vs = Vision("templates")
    print(f"rect {window.rect}")
    dt = data(window.rect)
    f = find(vision=vs,windows=window,dt=dt)
    tr = Transfer(vs,window,dt,f)
    flag = False
    time.sleep(.5)
    recipient_pos = vs.get_template_rect(window.rect,"target")
    dt.set_recipient_rect(recipient_pos)
    rect = dt.get_template_rect("btn_open_gold_num_pad")
    tr.set_transport_count(5)
    print(f"rect player: {recipient_pos}")
    while True:
        if must_stop(): break
        f.find_target_update(0.01)
        if keyboard.is_pressed("k"):
            action = [
                "num_pad"
            ]
            f.set_action(action=action,rect=rect, need_scan=True,radius=0.2)
        if keyboard.is_pressed("h"):
            break
        time.sleep(.01)

def testData():
    window = GameWindow("Call of Dragons")
    window.setup_window()
    vs = Vision("templates")
    dt = data(window.rect)
    time.sleep(.3)

    rect = dt.get_template_rect("gold_num_board_rect")
    img = vs.get_image_by_rect(rect=rect)
    cv.imshow("test rect" , img)
    #value = vs.ocr(img=img)
    #print(value)

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
def must_stop():
        if keyboard.is_pressed("esc"):
            print("Đã thoát chương trình")
            return True

if __name__ == "__main__":
    keyboard.add_hotkey("esc", must_stop)
    ctypes.windll.user32.SetProcessDPIAware()
    testFInd()
    #testData()
    #testMatch()
    cv.waitKey(0)

"""""
#click assistance
        elif self.step_index == DETAIL_TRANSFER_STEP.ASSISTANCE:
            if self.step_start:
                self.find.set_action(["btn_assistance"],None,True)
                self.step_start = False
            if self.find.running == False:
                self.step_start = True
                self.step_index = DETAIL_TRANSFER_STEP.NUMBER_PAD
        
        #click num pad
        elif self.step_index == DETAIL_TRANSFER_STEP.NUMBER_PAD:
            if self.step_start:
                self.find.set_action(["num_pad"],self.numPad_rect,True)
                self.step_start = False
            if self.find.running == False:
                scr = self.vision.get_image_by_rect(self.numBoard_rect)
                wtm = self.vision.is_template_match(scr,"board_num",.85)
                if wtm is not None:
                    self.step_start = True
                    self.step_index = DETAIL_TRANSFER_STEP.TRANSPORT

        #click paste -> confirm -> transfer
        elif self.step_index == DETAIL_TRANSFER_STEP.TRANSPORT:
            if self.step_start:
                self.transport_index = 0
                self.step_start = False
            if self.transport_index == 0:
                self.find.set_action([
                    "btn_paste",
                    "btn_confirm",
                ],self.numBoard_rect,True)
                self.transport_index = 1

            elif self.transport_index == 1:
                if not self.find.running:
                    self.find.set_action(["btn_transport"],None,False)
                    self.transport_index = 2

            elif self.transport_index == 2 and not self.find.running:
                if not self.find.running:
                    self.step_index =DETAIL_TRANSFER_STEP.STEP_FINISH
            
        elif self.step_index == DETAIL_TRANSFER_STEP.STEP_FINISH:
            self.when_finished_a_transport()
            self.step_start = True

"""""