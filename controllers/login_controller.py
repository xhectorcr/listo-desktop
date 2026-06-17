import threading
from typing import Callable
from services.auth_service import AuthService

class LoginController:
    """
    Coordina la vista de login con el servicio de autenticación.
    Maneja la ejecución asíncrona (hilos) para no bloquear la UI.
    """
    def __init__(self, auth_service: AuthService = None):
        self.service = auth_service or AuthService()

    def handle_login(self, correo: str, password: str, on_success: Callable[[], None], on_error: Callable[[str], None]):
        """
        Ejecuta el login en un hilo separado e invoca los callbacks según el resultado.
        """
        def _login_task():
            result = self.service.authenticate(correo, password)
            if result.success:
                on_success()
            else:
                on_error(result.message)

        # Inicia el hilo en modo daemon para que no bloquee el cierre de la app
        threading.Thread(target=_login_task, daemon=True).start()
