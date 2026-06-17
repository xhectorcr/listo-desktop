from typing import List, Optional
from core.http_client import HttpClient
from core.exceptions import AppException
from domain.models.user import User

class UserRepository:
    def __init__(self, http_client: HttpClient = HttpClient):
        self.http_client = http_client

    def get_usuarios_activos(self, page: int = 1, size: int = 50, search: str = "") -> List[User]:
        try:
            params = {"pageNumber": page, "pageSize": size, "pSearch": search}
            response = self.http_client.get("/usuario/lista/activos", params=params)
            data = response.get("data", [])
            return [User.from_dict(u, default_activo=True) for u in data]
        except AppException:
            return []

    def get_usuarios_inactivos(self, page: int = 1, size: int = 50, search: str = "") -> List[User]:
        try:
            params = {"pageNumber": page, "pageSize": size, "pSearch": search}
            response = self.http_client.get("/usuario/lista/inactivos", params=params)
            data = response.get("data", [])
            return [User.from_dict(u, default_activo=False) for u in data]
        except AppException:
            return []

    def suspender_usuario(self, usuario_id: str) -> bool:
        try:
            self.http_client.delete(f"/usuario/suspender/{usuario_id}")
            return True
        except AppException:
            return False

    def reactivar_usuario(self, usuario_id: str) -> bool:
        try:
            self.http_client.put(f"/usuario/reactivar/{usuario_id}")
            return True
        except AppException:
            return False

    def get_usuario_esperando(self) -> Optional[User]:
        try:
            response = self.http_client.get("/usuario/esperando")
            data = response.get("data")
            return User.from_dict(data) if data else None
        except AppException:
            return None

    def get_usuarios_en_tienda(self) -> List[User]:
        try:
            response = self.http_client.get("/usuario/en-tienda")
            data = response.get("data", [])
            return [User.from_dict(u) for u in data]
        except AppException:
            return []

    def asignar_track(self, usuario_id: str, track_id: str) -> bool:
        payload = {"idUsuario": usuario_id, "trackId": str(track_id)}
        try:
            self.http_client.post("/usuario/asignar-track", json_data=payload)
            return True
        except AppException:
            return False

    def limpiar_tienda(self) -> bool:
        try:
            self.http_client.post("/usuario/limpiar-tienda")
            return True
        except AppException:
            return False
