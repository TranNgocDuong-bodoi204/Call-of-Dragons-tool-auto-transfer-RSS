from enum import Enum
from dataconf import dataCof as Data
import action
from window_handler import GameWindow as window
from states.find_target import Find_And_Click_Target as Find
import time
from vision import Vision
class Transfer_Type(Enum):
    Gold = 0
    Wood = 1
    Ore = 2
    Done = 3


class Transfer:

    def  __init__(self,vs:Vision,game:window, dt:Data, find: Find):
        self.type = Transfer_Type.Gold

        self.window = game
        self.vision = vs
        self.data = dt
        self.find = find

        self.t_index = 1
        self.flag_set_action = False

        self.temp_time = 0

    def Do_Transfer(self):
        if self.type == Transfer_Type.Gold:
            self.__do_transfer_gold()
        elif self.type == Transfer_Type.Wood:
            self.__do_transfer_wood()
        elif self.type == Transfer_Type.Ore:
            self.__do_transfer_ore()

    def reset_variables(self):
        self.t_index = 1
        pass

    def __do_transfer_gold(self):
        if self.temp_time == 0:
            self.temp_time = time.time()

        if self.data.transfer_data["gtt"] <= 0:
            self.type = Transfer_Type.Wood
            self.reset_variables()
            print(f"thoi thuc hien: {time.time() - self.temp_time}")
            #return True
        
        else:
            if self.t_index == 1:
                if not self.flag_set_action:
                    self.find.set_action([
                        "target",
                        "btn_assistance"
                    ],True)
                    self.flag_set_action = True
                if not self.find.running:
                    self.t_index = 2
                    self.flag_set_action = False

            elif self.t_index == 2:
                if not self.flag_set_action:
                    self.find.set_action([
                        "btn_open_gold_num_pad",
                        "btn_open_gold_num_pad",
                        "btn_paste",
                        "btn_confirm",
                        "btn_transport",
                    ],False)
                    self.flag_set_action = True
                if not self.find.running:
                    self.data.transfer_data["gtt"] -= 1
                    self.t_index = 1
                    return

        

    def  __do_transfer_wood(self):
        if self.data.transfer_data["wtt"] <= 0:
            self.type == Transfer_Type.Ore
            return

    def __do_transfer_ore(self):
        if self.data.transfer_data["ott"] <= 0:
            self.type == Transfer_Type.Done
            return