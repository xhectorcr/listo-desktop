from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id_usuario: str
    nombre: str
    correo: str
    saldo: float = 0.0
    estrellas: int = 0
    activo: bool = True

    @classmethod
    def from_dict(cls, data: dict, default_activo: bool = True) -> 'User':
        return cls(
            id_usuario=str(data.get('idUsuario', data.get('id', 'N/A'))),
            nombre=data.get('nombre', 'Sin nombre'),
            correo=data.get('correo', 'Sin correo'),
            saldo=float(data.get('saldo', 0) or 0),
            estrellas=int(data.get('estrellas', 0) or 0),
            activo=data.get('estado', data.get('activo', default_activo))
        )
