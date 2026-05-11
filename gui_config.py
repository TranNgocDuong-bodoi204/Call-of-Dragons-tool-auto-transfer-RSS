import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import shutil
import os


class ConfigGUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Tool Config")
        self.root.geometry("350x350")

        self.selected_image = None
        self.preview_image = None

        # vùng hiển thị ảnh
        self.image_label = tk.Label(
            self.root,
            text="No Image",
            width=0,
            height=0,
            bg="gray"
        )
        self.image_label.pack(pady=10)

        # button chọn ảnh
        tk.Button(
            self.root,
            text="Choose Image",
            command=self.choose_image
        ).pack()

        # button save
        tk.Button(
            self.root,
            text="Save",
            command=self.save_image
        ).pack(pady=10)

    def choose_image(self):

        file_path = filedialog.askopenfilename(
            title="Choose Image",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg")
            ]
        )

        if not file_path:
            return

        self.selected_image = file_path

        # mở ảnh
        image = Image.open(file_path)

        # resize preview
        image.thumbnail((200, 200))

        # convert sang tkinter image
        self.preview_image = ImageTk.PhotoImage(image)

        # hiển thị ảnh
        self.image_label.config(
            image=self.preview_image,
            text=""
        )

    def save_image(self):

        if not self.selected_image:

            messagebox.showerror(
                "Error",
                "Please choose image first"
            )
            return

        os.makedirs("templates", exist_ok=True)

        target_path = os.path.join(
            "templates",
            "target.png"
        )

        shutil.copyfile(
            self.selected_image,
            target_path
        )

        messagebox.showinfo(
            "Success",
            "Saved to templates/target.png"
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":

    gui = ConfigGUI()
    gui.run()