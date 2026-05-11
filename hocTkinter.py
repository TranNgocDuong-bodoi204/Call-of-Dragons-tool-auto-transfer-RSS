import tkinter as tk
from tkinter import filedialog
import os

# ── MÀU SẮC ─────────────────────────────────────────────
BG         = "#f5f5f5"
CARD       = "#ffffff"
BORDER     = "#e0e0e0"
TEXT       = "#1a1a1a"
MUTED      = "#888888"
ACCENT     = "#cf7b54"
ENTRY_BG   = "#fafafa"
WARN_BG    = "#fffbeb"
WARN_TEXT  = "#92400e"

# ── FONT ─────────────────────────────────────────────────
FONT_TITLE   = ("Segoe UI", 15, "bold")
FONT_SECTION = ("Segoe UI", 8,  "bold")
FONT_LABEL   = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_BTN     = ("Segoe UI", 10, "bold")
FONT_RADIO   = ("Segoe UI", 11)

# ═══════════════════════════════════════════════════════
# HÀM TIỆN ÍCH
# ═══════════════════════════════════════════════════════

def make_card(parent):
    """Tạo card có viền mỏng, nền trắng."""
    outer = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
    inner = tk.Frame(outer, bg=CARD, padx=16, pady=14)
    inner.pack(fill="x")
    return outer, inner

def make_section_title(parent, text):
    """Tiêu đề nhỏ in hoa của mỗi section."""
    tk.Label(parent, text=text.upper(),
             font=FONT_SECTION, fg=MUTED, bg=CARD).pack(anchor="w", pady=(0, 8))

def make_input_row(parent, label_text):
    """Một hàng gồm label + ô nhập liệu."""
    row = tk.Frame(parent, bg=CARD)
    row.pack(fill="x", pady=4)

    tk.Label(row, text=label_text, font=FONT_LABEL,
             fg=TEXT, bg=CARD, width=24, anchor="w").pack(side="left")

    entry = tk.Entry(row, width=14, font=FONT_LABEL,
                     bg=ENTRY_BG, fg=TEXT, insertbackground=ACCENT,
                     relief="flat", bd=0,
                     highlightthickness=1,
                     highlightbackground=BORDER,
                     highlightcolor=ACCENT)
    entry.pack(side="left")
    return entry

# ═══════════════════════════════════════════════════════
# CỬA SỔ CHÍNH
# ═══════════════════════════════════════════════════════

window = tk.Tk()
window.title("COD Transfer Tool")
window.geometry("480x580")
window.configure(bg=BG)
window.resizable(False, False)

# ── THANH DƯỚI (luôn cố định) ────────────────────────────
bottom = tk.Frame(window, bg=BG)
bottom.pack(side="bottom", fill="x")

tk.Frame(bottom, bg=BORDER, height=1).pack(fill="x")

tk.Button(bottom, text="Bắt đầu chuyển tài nguyên",
          font=FONT_BTN, fg="#ffffff", bg=ACCENT,
          activebackground="#b5693d", activeforeground="#ffffff",
          relief="flat", bd=0, cursor="hand2", pady=12
          ).pack(fill="x", padx=20, pady=(12, 6))

tk.Label(bottom, text="Nhấn ESC để dừng khẩn cấp bất kỳ lúc nào",
         font=FONT_SMALL, fg=MUTED, bg=BG).pack(pady=(0, 12))

# ── VÙNG CUỘN ────────────────────────────────────────────
canvas    = tk.Canvas(window, bg=BG, highlightthickness=0)
scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Frame chứa toàn bộ nội dung bên trong canvas
content = tk.Frame(canvas, bg=BG)
content_id = canvas.create_window((0, 0), window=content, anchor="nw")

# Cập nhật vùng cuộn khi nội dung thay đổi kích thước
content.bind("<Configure>", lambda e: (
    canvas.configure(scrollregion=canvas.bbox("all")),
    canvas.itemconfig(content_id, width=canvas.winfo_width())
))
canvas.bind("<Configure>", lambda e: canvas.itemconfig(content_id, width=e.width))
canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

# ═══════════════════════════════════════════════════════
# NỘI DUNG
# ═══════════════════════════════════════════════════════

# ── HEADER ───────────────────────────────────────────────
header = tk.Frame(content, bg=BG)
header.pack(fill="x", padx=20, pady=(20, 4))
tk.Label(header, text="COD Transfer Tool",  font=FONT_TITLE, fg=TEXT,  bg=BG).pack(anchor="w")
tk.Label(header, text="Made by Tran Ngoc Duong", font=FONT_SMALL, fg=MUTED, bg=BG).pack(anchor="w")
tk.Frame(content, bg=BORDER, height=1).pack(fill="x", padx=20, pady=(10, 0))

# ── ẢNH NGƯỜI CHƠI ───────────────────────────────────────
card_img, c_img = make_card(content)
card_img.pack(fill="x", padx=20, pady=(14, 0))
make_section_title(c_img, "Ảnh người chơi")

row_img = tk.Frame(c_img, bg=CARD)
row_img.pack(fill="x")

