import math
import random
from enum import Enum, auto
import queue
import keyboard as key
import time
import action as ac
from vision import Vision
from window_handler import GameWindow as Windows
from dataconf import dataCof as cof

txt_gold = "gold"
txt_wood = "wood"
txt_ore = "ore"
txt_tax = "tax"
txt_time = "time"

default_radius = 5

class OcrStep(Enum):
    GOLD = auto()
    WOOD = auto()
    ORE  = auto()
    TAX  = auto()
    TIME = auto()
    DONE = auto()

class Find_And_Click_Target:
    def __init__(self, vision: Vision, windows: Windows, dt:cof ):
        # config
        self.vs = vision
        self.win = windows
        self.data = dt

        self.move_step_min = 0.06
        self.move_step_max = 0.15
        self.mouse_down_time_min = 0.1
        self.mouse_down_time_max = 0.2
        self.mouse_up_time_min = 0.1
        self.mouse_up_time_max = 0.2

        self.step_index = 0 # default
        self.ocr_step = OcrStep.GOLD
        self.ocr_finished = False
        self.step_done = True
        self.step_start = True

        self.running = False
        self.can_set_new_action = True
        self.can_set_new_target = True
        self.is_need_scan = True

        self.action_queue = queue.Queue()
        self.current_target_name = ""
        self.rect = self.win.rect
        self.radius_around = 5
        self.target_position = (0,0)

        # step variable

        # người chơi cần chuyển rss

        self.mouse_pos = (0,0)
        self.neo = (0,0)
        self.move_step = .1
        self.t = 0

    def set_action(self,action,rect = None, need_scan = True, radius = None):
        if self.can_set_new_action and not self.running:
            for i in range(0, len(action)):
                self.action_queue.put(action[i])
            if rect is None:
                self.rect = self.win.rect
            else:
                self.rect = rect
            if radius is None:
                self.radius_around =default_radius
            else:
                self.radius_around = radius

            self.running = True
            self.can_set_new_action = False 
            self.is_need_scan = need_scan 
        return
    
    def find_target_update(self, delta):
        if self.action_queue.empty() and self.running == False:
            self.can_set_new_action = True
            return
        else:
            # set new target one time when enter movement
            if self.can_set_new_target:
                self.current_target_name = self.action_queue.get()
                self.step_index = 0
                self.step_start = True
                self.can_set_new_target = False
            if self.current_target_name != "": 
                self.move_template(current_target_string=self.current_target_name,delta=delta)


    def move_template(self,current_target_string, delta):
        if self.step_index == 0: # lấy vị trí của target
            # nếu cần scan thì chụp ảnh trong vùng rect rồi so sánh với template trong dictionary
            # trả về location và gán cho target
            # ngược lại sẽ lấy vị trí từ self.data dựa vào current_target_string rồi gán cho target
            if self.is_need_scan:
                try:
                    if self.step_start:
                        self.target_position == (0,0)
                        self.step_start = False
                    
                    screenshot = self.vs.get_image_by_rect(self.rect)
                    self.target_position = self.vs.get_template_location(
                        rect= self.rect,
                        screen_shot= screenshot,
                        template_name= current_target_string,
                        threshold= .95) 
                    if self.target_position == None:
                        return
                    else:
                        self.step_start = True
                        self.step_index = 1
                except Exception as e:
                    print(f"Error in find_target class- move_template at {self.step_index} \n ERROR NAME: {e}")
                    return
            else:
                self.target_position = self.data.get_target_position(current_target_string)
                self.step_index = 1
                self.step_start = True
                
        elif self.step_index == 1: # di chuyển đến target
            try:
                if self.step_start: 
                    self.t = 0
                    self.target_position = ac.random_position_around(self.target_position,self.radius_around)
                    self.mouse_pos = ac.get_mouse_pos()
                    self.neo = ac.get_neo(self.target_position)
                    self.move_step = random.uniform(self.move_step_min,self.move_step_max)
                    self.step_start = False
                self.t += self.move_step
                self.t = min(self.t, 1)
                rs = ac.human_like_move(self.mouse_pos,self.neo,self.target_position,self.t)
                if rs == "done":
                    self.step_index = 2
                    self.step_start = True
            except Exception as e:
                print(f"Error in find_target class - move_template at {self.step_index} \n ERROR NAME: {e}")

        elif self.step_index == 2: # click target
            try:
                if self.step_start:
                    self.step_time = 0
                    self.down_time = random.uniform(self.mouse_down_time_min, self.mouse_down_time_max)
                    self.up_time = self.down_time + random.uniform(self.mouse_up_time_min, self.mouse_up_time_max)
                    self.mouse_is_down = False
                    self.step_start = False
                
                self.step_time += delta
                if not self.mouse_is_down and self.step_time >= self.down_time:
                    ac.input.mouseDown()
                    self.mouse_is_down = True
                if self.mouse_is_down and self.step_time >= self.up_time:
                    ac.input.mouseUp()
                    self.step_index = 999
            except Exception as e:
                print(f"Error in find_target class - move_template at {self.step_index} \n ERROR NAME: {e}")
        
        if self.step_index == 999: # DONE
            if self.action_queue.empty():
                self.running = False
                self.can_set_new_action = True
                return
            else:
                self.can_set_new_target = True
                self.running = True


    def ocr_target(self):
        try:
            if self.ocr_step == OcrStep.GOLD:
                img = self.vs.get_image_by_rect(self.data.get_template_rect(txt_gold))
                value = self.vs.ocr(img=img)
                if value is not None:
                    self.data.set_gold(value)
                    self.ocr_step = OcrStep.WOOD
                return False

            elif self.ocr_step == OcrStep.WOOD:
                img = self.vs.get_image_by_rect(self.data.get_template_rect(txt_wood))
                value = self.vs.ocr(img=img)
                if value is not None:
                    self.data.set_wood(value)
                    self.ocr_step = OcrStep.ORE
                return False

            elif self.ocr_step == OcrStep.ORE:
                img = self.vs.get_image_by_rect(self.data.get_template_rect(txt_ore))
                value = self.vs.ocr(img=img)
                if value is not None:
                    self.data.set_ore(value)
                    self.ocr_step = OcrStep.TAX
                return False

            elif self.ocr_step == OcrStep.TAX:
                img = self.vs.get_image_by_rect(self.data.get_template_rect(txt_tax))
                value = self.vs.ocr(img=img)
                if value is not None:
                    self.data.set_tax(value)
                    self.ocr_step = OcrStep.TIME
                return False

            elif self.ocr_step == OcrStep.TIME:
                img = self.vs.get_image_by_rect(self.data.get_template_rect(txt_time))
                value = self.vs.ocr(img=img)
                if value is not None:
                    self.data.set_time(value)
                    self.ocr_step = OcrStep.DONE
                return False

            elif self.ocr_step == OcrStep.DONE:
                return True

        except Exception as e:
            self.step_done = False
            print(f"Error ocr_target - step: {self.ocr_step} - {e}")
            return False

    