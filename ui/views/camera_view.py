import customtkinter as ctk
from PIL import Image
import cv2
import threading
import time
import platform
from ultralytics import YOLO
from services.api_service import ApiService

class CameraView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        try:
            self.model = YOLO("models/ai/best.pt")
        except Exception as e:
            print("No se pudo cargar el modelo:", e)
            self.model = None

        self.cap = None
        self.running = False
        self.processed_ids = {}

        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Cámara (Izquierda)
        self.video_label = ctk.CTkLabel(self.main_container, text="")
        self.video_label.pack(side="left", expand=True, fill="both")
        
        # Panel (Derecha)
        self.right_panel = ctk.CTkFrame(self.main_container, width=250)
        self.right_panel.pack(side="right", fill="y", padx=(20, 0))
        
        self.lbl_title_users = ctk.CTkLabel(self.right_panel, text="Usuarios en Tienda", font=("Arial", 16, "bold"))
        self.lbl_title_users.pack(pady=10)
        
        self.lbl_active_users = ctk.CTkLabel(self.right_panel, text="Ninguno", justify="left")
        self.lbl_active_users.pack(pady=10, padx=10, fill="x")

        self.btn_toggle_cam = ctk.CTkButton(self.right_panel, text="Encender Cámara", command=self.toggle_camera)
        self.btn_toggle_cam.pack(pady=10)

        self.btn_limpiar = ctk.CTkButton(
            self.right_panel, text="Limpiar Tienda", 
            fg_color="#FF5A1F", hover_color="#E64A19",
            command=self.limpiar_tienda
        )
        self.btn_limpiar.pack(pady=10)

    def limpiar_tienda(self):
        exito = ApiService.limpiar_tienda()
        if exito:
            print("Tienda limpiada. Todos los usuarios han sido reseteados.")
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Éxito", "La tienda ha sido limpiada.")
            if hasattr(self, 'track_to_user_map'):
                self.track_to_user_map.clear()
        else:
            print("Error al limpiar tienda.")

    def toggle_camera(self):
        if not self.running:
            self.running = True
            self.btn_toggle_cam.configure(text="Apagar Cámara", fg_color="#C62828", hover_color="#B71C1C")
            
            api = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
            self.cap = cv2.VideoCapture(0, api)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.latest_frame = None
            self.latest_annotated = None
            self.yolo_running = False
            self.active_tracks = {} # Diccionario para mantener Track IDs y su timestamp
            self.track_to_user_map = {} # Mapeo {track_id: usuario_id}
            self.notified_users = set() # Usuarios que ya mostraron toast de ingreso

            # HILO 1: Leer la cámara constantemente
            def camera_reader():
                while self.running and self.cap is not None:
                    ret, frame = self.cap.read()
                    if ret:
                        self.latest_frame = frame
                    time.sleep(0.01)

            self.product_states = {} # {track_id: {"class": name, "intersectors": set(), "last_seen": time, "taken_by": None}}
            self.finished_tracks = set() # tracks que ya cruzaron la salida

            def check_intersection(boxA, boxB):
                xA = max(boxA[0], boxB[0])
                yA = max(boxA[1], boxB[1])
                xB = min(boxA[2], boxB[2])
                yB = min(boxA[3], boxB[3])
                return max(0, xB - xA) * max(0, yB - yA) > 0

            # HILO 2: Procesar YOLO
            def yolo_worker():
                while self.running:
                    if self.latest_frame is not None and not self.yolo_running:
                        self.yolo_running = True
                        frame_copy = self.latest_frame.copy()
                        
                        try:
                            results = self.model.track(frame_copy, persist=True, tracker="bytetrack.yaml", verbose=False)
                            # Ya no usamos plot() de YOLO para evitar textos duplicados
                            annotated_frame = frame_copy.copy()
                            
                            # Dibujar línea de salida (X = 500)
                            cv2.line(annotated_frame, (500, 0), (500, 480), (0, 0, 255), 2)
                            cv2.putText(annotated_frame, "SALIDA", (510, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                            
                            self.latest_annotated = annotated_frame
                            
                            boxes = results[0].boxes
                            if boxes is not None and hasattr(boxes, 'id') and boxes.id is not None:
                                track_ids = boxes.id.cpu().numpy().astype(int)
                                clss = boxes.cls.cpu().numpy().astype(int)
                                xyxys = boxes.xyxy.cpu().numpy()
                                confs = boxes.conf.cpu().numpy()
                                
                                current_persons = {}
                                current_products = {}

                                for track_id, cls_id, bbox, conf in zip(track_ids, clss, xyxys, confs):
                                    class_name = self.model.names[cls_id]
                                    
                                    if class_name == "person" or class_name == "persona":
                                        current_persons[track_id] = bbox
                                        self.active_tracks[track_id] = time.time()
                                        
                                        uid = self.track_to_user_map.get(track_id)
                                        # Buscar el nombre en self.backend_users
                                        nombre = "Desconocido"
                                        for u in self.backend_users:
                                            u_id = u.get("idUsuario") or u.get("IDUsuario") or u.get("idusuario")
                                            if u_id == uid:
                                                nombre = u.get("nombre") or u.get("Nombre") or "Desconocido"
                                                break
                                                
                                        # Dibujar etiqueta manual y caja
                                        if uid:
                                            label_text = f"{nombre} (ID: {uid}) {conf:.2f}"
                                            color = (0, 255, 0) # Verde si está asignado
                                        else:
                                            label_text = f"Persona (Track: {track_id}) {conf:.2f}"
                                            color = (0, 255, 255) # Amarillo si no
                                            
                                        # Dibujar caja
                                        cv2.rectangle(annotated_frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)
                                        
                                        # Dibujar fondo para el texto para mayor visibilidad
                                        (text_w, text_h), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                                        cv2.rectangle(annotated_frame, (int(bbox[0]), int(bbox[1]) - 30), (int(bbox[0]) + text_w, int(bbox[1])), color, -1)
                                        
                                        # Dibujar texto
                                        cv2.putText(annotated_frame, label_text, (int(bbox[0]), int(bbox[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

                                        # Paso 10: Salida de la tienda
                                        # Si el centro de la persona cruza X=500
                                        center_x = (bbox[0] + bbox[2]) / 2
                                        if center_x > 500 and track_id not in self.finished_tracks:
                                            self.finished_tracks.add(track_id)
                                            # Buscar si está vinculado a un usuario
                                            usuario_id = self.track_to_user_map.get(track_id)
                                            if usuario_id:
                                                print(f"Persona {track_id} cruzó la salida. Finalizando compra de Usuario {usuario_id}")
                                                threading.Thread(target=ApiService.finalizar_compra, args=(usuario_id,), daemon=True).start()
                                                del self.track_to_user_map[track_id]
                                    else:
                                        current_products[track_id] = (class_name, bbox)
                                        label_text = f"{class_name} {conf:.2f}"
                                        p_color = (255, 0, 0) # Azul para productos
                                        
                                        cv2.rectangle(annotated_frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), p_color, 2)
                                        
                                        (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                                        cv2.rectangle(annotated_frame, (int(bbox[0]), int(bbox[1]) - 25), (int(bbox[0]) + tw, int(bbox[1])), p_color, -1)
                                        
                                        cv2.putText(annotated_frame, label_text, (int(bbox[0]), int(bbox[1]) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                                # Paso 9: Lógica Tomar/Devolver
                                current_time = time.time()
                                
                                # Actualizar estado de productos actuales
                                for p_tid, (p_class, p_box) in current_products.items():
                                    if p_tid not in self.product_states:
                                        self.product_states[p_tid] = {"class": p_class, "intersectors": set(), "last_seen": current_time, "taken_by": None}
                                    
                                    state = self.product_states[p_tid]
                                    state["last_seen"] = current_time
                                    
                                    # Si estaba tomado y reaparece -> DEVOLVER
                                    if state["taken_by"] is not None:
                                        usuario_id = self.track_to_user_map.get(state["taken_by"])
                                        if usuario_id:
                                            print(f"Producto {p_class} devuelto por persona {state['taken_by']} (Usuario {usuario_id})")
                                            threading.Thread(target=ApiService.remover_carrito, args=(usuario_id, p_class), daemon=True).start()
                                        state["taken_by"] = None

                                    # Calcular intersecciones con personas en este frame
                                    state["intersectors"].clear()
                                    for pers_tid, pers_box in current_persons.items():
                                        if check_intersection(p_box, pers_box):
                                            state["intersectors"].add(pers_tid)

                                # Revisar productos que desaparecieron (más de 1 segundo sin ver)
                                for p_tid in list(self.product_states.keys()):
                                    state = self.product_states[p_tid]
                                    if current_time - state["last_seen"] > 1.0 and state["taken_by"] is None:
                                        # Desapareció! Si interactuaba con alguien, lo tomó
                                        if len(state["intersectors"]) > 0:
                                            # Asignar a la primera persona que lo estaba tocando
                                            pers_tid = list(state["intersectors"])[0]
                                            state["taken_by"] = pers_tid
                                            
                                            usuario_id = self.track_to_user_map.get(pers_tid)
                                            if usuario_id:
                                                print(f"Producto {state['class']} tomado por persona {pers_tid} (Usuario {usuario_id})")
                                                threading.Thread(target=ApiService.agregar_carrito, args=(usuario_id, state["class"], 1.0), daemon=True).start()
                                        else:
                                            # Desapareció sin que nadie lo tocara (error de cámara), lo borramos
                                            del self.product_states[p_tid]
                                            
                        except Exception as e:
                            print("Error en YOLO Tracking:", e)
                        
                        self.yolo_running = False
                    time.sleep(0.005)

            self.backend_users = [] # Almacena la lista de usuarios devuelta por el backend

            # HILO 3: Vincular "Usuarios en Tienda" con "Nuevos Track IDs"
            def user_assignment_worker():
                while self.running:
                    # Limpiar tracks viejos que ya no están en cámara (más de 5 segundos sin verse)
                    current_time = time.time()
                    for t_id in list(self.active_tracks.keys()):
                        if current_time - self.active_tracks[t_id] > 5.0:
                            del self.active_tracks[t_id]
                            # Si este track estaba asignado a un usuario, lo desvinculamos localmente
                            # para que pueda ser reasignado cuando vuelva a aparecer
                            if t_id in self.track_to_user_map:
                                del self.track_to_user_map[t_id]

                    # 1. Obtener todos los usuarios que están en la tienda
                    usuarios_en_tienda = ApiService.get_usuarios_en_tienda()
                    self.backend_users = usuarios_en_tienda
                    
                    if usuarios_en_tienda:
                        # 2. Encontrar qué usuarios necesitan un Track ID
                        assigned_user_ids = list(self.track_to_user_map.values())
                        
                        for user in usuarios_en_tienda:
                            id_usuario = user.get("idUsuario") or user.get("IDUsuario") or user.get("idusuario")
                            estado_sesion = user.get("estadoSesion") or user.get("EstadoSesion")
                            nombre_usuario = user.get("nombre") or user.get("Nombre") or "Desconocido"
                            
                            # NOTIFICACIÓN TEMPORAL DE INGRESO
                            if estado_sesion == "EsperandoAsignacion" and id_usuario and id_usuario not in self.notified_users:
                                self.notified_users.add(id_usuario)
                                self.after(0, lambda n=nombre_usuario, i=id_usuario: self.show_toast_notification(n, i))

                            if id_usuario and id_usuario not in assigned_user_ids:
                                # Este usuario está en la tienda pero no tiene track asignado
                                unassigned_tracks = [t_id for t_id in self.active_tracks.keys() if t_id not in self.track_to_user_map]
                                
                                if unassigned_tracks:
                                    nuevo_track_id = unassigned_tracks[0] # Tomar el primer track libre
                                    
                                    if estado_sesion == "EsperandoAsignacion":
                                        print(f"Asignando Usuario Nuevo {id_usuario} al Track ID {nuevo_track_id}")
                                        exito = ApiService.asignar_track(id_usuario, nuevo_track_id)
                                        if exito:
                                            self.track_to_user_map[nuevo_track_id] = id_usuario
                                            assigned_user_ids.append(id_usuario)
                                            print("Asignación completada exitosamente en el backend.")
                                    elif estado_sesion == "Comprando":
                                        # Ya está comprando, solo perdió su track. Lo reasignamos localmente.
                                        print(f"Re-asignando Usuario Existente {id_usuario} al Track ID {nuevo_track_id}")
                                        self.track_to_user_map[nuevo_track_id] = id_usuario
                                        assigned_user_ids.append(id_usuario)
                    
                    time.sleep(1) # Consultar cada 1 segundo

            threading.Thread(target=camera_reader, daemon=True).start()
            threading.Thread(target=yolo_worker, daemon=True).start()
            threading.Thread(target=user_assignment_worker, daemon=True).start()

            # Comenzar a actualizar la UI en el Hilo Principal
            self.update_ui()
        else:
            self.running = False
            self.btn_toggle_cam.configure(text="Encender Cámara", fg_color=["#3a7ebf", "#1f538d"], hover_color=["#325882", "#14375e"])
            if self.cap:
                self.cap.release()
                self.cap = None
            self.video_label.configure(image="")

    def update_ui(self):
        if not self.running:
            return

        # Si tenemos un frame procesado por YOLO, lo pintamos
        if self.latest_annotated is not None:
            try:
                annotated_frame_rgb = cv2.cvtColor(self.latest_annotated, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(annotated_frame_rgb)
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(640, 480))
                self.video_label.configure(image=ctk_image, text="")
                
                # Actualizar el panel de usuarios usando self.backend_users
                if hasattr(self, 'backend_users') and self.backend_users:
                    users_text = ""
                    for user in self.backend_users:
                        uid = user.get("idUsuario") or user.get("IDUsuario") or user.get("idusuario")
                        nombre = user.get("nombre") or user.get("Nombre") or f"ID {uid}"
                        
                        # Buscar si este usuario tiene un track id asignado
                        assigned_track = None
                        for tid, u_id in self.track_to_user_map.items():
                            if u_id == uid:
                                assigned_track = tid
                                break
                        
                        carrito = user.get("carrito") or user.get("Carrito") or []
                        carrito_text = f"Carrito: [{', '.join(carrito)}]" if carrito else "Carrito vacío"
                        
                        if assigned_track is not None:
                            users_text += f"> {nombre} (ID: {uid}) - Track: {assigned_track} | {carrito_text}\n"
                        else:
                            users_text += f"> {nombre} (ID: {uid}) - Buscando... | {carrito_text}\n"
                            
                    self.lbl_active_users.configure(text=users_text)
                else:
                    self.lbl_active_users.configure(text="Ninguno")
                    
            except Exception as e:
                print(f"Error en update_ui: {e}")

        # Llamar recursivamente cada 20ms (equivale a ~50 FPS para la UI)
        self.after(20, self.update_ui)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

    def show_toast_notification(self, nombre, id_usuario):
        toast = ctk.CTkFrame(self.main_container, fg_color="#2b2b2b", corner_radius=10, border_width=2, border_color="#FF5A1F")
        # Posicionarlo en la parte superior, centrado
        toast.place(relx=0.5, rely=0.05, anchor="n")
        
        lbl = ctk.CTkLabel(toast, text=f"¡El usuario {nombre} (ID: {id_usuario}) validó su PIN y va a entrar!", 
                           font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        lbl.pack(padx=20, pady=15)
        
        # Eliminar el toast después de 5 segundos
        self.after(5000, toast.destroy)
