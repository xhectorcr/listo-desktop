from typing import List, Tuple
from repositories.product_repository import ProductRepository, CategoryRepository
from domain.models.product import Product, Category

class ProductService:
    def __init__(self, product_repo: ProductRepository = None, category_repo: CategoryRepository = None):
        self.product_repo = product_repo or ProductRepository()
        self.category_repo = category_repo or CategoryRepository()

    def get_all_products(self, page: int = 1, size: int = 15) -> List[Product]:
        return self.product_repo.get_productos(page=page, size=size)

    def save_product(self, product: Product) -> Tuple[bool, str]:
        if not product.nombre or product.precio <= 0 or product.id_categoria <= 0:
            return False, "Nombre, Precio válido y Categoría son obligatorios."
            
        if product.id_producto == 0:
            success = self.product_repo.create_producto(product)
            return success, "Producto creado exitosamente." if success else "Error al crear producto."
        else:
            success = self.product_repo.update_producto(product)
            return success, "Producto actualizado exitosamente." if success else "Error al actualizar producto."

    def delete_product(self, product_id: int) -> Tuple[bool, str]:
        if product_id <= 0:
            return False, "ID de producto inválido."
        success = self.product_repo.delete_producto(product_id)
        return success, "Producto eliminado correctamente." if success else "Error al eliminar producto."

class CategoryService:
    _categories_cache: List[Category] = []

    def __init__(self, category_repo: CategoryRepository = None):
        self.repo = category_repo or CategoryRepository()

    def get_all_categories(self, force_refresh: bool = False) -> List[Category]:
        if not CategoryService._categories_cache or force_refresh:
            CategoryService._categories_cache = self.repo.get_categorias()
        return CategoryService._categories_cache

    def create_category(self, name: str) -> Tuple[bool, str]:
        name = name.strip()
        if not name:
            return False, "El nombre de la categoría no puede estar vacío."
        success = self.repo.create_categoria(name)
        if success:
            CategoryService._categories_cache.clear()
        return success, "Categoría creada correctamente." if success else "Error al crear categoría."
