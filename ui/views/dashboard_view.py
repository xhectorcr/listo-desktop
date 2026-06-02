import customtkinter as ctk
from ui.views.users_view import UsersView
from ui.views.camera_view import CameraView
from ui.views.products_view import ProductsView
from ui.views.premios_view import PremiosView

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master, fg_color="transparent")
        self.on_logout = on_logout

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#2C2C2C")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Profile / Logo Area
        self.profile_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.profile_frame.grid(row=0, column=0, pady=(20, 20))
        
        self.logo_circle = ctk.CTkFrame(self.profile_frame, width=50, height=50, corner_radius=25, fg_color="#FF5A1F")
        self.logo_circle.pack()
        self.logo_circle.pack_propagate(False)
        ctk.CTkLabel(self.logo_circle, text="A", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(self.profile_frame, text="Administrador", font=ctk.CTkFont(weight="bold", size=16), text_color="white").pack(pady=(10, 0))
        ctk.CTkLabel(self.profile_frame, text="Admin Rol", font=ctk.CTkFont(size=12), text_color="gray").pack()

        # Navigation Buttons
        self.btn_camera = self.create_nav_button(1, "Monitor en Vivo", self.show_camera_view)
        self.btn_users = self.create_nav_button(2, "Usuarios", self.show_users_view)
        self.btn_products = self.create_nav_button(3, "Inventario", self.show_products_view)
        self.btn_premios = self.create_nav_button(4, "Premios y Cupones", self.show_premios_view)

        # Logout Button
        self.btn_logout = ctk.CTkButton(
            self.sidebar_frame, 
            text="Cerrar Sesión", 
            fg_color="transparent", 
            text_color="#FF5252", 
            hover_color="#3D2929",
            command=self.on_logout
        )
        self.btn_logout.grid(row=6, column=0, pady=20, padx=20)

        # --- Main Content Area ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # Views
        self.camera_view = CameraView(self.main_content)
        self.users_view = UsersView(self.main_content)
        self.products_view = ProductsView(self.main_content)
        self.premios_view = PremiosView(self.main_content)

        self.current_view = None
        self.show_users_view() # Mostrar usuarios por defecto

    def create_nav_button(self, row, text, command):
        btn = ctk.CTkButton(
            self.sidebar_frame, 
            text=text, 
            fg_color="transparent", 
            text_color="white", 
            hover_color="#FF5A1F",
            anchor="w",
            command=command
        )
        btn.grid(row=row, column=0, pady=5, padx=20, sticky="ew")
        return btn

    def switch_view(self, new_view):
        if self.current_view is not None:
            self.current_view.grid_forget()
        self.current_view = new_view
        self.current_view.grid(row=0, column=0, sticky="nsew")

    def show_camera_view(self):
        self.switch_view(self.camera_view)

    def show_users_view(self):
        self.switch_view(self.users_view)

    def show_products_view(self):
        self.switch_view(self.products_view)

    def show_premios_view(self):
        self.switch_view(self.premios_view)
