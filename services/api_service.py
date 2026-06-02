import requests

BASE_URL = "https://listo-backend-1.onrender.com/api"
# O usa "http://localhost:XXXX/api" si tu backend local corre ahí

class ApiService:
    @staticmethod
    def login(correo, password):
        url = f"{BASE_URL}/usuario/login"
        payload = {"correo": correo, "password": password}
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "message": "Credenciales inválidas"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_usuarios(page=1, size=50):
        url = f"{BASE_URL}/usuario/lista/activos?pageNumber={page}&pageSize={size}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except:
            return []

    @staticmethod
    def get_productos(page=1, size=50):
        url = f"{BASE_URL}/producto/lista/activos?pageNumber={page}&pageSize={size}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except:
            return []

    @staticmethod
    def get_categorias():
        url = f"{BASE_URL}/categoria/lista"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return []
        except:
            return []

    @staticmethod
    def create_categoria(nombre):
        url = f"{BASE_URL}/categoria"
        payload = {"idCategoria": 0, "nombre": nombre, "activo": True}
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "message": "Error al crear categoría"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def create_producto(producto_data):
        url = f"{BASE_URL}/producto"
        try:
            response = requests.post(url, json=producto_data, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "message": "Error al crear producto"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def update_producto(producto_data):
        url = f"{BASE_URL}/producto"
        try:
            response = requests.put(url, json=producto_data, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "message": "Error al actualizar producto"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def delete_producto(producto_id):
        url = f"{BASE_URL}/producto?id={producto_id}"
        try:
            response = requests.delete(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "message": "Error al eliminar producto"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def agregar_carrito(usuario_id, label, confidence):
        url = f"{BASE_URL}/carrito/agregar"
        payload = {
            "UsuarioId": usuario_id,
            "YoloLabel": label,
            "Confidence": confidence
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print("Error al agregar a carrito:", e)

    @staticmethod
    def enviar_cupon(email):
        url = f"{BASE_URL}/Descuento/enviar-cupon"
        # El backend espera un simple string en el body.
        # requests lo convierte a JSON string si le pasamos json=email
        try:
            response = requests.post(url, json=email, timeout=10)
            if response.status_code == 200:
                return {"success": True, "message": "Cupón enviado"}
            return {"success": False, "message": "Error al enviar cupón"}
        except Exception as e:
            return {"success": False, "message": str(e)}
