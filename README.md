# 📦 YOLO + FastAPI Streaming API

## 📖 Descripción
Este proyecto implementa una API en **FastAPI** que utiliza un modelo **YOLO (Ultralytics)** para detectar objetos en tiempo real desde la cámara.  

El sistema:
- Captura video en vivo desde la webcam
- Procesa los frames con YOLO
- Dibuja las detecciones sobre la imagen
- Envía detecciones nuevas a un backend externo (carrito)
- Expone un stream MJPEG accesible vía HTTP

---

## ⚙️ Requisitos

### 🧩 Dependencias
Instalar con:

```bash
pip install fastapi uvicorn opencv-python ultralytics httpx
