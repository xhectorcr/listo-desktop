from dataclasses import dataclass
from typing import Optional, Any, Dict

@dataclass
class AuthCredentials:
    correo: str
    password: str

@dataclass
class AuthResult:
    success: bool
    message: str = ""
    data: Optional[Dict[str, Any]] = None
