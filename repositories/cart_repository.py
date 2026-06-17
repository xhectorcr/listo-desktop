from core.http_client import HttpClient
from core.exceptions import AppException

class CartRepository:
    def __init__(self, http_client: HttpClient = HttpClient):
        self.http_client = http_client

    def agregar_item(self, usuario_id: str, label: str, confidence: float) -> bool:
        payload = {
            "UsuarioId": usuario_id,
            "YoloLabel": label,
            "Confidence": confidence
        }
        try:
            self.http_client.post("/carrito/agregar", json_data=payload, timeout=5)
            return True
        except AppException as e:
            print("Error al agregar a carrito:", e.message)
            return False

    def remover_item(self, usuario_id: str, label: str) -> bool:
        payload = {
            "UsuarioId": usuario_id,
            "YoloLabel": label,
            "Confidence": 1.0
        }
        try:
            self.http_client.post("/carrito/remover", json_data=payload, timeout=5)
            return True
        except AppException as e:
            print("Error al remover del carrito:", e.message)
            return False

    def finalizar_compra(self, usuario_id: str) -> bool:
        try:
            self.http_client.post("/carrito/finalizar", json_data=usuario_id, timeout=5)
            return True
        except AppException as e:
            print("Error al finalizar compra:", e.message)
            return False
