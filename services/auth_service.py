from repositories.auth_repository import AuthRepository
from domain.models.auth import AuthCredentials, AuthResult

class AuthService:
    """
    Responsable de la lógica de negocio y validaciones para la autenticación.
    """
    def __init__(self, auth_repository: AuthRepository = None):
        self.repository = auth_repository or AuthRepository()

    def authenticate(self, correo: str, password: str) -> AuthResult:
        correo_limpio = correo.strip()
        
        if not correo_limpio or not password:
            return AuthResult(success=False, message="Correo y contraseña son requeridos.")
        
        # Validaciones de negocio adicionales (ej. formato de correo) podrían ir aquí
        
        credentials = AuthCredentials(correo=correo_limpio, password=password)
        return self.repository.login(credentials)
