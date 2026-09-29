import base64
import hashlib
import json
import pandas as pd
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==========================================
st.set_page_config(
    page_title="Bayamon Truck Parts - CRM",
    page_icon="🚛",
    layout="wide"
)

# ==========================================
# 2. INICIALIZACIÓN DE FIREBASE FIRESTORE
# ==========================================
if not firebase_admin._apps:
    try:
        # Lee el JSON de credenciales almacenado en los secretos de Streamlit Cloud
        creds_dict = json.loads(st.secrets["firebase_json"])
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")
        st.stop()

db = firestore.client()

# ==========================================
# 3. FUNCIONES DE UTILIDAD Y SEGURIDAD
# ==========================================
def hash_password(password):
    """Genera un hash SHA-256 para las contraseñas."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def autenticar_usuario(username, password):
    """Verifica las credenciales del usuario en Firestore."""
    try:
        users_ref = db.collection("usuarios")
        query = (
            users_ref.where("username", "==", username.strip().lower())
            .where("password_hash", "==", hash_password(password))
            .limit(1)
            .get()
        )
        
        for doc in query:
            return doc.to_dict()
        return None
    except Exception as e:
        st.error(f"Error en la autenticación: {e}")
        return None

# ==========================================
# 4. SISTEMA DE LOGIN EN STREAMLIT
# ==========================================
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.title("🚛 Bayamon Truck Parts - CRM Login")
    
    with st.form("login_form"):
        usuario_input = st.text_input("Usuario")
        password_input = st.text_input("Contraseña", type="password")
        submit_btn = st.form_submit_button("Iniciar Sesión")
        
        if submit_btn:
            user_data = autenticar_usuario(usuario_input, password_input)
            if user_data:
                st.session_state["user"] = user_data
                st.success("¡Bienvenido!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    st.stop()

# ==========================================
# 5. APLICACIÓN PRINCIPAL (POST-LOGIN)
# ==========================================
usuario_actual = st.session_state["user"]

st.sidebar.title(f"Hola, {usuario_actual.get('nombre', 'Usuario')}")
menu = st.sidebar.radio("Navegación", ["Clientes", "Notas y Seguimiento", "Cerrar Sesión"])

if menu == "Cerrar Sesión":
    st.session_state["user"] = None
    st.rerun()

# --- SECCIÓN DE CLIENTES ---
if menu == "Clientes":
    st.title("Gestión de Clientes - Bayamon Truck Parts")
    
    # Ejemplo de lectura de clientes desde Firestore
    try:
        clientes_ref = db.collection("clientes").stream()
        filas = []
        for doc in clientes_ref:
            c = doc.to_dict()
            c["ID"] = doc.id
            filas.append(c)
        
        if filas:
            df = pd.DataFrame(filas)
            # Asegurar columnas deseadas si existen
            columnas_mostrar = [col for col in ["ID", "Empresa", "Sector", "Nombre", "Apellido", "Cargo", "Email", "Teléfono"] if col in df.columns]
            st.dataframe(df[columnas_mostrar], use_container_width=True)
        else:
            st.info("No hay clientes registrados todavía.")
            
    except Exception as e:
        st.error(f"Error al cargar los clientes: {e}")

# --- SECCIÓN DE NOTAS Y SEGUIMIENTO ---
elif menu == "Notas y Seguimiento":
    st.title("Notas de Seguimiento")
    
    cliente_id_input = st.text_input("Ingrese el ID del Cliente para ver sus notas:")
    
    if cliente_id_input:
        try:
            # CONSULTA SEGURA: Filtramos por cliente SIN usar .order_by() en Firestore
            # para evitar por completo el error FailedPrecondition (índice compuesto).
            notas_docs = db.collection("notas").where("id_cliente", "==", cliente_id_input.strip()).stream()
            notas = [n.to_dict() for n in notas_docs]
            
            if notas:
                df_notas = pd.DataFrame(notas)
                
                # ORDENAMIENTO SEGURO EN PANDAS: Ordenamos por fecha localmente
                if "fecha" in df_notas.columns:
                    df_notas = df_notas.sort_values(by="fecha", ascending=False)
                
                st.dataframe(df_notas, use_container_width=True)
            else:
                st.info("No se encontraron notas para este cliente.")
                
        except Exception as e:
            st.error(f"Error al cargar las notas: {e}")
