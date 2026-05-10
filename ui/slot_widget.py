import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk

class SlotWidget(ctk.CTkFrame):
    def __init__(self, master, slot_id):
        super().__init__(master, width=140, height=140)

        self.slot_id = slot_id
        self.image_path = None

        self.button = ctk.CTkButton(
            self,
            text="+",
            width=120,
            height=120,
            command=self.load_image
        )

        self.button.pack(padx=10, pady=10)

    def load_image(self):
        path = filedialog.askopenfilename()

        if not path:
            return

        self.image_path = path

        image = Image.open(path)
        image.thumbnail((120, 120))

        photo = ImageTk.PhotoImage(image)

        self.button.configure(text="", image=photo)
        self.button.image = photo
