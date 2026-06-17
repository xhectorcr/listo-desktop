import requests

BASE_URL = "http://localhost:5115/api"
# BASE_URL = "https://listo-backend-1.onrender.com/api"

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
    def get_usuarios(page=1, size=50, search=""):
        url = f"{BASE_URL}/usuario/lista/activos?pageNumber={page}&pageSize={size}&pSearch={search}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except:
            return []

    @staticmethod
    def get_usuarios_inactivos(search=""):
        url = f"{BASE_URL}/usuario/lista/inactivos?pSearch={search}"
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

    @staticmethod
    def get_usuario_esperando():
        url = f"{BASE_URL}/usuario/esperando"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json().get("data")
            return None
        except:
            return None

    @staticmethod
    def get_usuarios_en_tienda():
        url = f"{BASE_URL}/usuario/en-tienda"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json().get("data", [])
            return []
        except:
            return []

    @staticmethod
    def asignar_track(usuario_id, track_id):
        url = f"{BASE_URL}/usuario/asignar-track"
        payload = {
            "idUsuario": usuario_id,
            "trackId": str(track_id)
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                return True
            return False
        except:
            return False

    @staticmethod
    def remover_carrito(usuario_id, label):
        url = f"{BASE_URL}/carrito/remover"
        payload = {
            "UsuarioId": usuario_id,
            "YoloLabel": label,
            "Confidence": 1.0
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as e:
            print("Error al remover del carrito:", e)

    @staticmethod
    def finalizar_compra(usuario_id):
        url = f"{BASE_URL}/carrito/finalizar"
        try:
            requests.post(url, json=usuario_id, timeout=5)
        except Exception as e:
            print("Error al finalizar compra:", e)

    @staticmethod
    def suspender_usuario(usuario_id):
        url = f"{BASE_URL}/usuario/suspender/{usuario_id}"
        try:
            response = requests.delete(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "message": "Error al suspender usuario"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def reactivar_usuario(usuario_id):
        url = f"{BASE_URL}/usuario/reactivar/{usuario_id}"
        try:
            response = requests.put(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"success": False, "message": "Error al reactivar usuario"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    @staticmethod
    def limpiar_tienda():
        url = f"{BASE_URL}/usuario/limpiar-tienda"
        try:
            response = requests.post(url, timeout=5)
            if response.status_code == 200:
                return True
            return False
        except Exception as e:
            print("Error al limpiar tienda:", e)
            return False
