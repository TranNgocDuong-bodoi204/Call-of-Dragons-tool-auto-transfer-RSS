#class window_handler
1. window.rect => __find_window_rect()

2. __find_window_rect => (real_left, real_top, w, h)

3. setup_window()
    __find_window()
    is_minimized()
    __focus_window()
    __find_window_rect()

#class vision
1. get_image(rect) => img
2. is_match(self, img, template_name, threshold=0.6) => res,loc

#class action

Đỏ 🔴(0, 0, 255)
Xanh lá 🟢(0, 255, 0)
Xanh dương 🔵(255, 0, 0)