import base64
import hashlib
import json
import pandas as pd
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Bayamon Truck Parts - CRM",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 Bayamon Truck Parts - Panel de Diagnóstico")

# ==========================================
# 2. CONEXIÓN SEGURA A FIREBASE FIRESTORE
# ==========================================
db = None
try:
    if not firebase_admin._apps:
        if "firebase_json" in st.secrets:
            creds_dict = json.loads(st.secrets["firebase_json"])
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
        else:
            st.error("⚠️ Falta configurar el secreto 'firebase_json' en Streamlit Cloud.")
            st.stop()
    
    db = firestore.client()
    st.success("✅ Conexión con Firebase establecida correctamente.")
except Exception as e:
    st.error(f"❌ Error crítico al conectar con Firebase: {e}")
    st.stop()

# ==========================================
# 3. FUNCIONES DE AUTENTICACIÓN
# ==========================================
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def autenticar_usuario(username, password):
    try:
        users_ref = db.collection("usuarios")
        query = users_ref.where("username", "==", username.strip().lower()).limit(1).get()
        password_hash_input = hash_password(password)
        
        for doc in query:
            user_data = doc.to_dict()
            if user_data.get("password_hash") == password_hash_input:
                return user_data
        return None
    except Exception as e:
        st.error(f"Error en la autenticación: {e}")
        return None

# ==========================================
# 4. SISTEMA DE LOGIN
# ==========================================
if "user" not in st.session_state:
    st.session_state["user"] = None

if st.session_state["user"] is None:
    st.subheader("Iniciar Sesión")
    with st.form("login_form"):
        usuario_input = st.text_input("Usuario")
        password_input = st.text_input("Contraseña", type="password")
        submit_btn = st.form_submit_button("Entrar")
        
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
# 5. APLICACIÓN PRINCIPAL
# ==========================================
usuario_actual = st.session_state["user"]

st.sidebar.title(f"Hola, {usuario_actual.get('nombre', 'Usuario')}")
menu = st.sidebar.radio("Navegación", ["Clientes", "Notas y Seguimiento", "Cerrar Sesión"])

if menu == "Cerrar Sesión":
    st.session_state["user"] = None
    st.rerun()

# --- SECCIÓN DE CLIENTES ---
if menu == "Clientes":
    st.header("Gestión de Clientes")
    try:
        clientes_ref = db.collection("clientes").stream()
        filas = []
        for doc in clientes_ref:
            c = doc.to_dict()
            c["ID"] = doc.id
            filas.append(c)
        
        if filas:
            df = pd.DataFrame(filas)
            columnas_mostrar = [col for col in ["ID", "Empresa", "Sector", "Nombre", "Apellido", "Cargo", "Email", "Teléfono"] if col in df.columns]
            st.dataframe(df[columnas_mostrar], use_container_width=True)
        else:
            st.info("No hay clientes registrados todavía.")
    except Exception as e:
        st.error(f"Error al cargar clientes: {e}")

# --- SECCIÓN DE NOTAS Y SEGUIMIENTO ---
elif menu == "Notas y Seguimiento":
    st.header("Notas de Seguimiento")
    cliente_id_input = st.text_input("Ingrese el ID del Contacto/Cliente para ver sus notas:")
    
    if cliente_id_input:
        try:
            notas_docs = db.collection("notas").where("id_contacto", "==", cliente_id_input.strip()).stream()
            notas = [n.to_dict() for n in notas_docs]
            
            if notas:
                df_notas = pd.DataFrame(notas)
                if "fecha" in df_notas.columns:
                    df_notas = df_notas.sort_values(by="fecha", ascending=False)
                st.dataframe(df_notas, use_container_width=True)
            else:
                st.info("No se encontraron notas para este contacto.")
        except Exception as e:
            st.error(f"Error al cargar notas: {e}")
