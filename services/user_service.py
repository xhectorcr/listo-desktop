from typing import List, Tuple, Optional
from repositories.user_repository import UserRepository
from domain.models.user import User

class UserService:
    def __init__(self, user_repository: UserRepository = None):
        self.repository = user_repository or UserRepository()

    def obtener_resumen_usuarios(self, search: str = "") -> Tuple[List[User], List[User]]:
        """Devuelve una tupla con (usuarios_activos, usuarios_inactivos)"""
        activos = self.repository.get_usuarios_activos(page=1, size=100, search=search)
        inactivos = self.repository.get_usuarios_inactivos(search=search)
        return activos, inactivos

    def suspender(self, usuario_id: str) -> Tuple[bool, str]:
        if not usuario_id or usuario_id == 'N/A':
            return False, "ID de usuario inválido."
        success = self.repository.suspender_usuario(usuario_id)
        return success, "Usuario suspendido correctamente." if success else "Error al suspender."

    def reactivar(self, usuario_id: str) -> Tuple[bool, str]:
        if not usuario_id or usuario_id == 'N/A':
            return False, "ID de usuario inválido."
        success = self.repository.reactivar_usuario(usuario_id)
        return success, "Usuario reactivado correctamente." if success else "Error al reactivar."

    # Métodos usados posiblemente por otras vistas (ej. Dashboard / Tracking)
    def obtener_usuario_esperando(self) -> Optional[User]:
        return self.repository.get_usuario_esperando()

    def obtener_usuarios_en_tienda(self) -> List[User]:
        return self.repository.get_usuarios_en_tienda()

    def limpiar_estado_tienda(self) -> bool:
        return self.repository.limpiar_tienda()

    def asignar_track(self, usuario_id: str, track_id: str) -> bool:
        return self.repository.asignar_track(usuario_id, track_id)
