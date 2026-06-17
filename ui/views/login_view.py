import customtkinter as ctk
from controllers.login_controller import LoginController

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color="transparent")
        self.on_login_success = on_login_success
        self.controller = LoginController()

        # Container principal centrado
        self.container = ctk.CTkFrame(self, width=550, height=520, corner_radius=20)
        self.container.pack_propagate(False)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo / Título
        self.logo_circle = ctk.CTkFrame(self.container, width=60, height=60, corner_radius=30, fg_color="#FF5A1F")
        self.logo_circle.pack(pady=(40, 15))
        self.logo_circle.pack_propagate(False)
        
        self.logo_text = ctk.CTkLabel(self.logo_circle, text="L!", font=ctk.CTkFont(size=28, weight="bold"), text_color="white")
        self.logo_text.place(relx=0.5, rely=0.5, anchor="center")

        self.title_label = ctk.CTkLabel(self.container, text="LISTO! GO", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(0, 5))

        self.subtitle_label = ctk.CTkLabel(self.container, text="Portal Administrativo", text_color="gray", font=ctk.CTkFont(size=14))
        self.subtitle_label.pack(pady=(0, 40))

        # Formulario - Correo
        self.correo_label = ctk.CTkLabel(self.container, text="Usuario / Correo", font=ctk.CTkFont(weight="bold"))
        self.correo_label.pack(anchor="w", padx=40)
        
        self.correo_entry = ctk.CTkEntry(self.container, placeholder_text="admin@listogo.com", height=40, border_color="#FF5A1F")
        self.correo_entry.pack(fill="x", padx=40, pady=(5, 20))

        # Formulario - Contraseña
        self.password_label = ctk.CTkLabel(self.container, text="Contraseña", font=ctk.CTkFont(weight="bold"))
        self.password_label.pack(anchor="w", padx=40)
        
        self.password_entry = ctk.CTkEntry(self.container, placeholder_text="••••••••", show="*", height=40, border_color="#FF5A1F")
        self.password_entry.pack(fill="x", padx=40, pady=(5, 10))

        # Mensaje de Error
        self.error_label = ctk.CTkLabel(self.container, text="", text_color="red")
        self.error_label.pack(pady=5)

        # Botón Login
        self.btn_login = ctk.CTkButton(
            self.container, 
            text="Ingresar al Dashboard", 
            fg_color="#FF5A1F", 
            hover_color="#E64A19", 
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.handle_login
        )
        self.btn_login.pack(fill="x", padx=40, pady=(10, 40))

    def handle_login(self):
        correo = self.correo_entry.get()
        password = self.password_entry.get()

        # UI state changes
        self.btn_login.configure(state="disabled", text="Cargando...")
        self.error_label.configure(text="")

        # Usar after(0, callback) para volver al main thread al modificar la UI
        def _on_success():
            self.after(0, self.on_login_success)

        def _on_error(message: str):
            self.after(0, lambda: self.show_error(message))

        self.controller.handle_login(
            correo=correo, 
            password=password, 
            on_success=_on_success, 
            on_error=_on_error
        )

    def show_error(self, message):
        self.error_label.configure(text=message)
        self.btn_login.configure(state="normal", text="Ingresar al Dashboard")
