from enum import Enum
import random

import win32api
import win32con

# my component
from vision import Vision
import action as action
from dataconf import dataCof as data
from states.find_target import Find_And_Click_Target as Find
from states.setup_transfer_data import SetUp_Transfer as Setup
from states.transfer import Transfer

import keyboard
from window_handler import GameWindow
import time
import cv2 as cv
import ctypes

class state(Enum):
    DEFAULT = 0
    FIND_TARGET = 1
    SETUP_TRANSFER = 2
    TRANSFER = 3
    DONE = 4

class Bot:
    def __init__(self, vision: Vision, window_handler: GameWindow, dataCof :data, find :Find, setup: Setup,transfer:Transfer):
        self._current_state = state.DEFAULT
        # config main loop
        self._is_running = True
        self.fps = 100
        self.runtime = 0
        self.timer = 0

        self.delay_running = False

        self.vision = vision
        self.window = window_handler
        self.data = dataCof
        self.find = find
        self.setup = setup
        self.transfer = transfer

        # state variables
        self.is_enter_completed = False

        self.start = True
        self.is_exited = False
        self.step_start = True
        self.step_time = 0
        
        # default state variables
        self.space_count = 0
        # find_target_state variables
        self.find_target_index = 0
        self.step_done =False


    def default_state(self, delta):
        if self.step_start:
            self.step_time = 0
            self.space_count = 0
            self.step_start = False

        self.step_time += delta
        if self.space_count >= 2:
            self.space_count = 0
            try:
                time.sleep(.2)
                recipient_pos = vision.get_template_rect(window.rect,"target")
                self.data.set_recipient_position(recipient_pos)
                self.change_state(state.FIND_TARGET)
                return
            except Exception as er:
                print("Chưa tìm thấy người nhận, đang thử lại")
                return
        
        if self.step_time >= .5:
            action.press_key('space')
            self.space_count += 1
            self.step_time = 0

    def find_target_state(self, delta):
        if self.find_target_index == 0:
            self.find.set_action([
                "target",
                "btn_assistance",
            ],True)
            self.find_target_index = 1
        else:
            if not self.find.running:
                time.sleep(.2)
                rs = self.find.ocr_target()
                if rs:
                    self.change_state(state.SETUP_TRANSFER)
                    return 

    def setup_transfer(self):
        if self.setup.SetUp() == True:
            self.change_state(state.DONE)
            return
    def Transfer_RSS(self):
        if self.transfer.Do_Transfer():
            self.change_state(state.DONE)
            return
    def start_delay(self,delay):
        if not self.delay_running:
            self.timer = time.time() + delay
            self.delay_running = True
    
    def stop_delay(self):
        if not self.delay_running:
            return False
        if time.time() >= self.timer :
            self.delay_running = False
            return True
        return False
    
    def run(self):
        last_time = time.time()
        frame_perriod = 1 / self.fps    

        while self._is_running:
            now = time.time()
            delta = now - last_time
            last_time = now

            # cập nhật di chuyển 
            self.find.find_target_update(delta=delta)

            if self._current_state == state.DEFAULT:
                # hàm này sẽ ấn space 2 lần để reset độ phóng của bản đồ
                self.default_state(delta)

            elif self._current_state == state.FIND_TARGET:
                self.find_target_state(delta)

            elif self._current_state == state.SETUP_TRANSFER:
                self.setup_transfer()

            elif self._current_state == state.TRANSFER:
                self.Transfer_RSS()                
            elif self._current_state == state.DONE:
                pass
            # FPS control
            elapsed = time.time() - now
            if elapsed < frame_perriod:
                time.sleep(frame_perriod - elapsed)

    
    def enter_state(self, state):
        if self.is_enter_completed == True:
            return

        if state == state.DEFAULT:
            print("Entering state: DEFAULT")

        elif state == state.FIND_TARGET:
            self.step_done = False
            self.find_target_index = 0
            print("ĐANG SETUP DỮ LIỆU, VUI LÒNG ĐỢI")
        elif state == state.SETUP_TRANSFER:
            pass    
        elif state == state.TRANSFER:
            print("Entering state: TRANSFER")
        elif state == state.DONE:
            print("Entering state: DONE")
        self.step_done = False
        self.is_enter_completed = False

    def exit_state(self, state):
        if self.is_exited == True:
            return

        if state == state.DEFAULT:
            print("Exiting state: DEFAULT")
        elif state == state.FIND_TARGET:
            print("Exiting state: FIND_TARGET")
        elif state == state.SETUP_TRANSFER:
            print("Exiting state: SETUP_TRANSFER")
        elif state == state.TRANSFER:
            print("Exiting state: TRANSFER")
        elif state == state.DONE:
            print("Exiting state: ERROR")
        self.step_done = True
        self.is_exited = True

    def change_state(self, new_state):
        print("####\n--->")
        self.step_start = True
        if new_state == self._current_state:
            print(f"Already in state: {self._current_state.name} - no state change. ERROR")
            return
        self.is_exited = False
        self.exit_state(self._current_state)
        self._current_state = new_state
        self.is_enter_completed = False
        self.enter_state(self._current_state)
        print(f"Current state: {self._current_state.name}")

    def stop(self):
        self._is_running = False
        print("Bot stopped.")



if __name__ == "__main__":
    # setup
    ctypes.windll.user32.SetProcessDPIAware()
    window = GameWindow("Call of Dragons")
    window.setup_window()
    vision = Vision("templates")


    dCof = data(rect=window.rect)
    find = Find(vision=vision,windows=window,dt=dCof)
    set = Setup(dt=dCof,find=find)
    transfer = Transfer(vs=vision,game=window,dt=dCof,find=find)

    bot = Bot(vision, window,dCof,find,set,transfer)
    bot.run()
    #bot.reset_delay()
    cv.waitKey(0)
