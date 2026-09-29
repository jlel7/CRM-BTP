import streamlit as st
import pandas as pd
import os
import base64
import hashlib
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# 1. Configuración de la página web
st.set_page_config(
    page_title="BAYAMON TRUCK PARTS | CRM", 
    page_icon="🚛",
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. INICIALIZACIÓN DE FIREBASE FIRESTORE
if not firebase_admin._apps:
    # Opción A: Buscar el archivo JSON local en la misma carpeta
    cred_path = os.path.join(os.path.dirname(__file__), "firebase_credentials.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Opción B: Si usas los Secrets de Streamlit Cloud
        try:
            import json
            secrets_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(secrets_dict)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            st.error(f"⚠️ No se encontró la configuración de Firebase. Asegúrate de colocar 'firebase_credentials.json' o configurarlo en st.secrets. Error: {e}")
            st.stop()

db = firestore.client()

# 3. GENERADOR DEL CAMIÓN SVG EN FORMATO BASE64
svg_truck_raw = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 85" width="170" height="72">
  <defs>
    <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" />
      <stop offset="50%" stop-color="#2563eb" />
      <stop offset="100%" stop-color="#1d4ed8" />
    </linearGradient>
    <linearGradient id="metalGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#f1f5f9" />
      <stop offset="100%" stop-color="#94a3b8" />
    </linearGradient>
  </defs>
  <rect x="5" y="14" width="105" height="46" rx="3" fill="#334155" stroke="#64748b" stroke-width="2" />
  <line x1="12" y1="22" x2="102" y2="22" stroke="#475569" stroke-width="1.5" />
  <line x1="12" y1="30" x2="102" y2="30" stroke="#475569" stroke-width="1.5" />
  <line x1="12" y1="38" x2="102" y2="38" stroke="#475569" stroke-width="1.5" />
  <line x1="12" y1="46" x2="102" y2="46" stroke="#475569" stroke-width="1.5" />
  <rect x="116" y="2" width="4" height="26" rx="2" fill="url(#metalGrad)" />
  <path d="M112 24 L132 12 L162 12 L185 34 L190 46 L190 62 L112 62 Z" fill="url(#bodyGrad)" stroke="#1e3a8a" stroke-width="1.5" />
  <path d="M158 16 L180 35 L160 35 L158 16 Z" fill="#ffffff" opacity="0.9" />
  <path d="M136 16 L154 16 L154 35 L136 35 Z" fill="#cbd5e1" opacity="0.85" />
  <rect x="186" y="42" width="6" height="18" rx="2" fill="url(#metalGrad)" />
  <rect x="183" y="58" width="11" height="6" rx="2" fill="#e2e8f0" />
  <circle cx="189" cy="50" r="3" fill="#fbbf24" />
  <rect x="120" y="50" width="22" height="10" rx="4" fill="url(#metalGrad)" />
  <circle cx="28" cy="64" r="10" fill="#0f172a" stroke="#94a3b8" stroke-width="2.5" />
  <circle cx="28" cy="64" r="4.5" fill="#f8fafc" />
  <circle cx="52" cy="64" r="10" fill="#0f172a" stroke="#94a3b8" stroke-width="2.5" />
  <circle cx="52" cy="64" r="4.5" fill="#f8fafc" />
  <circle cx="132" cy="64" r="10" fill="#0f172a" stroke="#94a3b8" stroke-width="2.5" />
  <circle cx="132" cy="64" r="4.5" fill="#f8fafc" />
  <circle cx="174" cy="64" r="10" fill="#0f172a" stroke="#94a3b8" stroke-width="2.5" />
  <circle cx="174" cy="64" r="4.5" fill="#f8fafc" />
</svg>"""

truck_base64 = base64.b64encode(svg_truck_raw.encode("utf-8")).decode("utf-8")

# 4. CSS GLOBAL: ESTILO MODERNO, ERGONÓMICO Y DE ALTO CONTRASTE
st.markdown("""
    <style>
        .stApp { background-color: #f8fafc !important; }
        .hero-banner {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #1e3a8a 100%);
            border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem;
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 4px 15px rgba(15, 23, 42, 0.2); border: 1px solid #334155;
        }
        .hero-banner h1, .hero-banner .brand-title {
            font-size: 2.2rem !important; font-weight: 900 !important; color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important; margin: 0 !important; line-height: 1.2 !important;
            text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5); white-space: nowrap;
        }
        .hero-banner p, .hero-banner .brand-subtitle {
            color: #93c5fd !important; -webkit-text-fill-color: #93c5fd !important;
            font-size: 1rem !important; font-weight: 500 !important; margin-top: 6px !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #f1f5f9 !important; border-right: 2px solid #cbd5e1 !important;
        }
        .user-badge {
            background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px;
            padding: 0.75rem 1rem; margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between;
        }
        input, select, textarea {
            background-color: #ffffff !important; color: #0f172a !important;
            border: 1.5px solid #64748b !important; border-radius: 6px !important; font-size: 0.95rem !important; font-weight: 600 !important;
        }
        label, .stTextInput label, .stSelectbox label, .stTextArea label {
            color: #0f172a !important; font-weight: 700 !important; font-size: 0.92rem !important;
        }
        button, .stButton > button, .stFormSubmitButton > button {
            background-color: #2563eb !important; color: #ffffff !important; border: 1px solid #1d4ed8 !important;
            border-radius: 8px !important; font-size: 1rem !important; font-weight: 700 !important;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3) !important; padding: 0.5rem 1rem !important;
        }
        button p, .stButton > button p, button span { color: #ffffff !important; font-weight: 700 !important; }
        button:hover, .stButton > button:hover { background-color: #1d4ed8 !important; box-shadow: 0 6px 14px rgba(29, 78, 216, 0.4) !important; }
        [data-testid="stFileUploaderDropzone"] { background-color: #ffffff !important; border: 2px dashed #64748b !important; border-radius: 8px !important; }
        .kpi-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
        .kpi-card {
            background-color: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 10px; padding: 1rem 1.2rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04); border-left: 5px solid #2563eb; display: flex; align-items: center; justify-content: space-between;
        }
        .kpi-label { font-size: 0.82rem; text-transform: uppercase; font-weight: 800; color: #475569 !important; }
        .kpi-value { font-size: 1.8rem; font-weight: 900; color: #0f172a !important; margin-top: 2px; }
        .contact-card { background: #ffffff; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 1.2rem; margin-bottom: 1.2rem; }
        .note-bubble {
            background-color: #ffffff; border: 1px solid #cbd5e1; border-left: 4px solid #2563eb;
            border-radius: 6px; padding: 0.9rem 1rem; margin-bottom: 0.85rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        }
        .note-meta { display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 700; margin-bottom: 6px; }
        .note-body { font-size: 0.95rem; color: #0f172a !important; font-weight: 500; line-height: 1.4; }
    </style>
""", unsafe_allow_html=True)

# 5. FUNCIONES DE SEGURIDAD Y DATOS (FIRESTORE)
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def inicializar_admin_default():
    users_ref = db.collection("usuarios")
    admin_query = users_ref.where("username", "==", "admin").limit(1).get()
    if not list(admin_query):
        users_ref.add({
            "username": "admin",
            "nombre_completo": "Administrador Principal",
            "password_hash": hash_password("admin123"),
            "rol": "Admin",
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

inicializar_admin_default()

# 6. CONTROL DE SESIÓN (LOGIN)
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.session_state["nombre_completo"] = None
    st.session_state["rol"] = None

def autenticar_usuario(username, password):
    users_ref = db.collection("usuarios")
    query = users_ref.where("username", "==", username.strip().lower()).where("password_hash", "==", hash_password(password)).limit(1).get()
    docs = list(query)
    if docs:
        user_data = docs[0].to_dict()
        user_data["id"] = docs[0].id
        return user_data
    return None

# ==========================================
# PANTALLA DE INICIO DE SESIÓN
# ==========================================
if not st.session_state["autenticado"]:
    col_izq, col_centro, col_der = st.columns([1, 1.4, 1])
    with col_centro:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <img src="data:image/svg+xml;base64,{truck_base64}" alt="Camión" style="max-width: 160px; margin: 0 auto; display: block;" />
                <h2 style="color: #0f172a; margin: 15px 0 5px 0; font-weight: 900;">BAYAMON TRUCK PARTS</h2>
                <p style="color: #64748b; font-size: 0.95rem;">Acceso al CRM en la Nube (Firebase)</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("form_login"):
            usuario_input = st.text_input("Usuario", placeholder="Ingresa tu usuario...")
            password_input = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña...")
            btn_entrar = st.form_submit_button("Iniciar Sesión", use_container_width=True)

            if btn_entrar:
                datos_user = autenticar_usuario(usuario_input, password_input)
                if datos_user:
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = datos_user["username"]
                    st.session_state["nombre_completo"] = datos_user["nombre_completo"]
                    st.session_state["rol"] = datos_user["rol"]
                    st.success("Acceso concedido.")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
        
        st.info("💡 **Primer acceso:** Usuario: `admin` | Contraseña: `admin123`")
    st.stop()

# ==========================================
# APLICACIÓN PRINCIPAL
# ==========================================
def obtener_metricas():
    total_empresas = len(list(db.collection("clientes").stream()))
    total_contactos = len(list(db.collection("contactos").stream()))
    total_notas = len(list(db.collection("notas").stream()))
    return total_empresas, total_contactos, total_notas

total_empresas, total_contactos, total_notas = obtener_metricas()

st.markdown(f"""
<div class="hero-banner">
    <div>
        <h1 class="brand-title">BAYAMON TRUCK PARTS</h1>
        <p class="brand-subtitle">Gestión inteligente en la nube con Firebase Firestore</p>
    </div>
    <div>
        <img src="data:image/svg+xml;base64,{truck_base64}" alt="Camión Heavy Duty" style="display: block; max-width: 170px;" />
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div>
            <div class="kpi-label">Empresas Clientes</div>
            <div class="kpi-value">{total_empresas}</div>
        </div>
        <div style="font-size: 2.2rem;">🏢</div>
    </div>
    <div class="kpi-card" style="border-left-color: #0284c7;">
        <div>
            <div class="kpi-label">Contactos Activos</div>
            <div class="kpi-value">{total_contactos}</div>
        </div>
        <div style="font-size: 2.2rem;">👥</div>
    </div>
    <div class="kpi-card" style="border-left-color: #d97706;">
        <div>
            <div class="kpi-label">Notas de Seguimiento</div>
            <div class="kpi-value">{total_notas}</div>
        </div>
        <div style="font-size: 2.2rem;">📝</div>
    </div>
</div>
""", unsafe_allow_html=True)

# BARRA LATERAL
st.sidebar.markdown(f"""
    <div class="user-badge">
        <div>
            <div style="font-size: 0.95rem; font-weight: 800; color: #0f172a;">👤 {st.session_state['nombre_completo']}</div>
            <div style="font-size: 0.8rem; color: #2563eb; font-weight: 600;">Rol: {st.session_state['rol']}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

if st.sidebar.button("Cerrar Sesión", use_container_width=True):
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.session_state["nombre_completo"] = None
    st.session_state["rol"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### ➕ Registrar Contacto")
with st.sidebar.form("form_contacto", clear_on_submit=True):
    empresa = st.text_input("Empresa *", placeholder="Ej: Transportes del Norte")
    sector = st.text_input("Sector", placeholder="Ej: Carga Pesada / Logística")
    nombre = st.text_input("Nombre *", placeholder="Ej: Carlos")
    apellido = st.text_input("Apellido *", placeholder="Ej: Rivera")
    cargo = st.text_input("Cargo", placeholder="Ej: Gerente de Flota")
    email = st.text_input("Email", placeholder="ejemplo@correo.com")
    telefono = st.text_input("Teléfono", placeholder="Ej: 787-555-0199")
    
    submit = st.form_submit_button("Guardar Registro", use_container_width=True)
    if submit:
        if not empresa.strip() or not nombre.strip() or not apellido.strip():
            st.sidebar.error("Empresa, Nombre y Apellido son obligatorios.")
        else:
            try:
                # Verificar duplicados por teléfono o email
                duplicado = False
                if telefono.strip():
                    t_check = list(db.collection("contactos").where("telefono", "==", telefono.strip()).limit(1).get())
                    if t_check: duplicado = True
                if email.strip() and not duplicado:
                    e_check = list(db.collection("contactos").where("email", "==", email.strip()).limit(1).get())
                    if e_check: duplicado = True

                if duplicado:
                    st.sidebar.warning("Este contacto ya existe (teléfono o email coinciden).")
                else:
                    # Guardar cliente
                    cliente_ref = db.collection("clientes").add({
                        "nombre_empresa": empresa.strip(),
                        "sector": sector.strip()
                    })
                    id_cliente = cliente_ref[1].id

                    # Guardar contacto vinculado
                    db.collection("contactos").add({
                        "id_cliente": id_cliente,
                        "nombre": nombre.strip(),
                        "apellido": apellido.strip(),
                        "cargo": cargo.strip(),
                        "email": email.strip(),
                        "telefono": telefono.strip(),
                        "nombre_empresa_cache": empresa.strip(), # Para facilitar filtros
                        "sector_cache": sector.strip()
                    })
                    st.sidebar.success("¡Contacto guardado con éxito!")
                    st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

# IMPORTACIÓN MASIVA
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Importación Masiva")
archivo_excel = st.sidebar.file_uploader("Cargar archivo .xlsx", type=["xlsx", "xls"])

if archivo_excel is not None:
    if st.sidebar.button("Procesar e Importar", use_container_width=True):
        try:
            df_import = pd.read_excel(archivo_excel)
            importados = 0
            for _, row in df_import.iterrows():
                emp = str(row.get('Empresa', '')).strip()
                sec = str(row.get('Sector', '')).strip()
                nom = str(row.get('Nombre', '')).strip()
                ape = str(row.get('Apellido', '')).strip()
                car = str(row.get('Cargo', '')).strip()
                eml = str(row.get('Email', '')).strip()
                tel = str(row.get('Telefono', '')).strip()

                if not emp or not nom or not ape or emp == 'nan':
                    continue

                cliente_ref = db.collection("clientes").add({
                    "nombre_empresa": emp,
                    "sector": sec if sec != 'nan' else ''
                })
                id_cliente = cliente_ref[1].id

                db.collection("contactos").add({
                    "id_cliente": id_cliente,
                    "nombre": nom,
                    "apellido": ape,
                    "cargo": car if car != 'nan' else '',
                    "email": eml if eml != 'nan' else '',
                    "telefono": tel if tel != 'nan' else '',
                    "nombre_empresa_cache": emp,
                    "sector_cache": sec if sec != 'nan' else ''
                })
                importados += 1

            st.sidebar.success(f"Se importaron {importados} contactos exitosamente.")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error al procesar archivo: {e}")

# PESTAÑAS PRINCIPALES
pestanas_nombres = ["📋 Directorio y Notas", "✏️ Modificar Registros"]
if st.session_state["rol"] == "Admin":
    pestanas_nombres.append("👥 Gestión de Usuarios")

pestanas = st.tabs(pestanas_nombres)

# ------------------------------------------
# PESTAÑA 1: DIRECTORIO Y NOTAS
# ------------------------------------------
with pestanas[0]:
    filtro = st.text_input("Buscador Central", placeholder="🔍 Buscar por empresa, nombre, cargo, teléfono, email...", label_visibility="collapsed")

    contactos_docs = db.collection("contactos").stream()
    filas = []
    for doc in contactos_docs:
        c = doc.to_dict()
        c_id = doc.id
        filas.append([
            c_id, 
            c.get("nombre_empresa_cache", "Sin empresa"), 
            c.get("sector_cache", "General"), 
            c.get("nombre", ""), 
            c.get("apellido", ""), 
            c.get("cargo", ""), 
            c.get("email", ""), 
            c.get("telefono", "")
        ])

    if filas:
        df = pd.DataFrame(filas, columns=["ID", "Empresa", "Sector", "Nombre", "Apellido", "Cargo", "Email", "Teléfono"])
        
        if filtro:
            f_lower = filtro.lower()
            df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(f_lower).any(), axis=1)]

        st.dataframe(df.drop(columns=["ID"]), use_container_width=True, height=260, hide_index=True)

        if not df.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 💬 Bitácora y Seguimiento Comercial")
            
            nombres_opciones = {f"{row[3]} {row[4]} — {row[1]}": row[0] for row in df.values}
            seleccion_contacto = st.selectbox("Seleccionar contacto para ver historial:", options=list(nombres_opciones.keys()))
            
            if seleccion_contacto:
                id_sel = nombres_opciones[seleccion_contacto]
                datos_sel = df[df["ID"] == id_sel].values[0]
                _, s_emp, s_sec, s_nom, s_ape, s_cargo, s_email, s_tel = datos_sel

                st.markdown(f"""
                    <div class="contact-card">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                            <div>
                                <h3 style="margin: 0; color: #0f172a; font-size: 1.3rem; font-weight: 800;">{s_nom} {s_ape}</h3>
                                <p style="margin: 4px 0 0 0; color: #334155; font-weight: 700;">{s_emp} &nbsp;•&nbsp; <span style="color:#2563eb;">{s_cargo or 'Sin cargo'}</span></p>
                                <p style="margin: 3px 0 0 0; color: #64748b; font-size: 0.9rem;">Sector: {s_sec or 'General'}</p>
                            </div>
                            <div style="text-align: right; font-size: 0.95rem; margin-top: 5px;">
                                <div style="color: #0f172a;">📞 <strong>{s_tel or 'Sin teléfono'}</strong></div>
                                <div style="color: #0f172a;">✉️ <strong>{s_email or 'Sin correo'}</strong></div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_historial, col_nueva_nota = st.columns([1.2, 1])

                with col_historial:
                    st.markdown("#### Historial de Interacciones")
                    notas_docs = db.collection("notas").where("id_contacto", "==", id_sel).order_by("fecha", direction=firestore.Query.DESCENDING).stream()
                    notas = [n.to_dict() for n in notas_docs]

                    if notas:
                        for nota_item in notas:
                            st.markdown(f"""
                                <div class="note-bubble">
                                    <div class="note-meta">
                                        <span style="color: #2563eb;">📅 {nota_item.get('fecha', '')}</span>
                                        <span style="color: #64748b;">👤 Por: <strong>{nota_item.get('autor', 'Desconocido')}</strong></span>
                                    </div>
                                    <div class="note-body">{nota_item.get('nota', '')}</div>
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No hay notas previas registradas para este contacto.")

                with col_nueva_nota:
                    st.markdown("#### Registrar Nueva Nota")
                    with st.form("form_nota", clear_on_submit=True):
                        nueva_nota = st.text_area(
                            "Detalles de la conversación o acuerdo:", 
                            placeholder="Ej: Se coordinó entrega de repuestos...",
                            height=120
                        )
                        submit_nota = st.form_submit_button("Guardar Nota", use_container_width=True)
                        if submit_nota and nueva_nota.strip():
                            db.collection("notas").add({
                                "id_contacto": id_sel,
                                "autor": st.session_state["nombre_completo"],
                                "nota": nueva_nota.strip(),
                                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.success("Nota agregada correctamente.")
                            st.rerun()
    else:
        st.info("No se encontraron registros activos en Firestore.")

# ------------------------------------------
# PESTAÑA 2: MODIFICAR / EDITAR CONTACTOS
# ------------------------------------------
with pestanas[1]:
    st.markdown("### Modificar Datos de Contacto y Empresa")
    
    contactos_docs = db.collection("contactos").stream()
    todos_contactos = []
    for doc in contactos_docs:
        c = doc.to_dict()
        todos_contactos.append((doc.id, c.get("nombre_empresa_cache", ""), c.get("nombre", ""), c.get("apellido", ""), c.get("email", ""), c))

    if todos_contactos:
        dict_edit = {f"{row[2]} {row[3]} — {row[1]} ({row[4] or 'Sin email'})": row[0] for row in todos_contactos}
        contacto_a_editar = st.selectbox("Seleccione el contacto que desea actualizar:", options=list(dict_edit.keys()))

        if contacto_a_editar:
            id_editar = dict_edit[contacto_a_editar]
            contacto_doc_ref = db.collection("contactos").document(id_editar)
            contacto_data = contacto_doc_ref.get().to_dict()

            if contacto_data:
                e_empresa = contacto_data.get("nombre_empresa_cache", "")
                e_sector = contacto_data.get("sector_cache", "")
                e_nombre = contacto_data.get("nombre", "")
                e_apellido = contacto_data.get("apellido", "")
                e_cargo = contacto_data.get("cargo", "")
                e_email = contacto_data.get("email", "")
                e_telefono = contacto_data.get("telefono", "")
                id_cliente = contacto_data.get("id_cliente", "")

                with st.form("form_edicion"):
                    st.markdown("##### Información Comercial")
                    col1, col2 = st.columns(2)
                    with col1:
                        nuevo_empresa = st.text_input("Empresa *", value=str(e_empresa))
                        nuevo_sector = st.text_input("Sector Industrial", value=str(e_sector))
                    with col2:
                        nuevo_cargo = st.text_input("Cargo del Contacto", value=str(e_cargo))
                    
                    st.markdown("##### Información Personal")
                    col3, col4 = st.columns(2)
                    with col3:
                        nuevo_nombre = st.text_input("Nombre *", value=str(e_nombre))
                        nuevo_email = st.text_input("Correo Electrónico", value=str(e_email))
                    with col4:
                        nuevo_apellido = st.text_input("Apellido *", value=str(e_apellido))
                        nuevo_telefono = st.text_input("Teléfono", value=str(e_telefono))

                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_actualizar = st.form_submit_button("Guardar Cambios Actualizados", use_container_width=True)

                    if btn_actualizar:
                        if not nuevo_empresa.strip() or not nuevo_nombre.strip() or not nuevo_apellido.strip():
                            st.error("Empresa, Nombre y Apellido no pueden quedar vacíos.")
                        else:
                            try:
                                # Actualizar cliente si existe
                                if id_cliente:
                                    db.collection("clientes").document(id_cliente).update({
                                        "nombre_empresa": nuevo_empresa.strip(),
                                        "sector": nuevo_sector.strip()
                                    })
                                
                                # Actualizar contacto
                                contacto_doc_ref.update({
                                    "nombre": nuevo_nombre.strip(),
                                    "apellido": nuevo_apellido.strip(),
                                    "cargo": nuevo_cargo.strip(),
                                    "email": nuevo_email.strip(),
                                    "telefono": nuevo_telefono.strip(),
                                    "nombre_empresa_cache": nuevo_empresa.strip(),
                                    "sector_cache": nuevo_sector.strip()
                                })

                                st.success("Registro actualizado exitosamente.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al actualizar: {e}")
    else:
        st.info("No hay contactos disponibles para modificar.")

# ------------------------------------------
# PESTAÑA 3: GESTIÓN DE USUARIOS (SOLO ADMIN)
# ------------------------------------------
if st.session_state["rol"] == "Admin":
    with pestanas[2]:
        st.markdown("### 👥 Administración Completa de Usuarios")

        subtab_lista, subtab_crear, subtab_editar, subtab_eliminar = st.tabs([
            "📋 Lista de Usuarios", 
            "➕ Crear Usuario", 
            "✏️ Modificar Usuario", 
            "🗑️ Eliminar Usuario"
        ])

        usuarios_docs = db.collection("usuarios").stream()
        usuarios_db = []
        for doc in usuarios_docs:
            u = doc.to_dict()
            usuarios_db.append((doc.id, u.get("username", ""), u.get("nombre_completo", ""), u.get("rol", ""), u.get("fecha_creacion", "")))

        # 1. LISTADO
        with subtab_lista:
            if usuarios_db:
                df_usuarios = pd.DataFrame(usuarios_db, columns=["ID", "Usuario", "Nombre Completo", "Rol", "Fecha de Creación"])
                st.dataframe(df_usuarios.drop(columns=["ID"]), use_container_width=True, hide_index=True)
            else:
                st.info("No hay usuarios registrados.")

        # 2. CREAR
        with subtab_crear:
            st.markdown("#### Registrar un Nuevo Acceso")
            with st.form("form_nuevo_usuario", clear_on_submit=True):
                col_u1, col_u2 = st.columns(2)
                with col_u1:
                    nuevo_user = st.text_input("Nombre de Usuario (Login) *", placeholder="Ej: crivera")
                    nuevo_nombre = st.text_input("Nombre Completo *", placeholder="Ej: Carlos Rivera")
                with col_u2:
                    nuevo_pass = st.text_input("Contraseña *", type="password", placeholder="Contraseña segura...")
                    nuevo_rol = st.selectbox("Rol", options=["Vendedor", "Admin"])
                
                btn_crear_user = st.form_submit_button("Crear Nuevo Usuario", use_container_width=True)
                if btn_crear_user:
                    if not nuevo_user.strip() or not nuevo_nombre.strip() or not nuevo_pass.strip():
                        st.error("Todos los campos marcados con * son obligatorios.")
                    else:
                        # Verificar si ya existe el username
                        existe = list(db.collection("usuarios").where("username", "==", nuevo_user.strip().lower()).limit(1).get())
                        if existe:
                            st.error("Ese nombre de usuario ya existe. Por favor elige otro.")
                        else:
                            db.collection("usuarios").add({
                                "username": nuevo_user.strip().lower(),
                                "nombre_completo": nuevo_nombre.strip(),
                                "password_hash": hash_password(nuevo_pass),
                                "rol": nuevo_rol,
                                "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            st.success(f"Usuario '{nuevo_user}' creado exitosamente.")
                            st.rerun()

        # 3. EDITAR
        with subtab_editar:
            st.markdown("#### Modificar Datos o Cambiar Contraseña")
            if usuarios_db:
                dict_usuarios_edit = {f"{u[1]} — {u[2]} ({u[3]})": u for u in usuarios_db}
                seleccion_u_edit = st.selectbox("Seleccione el usuario que desea modificar:", options=list(dict_usuarios_edit.keys()), key="select_user_edit")
                
                if seleccion_u_edit:
                    u_data = dict_usuarios_edit[seleccion_u_edit]
                    id_u, u_user, u_nombre, u_rol, _ = u_data

                    with st.form("form_editar_usuario"):
                        col_ed1, col_ed2 = st.columns(2)
                        with col_ed1:
                            st.text_input("Usuario (Login)", value=u_user, disabled=True)
                            nombre_editado = st.text_input("Nombre Completo *", value=u_nombre)
                        with col_ed2:
                            roles_disponibles = ["Vendedor", "Admin"]
                            indice_rol = roles_disponibles.index(u_rol) if u_rol in roles_disponibles else 0
                            rol_editado = st.selectbox("Rol asignado", options=roles_disponibles, index=indice_rol)
                            pass_editada = st.text_input("Nueva Contraseña (opcional)", type="password", placeholder="Dejar en blanco para mantener la actual")

                        btn_actualizar_user = st.form_submit_button("Guardar Cambios del Usuario", use_container_width=True)
                        if btn_actualizar_user:
                            if not nombre_editado.strip():
                                st.error("El nombre completo no puede quedar vacío.")
                            else:
                                user_ref = db.collection("usuarios").document(id_u)
                                if pass_editada.strip():
                                    user_ref.update({
                                        "nombre_completo": nombre_editado.strip(),
                                        "rol": rol_editado,
                                        "password_hash": hash_password(pass_editada.strip())
                                    })
                                else:
                                    user_ref.update({
                                        "nombre_completo": nombre_editado.strip(),
                                        "rol": rol_editado
                                    })

                                if u_user == st.session_state["usuario"]:
                                    st.session_state["nombre_completo"] = nombre_editado.strip()
                                    st.session_state["rol"] = rol_editado

                                st.success(f"Usuario '{u_user}' actualizado exitosamente.")
                                st.rerun()
            else:
                st.info("No hay usuarios disponibles.")

        # 4. ELIMINAR
        with subtab_eliminar:
            st.markdown("#### Dar de Baja una Cuenta")
            if usuarios_db:
                dict_usuarios_del = {f"{u[1]} — {u[2]} ({u[3]})": u for u in usuarios_db}
                seleccion_u_del = st.selectbox("Seleccione el usuario que desea eliminar:", options=list(dict_usuarios_del.keys()), key="select_user_del")

                if seleccion_u_del:
                    u_del_data = dict_usuarios_del[seleccion_u_del]
                    id_del, user_del, nombre_del, rol_del, _ = u_del_data

                    st.warning(f"⚠️ **Atención:** Estás a punto de eliminar permanentemente al usuario **{user_del} ({nombre_del})**.")

                    with st.form("form_eliminar_usuario"):
                        btn_confirmar_baja = st.form_submit_button("Confirmar y Eliminar Usuario", use_container_width=True)
                        if btn_confirmar_baja:
                            if user_del == st.session_state["usuario"]:
                                st.error("❌ No puedes eliminar tu propia cuenta mientras estás conectado.")
                            else:
                                admins = [u for u in usuarios_db if u[3] == "Admin"]
                                if rol_del == "Admin" and len(admins) <= 1:
                                    st.error("❌ No se puede eliminar el único administrador del sistema.")
                                else:
                                    db.collection("usuarios").document(id_del).delete()
                                    st.success(f"El usuario '{user_del}' ha sido eliminado exitosamente.")
                                    st.rerun()
            else:
                st.info("No hay usuarios para eliminar.")