lb_image = tk.Label(row_img, text="Chưa chọn ảnh",
                    font=FONT_LABEL, fg=MUTED, bg=ENTRY_BG,
                    width=28, anchor="w", padx=8,
                    relief="flat",
                    highlightthickness=1, highlightbackground=BORDER)
lb_image.pack(side="left", ipady=7)

def choose_image():
    path = filedialog.askopenfilename(
        title="Chọn ảnh người chơi",
        filetypes=[("Ảnh", "*.png *.jpg *.jpeg")]
    )
    if path:
        lb_image.config(text=os.path.basename(path), fg=TEXT)

tk.Button(row_img, text="Chọn ảnh",
          font=FONT_LABEL, fg="#ffffff", bg=ACCENT,
          activebackground="#b5693d", activeforeground="#ffffff",
          relief="flat", bd=0, padx=14, cursor="hand2",
          command=choose_image
          ).pack(side="left", padx=(8, 0), ipady=7)

tk.Label(c_img, text="Chọn ảnh chụp màn hình của người chơi cần nhận tài nguyên.",
         font=FONT_SMALL, fg=MUTED, bg=CARD).pack(anchor="w", pady=(8, 0))

# ── CHẾ ĐỘ CHUYỂN ────────────────────────────────────────
card_mode, c_mode = make_card(content)
card_mode.pack(fill="x", padx=20, pady=(10, 0))
make_section_title(c_mode, "Chế độ chuyển")

transfer_mode = tk.IntVar(value=1)

# Card số lượng — tạo sẵn nhưng chưa hiện
card_qty, c_qty = make_card(content)

# Card hướng dẫn — tạo sẵn, pack sau
card_guide, c_guide = make_card(content)

def show_qty():
    """Hiện card số lượng, đẩy hướng dẫn xuống dưới."""
    card_guide.pack_forget()
    card_qty.pack(fill="x", padx=20, pady=(10, 0))
    card_guide.pack(fill="x", padx=20, pady=(10, 0))

def hide_qty():
    """Ẩn card số lượng."""
    card_guide.pack_forget()
    card_qty.pack_forget()
    card_guide.pack(fill="x", padx=20, pady=(10, 0))

rb_style = dict(
    font=FONT_RADIO, fg=TEXT, bg=CARD,
    activebackground=CARD, activeforeground=ACCENT,
    selectcolor="#ffffff",
    relief="flat", bd=0, cursor="hand2"
)

tk.Radiobutton(c_mode, text="Chuyển toàn bộ tài nguyên hiện có",
               variable=transfer_mode, value=1,
               command=hide_qty, **rb_style).pack(anchor="w", pady=6, padx=4)

tk.Radiobutton(c_mode, text="Chuyển theo số lượng tùy chỉnh",
               variable=transfer_mode, value=2,
               command=show_qty, **rb_style).pack(anchor="w", pady=6, padx=4)

# ── SỐ LƯỢNG & THUẾ (ẩn mặc định) ───────────────────────
make_section_title(c_qty, "Số lượng & Thuế")

warn = tk.Frame(c_qty, bg=WARN_BG, padx=10, pady=8,
                highlightthickness=1, highlightbackground="#fcd34d")
warn.pack(fill="x", pady=(0, 12))
tk.Label(warn,
         text="⚠  Nhập đúng số lượng tài nguyên hiện có trong kho.\n"
              "    Sai lệch sẽ khiến tool hoạt động không chính xác.",
         font=FONT_SMALL, fg=WARN_TEXT, bg=WARN_BG,
         justify="left").pack(anchor="w")

input_tax  = make_input_row(c_qty, "Thuế giao dịch (%):")
input_gold = make_input_row(c_qty, "Số lượng vàng (Gold):")
input_wood = make_input_row(c_qty, "Số lượng gỗ (Wood):")
input_ore  = make_input_row(c_qty, "Số lượng quặng (Ore):")

# ── HƯỚNG DẪN SỬ DỤNG ────────────────────────────────────
card_guide.pack(fill="x", padx=20, pady=(10, 0))
make_section_title(c_guide, "Hướng dẫn sử dụng")

guide_lines = [
    ("1.", "Chọn ảnh người chơi cần nhận tài nguyên."),
    ("2.", "Chọn chế độ chuyển phù hợp với nhu cầu."),
    ("3.", "Nếu chuyển theo số lượng, nhập đúng lượng tài nguyên hiện có."),
    ("4.", "Nhấn \"Bắt đầu\" — tool sẽ tự động thực hiện, không cần thao tác thêm."),
    ("5.", "Nhấn ESC bất kỳ lúc nào để dừng khẩn cấp."),
]

for num, text in guide_lines:
    row = tk.Frame(c_guide, bg=CARD)
    row.pack(fill="x", pady=2)
    tk.Label(row, text=num,  font=FONT_SMALL, fg=ACCENT, bg=CARD, width=2, anchor="w").pack(side="left")
    tk.Label(row, text=text, font=FONT_SMALL, fg=TEXT,   bg=CARD,
             anchor="w", wraplength=380, justify="left").pack(side="left", padx=(6, 0))

tk.Frame(content, bg=BG, height=16).pack()

window.mainloop()