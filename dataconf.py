from pathlib import Path
import json
class dataCof:
    def __init__(self, rect):
        # template position
        self.path = "regions.json"
        
        # conf
        self.templates_pos = {}

        self.recipient_pos = (0,0)

        self.offset_client = (0, 0)
        self.__load_data(rect=rect)

        # data of target
        self.target_data = {
            "tax" : 0,
            "gold" : 0,
            "wood" : 0,
            "ore" : 0,
            "time" : 0 
        }
        self.transfer_data = {
            "gtt" : 0,
            "wtt" : 0,
            "ott" : 0,
            "t" : 0
        }
    
    def __load_data(self, rect):
        regions = self.__load_regions()
        for name, region in regions.items():
            real_x = rect[0] + region["x"] + self.offset_client[0]
            real_y = rect[1] + region["y"] + self.offset_client[1]
            self.templates_pos[name] = {
                "x" : real_x, 
                "y": real_y,
                "w": region["w"],
                "h": region["h"]
            }
    
    def set_recipient_rect(self, rect):
        self.templates_pos["target"] = {
            "x" : rect[0],
            "y" : rect[1],
            "w" : rect[2],
            "h": rect[3]
        }
        
    def set_transfer_data(self, g,w,o,t):
        self.transfer_data["gtt"] = g
        self.transfer_data["wtt"] = w
        self.transfer_data["ott"] = o
        self.transfer_data["t"] = t

    def set_target_data(self,tax,gold,wood, ore, time):
        self.target_data["tax"] = tax
        self.target_data["gold"] = gold
        self.target_data["wood"] = wood
        self.target_data["ore"] = ore
        self.target_data["time"] = time
    def set_tax(self, tax):
        self.target_data["tax"] = tax
    def set_gold(self,gold):
        self.target_data["gold"] = gold
    def set_wood(self,wood):
        self.target_data["wood"] = wood
    def set_ore(self,ore):
        self.target_data["ore"] = ore
    def set_time(self,time):
        self.target_data["time"] = time

    def get_template_rect(self, name : str):
        return (self.templates_pos[name]["x"],
                self.templates_pos[name]["y"],
                self.templates_pos[name]["w"],
                self.templates_pos[name]["h"])
    def get_target_position(self,name : str):
        x,y,w,h = self.get_template_rect(name=name)
        center_x = x + w / 2
        center_y = y + h / 2
        return (int(center_x) ,int(center_y))
        
    def __load_regions(self):
        if Path(self.path).exists:
            with open(self.path,"r") as f:
                return json.load(f)
        else:
            return {}