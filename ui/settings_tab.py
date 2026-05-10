import customtkinter as ctk

class SettingsTab(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        label = ctk.CTkLabel(
            self,
            text="System Core"
        )
        label.pack(pady=20)
