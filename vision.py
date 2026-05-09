from tempfile import template

import cv2 as cv
import numpy as np
import os
import mss
import pytesseract

import re


class Vision:
    def __init__(self, assets_path):
        self.assets_path = assets_path
        self.templates = {}

        self.__find_templates()
        pass

#region Template Loading hàm chạy khi khởi tạo class
    def __find_templates(self):
        if not os.path.exists(self.assets_path):
            print(f"Assets path '{self.assets_path}' không tồn tại., hãy kiểm tra lại {self.assets_path} chứa ảnh mẫu")
            return
        for file in os.listdir(self.assets_path):
            if file.endswith(('.png', '.jpg', '.jpeg')):
                # Tách tên file và phần mở rộng (Vd: 'wood.png' -> 'wood')
                name = os.path.splitext(file)[0]
                
                # Đường dẫn đầy đủ đến file
                path = os.path.join(self.assets_path, file)
                
                # Đọc ảnh bằng OpenCV
                img = cv.imread(path, cv.IMREAD_GRAYSCALE)  # Đọc ảnh ở chế độ grayscale
                
                if img is not None:
                    self.templates[name] = img
                else:
                    print(f"Không thể đọc ảnh: {file}")
        if len(self.templates) == 0:
            print(f"Không tìm thấy ảnh mẫu nào trong '{self.assets_path}'. Hãy chắc chắn thư mục này chứa ảnh mẫu.")
        else:
            print(f"--- Đã nạp tổng cộng {len(self.templates)} ảnh mẫu vào RAM ---")
# endregion
    def get_template(self,name):
        return self.templates[name]

#region Capture Screen
    def get_image_by_rect(self, rect, left_percent= 0, top_percent=0, right_percent=0, bottom_percent=0):
        left, top, width, height = rect

        left = int(left + width * left_percent / 100)
        top =  int(top + height * top_percent / 100) 
        width = int(width * (100 - (right_percent + left_percent)) / 100)
        height = int(height * (100 - (bottom_percent + top_percent)) / 100)

        # capture screen
        with mss.mss() as sct:
            monitor = {
                'left':left,
                'top':top,
                'width':width,
                'height':height
            }
            img = sct.grab(monitor)
            img = np.array(img)
            img = cv.cvtColor(img, cv.COLOR_BGRA2GRAY)
        return img
    
    
#endregion

#region Match Template
    def is_template_match(self, screen_shot, template_name, threshold=0.6):
        if template_name not in self.templates:
            print(f"Ảnh mẫu '{template_name}' không tồn tại. Hãy kiểm tra lại tên ảnh mẫu.")
            return None
        template = self.templates[template_name]
        res = cv.matchTemplate(screen_shot, template, cv.TM_CCOEFF_NORMED)
        _, maxVal, _, maxLoc = cv.minMaxLoc(res)
        if maxVal >= threshold:
            #highlight_match(res, screen_shot, template)
            return maxLoc
        else:
            #print(f"Không tìm thấy '{template_name}'. Độ tin cậy cao nhất: {maxVal:.2f}")
            return None
    
#endregion
    def get_template_rect(self, rect, template_Name :str, threshold = .85):
        img = self.get_image_by_rect(rect=rect)
        template_img = self.get_template(template_Name)
        match = cv.matchTemplate(image=img,templ=template_img,method=cv.TM_CCOEFF_NORMED)
        _, maxVal,_,maxLoc = cv.minMaxLoc(match)

        if maxVal >= threshold:
            s = template_img.shape
            h = s[0]
            w = s[1]

            templ_rect = (
            maxLoc[0] + rect[0],  
            maxLoc[1] +rect[1], 
            w,
            h)
            return templ_rect
        else:
            return None

    def get_template_location(self, rect, screen_shot, template_name, threshold=0.70):
        maxLoc = self.is_template_match(screen_shot, template_name, threshold)
        if maxLoc is not None:
            template = self.templates[template_name]
            w, h = template.shape[1], template.shape[0]
            center_x = maxLoc[0] + w // 2
            center_y = maxLoc[1] + h // 2
            screen_pos = (rect[0] + center_x, rect[1] + center_y)
            return screen_pos
        else:
            return None

    def ocr(self, img):
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

        text = raw.upper().strip()
        match = re.search(r"([\d.]+)([MKB]?)", text)
        if not match:
            return None
        number = float(match.group(1))
        suffix = match.group(2)
        multipliers = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
        value = number * multipliers.get(suffix, 1)
        return value

def highlight_match(res, img, template):
    minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(res)
    w = template.shape[1]
    h = template.shape[0]

    top_left = maxLoc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    img_color = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    cv.rectangle(img_color, top_left, bottom_right, (0, 0, 255), 2)  # Đỏ

    cv.imshow("Matched Result Point", img_color)
