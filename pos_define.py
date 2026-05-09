import ctypes
import json
import cv2
import numpy as np
from pathlib import Path

SAVE_FILE = "regions.json"
OFFSET_CLIENT = (10,20)


def load_regions():
    if Path(SAVE_FILE).exists():
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_regions(regions):
    with open(SAVE_FILE, "w") as f:
        json.dump(regions, f, indent=4)
    print(f"Đã lưu vào {SAVE_FILE}")


def focus_opencv_window(title):
    try:
        import win32gui
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            win32gui.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"[focus] {e}")


def region_tool(screenshot):
    ctypes.windll.user32.SetProcessDPIAware()
    """
    Nhận vào screenshot (numpy array, 1600x900) của game window.
    Cho phép người dùng chọn vùng bằng cách click 2 điểm trên ảnh.
    Tọa độ lưu là relative so với góc (0,0) của window: x, y, w, h.
    """
    WIN = "Region Tool"
    regions = load_regions()
    clicks = []
    state = {"mode": "idle", "name": ""}
    mouse_pos = {"x": 0, "y": 0}

    def on_mouse(event, x, y, flags, param):
        mouse_pos["x"], mouse_pos["y"] = x, y
        if event == cv2.EVENT_LBUTTONDOWN:
            if state["mode"] in ("click1", "click2"):
                clicks.append((x, y))

    cv2.namedWindow(WIN)
    cv2.setMouseCallback(WIN, on_mouse)

    def draw(hint=None, p1=None, flash_region=None):
        img = screenshot.copy()

        # Vẽ các region đã lưu — xanh lá
        for name, r in regions.items():
            x, y, w, h = r["x"], r["y"], r["w"], r["h"]
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 200, 0), 2)
            cv2.putText(
                img, name, (x, max(y - 6, 12)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1
            )

        # Flash region vừa lưu — đỏ
        if flash_region:
            x, y, w, h = flash_region
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # Live preview hình chữ nhật khi đang chờ click2
        if p1 and state["mode"] == "click2":
            mx, my = mouse_pos["x"], mouse_pos["y"]
            rx, ry = min(p1[0], mx), min(p1[1], my)
            rw, rh = abs(mx - p1[0]), abs(my - p1[1])
            cv2.rectangle(img, (rx, ry), (rx + rw, ry + rh), (0, 165, 255), 1)
            cv2.circle(img, p1, 5, (0, 165, 255), -1)

        # Hint bar
        if hint:
            bar_w = len(hint) * 10 + 10
            cv2.rectangle(img, (0, 0), (bar_w, 30), (30, 30, 30), -1)
            cv2.putText(
                img, hint, (5, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1
            )

        return img

    print("=== Region Tool ===")
    print("  1: Thêm vùng  |  2: Xem danh sách  |  3: Xóa vùng cuối  |  ESC: Thoát")

    while True:

        # ── IDLE ──────────────────────────────────────────────────────────────
        if state["mode"] == "idle":
            cv2.imshow(WIN, draw("1:Them  2:Xem  3:Xoa  ESC:Thoat"))
            key = cv2.waitKey(30) & 0xFF

            if key == ord('1'):
                name = input("Nhập tên vùng: ").strip()
                if not name:
                    print("Tên không được để trống!")
                    continue
                state["name"] = name
                state["mode"] = "click1"
                clicks.clear()
                focus_opencv_window(WIN)   # auto focus vào ảnh
                print(f"  → Click góc trên-trái cho '{name}'")

            elif key == ord('2'):
                if not regions:
                    print("Chưa có vùng nào.")
                else:
                    print("\n--- Danh sách ---")
                    for n, r in regions.items():
                        print(f"  {n}: x={r['x']} y={r['y']} w={r['w']} h={r['h']}")

            elif key == ord('3'):
                if regions:
                    last = list(regions.keys())[-1]
                    del regions[last]
                    save_regions(regions)
                    print(f"Đã xóa '{last}'")
                else:
                    print("Không có vùng nào để xóa.")

            elif key == 27:  # ESC
                break

        # ── CLICK 1 ───────────────────────────────────────────────────────────
        elif state["mode"] == "click1":
            cv2.imshow(WIN, draw(f"[{state['name']}] Click goc tren-trai"))
            cv2.waitKey(30)
            if len(clicks) >= 1:
                print(f"  → Góc trên-trái: {clicks[0]} — Click góc dưới-phải")
                state["mode"] = "click2"

        # ── CLICK 2 ───────────────────────────────────────────────────────────
        elif state["mode"] == "click2":
            p1 = clicks[0] if clicks else None
            cv2.imshow(WIN, draw(f"[{state['name']}] Click goc duoi-phai", p1=p1))
            cv2.waitKey(30)
            if len(clicks) >= 2:
                x1, y1 = clicks[0]
                x2, y2 = clicks[1]
                x, y = min(x1, x2), min(y1, y2)
                w, h = abs(x2 - x1), abs(y2 - y1)

                regions[state["name"]] = {"x": x, "y": y, "w": w, "h": h}
                save_regions(regions)
                print(f"✅ '{state['name']}': x={x} y={y} w={w} h={h}")

                # Flash region đỏ 0.7s rồi về idle
                cv2.imshow(WIN, draw(flash_region=(x, y, w, h)))
                cv2.waitKey(700)

                clicks.clear()
                state["mode"] = "idle"

    cv2.destroyAllWindows()
    print("Thoát.")