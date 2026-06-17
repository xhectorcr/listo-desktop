from typing import List, Dict, Any
from core.http_client import HttpClient
from core.exceptions import AppException
from domain.models.product import Product, Category

class ProductRepository:
    def __init__(self, http_client: HttpClient = HttpClient):
        self.http_client = http_client

    def get_productos(self, page: int = 1, size: int = 50) -> List[Product]:
        try:
            params = {"pageNumber": page, "pageSize": size}
            response = self.http_client.get("/producto/lista/activos", params=params)
            data = response.get("data", [])
            return [Product.from_dict(p) for p in data]
        except AppException:
            return []

    def create_producto(self, producto: Product) -> bool:
        try:
            self.http_client.post("/producto", json_data=producto.to_dict())
            return True
        except AppException:
            return False

    def update_producto(self, producto: Product) -> bool:
        try:
            self.http_client.put("/producto", json_data=producto.to_dict())
            return True
        except AppException:
            return False

    def delete_producto(self, producto_id: int) -> bool:
        try:
            self.http_client.delete(f"/producto?id={producto_id}")
            return True
        except AppException:
            return False

class CategoryRepository:
    def __init__(self, http_client: HttpClient = HttpClient):
        self.http_client = http_client

    def get_categorias(self) -> List[Category]:
        try:
            # En la versión original de ApiService asume que /categoria/lista devuelve una lista directamente o un objeto con "data"
            response = self.http_client.get("/categoria/lista")
            data = response.get("data", response) if isinstance(response, dict) else response
            if isinstance(data, list):
                return [Category.from_dict(c) for c in data]
            return []
        except AppException:
            return []

    def create_categoria(self, nombre: str) -> bool:
        payload = {"idCategoria": 0, "nombre": nombre, "activo": True}
        try:
            self.http_client.post("/categoria", json_data=payload)
            return True
        except AppException:
            return False
