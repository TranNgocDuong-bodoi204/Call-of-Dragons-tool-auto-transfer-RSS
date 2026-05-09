import math
import random
import queue
import pydirectinput as input
import pytesseract
import numpy as np
import time

pytesseract.pytesseract.tesseract_cmd = r'E:\Apps\tesseract.exe'

def press_key(key):
    random_delay()
    input.press(key)

def random_delay(min_delay=0.1, max_delay=0.3):
    delay = np.random.uniform(min_delay, max_delay)
    time.sleep(delay)

def lerp(a, b, t):
    return a + (b - a) * t

def ease_in_out(t):
    return (1 - math.cos(math.pi * t)) / 2

def bezier(p0, p1, p2, t):
    t = ease_in_out(t)
    x = lerp(lerp(p0[0], p1[0], t), lerp(p1[0], p2[0], t), t)
    y = lerp(lerp(p0[1], p1[1], t), lerp(p1[1], p2[1], t), t)
    return x, y

def get_neo(target_pos):
    mouse_pos = input.position()
    center = ((mouse_pos[0] + target_pos[0]) / 2, (mouse_pos[1] + target_pos[1]) / 2)
    distance_center_x = random.uniform(-100,100) 
    distance_center_y = random.uniform(-100,100)
    
    neo = (center[0]+distance_center_x, center[1]+distance_center_y)
    return neo

def human_like_move(mouse_pos,neo,target,t):
    x,y = bezier(mouse_pos,neo,target,t)
    if t >= 1:
        return "done"
    move_step(((int)(x), (int)(y)))

def move_step(target):
    input.PAUSE = 0.005
    random_pos = jitter_position(target, jitter=2)
    input.moveTo(random_pos[0], random_pos[1])

def jitter_position(target, jitter=1):
    if random.uniform(0,100) < 40:
        x = target[0] + random.randint(-jitter, jitter)
        y = target[1] + random.randint(-jitter, jitter)
        return (x, y)
    return target

def random_position_around(target, radius):
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, radius)
    x = target[0] + distance * math.cos(angle)
    y = target[1] + distance * math.sin(angle)
    return ((int)(x), (int)(y))


def distanceTo(target_x, target_y, mouse_position=None):
    if mouse_position is None:
        mouse_position = input.position()
    distance = np.sqrt(np.power(target_x - mouse_position[0], 2) + np.power(target_y - mouse_position[1], 2))
    return distance
def get_mouse_pos():
    return input.position()

class moveto_click_template:
    def __init__(self):
        self.action_queue = queue.Queue()

        self.can_set_new_action = True
        self.can_set_target = False
        self.running = False
        self.current_target = None

        # step flags
        self.step1_done = False
        self.step2_done = False
        self.step3_done = False
        self.step_start = True

        # step 2 - movement
        self.target_position = (0, 0)
        self.t = 0
        self.move_step = 0.1
        self.mouse_pos = (0, 0)
        self.neo = (0, 0)

        # step 3 - click timing
        self.step_time = 0
        self.down_time = 0
        self.up_time = 0
        self.mouse_is_down = False

    def set_action(self, actions_arr):
        # actions_arr = ["btn_login", "btn_assistance", ...]
        if self.can_set_new_action:
            for action in actions_arr:
                self.action_queue.put(action)
            self.can_set_new_action = False

    def update(self, vision, window, delta):
        if not self.running:
            if self.action_queue.empty():
                self.can_set_new_action = True  # toàn bộ xong
                return
            else:
                self.can_set_target = True       # còn item, pop tiếp

        if self.can_set_target:
            self.can_set_target = False
            self.current_target = self.action_queue.get()
            self.running = True

        self.click_template(self.current_target, vision, window, delta)

    def reset_data_when_complete_aclick(self):
        self.step1_done = False
        self.step2_done = False
        self.step3_done = False
        self.step_start = True
        self.target_position = (0, 0)
        self.t = 0
        self.mouse_pos = (0, 0)
        self.neo = (0, 0)
        self.step_time = 0
        self.down_time = 0
        self.up_time = 0
        self.mouse_is_down = False
        self.running = False  # trigger update() lấy action tiếp theo

    def click_template(self, action, vision, window, delta):
        try:
            # step 1: tìm target
            if not self.step1_done and not self.step2_done and not self.step3_done:
                screenshot = vision.get_image(window.rect)
                self.target_position = vision.get_template_location(
                    window.rect, screenshot,
                    action,
                    threshold=.95)
                if self.target_position is not None:
                    print(f"template={action}, found at: {self.target_position}")
                    self.step1_done = True
                    self.step_start = True
                    print("Step 1 done")

            # step 2: di chuyển đến target
            elif not self.step2_done and self.step1_done:
                if self.step_start:
                    self.t = 0
                    self.target_position = random_position_around(self.target_position, radius=10)
                    self.mouse_pos = get_mouse_pos()
                    self.neo = get_neo(self.target_position)
                    self.move_step = random.uniform(0.05, 0.1)
                    self.step_start = False

                self.t += self.move_step
                self.t = min(self.t, 1)
                rs = human_like_move(self.mouse_pos, self.neo, self.target_position, self.t)

                if rs == "done":
                    self.step2_done = True
                    self.step_start = True
                    print("Step 2 done")

            # step 3: click
            elif not self.step3_done and self.step2_done:
                if self.step_start:
                    self.step_time = 0
                    self.down_time = random.uniform(0.1, 0.2)
                    self.up_time = self.down_time + random.uniform(0.1, 0.2)
                    self.mouse_is_down = False
                    self.step_start = False

                self.step_time += delta

                if not self.mouse_is_down and self.step_time >= self.down_time:
                    input.mouseDown()
                    self.mouse_is_down = True

                if self.mouse_is_down and self.step_time >= self.up_time:
                    input.mouseUp()
                    self.step3_done = True
                    print("Step 3 done")
                    self.reset_data_when_complete_aclick()  # running = False ở đây

        except Exception as e:
            print(f"ERROR click_template: {e}")
 