from core.http_client import HttpClient
from core.exceptions import AppException
from domain.models.auth import AuthCredentials, AuthResult

class AuthRepository:
    """
    Responsable de interactuar con la API para la autenticación.
    """
    def __init__(self, http_client: HttpClient = HttpClient):
        self.http_client = http_client

    def login(self, credentials: AuthCredentials) -> AuthResult:
        payload = {
            "correo": credentials.correo,
            "password": credentials.password
        }
        
        try:
            response_data = self.http_client.post("/usuario/login", json_data=payload)
            # El backend devuelve un json con datos
            return AuthResult(
                success=True,
                message="Login exitoso",
                data=response_data
            )
        except AppException as e:
            # Captura errores de red o errores de la API (ej. 401, 500)
            return AuthResult(
                success=False,
                message=e.message or "Credenciales inválidas"
            )
