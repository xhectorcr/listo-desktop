import customtkinter as ctk
from core.config import Config
from ui.app import AdminApp

if __name__ == "__main__":
    ctk.set_appearance_mode(Config.APPEARANCE_MODE)
    ctk.set_default_color_theme(Config.COLOR_THEME)
    
    app = AdminApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()