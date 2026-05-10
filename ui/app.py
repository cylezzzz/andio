import customtkinter as ctk
from ui.slot_widget import SlotWidget

class ForgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Forge")
        self.geometry("1600x900")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()
        self.create_workspace()

    def create_topbar(self):
        topbar = ctk.CTkFrame(self)
        topbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.slots = []

        for i in range(5):
            slot = SlotWidget(topbar, slot_id=i+1)
            slot.pack(side="left", padx=10)
            self.slots.append(slot)

    def create_workspace(self):
        workspace = ctk.CTkFrame(self)
        workspace.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        render_button = ctk.CTkButton(
            workspace,
            text="INITIALIZE RENDER"
        )
        render_button.pack(pady=20)
