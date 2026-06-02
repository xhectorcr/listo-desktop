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

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.btn_toggle_cam = ctk.CTkButton(self, text="Encender Cámara", command=self.toggle_camera)
        self.btn_toggle_cam.pack(pady=10)

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

            # HILO 1: Leer la cámara constantemente (evita lag en el buffer)
            def camera_reader():
                while self.running and self.cap is not None:
                    ret, frame = self.cap.read()
                    if ret:
                        self.latest_frame = frame
                    time.sleep(0.01)

            # HILO 2: Procesar YOLO (pesado) en paralelo sin bloquear
            def yolo_worker():
                while self.running:
                    if self.latest_frame is not None and not self.yolo_running:
                        self.yolo_running = True
                        frame_copy = self.latest_frame.copy()
                        
                        try:
                            results = self.model(frame_copy, verbose=False)
                            annotated_frame = results[0].plot()
                            
                            self.latest_annotated = annotated_frame
                            
                            boxes = results[0].boxes
                            if boxes is not None and hasattr(boxes, 'cls'):
                                clss = boxes.cls.cpu().numpy().astype(int)
                                confs = boxes.conf.cpu().numpy()
                                user_id = 1 
                                
                                if user_id not in self.processed_ids:
                                    self.processed_ids[user_id] = {}
                                    
                                for idx, (cls_id, conf) in enumerate(zip(clss, confs)):
                                    key = f"{cls_id}_{idx}"
                                    if key not in self.processed_ids[user_id]:
                                        class_name = self.model.names[cls_id]
                                        self.processed_ids[user_id][key] = class_name
                                        
                                        threading.Thread(
                                            target=ApiService.agregar_carrito, 
                                            args=(user_id, class_name, float(conf)), 
                                            daemon=True
                                        ).start()
                        except Exception as e:
                            print("Error en YOLO:", e)
                        
                        self.yolo_running = False
                    time.sleep(0.005)
            
            threading.Thread(target=camera_reader, daemon=True).start()
            threading.Thread(target=yolo_worker, daemon=True).start()

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
            except Exception as e:
                pass

        # Llamar recursivamente cada 20ms (equivale a ~50 FPS para la UI)
        self.after(20, self.update_ui)

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
