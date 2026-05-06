import cv2
import platform
import threading
import time
import httpx
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = YOLO("models/best.pt")

# Silenciar warnings OpenCV
try:
    cv2.utils.logging.setLogLevel(cv2.utils.logging.LOG_LEVEL_ERROR)
except Exception:
    pass

# ── Cámara ──────────────────────────────────────────────
def open_camera(index=0, width=640, height=480):
    api = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
    c = cv2.VideoCapture(index, api)
    c.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    c.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    time.sleep(0.2)
    return c

cap: Optional[cv2.VideoCapture] = None
latest_frame = None
processed_frame = None
frame_lock = threading.Lock()
running = False

processed_ids = {}
sync_client = httpx.Client(timeout=5.0)

def send_to_backend(payload):
    try:
        sync_client.post("http://localhost:5115/api/carrito/agregar", json=payload)
    except Exception as e:
        print("Error backend:", e)

# ── Hilo 1: Captura ─────────────────────────────────────
def capture_loop():
    global latest_frame, cap
    while running:
        if cap is None or not cap.isOpened():
            cap = open_camera(0)
            time.sleep(0.5)
            continue
        ret, frame = cap.read()
        if ret and frame is not None:
            with frame_lock:
                latest_frame = frame
        else:
            time.sleep(0.05)

# ── Hilo 2: YOLO ────────────────────────────────────────
def yolo_loop():
    global processed_frame
    frame_count = 0
    while running:
        with frame_lock:
            frame = None if latest_frame is None else latest_frame.copy()

        if frame is None:
            time.sleep(0.01)
            continue

        frame_count += 1
        if frame_count % 2 != 0:
            time.sleep(0.005)
            continue

        try:
            results = model.predict(frame, verbose=False)
            annotated = results[0].plot()
        except Exception as e:
            print("Error YOLO:", e)
            annotated = frame

        # Lógica carrito
        try:
            boxes = results[0].boxes
            if boxes is not None and hasattr(boxes, 'cls'):
                clss = boxes.cls.cpu().numpy().astype(int)
                confs = boxes.conf.cpu().numpy()
                user_id = 1
                if user_id not in processed_ids:
                    processed_ids[user_id] = {}
                for idx, (cls_id, conf) in enumerate(zip(clss, confs)):
                    key = f"{cls_id}_{idx}"
                    if key not in processed_ids[user_id]:
                        class_name = model.names[cls_id]
                        processed_ids[user_id][key] = class_name
                        send_to_backend({
                            "UsuarioId": user_id,
                            "YoloLabel": class_name,
                            "Confidence": float(conf)
                        })
        except Exception as e:
            print("Error carrito:", e)

        with frame_lock:
            processed_frame = annotated

        time.sleep(0.005)

# ── MJPEG Stream ────────────────────────────────────────
def mjpeg_generator():
    while running:
        with frame_lock:
            pf = None if processed_frame is None else processed_frame.copy()
        if pf is None:
            time.sleep(0.01)
            continue
        _, buffer = cv2.imencode('.jpg', pf, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n'
        time.sleep(0.04)

@app.get("/video/{usuario_id}")
def video_stream(usuario_id: int):
    return StreamingResponse(mjpeg_generator(), media_type='multipart/x-mixed-replace; boundary=frame')

# ── Startup / Shutdown ──────────────────────────────────
@app.on_event("startup")
def on_startup():
    global cap, running
    cap = open_camera(0)
    running = True
    threading.Thread(target=capture_loop, daemon=True).start()
    threading.Thread(target=yolo_loop, daemon=True).start()

@app.on_event("shutdown")
def on_shutdown():
    global running
    running = False
    if cap:
        cap.release()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

    ##version estable