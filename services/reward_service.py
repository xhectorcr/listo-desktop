from typing import Tuple
from repositories.reward_repository import RewardRepository

class RewardService:
    def __init__(self, reward_repo: RewardRepository = None):
        self.repo = reward_repo or RewardRepository()

    def enviar_cupon_descuento(self, email: str) -> Tuple[bool, str]:
        email = email.strip()
        if not email or "@" not in email:
            return False, "Correo electrónico inválido."
        
        success = self.repo.enviar_cupon(email)
        return success, "Cupón enviado correctamente." if success else "Error al enviar el cupón."
