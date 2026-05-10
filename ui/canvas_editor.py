import customtkinter as ctk

class CanvasEditor(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.canvas = ctk.CTkCanvas(self)
        self.canvas.pack(fill="both", expand=True)
