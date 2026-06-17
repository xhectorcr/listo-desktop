import threading
from typing import Callable, List
from services.product_service import ProductService, CategoryService
from domain.models.product import Product, Category

class ProductsController:
    """Coordina las vistas de productos y categorías con los servicios."""
    def __init__(self, product_service: ProductService = None, category_service: CategoryService = None):
        self.product_service = product_service or ProductService()
        self.category_service = category_service or CategoryService()

    def load_data(self, page: int, on_success: Callable[[List[Product], List[Category]], None]):
        """Carga productos y categorías de forma asíncrona usando paginación."""
        def _fetch():
            products = self.product_service.get_all_products(page=page, size=15)
            categories = self.category_service.get_all_categories()
            on_success(products, categories)
        threading.Thread(target=_fetch, daemon=True).start()

    def save_product(self, product: Product, on_complete: Callable[[bool, str], None]):
        def _save():
            success, msg = self.product_service.save_product(product)
            on_complete(success, msg)
        threading.Thread(target=_save, daemon=True).start()

    def delete_product(self, product_id: int, on_complete: Callable[[bool, str], None]):
        def _delete():
            success, msg = self.product_service.delete_product(product_id)
            on_complete(success, msg)
        threading.Thread(target=_delete, daemon=True).start()

    def create_category(self, name: str, on_complete: Callable[[bool, str], None]):
        def _create():
            success, msg = self.category_service.create_category(name)
            on_complete(success, msg)
        threading.Thread(target=_create, daemon=True).start()
