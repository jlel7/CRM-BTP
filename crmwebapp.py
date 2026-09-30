# --- SECCIÓN DE NOTAS Y SEGUIMIENTO ---
elif menu == "Notas y Seguimiento":
    st.title("Notas y Seguimiento del Cliente")
    
    cliente_id_input = st.text_input("Ingrese el ID del Contacto/Cliente para ver sus notas:")
    
    if cliente_id_input:
        try:
            # Consulta a Firebase
            notas_docs = db.collection("notas").where("id_contacto", "==", cliente_id_input.strip()).stream()
            notas = [n.to_dict() for n in notas_docs]
            
            if notas:
                df_notas = pd.DataFrame(notas)
                
                # Asegurar que la fecha sea formato datetime para poder hacer cálculos
                if "fecha" in df_notas.columns:
                    df_notas["fecha"] = pd.to_datetime(df_notas["fecha"], errors='coerce', utc=True)
                    df_notas = df_notas.sort_values(by="fecha", ascending=False)
                    
                    st.markdown("---")
                    st.markdown("### 📊 Indicadores Clave (KPIs)")
                    
                    # Layout de 3 columnas para los KPIs
                    col1, col2, col3 = st.columns(3)
                    
                    # KPI 1: Total de Interacciones
                    total_notas = len(df_notas)
                    
                    # KPI 2: Fecha de la última interacción
                    ultima_fecha = df_notas["fecha"].iloc[0]
                    ultima_interaccion = ultima_fecha.strftime("%d %b %Y") if pd.notnull(ultima_fecha) else "N/A"
                    
                    # KPI 3: Actividad reciente (últimos 30 días)
                    hace_30_dias = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
                    notas_recientes = df_notas[df_notas["fecha"] >= hace_30_dias].shape[0]
                    
                    with col1:
                        st.metric(label="Total de Notas", value=total_notas)
                    with col2:
                        st.metric(label="Última Interacción", value=ultima_interaccion)
                    with col3:
                        st.metric(label="Interacciones (Últimos 30 días)", value=notas_recientes, delta=notas_recientes)
                        
                    st.markdown("---")
                    
                    # GRÁFICA INTERACTIVA: Frecuencia de notas por mes
                    st.markdown("#### 📈 Frecuencia de Contacto")
                    
                    # Agrupar las notas por la fecha (ignorando la hora)
                    df_grafica = df_notas.copy()
                    df_grafica["Dia"] = df_grafica["fecha"].dt.date
                    frecuencia = df_grafica.groupby("Dia").size().reset_index(name='Cantidad de Notas')
                    frecuencia = frecuencia.set_index("Dia")
                    
                    # Mostrar gráfica de barras
                    st.bar_chart(frecuencia, color="#1f77b4")
                    
                    st.markdown("#### 📝 Detalle Histórico")
                    
                    # Convertir fecha de nuevo a texto legible para la tabla
                    df_notas["fecha"] = df_notas["fecha"].dt.strftime("%Y-%m-%d %H:%M")
                    
                st.dataframe(df_notas, use_container_width=True)
            else:
                st.info("No se encontraron notas para este ID de contacto.")
                
        except Exception as e:
            st.error(f"Error al cargar las notas: {e}")
