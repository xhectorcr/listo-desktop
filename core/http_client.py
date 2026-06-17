import requests
from typing import Dict, Any, Optional
from core.config import Config
from core.exceptions import NetworkException, APIException

class HttpClient:
    """
    Cliente HTTP centralizado para evitar repetición de código y
    manejar excepciones y timeouts en un solo lugar.
    """
    
    @staticmethod
    def _handle_response(response: requests.Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            data = response.text

        if 200 <= response.status_code < 300:
            return data
        
        # Extraer mensaje de error del backend si existe
        error_msg = "Error desconocido"
        if isinstance(data, dict):
            error_msg = data.get("message", f"Error de API: {response.status_code}")
        elif isinstance(data, str):
            error_msg = data

        raise APIException(error_msg, status_code=response.status_code)

    @staticmethod
    def get(endpoint: str, params: Optional[Dict[str, Any]] = None, timeout: int = Config.HTTP_TIMEOUT_SECONDS) -> Any:
        url = f"{Config.API_BASE_URL}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=timeout)
            return HttpClient._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Error de conexión: {str(e)}")

    @staticmethod
    def post(endpoint: str, json_data: Any = None, timeout: int = Config.HTTP_TIMEOUT_SECONDS) -> Any:
        url = f"{Config.API_BASE_URL}{endpoint}"
        try:
            response = requests.post(url, json=json_data, timeout=timeout)
            return HttpClient._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Error de conexión: {str(e)}")

    @staticmethod
    def put(endpoint: str, json_data: Any = None, timeout: int = Config.HTTP_TIMEOUT_SECONDS) -> Any:
        url = f"{Config.API_BASE_URL}{endpoint}"
        try:
            response = requests.put(url, json=json_data, timeout=timeout)
            return HttpClient._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Error de conexión: {str(e)}")

    @staticmethod
    def delete(endpoint: str, timeout: int = Config.HTTP_TIMEOUT_SECONDS) -> Any:
        url = f"{Config.API_BASE_URL}{endpoint}"
        try:
            response = requests.delete(url, timeout=timeout)
            return HttpClient._handle_response(response)
        except requests.exceptions.RequestException as e:
            raise NetworkException(f"Error de conexión: {str(e)}")
