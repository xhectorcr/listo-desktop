import threading
from typing import Callable, List
from services.user_service import UserService
from services.reward_service import RewardService
from domain.models.user import User

class RewardsController:
    def __init__(self, user_service: UserService = None, reward_service: RewardService = None):
        self.user_service = user_service or UserService()
        self.reward_service = reward_service or RewardService()

    def load_users(self, page: int, on_success: Callable[[List[User]], None]):
        def _fetch():
            activos, _ = self.user_service.obtener_resumen_usuarios(page=page, size=15)
            on_success(activos)
        threading.Thread(target=_fetch, daemon=True).start()

    def send_coupon(self, email: str, on_complete: Callable[[bool, str], None]):
        def _send():
            success, message = self.reward_service.enviar_cupon_descuento(email)
            on_complete(success, message)
        threading.Thread(target=_send, daemon=True).start()
