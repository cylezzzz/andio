import customtkinter as ctk

class RenderPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(fill="x", padx=20, pady=20)
