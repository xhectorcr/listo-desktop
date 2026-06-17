from repositories.cart_repository import CartRepository

class CartService:
    """Lógica de negocio asociada al manejo del carrito en tiempo real."""
    def __init__(self, cart_repo: CartRepository = None):
        self.repo = cart_repo or CartRepository()

    def procesar_deteccion_agregar(self, usuario_id: str, label: str, confidence: float) -> bool:
        if not usuario_id or not label or confidence < 0.5:
            return False
        return self.repo.agregar_item(usuario_id, label, confidence)

    def procesar_deteccion_remover(self, usuario_id: str, label: str) -> bool:
        if not usuario_id or not label:
            return False
        return self.repo.remover_item(usuario_id, label)

    def checkout_usuario(self, usuario_id: str) -> bool:
        if not usuario_id:
            return False
        return self.repo.finalizar_compra(usuario_id)
