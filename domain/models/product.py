from dataclasses import dataclass
from typing import Optional

@dataclass
class Category:
    id_categoria: int
    nombre: str
    activo: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> 'Category':
        return cls(
            id_categoria=int(data.get('idCategoria', data.get('id', 0))),
            nombre=data.get('nombre', 'Sin nombre'),
            activo=data.get('activo', True)
        )

@dataclass
class Product:
    id_producto: int
    nombre: str
    descripcion: str
    precio: float
    stock: int
    id_categoria: int
    nombre_categoria: str = ""
    yolo_label: str = ""
    activo: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        return cls(
            id_producto=int(data.get('idProducto', data.get('id', 0))),
            nombre=data.get('nombre', 'Sin nombre'),
            descripcion=data.get('descripcion', ''),
            precio=float(data.get('precio', 0.0) or 0.0),
            stock=int(data.get('stock', 0) or 0),
            id_categoria=int(data.get('idCategoria', 0)),
            nombre_categoria=data.get('categoriaNombre', data.get('nombreCategoria', '')),
            yolo_label=data.get('yoloLabel', ''),
            activo=data.get('activo', True)
        )
    
    def to_dict(self) -> dict:
        return {
            "idProducto": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": self.precio,
            "stock": self.stock,
            "idCategoria": self.id_categoria,
            "yoloLabel": self.yolo_label,
            "activo": self.activo
        }
