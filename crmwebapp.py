import base64
import hashlib
import json
import os # <--- Nuevo import necesario
import pandas as pd
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Bayamon Truck Parts - CRM", page_icon="🚛", layout="wide")

# ==========================================
# 2. INICIALIZACIÓN DE FIREBASE FIRESTORE (ADAPTADO PARA RED LOCAL)
# ==========================================
db = None

if not firebase_admin._apps:
    try:
        # 1. Primero intenta buscar un archivo físico en tu computadora local
        if os.path.exists("firebase_credentials.json"):
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
            
        # 2. Si no hay archivo local, busca en los secretos (para cuando lo subas a la nube)
        elif "firebase_json" in st.secrets:
            creds_json = st.secrets["firebase_json"]
            creds_dict = json.loads(creds_json) if isinstance(creds_json, str) else dict(creds_json)
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
            
        else:
            st.error("⚠️ Falta la configuración de Firebase.")
            st.info("Para uso local: Descarga tu clave de Firebase y guárdala en esta misma carpeta con el nombre 'firebase_credentials.json'.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Error al inicializar las credenciales de Firebase: {e}")
        st.stop()

try:
    db = firestore.client()
except Exception as e:
    st.error(f"❌ Error al conectar con Firestore: {e}")
    st.stop()
