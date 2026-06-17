import customtkinter as ctk
import tkinter.messagebox as messagebox
from controllers.users_controller import UsersController
from domain.models.user import User

class UsersView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.controller = UsersController()

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

        self.stat_activos = self.create_stat_card(self.stats_frame, "Activos", "0")
        self.stat_activos.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.stat_suspendidos = self.create_stat_card(self.stats_frame, "Suspendidos", "0")
        self.stat_suspendidos.pack(side="left", expand=True, fill="x", padx=10)

        self.stat_saldo = self.create_stat_card(self.stats_frame, "Saldo Promedio", "S/ 0.00")
        self.stat_saldo.pack(side="left", expand=True, fill="x", padx=10)

        self.stat_estrellas = self.create_stat_card(self.stats_frame, "Estrellas Totales", "0 ⭐")
        self.stat_estrellas.pack(side="left", expand=True, fill="x", padx=(10, 0))

        # Search Row
        self.search_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.search_frame.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            self.search_frame, placeholder_text="Buscar por nombre o correo...", width=300
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.load_users())

        self.btn_search = ctk.CTkButton(
            self.search_frame, text="Buscar", width=100,
            command=self.load_users
        )
        self.btn_search.pack(side="left", padx=(0, 10))

        self.btn_refresh = ctk.CTkButton(
            self.search_frame, text="Actualizar", width=100,
            fg_color="#FF5A1F", hover_color="#E64A19",
            command=self.load_users
        )
        self.btn_refresh.pack(side="left")

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        self.tab_activos = self.tabview.add("Activos")
        self.tab_suspendidos = self.tabview.add("Suspendidos")

        self.scroll_activos = ctk.CTkScrollableFrame(self.tab_activos, fg_color="transparent")
        self.scroll_activos.pack(expand=True, fill="both")

        self.scroll_suspendidos = ctk.CTkScrollableFrame(self.tab_suspendidos, fg_color="transparent")
        self.scroll_suspendidos.pack(expand=True, fill="both")

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

    def update_stats(self, activos, suspendidos, saldo, estrellas):
        self.stat_activos.value_label.configure(text=f"{activos}")
        self.stat_suspendidos.value_label.configure(text=f"{suspendidos}")
        self.stat_saldo.value_label.configure(text=f"S/ {saldo:.2f}")
        self.stat_estrellas.value_label.configure(text=f"{estrellas} ⭐")

    def load_users(self):
        # Clear containers
        for widget in self.scroll_activos.winfo_children():
            widget.destroy()
        for widget in self.scroll_suspendidos.winfo_children():
            widget.destroy()
            
        loading_act = ctk.CTkLabel(self.scroll_activos, text="Cargando...")
        loading_act.pack(pady=20)
        loading_susp = ctk.CTkLabel(self.scroll_suspendidos, text="Cargando...")
        loading_susp.pack(pady=20)

        search_query = self.search_entry.get().strip()

        def _on_success(activos: list[User], inactivos: list[User]):
            self.after(0, lambda: self.render_users(activos, inactivos, loading_act, loading_susp))

        self.controller.load_users(search_query, _on_success)

    def render_users(self, activos, inactivos, lbl_act, lbl_susp):
        lbl_act.destroy()
        lbl_susp.destroy()
        
        if not activos:
            ctk.CTkLabel(self.scroll_activos, text="No hay usuarios activos.", text_color="gray").pack(pady=20)
        if not inactivos:
            ctk.CTkLabel(self.scroll_suspendidos, text="No hay usuarios suspendidos.", text_color="gray").pack(pady=20)

        sum_saldo = 0.0
        sum_estrellas = 0

        # Render Activos
        for user in activos:
            sum_saldo += user.saldo
            sum_estrellas += user.estrellas
            self.create_user_card(user, self.scroll_activos).pack(fill="x", pady=5)

        # Render Inactivos
        for user in inactivos:
            self.create_user_card(user, self.scroll_suspendidos).pack(fill="x", pady=5)

        total_activos = len(activos)
        total_suspendidos = len(inactivos)
        avg_saldo = sum_saldo / total_activos if total_activos > 0 else 0

        self.update_stats(total_activos, total_suspendidos, avg_saldo, sum_estrellas)

    def create_user_card(self, user: User, parent_container):
        card = ctk.CTkFrame(parent_container, corner_radius=8, fg_color="#2b2b2b")
        
        # Initial circle
        initial = user.nombre[0].upper() if user.nombre and user.nombre != 'Sin nombre' else "U"
        circle = ctk.CTkFrame(card, width=40, height=40, corner_radius=20, fg_color="#FF5A1F" if user.activo else "gray")
        circle.pack(side="left", padx=15, pady=15)
        circle.pack_propagate(False)
        ctk.CTkLabel(circle, text=initial, text_color="white", font=ctk.CTkFont(weight="bold")).place(relx=0.5, rely=0.5, anchor="center")

        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=10)

        ctk.CTkLabel(info_frame, text=user.nombre, font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"ID: {user.id_usuario} | {user.correo}", text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w")

        # Status & Balances
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=10)

        status_text = "Activo" if user.activo else "Suspendido"
        status_color = "green" if user.activo else "red"
        ctk.CTkLabel(right_frame, text=status_text, text_color=status_color, font=ctk.CTkFont(weight="bold")).pack(anchor="e")
        ctk.CTkLabel(right_frame, text=f"S/ {user.saldo:.2f} | {user.estrellas} ⭐", font=ctk.CTkFont(size=12)).pack(anchor="e")

        if user.activo and user.id_usuario != 'N/A':
            btn_suspender = ctk.CTkButton(
                right_frame, text="Suspender", width=80, height=24,
                fg_color="red", hover_color="#8B0000",
                command=lambda u=user.id_usuario: self.suspender_usuario(u)
            )
            btn_suspender.pack(anchor="e", pady=(5, 0))
        elif not user.activo and user.id_usuario != 'N/A':
            btn_activar = ctk.CTkButton(
                right_frame, text="Activar", width=80, height=24,
                fg_color="green", hover_color="#006400",
                command=lambda u=user.id_usuario: self.reactivar_usuario(u)
            )
            btn_activar.pack(anchor="e", pady=(5, 0))

        return card

    def suspender_usuario(self, uid):
        def _on_complete(success: bool, msg: str):
            if success:
                self.after(0, lambda: messagebox.showinfo("Éxito", msg))
                self.after(0, self.load_users)
            else:
                self.after(0, lambda: messagebox.showerror("Error", f"Error al suspender: {msg}"))

        self.controller.suspender_usuario(uid, _on_complete)

    def reactivar_usuario(self, uid):
        def _on_complete(success: bool, msg: str):
            if success:
                self.after(0, lambda: messagebox.showinfo("Éxito", msg))
                self.after(0, self.load_users)
            else:
                self.after(0, lambda: messagebox.showerror("Error", f"Error al activar: {msg}"))

        self.controller.reactivar_usuario(uid, _on_complete)

