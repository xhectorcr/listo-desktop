import customtkinter as ctk
import threading
from services.api_service import ApiService

class ProductsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        # Top section: Header
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=10)

        self.title_label = ctk.CTkLabel(
            self.top_frame, 
            text="Gestión de Inventario", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")

        self.btn_new = ctk.CTkButton(
            self.top_frame, text="+ Nuevo Producto", 
            fg_color="#FF5A1F", hover_color="#E64A19",
            command=self.show_product_form
        )
        self.btn_new.pack(side="right")

        # Filters section
        self.filters_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filters_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.btn_refresh = ctk.CTkButton(
            self.filters_frame, text="Actualizar", 
            fg_color="#333333", hover_color="#444444",
            width=100,
            command=self.load_products
        )
        self.btn_refresh.pack(side="left")

        # List Area
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(expand=True, fill="both", padx=20, pady=(0, 20))

        # Pagination Area
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Página 1", text_color="gray")
        self.lbl_page.pack(side="left")

        # Load data initially
        self.load_products()

    def load_products(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        loading_lbl = ctk.CTkLabel(self.scroll_frame, text="Cargando productos...")
        loading_lbl.pack(pady=20)

        def fetch():
            products = ApiService.get_productos(page=1, size=100)
            self.after(0, lambda: self.render_products(products, loading_lbl))

        threading.Thread(target=fetch, daemon=True).start()

    def render_products(self, products, loading_lbl):
        loading_lbl.destroy()
        
        if not products:
            ctk.CTkLabel(self.scroll_frame, text="No se encontraron productos.", text_color="gray").pack(pady=20)
            return

        for prod in products:
            self.create_product_card(prod).pack(fill="x", pady=5)

    def create_product_card(self, prod):
        nombre = prod.get('nombre', 'Sin nombre')
        precio = float(prod.get('precio', 0) or 0)
        stock = int(prod.get('stock', 0) or 0)
        yolo_label = prod.get('yoloLabel', 'N/A')
        categoria = prod.get('categoria', 'Sin asignar')

        card = ctk.CTkFrame(self.scroll_frame, corner_radius=8, fg_color="#2b2b2b")
        
        # Icon
        icon_frame = ctk.CTkFrame(card, width=40, height=40, corner_radius=8, fg_color="#e0e0e0")
        icon_frame.pack(side="left", padx=15, pady=15)
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="📦", font=ctk.CTkFont(size=20)).place(relx=0.5, rely=0.5, anchor="center")

        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, pady=10)

        ctk.CTkLabel(info_frame, text=nombre, font=ctk.CTkFont(weight="bold", size=14)).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"Etiqueta YOLO: {yolo_label} | Categoría: {categoria}", text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w")

        # Right side (Prices, Stock, Buttons)
        right_frame = ctk.CTkFrame(card, fg_color="transparent")
        right_frame.pack(side="right", padx=15, pady=10)

        ctk.CTkLabel(right_frame, text=f"S/ {precio:.2f}", font=ctk.CTkFont(weight="bold", size=16)).pack(anchor="e")
        stock_color = "red" if stock <= 5 else "gray"
        ctk.CTkLabel(right_frame, text=f"Stock: {stock}", text_color=stock_color, font=ctk.CTkFont(size=12)).pack(anchor="e")

        actions_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        actions_frame.pack(anchor="e", pady=(5,0))

        btn_edit = ctk.CTkButton(actions_frame, text="✏️", width=30, height=30, fg_color="#1f538d", command=lambda: self.show_product_form(prod))
        btn_edit.pack(side="left", padx=2)
        
        btn_del = ctk.CTkButton(actions_frame, text="🗑️", width=30, height=30, fg_color="#C62828", command=lambda: self.confirm_delete_product(prod))
        btn_del.pack(side="left", padx=2)

        return card

    def show_product_form(self, producto_editar=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Editar Producto" if producto_editar else "Nuevo Producto")
        modal.geometry("450x600")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        ctk.CTkLabel(modal, text="Formulario de Producto", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        scroll = ctk.CTkScrollableFrame(modal)
        scroll.pack(expand=True, fill="both", padx=20, pady=10)

        # Fields
        lbl_nombre = ctk.CTkLabel(scroll, text="Nombre del Producto")
        lbl_nombre.pack(anchor="w")
        ent_nombre = ctk.CTkEntry(scroll)
        ent_nombre.pack(fill="x", pady=(0, 10))
        if producto_editar: ent_nombre.insert(0, producto_editar.get("nombre", ""))

        lbl_desc = ctk.CTkLabel(scroll, text="Descripción")
        lbl_desc.pack(anchor="w")
        ent_desc = ctk.CTkEntry(scroll)
        ent_desc.pack(fill="x", pady=(0, 10))
        if producto_editar: ent_desc.insert(0, producto_editar.get("descripcion") or "")

        lbl_yolo = ctk.CTkLabel(scroll, text="Etiqueta YOLO")
        lbl_yolo.pack(anchor="w")
        ent_yolo = ctk.CTkEntry(scroll)
        ent_yolo.pack(fill="x", pady=(0, 10))
        if producto_editar: ent_yolo.insert(0, producto_editar.get("yoloLabel", ""))

        # Category Dropdown
        lbl_cat = ctk.CTkLabel(scroll, text="Categoría")
        lbl_cat.pack(anchor="w")
        
        cat_var = ctk.StringVar(value="Cargando...")
        opt_cat = ctk.CTkOptionMenu(scroll, variable=cat_var, values=["Cargando..."])
        opt_cat.pack(fill="x", pady=(0, 10))

        # Prices and Stock
        row_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 10))
        
        lbl_precio = ctk.CTkLabel(row_frame, text="Precio (S/.)")
        lbl_precio.pack(side="left", padx=(0, 5))
        ent_precio = ctk.CTkEntry(row_frame, width=80)
        ent_precio.pack(side="left", padx=(0, 20))
        if producto_editar: ent_precio.insert(0, str(producto_editar.get("precio", "0")))

        lbl_stock = ctk.CTkLabel(row_frame, text="Stock")
        lbl_stock.pack(side="left", padx=(0, 5))
        ent_stock = ctk.CTkEntry(row_frame, width=80)
        ent_stock.pack(side="left")
        if producto_editar: ent_stock.insert(0, str(producto_editar.get("stock", "0")))

        lbl_status = ctk.CTkLabel(modal, text="", text_color="red")
        lbl_status.pack(pady=5)

        categorias_map = {}

        def load_cats():
            cats = ApiService.get_categorias()
            if cats:
                for c in cats:
                    categorias_map[c["nombre"]] = c["idCategoria"]
                cat_names = list(categorias_map.keys())
                opt_cat.configure(values=cat_names)
                
                if producto_editar and producto_editar.get("idCategoria"):
                    # Find name by id
                    cat_name = next((name for name, id_c in categorias_map.items() if id_c == producto_editar["idCategoria"]), cat_names[0])
                    cat_var.set(cat_name)
                else:
                    cat_var.set(cat_names[0])
            else:
                opt_cat.configure(values=["Sin categorías"])
                cat_var.set("Sin categorías")

        threading.Thread(target=load_cats, daemon=True).start()

        def on_save():
            nombre = ent_nombre.get().strip()
            yolo = ent_yolo.get().strip()
            precio_str = ent_precio.get().strip()
            stock_str = ent_stock.get().strip()
            cat_name = cat_var.get()

            if not nombre or not yolo or not precio_str or not stock_str:
                lbl_status.configure(text="Por favor completa los campos requeridos", text_color="red")
                return

            try:
                precio = float(precio_str)
                stock = int(stock_str)
            except:
                lbl_status.configure(text="Precio y stock deben ser numéricos", text_color="red")
                return

            cat_id = categorias_map.get(cat_name, 0)

            payload = {
                "idProducto": producto_editar["idProducto"] if producto_editar else 0,
                "nombre": nombre,
                "descripcion": ent_desc.get().strip(),
                "yoloLabel": yolo,
                "precio": precio,
                "stock": stock,
                "idCategoria": cat_id,
                "activo": True
            }

            lbl_status.configure(text="Guardando...", text_color="white")
            btn_save.configure(state="disabled")

            def save_task():
                if producto_editar:
                    res = ApiService.update_producto(payload)
                else:
                    res = ApiService.create_producto(payload)
                
                def on_done():
                    if res.get("success"):
                        modal.destroy()
                        self.load_products()
                    else:
                        lbl_status.configure(text=res.get("message", "Error al guardar"), text_color="red")
                        btn_save.configure(state="normal")
                self.after(0, on_done)

            threading.Thread(target=save_task, daemon=True).start()

        btn_save = ctk.CTkButton(modal, text="Guardar Producto", fg_color="#FF5A1F", hover_color="#E64A19", command=on_save)
        btn_save.pack(pady=10)

    def confirm_delete_product(self, prod):
        modal = ctk.CTkToplevel(self)
        modal.title("Eliminar Producto")
        modal.geometry("350x200")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        ctk.CTkLabel(modal, text="¿Eliminar Producto?", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        ctk.CTkLabel(modal, text=f"¿Estás seguro que deseas eliminar\n'{prod.get('nombre', '')}'?").pack()

        lbl_status = ctk.CTkLabel(modal, text="", text_color="red")
        lbl_status.pack(pady=5)

        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.pack(pady=10)

        def on_delete():
            btn_del.configure(state="disabled")
            lbl_status.configure(text="Eliminando...")

            def del_task():
                # Try with idProducto or id
                p_id = prod.get("idProducto") or prod.get("id")
                res = ApiService.delete_producto(p_id)
                def on_done():
                    if res.get("success"):
                        modal.destroy()
                        self.load_products()
                    else:
                        lbl_status.configure(text=res.get("message", "Error al eliminar"))
                        btn_del.configure(state="normal")
                self.after(0, on_done)
            threading.Thread(target=del_task, daemon=True).start()

        ctk.CTkButton(btn_frame, text="Cancelar", width=100, fg_color="gray", command=modal.destroy).pack(side="left", padx=10)
        btn_del = ctk.CTkButton(btn_frame, text="Eliminar", width=100, fg_color="#C62828", hover_color="#B71C1C", command=on_delete)
        btn_del.pack(side="left", padx=10)
