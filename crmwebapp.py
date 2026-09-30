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

# ==========================================
# 2. INICIALIZACIÓN DE FIREBASE FIRESTORE
# ==========================================
db = None

if not firebase_admin._apps:
    try:
        if "firebase_json" in st.secrets:
            creds_json = st.secrets["firebase_json"]
            creds_dict = json.loads(creds_json) if isinstance(creds_json, str) else dict(creds_json)
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
        else:
            st.error("⚠️ Error de configuración: No se encontró 'firebase_json' en st.secrets.")
            st.stop()
    except Exception as e:
        st.error(f"❌ Error al inicializar las credenciales de Firebase: {e}")
        st.stop()

try:
    db = firestore.client()
except Exception as e:
    st.error(f"❌ Error al conectar con Firestore: {e}")
    st.stop()

# ==========================================
# 3. FUNCIONES DE SEGURIDAD
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
        st.error(f"Error al cargar los clientes: {e}")

# --- SECCIÓN DE NOTAS CON KPIS ---
elif menu == "Notas y Seguimiento":
    st.title("Notas y Seguimiento del Cliente")
    cliente_id_input = st.text_input("Ingrese el ID del Contacto/Cliente para ver sus notas:")
    
    if cliente_id_input:
        try:
            notas_docs = db.collection("notas").where("id_contacto", "==", cliente_id_input.strip()).stream()
            notas = [n.to_dict() for n in notas_docs]
            
            if notas:
                df_notas = pd.DataFrame(notas)
                if "fecha" in df_notas.columns:
                    # Convertir a datetime para cálculos de KPI
                    df_notas["fecha"] = pd.to_datetime(df_notas["fecha"], errors='coerce', utc=True)
                    df_notas = df_notas.sort_values(by="fecha", ascending=False)
                    
                    st.markdown("---")
                    st.markdown("### 📊 Indicadores Clave (KPIs)")
                    
                    col1, col2, col3 = st.columns(3)
                    total_notas = len(df_notas)
                    
                    ultima_fecha = df_notas["fecha"].iloc[0]
                    ultima_interaccion = ultima_fecha.strftime("%d %b %Y") if pd.notnull(ultima_fecha) else "N/A"
                    
                    hace_30_dias = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
                    notas_recientes = df_notas[df_notas["fecha"] >= hace_30_dias].shape[0]
                    
                    with col1:
                        st.metric(label="Total de Notas", value=total_notas)
                    with col2:
                        st.metric(label="Última Interacción", value=ultima_interaccion)
                    with col3:
                        st.metric(label="Interacciones (Últimos 30 días)", value=notas_recientes, delta=notas_recientes)
                        
                    st.markdown("---")
                    st.markdown("#### 📈 Frecuencia de Contacto")
                    
                    df_grafica = df_notas.copy()
                    df_grafica["Dia"] = df_grafica["fecha"].dt.date
                    frecuencia = df_grafica.groupby("Dia").size().reset_index(name='Cantidad de Notas')
                    frecuencia = frecuencia.set_index("Dia")
                    st.bar_chart(frecuencia, color="#1f77b4")
                    
                    st.markdown("#### 📝 Detalle Histórico")
                    # Formatear la fecha para que se vea legible en la tabla final
                    df_notas["fecha"] = df_notas["fecha"].dt.strftime("%Y-%m-%d %H:%M")
                    
                st.dataframe(df_notas, use_container_width=True)
            else:
                st.info("No se encontraron notas para este ID de contacto.")
                
        except Exception as e:
            st.error(f"Error al cargar las notas: {e}")
