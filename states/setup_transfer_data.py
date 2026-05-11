import math
from dataconf import dataCof as Data
from states.find_target import Find_And_Click_Target as Find
class SetUp_Transfer:
    def __init__(self, dt: Data,find: Find):
        self.data = dt
        self.find = find

        self.setup_index = 0
        self.flag = False

    def SetUp(self):
        try:
            if self.setup_index == 0:
                if self.do_setup_data():
                    self.setup_index = 1
                    return False
            elif self.setup_index == 1:
                if self.do_setup_transfer_move():
                    return True
            else:
                self.setup_index = 0
                return False
        except Exception as e:
            print(f"Có lỗi xảy ra trong lúc setup dữ liệu vận chuyển: {e}")
            return False

    def do_setup_data(self):

        t_amount = self.calculate_transfer_amount_by_tax(self.data.target_data["tax"])
        g = self.data.target_data["gold"]
        w = self.data.target_data["wood"]
        o = self.data.target_data["ore"]

        gtt = math.floor(g / t_amount)
        wtt = math.floor(w / t_amount)
        ott = math.floor(o / t_amount)
        t = self.data.target_data["time"]*2 + 2
        self.data.set_transfer_data(gtt,wtt,ott,t)

        print(f"Set up data hoàn thành")
        return True
    
    def do_setup_transfer_move(self):
        if not self.flag:
            self.find.set_action([
                "btn_open_gold_num_pad",
                "btn_5",
                "btn_0",
                "btn_0",
                "btn_0",
                "btn_0",
                "btn_0",
                "btn_0",
                "btn_copy",
                "btn_confirm",
                "btn_back"
            ],None, False)
            self.flag = True
        if not self.find.running:
            return True

    def calculate_transfer_amount_by_tax(self,tax):
        t = int(tax)
        if t == 20:
            return 1800000
        elif t == 19:
            return 2000000
        elif t == 18:
            return 2200000
        elif t == 17:
            return 2400000
        elif t == 16:
            return 2600000
        elif t == 15:
            return 2800000
        elif t == 14:
            return 3000000
        elif t == 12:
            return 3500000
        elif t == 10:
            return 4000000
        elif t == 8:
            return 5000000
        elif t == 35:
            return 10000