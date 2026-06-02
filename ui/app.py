import customtkinter as ctk
from core.config import Config
from ui.views.login_view import LoginView
from ui.views.dashboard_view import DashboardView

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(Config.APP_TITLE)
        self.geometry(Config.APP_GEOMETRY)

        self.login_view = None
        self.dashboard_view = None

        self.show_login()

    def show_login(self):
        if self.dashboard_view:
            self.dashboard_view.pack_forget()
            self.dashboard_view.destroy()
            self.dashboard_view = None
            
        self.login_view = LoginView(self, self.on_login_success)
        self.login_view.pack(expand=True, fill="both")

    def on_login_success(self):
        self.login_view.pack_forget()
        self.login_view.destroy()
        self.login_view = None
        
        self.dashboard_view = DashboardView(self, self.on_logout)
        self.dashboard_view.pack(expand=True, fill="both")

    def on_logout(self):
        self.show_login()

    def on_closing(self):
        if self.dashboard_view and hasattr(self.dashboard_view, "camera_view"):
            if hasattr(self.dashboard_view.camera_view, "stop"):
                self.dashboard_view.camera_view.stop()
        self.destroy()
