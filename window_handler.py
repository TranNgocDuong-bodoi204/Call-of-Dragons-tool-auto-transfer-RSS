import win32gui
import win32con
import time

class GameWindow:
    def __init__(self, window_name):
        self._window_name = window_name
        self.__hwnd = None
        self.__rect = None

    # getters
    @property
    def hwnd(self):
        return self.__hwnd
    @property
    def rect(self):
        return self.__find_window_rect()

    def __find_window(self):
        """Tìm handle (hwnd) của cửa sổ game"""
        self.__hwnd = win32gui.FindWindow(None, self._window_name)
        
        if self.__hwnd == 0:
            return False
        return True

    def is_minimized(self):
        """Kiểm tra xem game có đang bị thu nhỏ (iconize) không"""
        if self.__hwnd:
            return win32gui.IsIconic(self.__hwnd)
        return False
    
    def focus_window(self):
        """Đưa cửa sổ game lên trước (focus)"""
        if not self.__hwnd:
            print("Lỗi!! Chưa tìm thấy cửa sổ game.")
            return False
        try:
            win32gui.ShowWindow(self.__hwnd, win32con.SW_RESTORE)  # Phục hồi nếu bị thu nhỏ
            win32gui.SetForegroundWindow(self.__hwnd)  # Đưa lên trước
            return True
        except Exception as e:
            print(f"Lỗi khi focus cửa sổ: {e}")
            return False

    def __find_window_rect(self):
        if not self.__hwnd:
            print("Lỗi!! Chưa tìm thấy cửa sổ game.")
            return None
        try:
            left, top, right, bottom = win32gui.GetClientRect(self.__hwnd)

            real_left, real_top = win32gui.ClientToScreen(self.__hwnd, (left, top))
            real_right, real_bottom = win32gui.ClientToScreen(self.__hwnd, (right, bottom))
            w = real_right - real_left
            h = real_bottom - real_top
            return (real_left, real_top, w, h)
        except Exception as e:
            print(f"Lỗi khi lấy Rect: {e}")
            return None

        
    def setup_window(self):
        if self.__find_window():
            print(f"Đã tìm thấy game! ID cửa sổ (hwnd): {self.__hwnd}")
        else:
            print("Không tìm thấy game. Hãy chắc chắn game đang mở.")
            return False
        if self.is_minimized(): 
            print("Game đang bị thu nhỏ, hãy mở game lên.")
            return False
        if not self.focus_window():
            print("Không thể focus cửa sổ game.")
            return False
        if self.__find_window_rect() is None:
            print("Không thể lấy kích thước cửa sổ game.")
            return False
        print(f"Thiết lập cửa sổ thành công!")
        return True