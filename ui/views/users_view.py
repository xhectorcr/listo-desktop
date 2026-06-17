import customtkinter as ctk
import threading
import tkinter.messagebox as messagebox
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

        def fetch():
            users_activos = ApiService.get_usuarios(page=1, size=100, search=search_query)
            users_inactivos = ApiService.get_usuarios_inactivos(search=search_query)
            self.after(0, lambda: self.render_users(users_activos, users_inactivos, loading_act, loading_susp))

        threading.Thread(target=fetch, daemon=True).start()

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
            saldo = float(user.get("saldo", 0) or 0)
            estrellas = int(user.get("estrellas", 0) or 0)
            sum_saldo += saldo
            sum_estrellas += estrellas
            self.create_user_card(user, self.scroll_activos).pack(fill="x", pady=5)

        # Render Inactivos
        for user in inactivos:
            user["activo"] = False # Ensure it's marked correctly
            self.create_user_card(user, self.scroll_suspendidos).pack(fill="x", pady=5)

        total_activos = len(activos)
        total_suspendidos = len(inactivos)
        avg_saldo = sum_saldo / total_activos if total_activos > 0 else 0

        self.update_stats(total_activos, total_suspendidos, avg_saldo, sum_estrellas)

    def create_user_card(self, user, parent_container):
        nombre = user.get('nombre', 'Sin nombre')
        correo = user.get('correo', 'Sin correo')
        uid = str(user.get('idUsuario', user.get('id', 'N/A')))
        saldo = float(user.get("saldo", 0) or 0)
        estrellas = int(user.get("estrellas", 0) or 0)
        activo = user.get("estado", user.get("activo", True))

        card = ctk.CTkFrame(parent_container, corner_radius=8, fg_color="#2b2b2b")
        
        # Initial circle
        initial = nombre[0].upper() if nombre else "U"
        circle = ctk.CTkFrame(card, width=40, height=40, corner_radius=20, fg_color="#FF5A1F" if activo else "gray")
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

        status_text = "Activo" if activo else "Suspendido"
        status_color = "green" if activo else "red"
        ctk.CTkLabel(right_frame, text=status_text, text_color=status_color, font=ctk.CTkFont(weight="bold")).pack(anchor="e")
        ctk.CTkLabel(right_frame, text=f"S/ {saldo:.2f} | {estrellas} ⭐", font=ctk.CTkFont(size=12)).pack(anchor="e")

        if activo and uid != 'N/A':
            btn_suspender = ctk.CTkButton(
                right_frame, text="Suspender", width=80, height=24,
                fg_color="red", hover_color="#8B0000",
                command=lambda u=uid: self.suspender_usuario(u)
            )
            btn_suspender.pack(anchor="e", pady=(5, 0))
        elif not activo and uid != 'N/A':
            btn_activar = ctk.CTkButton(
                right_frame, text="Activar", width=80, height=24,
                fg_color="green", hover_color="#006400",
                command=lambda u=uid: self.reactivar_usuario(u)
            )
            btn_activar.pack(anchor="e", pady=(5, 0))

        return card

    def suspender_usuario(self, uid):
        def do_suspend():
            res = ApiService.suspender_usuario(uid)
            if res and res.get("success"):
                messagebox.showinfo("Éxito", "Usuario suspendido correctamente.")
                self.after(0, self.load_users)
            else:
                msg = res.get("message") if res else "Desconocido"
                messagebox.showerror("Error", f"Error al suspender: {msg}")
        
        threading.Thread(target=do_suspend, daemon=True).start()

    def reactivar_usuario(self, uid):
        def do_reactivar():
            res = ApiService.reactivar_usuario(uid)
            if res and res.get("success"):
                messagebox.showinfo("Éxito", "Usuario activado correctamente.")
                self.after(0, self.load_users)
            else:
                msg = res.get("message") if res else "Desconocido"
                messagebox.showerror("Error", f"Error al activar: {msg}")
        
        threading.Thread(target=do_reactivar, daemon=True).start()

