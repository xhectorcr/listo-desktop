import threading
from typing import Callable, List
from services.user_service import UserService
from domain.models.user import User

class UsersController:
    """Coordina las vistas de usuarios con los servicios."""
    def __init__(self, user_service: UserService = None):
        self.service = user_service or UserService()

    def load_users(self, search_query: str, page: int, on_success: Callable[[List[User], List[User]], None]):
        """Carga usuarios activos e inactivos de manera asíncrona."""
        def _fetch_task():
            activos, inactivos = self.service.obtener_resumen_usuarios(search_query, page=page, size=15)
            on_success(activos, inactivos)
        
        threading.Thread(target=_fetch_task, daemon=True).start()

    def suspender_usuario(self, usuario_id: str, on_complete: Callable[[bool, str], None]):
        """Suspende un usuario de forma asíncrona."""
        def _suspend_task():
            success, message = self.service.suspender(usuario_id)
            on_complete(success, message)
            
        threading.Thread(target=_suspend_task, daemon=True).start()

    def reactivar_usuario(self, usuario_id: str, on_complete: Callable[[bool, str], None]):
        """Reactiva un usuario de forma asíncrona."""
        def _reactivate_task():
            success, message = self.service.reactivar(usuario_id)
            on_complete(success, message)
            
        threading.Thread(target=_reactivate_task, daemon=True).start()
