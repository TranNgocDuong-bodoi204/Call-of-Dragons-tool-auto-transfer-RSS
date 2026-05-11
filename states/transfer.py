from ast import Not
from enum import Enum
from dataconf import dataCof as Data
import action
from window_handler import GameWindow as window
from states.find_target import Find_And_Click_Target as Find
import time
from vision import Vision
class TRANSFER_TYPE(Enum):
    Gold = 0
    Wood = 1
    Ore = 2
    Done = 3

class DETAIL_TRANSFER_STEP(Enum):
    TARGET = 1
    ASSISTANCE = 2
    NUMBER_PAD = 36
    TRANSPORT = 4
    STEP_FINISH = 5

class Transfer:

    def  __init__(self,vs:Vision,game:window, dt:Data, find: Find):
        self.type = TRANSFER_TYPE.Gold

        self.window = game
        self.vision = vs
        self.data = dt
        self.find = find

        self.step_index = DETAIL_TRANSFER_STEP.TARGET

        self.gold_transport_count = 0
        self.wood_transport_count = 0
        self.ore_transport_count = 0
        self.transport_index = 0

        self.numPad_rect = None
        self.numBoard_rect = None
        self.is_set_num_rect = False

        # dùng để set action 2 lần trong state transport
        self.step_start = True
        self.transport_index = 0

    def set_transport_count(self, gold = 0, wood = 0, ore = 0):
        self.gold_transport_count = gold
        self.wood_transport_count = wood
        self.ore_transport_count = ore

    def Do_Transfer(self):
        if self.type == TRANSFER_TYPE.Gold:
            self.__do_transfer_gold()
        elif self.type == TRANSFER_TYPE.Wood:
            self.__do_transfer_wood()
        elif self.type == TRANSFER_TYPE.Ore:
            self.__do_transfer_ore()

    def __do_transfer_gold(self):
        if self.gold_transport_count <= 0:
            self.type = TRANSFER_TYPE.Wood
            self.is_set_num_rect = False
            return
        self.transfer()

    def  __do_transfer_wood(self):
        if self.wood_transport_count <= 0:
            self.type == TRANSFER_TYPE.Ore
            self.is_set_num_rect =  False
            return
        self.transfer()

    def __do_transfer_ore(self):
        if self.ore_transport_count <= 0:
            self.type == TRANSFER_TYPE.Done
            self.is_set_num_rect = False
        self.transfer()
    
    def transfer(self):
        if not self.is_set_num_rect:
            rs = self.get_num_pad_rect()
            self.numPad_rect = rs["num_pad"]
            self.numBoard_rect = rs["num_board"]
            self.is_set_num_rect = True
        
        #click player
        if self.step_index == DETAIL_TRANSFER_STEP.TARGET:
            if self.step_start:
                self.find.set_action(["target"],None,False)
                self.step_start = False
            if self.find.running == False:
                time.sleep(.6)
                scr = self.vision.get_image_by_rect(self.window.rect)
                tm = self.vision.is_template_match(scr,"board_assistance",.85)
                if tm is not None:
                    self.step_start = True # reset lại để qua step tiếp theo
                    self.step_index = DETAIL_TRANSFER_STEP.ASSISTANCE
                else:
                    self.step_start = True # quay lại step để ấn lại target
        
        elif self.step_index == DETAIL_TRANSFER_STEP.ASSISTANCE:
            if self.step_start:
                self.step_start = False
                self.find.set_action(["btn_assistance"],None,True)
            if not self.find.running:
                time.sleep(.05)
                self.step_index = DETAIL_TRANSFER_STEP.NUMBER_PAD
                self.step_start = True
        elif self.step_index == DETAIL_TRANSFER_STEP.NUMBER_PAD:
            if self.step_start:
                self.step_start = False
                self.find.set_action(["num_pad"], self.numPad_rect,True)
            if not self.find.running:
                time.sleep(.1)
                scr = self.vision.get_image_by_rect(
                    self.data.get_template_rect("num_board_rect")
                )
                ntm = self.vision.is_template_match(scr,"board_num",.85)
                self.step_start = True
                self.step_index = DETAIL_TRANSFER_STEP.TRANSPORT

        elif self.step_index == DETAIL_TRANSFER_STEP.TRANSPORT:
            if self.transport_index == 0:
                if self.step_start:
                    self.find.set_action([
                    "btn_paste",
                    "btn_confirm"],
                    self.numBoard_rect,
                    True,
                    3)
                    self.step_start = False
                if not self.find.running:
                    self.transport_index = 1
                    self.step_start = True
            elif self.transport_index == 1:
                if self.step_start:
                    self.find.set_action(["btn_transport"],None,False)
                    self.step_start = False
                if not self.find.running:
                    time.sleep(.1)
                    self.transport_index = 0
                    self.step_index = DETAIL_TRANSFER_STEP.STEP_FINISH
        
        elif self.step_index == DETAIL_TRANSFER_STEP.STEP_FINISH:
            self.when_finished_a_transport()
                
    def when_finished_a_transport(self):
        if self.type == TRANSFER_TYPE.Gold:
            self.gold_transport_count -= 1
        elif self.type == TRANSFER_TYPE.Wood:
            self.wood_transport_count -= 1
        elif self.type == TRANSFER_TYPE.Ore:
            self.ore_transport_count -=1
        self.step_index = DETAIL_TRANSFER_STEP.TARGET

    def prin_data(self):
        """In ra số lượng vận chuyển còn lại cho từng loại RSS."""
        print("Số lượng vận chuyển RSS:")
        print(f"  Gold: {self.gold_transport_count}")
        print(f"  Wood: {self.wood_transport_count}")
        print(f"  Ore: {self.ore_transport_count}")


    def get_num_pad_rect(self):
        if self.type == TRANSFER_TYPE.Gold:
            return {
                "num_pad" : self.data.get_template_rect("btn_open_gold_num_pad"),
                "num_board" :self.data.get_template_rect("gold_num_board_rect")
            }
        elif self.type == TRANSFER_TYPE.Wood:
            return {
                "num_pad": self.data.get_template_rect("btn_open_wood_num_pad"),
                "num_board": self.data.get_template_rect("wood_num_board_rect")
            }
        elif self.type == TRANSFER_TYPE.Ore:
            return {
                "num_pad" : self.data.get_template_rect("btn_open_ore_num_pad"),
                "num_board": self.data.get_template_rect("ore_num_board_rect")
            }
        raise ValueError(f"Unsupported type: {self.type}")