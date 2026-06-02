import customtkinter as ctk
import threading
from services.api_service import ApiService

class UsersView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Top section: Header and Stats
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=10)

        # Header Title
        self.title_label = ctk.CTkLabel(
            self.top_frame, 
            text="Usuarios Registrados", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.top_frame, 
            text="Monitorea a los usuarios, sus recompensas (estrellas) y saldos.", 
            text_color="gray"
        )
        self.subtitle_label.pack(anchor="w", pady=(0, 10))

        # Stats Row
        self.stats_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=10)

        self.stat_total = self.create_stat_card(self.stats_frame, "Total Usuarios", "0")
        self.stat_total.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.stat_saldo = self.create_stat_card(self.stats_frame, "Saldo Promedio", "S/ 0.00")
        self.stat_saldo.pack(side="left", expand=True, fill="x", padx=10)

        self.stat_estrellas = self.create_stat_card(self.stats_frame, "Estrellas Totales", "0 ⭐")
        self.stat_estrellas.pack(side="left", expand=True, fill="x", padx=(10, 0))

        # Refresh button
        self.btn_refresh = ctk.CTkButton(
            self.top_frame, text="Actualizar", 
            fg_color="#FF5A1F", hover_color="#E64A19",
            command=self.load_users
        )
        self.btn_refresh.pack(anchor="e", pady=(0,10))

        # List Area
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        # Load data initially
        self.load_users()

    def create_stat_card(self, parent, title, value):
        frame = ctk.CTkFrame(parent, corner_radius=10)
        lbl_title = ctk.CTkLabel(frame, text=title, text_color="gray", font=ctk.CTkFont(size=12))
        lbl_title.pack(anchor="w", padx=15, pady=(10, 0))
        
        lbl_val = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=18, weight="bold"))
        lbl_val.pack(anchor="w", padx=15, pady=(0, 10))
        
        frame.value_label = lbl_val
        return frame

    def update_stats(self, total, saldo, estrellas):
        self.stat_total.value_label.configure(text=f"{total}")
        self.stat_saldo.value_label.configure(text=f"S/ {saldo:.2f}")
        self.stat_estrellas.value_label.configure(text=f"{estrellas} ⭐")

    def load_users(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        loading_lbl = ctk.CTkLabel(self.scroll_frame, text="Cargando usuarios...")
        loading_lbl.pack(pady=20)

        def fetch():
            users = ApiService.get_usuarios(page=1, size=100)
            self.after(0, lambda: self.render_users(users, loading_lbl))

        threading.Thread(target=fetch, daemon=True).start()

    def render_users(self, users, loading_lbl):
        loading_lbl.destroy()
        
        if not users:
            ctk.CTkLabel(self.scroll_frame, text="No hay usuarios registrados.", text_color="gray").pack(pady=20)
            return

        total = len(users)
        sum_saldo = 0.0
        sum_estrellas = 0

        for user in users:
            saldo = float(user.get("saldo", 0) or 0)
            estrellas = int(user.get("estrellas", 0) or 0)
            sum_saldo += saldo
            sum_estrellas += estrellas

            self.create_user_card(user).pack(fill="x", pady=5)

        avg_saldo = sum_saldo / total if total > 0 else 0
        self.update_stats(total, avg_saldo, sum_estrellas)

    def create_user_card(self, user):
        nombre = user.get('nombre', 'Sin nombre')
        correo = user.get('correo', 'Sin correo')
        uid = str(user.get('id', 'N/A'))
        saldo = float(user.get("saldo", 0) or 0)
        estrellas = int(user.get("estrellas", 0) or 0)
        activo = user.get("activo", True)

        card = ctk.CTkFrame(self.scroll_frame, corner_radius=8, fg_color="#2b2b2b")
        
        # Initial circle
        initial = nombre[0].upper() if nombre else "U"
        circle = ctk.CTkFrame(card, width=40, height=40, corner_radius=20, fg_color="#FF5A1F")
        circle.pack(side="left", padx=15, pady=15)
        circle.pack_propagate(False)
        ctk.CTkLabel(circle, text=initial, text_color="white", font=ctk.CTkFont(weight="bold")).place(relx=0.5, rely=0.5, anchor="center")

        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=10)

        ctk.CTkLabel(info_frame, text=nombre, font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"ID: {uid} | {correo}", text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w")

        # Status & Balances
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=10)

        status_text = "Activo" if activo else "Inactivo"
        status_color = "green" if activo else "red"
        ctk.CTkLabel(right_frame, text=status_text, text_color=status_color, font=ctk.CTkFont(weight="bold")).pack(anchor="e")
        ctk.CTkLabel(right_frame, text=f"S/ {saldo:.2f} | {estrellas} ⭐", font=ctk.CTkFont(size=12)).pack(anchor="e")

        return card
