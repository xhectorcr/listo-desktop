import threading
from typing import List, Callable
from services.user_service import UserService
from services.cart_service import CartService
from domain.models.user import User

class CameraController:
    """Coordina las interacciones en tiempo real de la cámara con los servicios backend."""
    def __init__(self, user_service: UserService = None, cart_service: CartService = None):
        self.user_service = user_service or UserService()
        self.cart_service = cart_service or CartService()

    def limpiar_tienda(self, on_complete: Callable[[bool], None]):
        def _task():
            success = self.user_service.limpiar_estado_tienda()
            on_complete(success)
        threading.Thread(target=_task, daemon=True).start()

    def get_usuarios_en_tienda(self) -> List[User]:
        # Lo usamos de forma sincrona porque corre dentro de un hilo background en la vista
        return self.user_service.obtener_usuarios_en_tienda()

    def asignar_track(self, usuario_id: str, track_id: str) -> bool:
        return self.user_service.asignar_track(usuario_id, track_id)

    def agregar_carrito(self, usuario_id: str, label: str, confidence: float):
        def _task():
            self.cart_service.procesar_deteccion_agregar(usuario_id, label, confidence)
        threading.Thread(target=_task, daemon=True).start()

    def remover_carrito(self, usuario_id: str, label: str):
        def _task():
            self.cart_service.procesar_deteccion_remover(usuario_id, label)
        threading.Thread(target=_task, daemon=True).start()

    def finalizar_compra(self, usuario_id: str):
        def _task():
            self.cart_service.checkout_usuario(usuario_id)
        threading.Thread(target=_task, daemon=True).start()
