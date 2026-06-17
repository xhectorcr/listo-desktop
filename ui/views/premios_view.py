import customtkinter as ctk
import tkinter.messagebox as messagebox
import functools
from controllers.rewards_controller import RewardsController
from domain.models.user import User

class PremiosView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.controller = RewardsController()
        
        self.sent_coupons = 14 # Simulation count
        self.sending_states = {}
        self.current_page = 1
        self.cards_pool = []

        # Top section: Header
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(
            self.top_frame, 
            text="Premios y Cupones", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.top_frame, 
            text="Envía cupones promocionales a tus clientes fidelizados.", 
            text_color="gray"
        )
        self.subtitle_label.pack(anchor="w", pady=(0, 10))

        # Stats
        self.stats_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.stats_frame.pack(fill="x", pady=10)

        self.stat_campana = self.create_stat_card(self.stats_frame, "Campaña Activa", "BIENVENIDA15")
        self.stat_campana.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.stat_enviados = self.create_stat_card(self.stats_frame, "Cupones Enviados", str(self.sent_coupons))
        self.stat_enviados.pack(side="left", expand=True, fill="x", padx=10)

        self.stat_clientes = self.create_stat_card(self.stats_frame, "Clientes en Vista", "0")
        self.stat_clientes.pack(side="left", expand=True, fill="x", padx=(10, 0))

        # Manual send frame
        self.manual_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        self.manual_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(self.manual_frame, text="Enviar Cupón Manual", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        
        row_manual = ctk.CTkFrame(self.manual_frame, fg_color="transparent")
        row_manual.pack(fill="x", padx=20, pady=(0, 15))
        
        self.ent_email_manual = ctk.CTkEntry(row_manual, placeholder_text="ejemplo@correo.com")
        self.ent_email_manual.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        self.btn_send_manual = ctk.CTkButton(row_manual, text="Enviar", fg_color="#FF5A1F", hover_color="#E64A19", width=100, command=self.send_manual)
        self.btn_send_manual.pack(side="left")

        self.lbl_manual_status = ctk.CTkLabel(self.manual_frame, text="", text_color="red")
        self.lbl_manual_status.pack(anchor="w", padx=20, pady=(0, 10))

        # List Area
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(expand=True, fill="both", padx=20, pady=(0, 10))

        # Pagination Area
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="<", width=30, command=self.prev_page)
        self.btn_prev.pack(side="left", padx=5)

        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Página 1", text_color="gray")
        self.lbl_page.pack(side="left", padx=10)

        self.btn_next = ctk.CTkButton(self.pagination_frame, text=">", width=30, command=self.next_page)
        self.btn_next.pack(side="left", padx=5)

        self.loading_lbl = ctk.CTkLabel(self.scroll_frame, text="Cargando clientes...")

        # Load data initially
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

    def load_users(self):
        for card in self.cards_pool:
            card.pack_forget()
            
        self.loading_lbl.configure(text="Cargando clientes...")
        self.loading_lbl.pack(pady=20)
        self.lbl_page.configure(text=f"Página {self.current_page}")

        def _on_success(users: list[User]):
            self.after(0, lambda: self.render_users(users))

        self.controller.load_users(self.current_page, _on_success)

    def render_users(self, users: list[User]):
        self.loading_lbl.pack_forget()
        self.stat_clientes.value_label.configure(text=str(len(users)))

        if not users:
            if self.current_page > 1:
                self.current_page -= 1
                self.after(0, lambda: messagebox.showinfo("Fin", "No hay más clientes."))
                self.load_users()
            else:
                self.loading_lbl.configure(text="No hay clientes registrados.")
                self.loading_lbl.pack(pady=20)
            return

        while len(self.cards_pool) < len(users):
            self.cards_pool.append(self._create_empty_card())

        for i, user in enumerate(users):
            card = self.cards_pool[i]
            self._update_card(card, user)
            card.pack(fill="x", pady=5)

    def _create_empty_card(self):
        card = ctk.CTkFrame(self.scroll_frame, corner_radius=8, fg_color="#2b2b2b")
        
        circle = ctk.CTkFrame(card, width=40, height=40, corner_radius=20, fg_color="#FF5A1F")
        circle.pack(side="left", padx=15, pady=15)
        circle.pack_propagate(False)
        lbl_initial = ctk.CTkLabel(circle, text="C", text_color="white", font=ctk.CTkFont(weight="bold"))
        lbl_initial.place(relx=0.5, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=10)

        lbl_name = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(weight="bold", size=14))
        lbl_name.pack(anchor="w")
        lbl_desc = ctk.CTkLabel(info_frame, text="", text_color="gray", font=ctk.CTkFont(size=12))
        lbl_desc.pack(anchor="w")

        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=10)

        lbl_status = ctk.CTkLabel(right_frame, text="", text_color="green", font=ctk.CTkFont(size=10))
        lbl_status.pack(side="top", anchor="e")

        btn_send = ctk.CTkButton(
            right_frame, text="🎁 Enviar Cupón", 
            fg_color="#1f538d", hover_color="#14375e",
            width=100
        )
        btn_send.pack(side="bottom")

        card.widgets = {
            "initial": lbl_initial,
            "name": lbl_name,
            "desc": lbl_desc,
            "status": lbl_status,
            "btn_send": btn_send
        }
        return card

    def _update_card(self, card, user: User):
        w = card.widgets
        initial = user.nombre[0].upper() if user.nombre and user.nombre != 'Sin nombre' else "C"
        w["initial"].configure(text=initial)
        w["name"].configure(text=user.nombre)
        w["desc"].configure(text=f"{user.correo} | {user.estrellas} ⭐")
        w["status"].configure(text="")

        uid = user.id_usuario
        if self.sending_states.get(uid):
            w["btn_send"].configure(state="disabled", text="Enviando...", fg_color="#1f538d")
        else:
            w["btn_send"].configure(
                state="normal", text="🎁 Enviar Cupón", fg_color="#1f538d",
                command=functools.partial(self.send_to_user, user, w["btn_send"], w["status"])
            )

    def send_to_user(self, user: User, btn_send, lbl_status):
        uid = user.id_usuario
        if self.sending_states.get(uid): return
        
        self.sending_states[uid] = True
        btn_send.configure(state="disabled", text="Enviando...")
        lbl_status.configure(text="")

        def _on_complete(success: bool, msg: str):
            self.sending_states[uid] = False
            if success:
                self.after(0, lambda: btn_send.configure(text="¡Enviado!", fg_color="green"))
                self.sent_coupons += 1
                self.after(0, lambda: self.stat_enviados.value_label.configure(text=str(self.sent_coupons)))
            else:
                self.after(0, lambda: btn_send.configure(state="normal", text="Reintentar"))
                self.after(0, lambda: lbl_status.configure(text="Falló el envío", text_color="red"))

        self.controller.send_coupon(user.correo, _on_complete)

    def send_manual(self):
        email = self.ent_email_manual.get().strip()
        if not email:
            self.lbl_manual_status.configure(text="Ingresa un correo electrónico", text_color="red")
            return

        self.btn_send_manual.configure(state="disabled", text="Enviando...")
        self.lbl_manual_status.configure(text="")

        def _on_complete(success: bool, msg: str):
            self.after(0, lambda: self.btn_send_manual.configure(state="normal", text="Enviar"))
            if success:
                self.after(0, lambda: self.lbl_manual_status.configure(text="¡Cupón enviado exitosamente!", text_color="green"))
                self.after(0, lambda: self.ent_email_manual.delete(0, 'end'))
                self.sent_coupons += 1
                self.after(0, lambda: self.stat_enviados.value_label.configure(text=str(self.sent_coupons)))
            else:
                self.after(0, lambda: self.lbl_manual_status.configure(text=msg, text_color="red"))

        self.controller.send_coupon(email, _on_complete)
