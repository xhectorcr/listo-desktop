import customtkinter as ctk
import tkinter.messagebox as messagebox
import functools
from controllers.users_controller import UsersController
from domain.models.user import User

class UsersView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.controller = UsersController()
        
        self.current_page = 1
        self.cards_pool_activos = []
        self.cards_pool_inactivos = []

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
        self.search_entry.bind("<Return>", lambda e: self.force_reload())

        self.btn_search = ctk.CTkButton(
            self.search_frame, text="Buscar", width=100,
            command=self.force_reload
        )
        self.btn_search.pack(side="left", padx=(0, 10))

        self.btn_refresh = ctk.CTkButton(
            self.search_frame, text="Actualizar", width=100,
            fg_color="#FF5A1F", hover_color="#E64A19",
            command=self.force_reload
        )
        self.btn_refresh.pack(side="left")

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(expand=True, fill="both", padx=20, pady=(0, 10))

        self.tab_activos = self.tabview.add("Activos")
        self.tab_suspendidos = self.tabview.add("Suspendidos")

        self.scroll_activos = ctk.CTkScrollableFrame(self.tab_activos, fg_color="transparent")
        self.scroll_activos.pack(expand=True, fill="both")

        self.scroll_suspendidos = ctk.CTkScrollableFrame(self.tab_suspendidos, fg_color="transparent")
        self.scroll_suspendidos.pack(expand=True, fill="both")
        
        # Pagination Area
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="<", width=30, command=self.prev_page)
        self.btn_prev.pack(side="left", padx=5)

        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Página 1", text_color="gray")
        self.lbl_page.pack(side="left", padx=10)

        self.btn_next = ctk.CTkButton(self.pagination_frame, text=">", width=30, command=self.next_page)
        self.btn_next.pack(side="left", padx=5)

        self.loading_act_lbl = ctk.CTkLabel(self.scroll_activos, text="Cargando...")
        self.loading_susp_lbl = ctk.CTkLabel(self.scroll_suspendidos, text="Cargando...")

        # Load data initially
        self.load_users()

    def force_reload(self):
        self.current_page = 1
        self.load_users()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_users()

    def next_page(self):
        self.current_page += 1
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
        # Hide all pooled cards
        for card in self.cards_pool_activos:
            card.pack_forget()
        for card in self.cards_pool_inactivos:
            card.pack_forget()
            
        self.loading_act_lbl.configure(text="Cargando...")
        self.loading_act_lbl.pack(pady=20)
        self.loading_susp_lbl.configure(text="Cargando...")
        self.loading_susp_lbl.pack(pady=20)
        
        self.lbl_page.configure(text=f"Página {self.current_page}")

        search_query = self.search_entry.get().strip()

        def _on_success(activos: list[User], inactivos: list[User]):
            self.after(0, lambda: self.render_users(activos, inactivos))

        self.controller.load_users(search_query, self.current_page, _on_success)

    def render_users(self, activos, inactivos):
        self.loading_act_lbl.pack_forget()
        self.loading_susp_lbl.pack_forget()
        
        # Check if empty
        if not activos and not inactivos:
            if self.current_page > 1:
                self.current_page -= 1
                self.after(0, lambda: messagebox.showinfo("Fin", "No hay más usuarios."))
                self.load_users()
            else:
                self.loading_act_lbl.configure(text="No hay usuarios activos.")
                self.loading_act_lbl.pack(pady=20)
                self.loading_susp_lbl.configure(text="No hay usuarios suspendidos.")
                self.loading_susp_lbl.pack(pady=20)
                self.update_stats(0, 0, 0, 0)
            return

        if not activos and self.current_page == 1:
            self.loading_act_lbl.configure(text="No hay usuarios activos.")
            self.loading_act_lbl.pack(pady=20)
            
        if not inactivos and self.current_page == 1:
            self.loading_susp_lbl.configure(text="No hay usuarios suspendidos.")
            self.loading_susp_lbl.pack(pady=20)

        sum_saldo = 0.0
        sum_estrellas = 0

        # Pool scaling - Activos
        while len(self.cards_pool_activos) < len(activos):
            self.cards_pool_activos.append(self._create_empty_card(self.scroll_activos))

        for i, user in enumerate(activos):
            sum_saldo += user.saldo
            sum_estrellas += user.estrellas
            card = self.cards_pool_activos[i]
            self._update_card(card, user)
            card.pack(fill="x", pady=5)

        # Pool scaling - Inactivos
        while len(self.cards_pool_inactivos) < len(inactivos):
            self.cards_pool_inactivos.append(self._create_empty_card(self.scroll_suspendidos))

        for i, user in enumerate(inactivos):
            card = self.cards_pool_inactivos[i]
            self._update_card(card, user)
            card.pack(fill="x", pady=5)

        total_activos = len(activos) # Nota: esto es por página, en app real el count vendría del backend
        total_suspendidos = len(inactivos)
        avg_saldo = sum_saldo / total_activos if total_activos > 0 else 0

        self.update_stats(total_activos, total_suspendidos, avg_saldo, sum_estrellas)

    def _create_empty_card(self, parent_container):
        card = ctk.CTkFrame(parent_container, corner_radius=8, fg_color="#2b2b2b")
        
        circle = ctk.CTkFrame(card, width=40, height=40, corner_radius=20, fg_color="#FF5A1F")
        circle.pack(side="left", padx=15, pady=15)
        circle.pack_propagate(False)
        lbl_initial = ctk.CTkLabel(circle, text="U", text_color="white", font=ctk.CTkFont(weight="bold"))
        lbl_initial.place(relx=0.5, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=10)

        lbl_name = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(weight="bold", size=14))
        lbl_name.pack(anchor="w")
        lbl_desc = ctk.CTkLabel(info_frame, text="", text_color="gray", font=ctk.CTkFont(size=12))
        lbl_desc.pack(anchor="w")

        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=10)

        lbl_status = ctk.CTkLabel(right_frame, text="", font=ctk.CTkFont(weight="bold"))
        lbl_status.pack(anchor="e")
        lbl_balances = ctk.CTkLabel(right_frame, text="", font=ctk.CTkFont(size=12))
        lbl_balances.pack(anchor="e")

        btn_action = ctk.CTkButton(
            right_frame, text="", width=80, height=24
        )
        btn_action.pack(anchor="e", pady=(5, 0))

        card.widgets = {
            "circle": circle,
            "initial": lbl_initial,
            "name": lbl_name,
            "desc": lbl_desc,
            "status": lbl_status,
            "balances": lbl_balances,
            "btn_action": btn_action
        }
        return card

    def _update_card(self, card, user: User):
        w = card.widgets
        
        initial = user.nombre[0].upper() if user.nombre and user.nombre != 'Sin nombre' else "U"
        w["circle"].configure(fg_color="#FF5A1F" if user.activo else "gray")
        w["initial"].configure(text=initial)
        
        w["name"].configure(text=user.nombre)
        w["desc"].configure(text=f"ID: {user.id_usuario} | {user.correo}")
        
        status_text = "Activo" if user.activo else "Suspendido"
        status_color = "green" if user.activo else "red"
        w["status"].configure(text=status_text, text_color=status_color)
        w["balances"].configure(text=f"S/ {user.saldo:.2f} | {user.estrellas} ⭐")
        
        if user.id_usuario != 'N/A':
            w["btn_action"].pack(anchor="e", pady=(5, 0))
            if user.activo:
                w["btn_action"].configure(
                    text="Suspender", fg_color="red", hover_color="#8B0000",
                    command=functools.partial(self.suspender_usuario, user.id_usuario)
                )
            else:
                w["btn_action"].configure(
                    text="Activar", fg_color="green", hover_color="#006400",
                    command=functools.partial(self.reactivar_usuario, user.id_usuario)
                )
        else:
            w["btn_action"].pack_forget()

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
