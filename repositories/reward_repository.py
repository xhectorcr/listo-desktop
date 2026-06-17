from core.http_client import HttpClient
from core.exceptions import AppException

class RewardRepository:
    def __init__(self, http_client: HttpClient = HttpClient):
        self.http_client = http_client

    def enviar_cupon(self, email: str) -> bool:
        try:
            self.http_client.post("/Descuento/enviar-cupon", json_data=email, timeout=10)
            return True
        except AppException:
            return False
