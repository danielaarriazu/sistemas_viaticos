import streamlit as st
import os
import sys
import pandas as pd
from datetime import date, time

# Importación de nuestros módulos backend
import database as db
import personas
import destinos
import viaticos
import reportes

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para desarrollo y para el .exe compilado"""
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Si no estamos en el ejecutable, usamos la ruta donde está este script (.py)
        base_path = os.path.abspath(os.path.dirname(__file__))
    
    return os.path.join(base_path, relative_path)

# Configuración inicial de la página
st.set_page_config(page_title="Viáticos Armada", layout="wide", page_icon="⚓")

# --- FUNCIONES AUXILIARES ---
def inicializar_estado():
    """Inicializa las variables de sesión para mantener los datos al recargar la página."""
    if 'mr_buscado' not in st.session_state:
        st.session_state.mr_buscado = False
        st.session_state.datos_persona = {
            "dni": "", "nombre": "", "apellido": "", 
            "cod_jerarquia": "", "cod_destino": ""
        }
    campos_comision = [
        "lugar_origen", "destino_comision", "motivo", "orden"
    ]
    for campo in campos_comision:
        if campo not in st.session_state:
            st.session_state[campo] = ""
            
    if 'fecha_salida' not in st.session_state:
        st.session_state.fecha_salida = date.today()
    if 'hora_salida' not in st.session_state:
        st.session_state.hora_salida = time(0, 0)
    if 'fecha_regreso' not in st.session_state:
        st.session_state.fecha_regreso = date.today()
    if 'hora_regreso' not in st.session_state:
        st.session_state.hora_regreso = time(0, 0)
    if 'fecha_emision_recibo' not in st.session_state:
        st.session_state.fecha_emision_recibo = date.today()

def guardar_imagen_subida(uploaded_file, prefijo_nombre):
    """Guarda la imagen subida en la carpeta local segura del ejecutable."""
    if uploaded_file is not None:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.abspath(os.path.dirname(__file__))
            
        uploads_dir = os.path.join(base_dir, "uploads")
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            
        _, extension = os.path.splitext(uploaded_file.name)
        nuevo_nombre = f"{prefijo_nombre}{extension}"   
        file_path = os.path.join(uploads_dir, nuevo_nombre)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return ""

def buscar_mr(mr_input):
    """Busca el MR en la base de datos y actualiza el estado."""
    if mr_input:
        p = personas.obtener_persona(mr_input)
        if p:
            st.session_state.datos_persona = p
            st.session_state.mr_buscado = True
            
            # 👇 FORZAMOS LA ACTUALIZACIÓN DE LAS KEYS DE LOS WIDGETS 👇
            st.session_state["dni_input_key"] = str(p.get('dni', ''))
            st.session_state["nombre_input_key"] = p.get('nombre', '')
            st.session_state["apellido_input_key"] = p.get('apellido', '')
            
            st.success("Personal encontrado.")
        else:
            st.session_state.datos_persona = {"dni": "", "nombre": "", "apellido": "", "cod_jerarquia": "", "cod_destino": ""}
            st.session_state.mr_buscado = False
            
            # 👇 LIMPIAMOS LAS KEYS SI NO EXISTE 👇
            st.session_state["dni_input_key"] = ""
            st.session_state["nombre_input_key"] = ""
            st.session_state["apellido_input_key"] = ""
            
            st.warning("MR no registrado. Complete los datos para dar de alta.")

def limpiar_formulario_completo():
    """Resetea todas las variables de sesión para dejar el formulario en blanco."""
    # 1. Limpiar datos de Persona y MR
    st.session_state.mr_buscado = False
    st.session_state.datos_persona = {
        "dni": "", "nombre": "", "apellido": "", 
        "cod_jerarquia": "", "cod_destino": ""
    }
    
    # 2. Limpiar todos los campos de texto (Agregamos DNI, Nombre y Apellido a la lista)
    campos_texto = [
        "dni_input_key", "nombre_input_key", "apellido_input_key", 
        "lugar_origen_input_key", "destino_comision_input_key", 
        "motivo_input_key", "orden_input_key", "mr_input_key"
    ]
    for campo in campos_texto:
        if campo in st.session_state:
            st.session_state[campo] = ""
    
    # 3. Resetear fechas y horas a valores actuales
    from datetime import date, time
    st.session_state.fecha_salida = date.today()
    st.session_state.fecha_regreso = date.today()
    st.session_state.hora_salida = time(0, 0)
    st.session_state.hora_regreso = time(0, 0)
    st.session_state.fecha_emision_recibo = date.today()
    
# --- CARGA DE DATOS PARA SELECTBOXES ---
jerarquias_db = db.get_all_jerarquias()
lista_jerarquias = [f"{j['cod_jerarquia']} - {j['descripcion']}" for j in jerarquias_db] if jerarquias_db else []

lista_destinos_db = destinos.listar_destinos()
dict_destinos = {d['descripcion']: d['cod_destino'] for d in lista_destinos_db} if lista_destinos_db else {}
lista_desc_destinos = list(dict_destinos.keys())

inicializar_estado()

# ==========================================
# PANEL LATERAL (SIDEBAR)
# ==========================================
# 1. Definir la ruta local de la imagen
# 'img' es la carpeta y 'escudo.png' el nombre del archivo
ruta_escudo = resource_path(os.path.join("referencias", "Escudo_Armada_Argentina.png"))

# 2. Verificar si el archivo existe antes de mostrarlo para evitar errores
if os.path.exists(ruta_escudo):
    st.sidebar.image(ruta_escudo, width=150)
else:
    st.sidebar.error(f"No se encontró la imagen en: {ruta_escudo}")

st.sidebar.title("Navegación")
menu = st.sidebar.radio("Seleccione un módulo:", ["📊 Dashboard", "⚙️ Configuraciones"])

# ==========================================
# MÓDULO 1: DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    st.header("Carga de Viáticos - Anexo 38 (703.e)")
    
    # --- BLOQUE PERSONAL ---
    st.subheader("1. Datos del Personal")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        mr_input = st.text_input("M.R.", value="", key="mr_input_key")
        if st.button("Buscar MR", width="stretch"):
            buscar_mr(mr_input)
            
    with col2:
        st.write("") # Espaciador
        
    col3, col4, col5 = st.columns(3)
    with col3:
        dni = st.text_input("DNI", key="dni_input_key")
    with col4:
        nombre = st.text_input("Nombre", key="nombre_input_key")
    with col5:
        apellido = st.text_input("Apellido", key="apellido_input_key")

    col6, col7 = st.columns(2)
    with col6:
        # Preseleccionar jerarquía si existe
        cod_jer = st.session_state.datos_persona.get('cod_jerarquia', '')
        idx_jer = 0
        for i, val in enumerate(lista_jerarquias):
            if val.startswith(f"{cod_jer} -"):
                idx_jer = i
                break
        jerarquia_seleccionada = st.selectbox("Jerarquía", options=lista_jerarquias, index=idx_jer if lista_jerarquias else 0)

    with col7:
        # Preseleccionar destino si existe
        cod_dest_actual = st.session_state.datos_persona.get('cod_destino', '')
        desc_actual = next((desc for desc, cod in dict_destinos.items() if cod == cod_dest_actual), "")
        idx_dest = lista_desc_destinos.index(desc_actual) if desc_actual in lista_desc_destinos else 0
        destino_revista = st.selectbox("Destino de Revista", options=lista_desc_destinos, index=idx_dest if lista_desc_destinos else 0)

    if st.button("Guardar/Actualizar Personal", type="primary"):
        try:
            cod_jer_final = jerarquia_seleccionada.split(" - ")[0]
            cod_dest_final = dict_destinos.get(destino_revista)
            res = personas.guardar_persona(mr_input, dni, nombre, apellido, cod_jer_final, cod_dest_final)
            st.success(f"Personal {res} correctamente.")
        except Exception as e:
            st.error(str(e))

    st.divider()

    # --- BLOQUE COMISIÓN ---
    st.subheader("2. Detalle de la Comisión")
    col8, col9 = st.columns(2)
    with col8:
        lugar_origen = st.text_input("Lugar de Origen", value="",key="lugar_origen_input_key")
        destino_comision = st.text_input("Destino de la Comisión", value="",key="destino_comision_input_key")
        fecha_salida = st.date_input("Fecha de Salida", format="DD/MM/YYYY", key="fecha_salida")
        hora_salida = st.time_input("Hora de Salida", key="hora_salida")
    with col9:
        motivo = st.text_input("Motivo de Comisión", value="",key="motivo_input_key")
        orden = st.text_input("Por orden de (Nro / Autoridad)", value="",key="orden_input_key")
        fecha_regreso = st.date_input("Fecha de Regreso", format="DD/MM/YYYY",key="fecha_regreso")
        hora_regreso = st.time_input("Hora de Regreso",key="hora_regreso")

    st.divider()

    # --- BLOQUE EMISIÓN DEL RECIBO ---
    st.subheader("3. Datos de Emisión del Recibo")
    col10, col11 = st.columns(2)
    with col10:
        lugar_emision = st.text_input("Lugar de Emisión", value="Buenos Aires")
    with col11:
        fecha_emision_recibo = st.date_input("Fecha del Recibo", format="DD/MM/YYYY", key="fecha_emision_recibo")

    st.divider()
    
    # --- GENERAR word ---
    if st.button("📝 GENERAR RECIBO (WORD)", width="stretch", type="primary"):
        try:
            cod_dest_pdf = dict_destinos.get(destino_revista)
            if not cod_dest_pdf:
                st.error("Seleccione un destino de revista.")
                st.stop()

            dest_info = destinos.obtener_destino(cod_dest_pdf)
            detall_info = db.get_config_detall()

            cod_jerarquia = jerarquia_seleccionada.split(" - ")[0]
            query_cat = "SELECT c.categoria FROM jerarquias j JOIN categorias c ON j.id_cat = c.id_cat WHERE j.cod_jerarquia = ?"
            categoria_row = db.execute_query(query_cat, (cod_jerarquia,), fetch=True)
            categoria_nombre = categoria_row["categoria"] if categoria_row else "VOLUNTARIOS Y ASPIRANTES"

            mes_actual = fecha_salida.strftime("%Y-%m")
            sueldo_adm = db.get_sueldo_mes(mes_actual)
            if not sueldo_adm:
                st.error(f"No hay sueldo de Almirante cargado para el mes {mes_actual}.")
                st.stop()

            f_salida_str = fecha_salida.strftime("%d/%m/%Y")
            f_regreso_str = fecha_regreso.strftime("%d/%m/%Y")
            h_salida_str = hora_salida.strftime("%H:%M")
            h_regreso_str = hora_regreso.strftime("%H:%M")
            
            liquidacion = viaticos.liquidar_viatico(
                sueldo_almirante=sueldo_adm, 
                categoria=categoria_nombre, 
                fecha_salida=f_salida_str, 
                hora_salida=h_salida_str, 
                fecha_regreso=f_regreso_str, 
                hora_regreso=h_regreso_str
            )

            data_pdf = {
                "mr": mr_input, "dni": dni, "nombre": nombre, "apellido": apellido,
                "jerarquia_desc": jerarquia_seleccionada.split(" - ")[1],
                "destino_revista_desc": destino_revista, "cod_destino": cod_dest_pdf,
                "lugar_origen": lugar_origen, "destino_comision": destino_comision,
                "motivo": motivo, "orden": orden, "fecha_salida": f_salida_str,
                "lugar_emision": lugar_emision, "fecha_emision_recibo": fecha_emision_recibo.strftime("%d/%m/%Y"),
                "sello_detall_path": detall_info['sello_detall'] if detall_info else "",
                "firma_detall_path": detall_info['firma_detall'] if detall_info else "",
                "sello_director_path": dest_info['sello_director'] if dest_info else "",
                "firma_director_path": dest_info['firma_director'] if dest_info else "",
                "total_calculado": liquidacion["total_calculado"],
                "detalle_breakdown": liquidacion["detalle_breakdown"],
                "importe_diario": liquidacion["importe_diario"], "categoria": categoria_nombre
            }

            # Lógica para evitar sobreescritura: Apellido_MR_Mes_Año.docx
            mes_salida_fmt = fecha_salida.strftime("%m_%Y")
            nombre_word = f"Recibo_{apellido}_{mr_input}_{mes_salida_fmt}.docx"
            nombre_docx = reportes.obtener_nombre_unico(nombre_word, ".docx")
            
            # Ejecución directa del Word
            reportes.build_receipt_docx(nombre_word, data_pdf)
            
            st.divider()
            
            # Botón único de descarga en formato Word (.docx)
            with open(nombre_word, "rb") as word_file:
                st.download_button(
                    label="⬇️ Descargar archivo Word (.docx)", 
                    data=word_file, 
                    file_name=nombre_word, 
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                    type="primary", 
                    on_click=limpiar_formulario_completo
                )
            st.success(f"¡Recibo Word generado con éxito!")
            
        except Exception as e:
            st.error(f"Error al generar el archivo Word: {e}")
# ==========================================
# MÓDULO 2: CONFIGURACIONES
# ==========================================
elif menu == "⚙️ Configuraciones":
    st.header("Configuraciones del Sistema")
    
    tab1, tab2, tab3 = st.tabs(["🏛️ Detall Personal Militar", "📍 Destinos y Directores", "💰 Haberes"])
    
    # --- TAB 1: DETALL ---
    with tab1:
        st.subheader("Configuración de División Personal Militar (Detall)")
        st.caption("💡 Aca configuramos el sello y la firma de la Div. Personal Militar.")
        detall_actual = db.get_config_detall()
                
        sello_detall = st.file_uploader("Subir Sello del Detall", type=['png', 'jpg', 'jpeg'], key="sd")
        firma_detall = st.file_uploader("Subir Aclaración de la Firma del Jefe de Personal", type=['png', 'jpg', 'jpeg'], key="fd")
        
        # Mostrar imágenes actuales si existen
        if detall_actual:
            col_prev1, col_prev2 = st.columns(2)
            with col_prev1:
                if detall_actual.get('sello_detall') and os.path.exists(detall_actual['sello_detall']):
                    st.image(detall_actual['sello_detall'], caption="Sello actual", width=120)
            with col_prev2:
                if detall_actual.get('firma_detall') and os.path.exists(detall_actual['firma_detall']):
                    st.image(detall_actual['firma_detall'], caption="Firma actual", width=150)
        
        if st.button("Guardar Detall"):
            try:
                ruta_sd = guardar_imagen_subida(sello_detall, "detall_sello") if sello_detall else (detall_actual.get('sello_detall', '') if detall_actual else '')
                ruta_fd = guardar_imagen_subida(firma_detall, "detall_firma") if firma_detall else (detall_actual.get('firma_detall', '') if detall_actual else '')
                db.save_config_detall(ruta_sd, ruta_fd)
                st.success("Detall configurado con éxito.")
            except Exception as e:
                st.error(str(e))

    with tab2:
        st.subheader("Alta / Actualización de Destino")
        st.caption("💡 Aca configuramos el sello y la aclaracion de firma de los Directores/Comandantes de los destinos.")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            cod_destino = st.text_input("Código Numérico (Ej. 697000)")
        with col_d2:
            desc_destino = st.text_input("Descripción (Ej. DIRI)")
         
        sello_dir = st.file_uploader("Subir Sello del Director/Comandante", type=['png', 'jpg', 'jpeg'], key="sdir")
        firma_dir = st.file_uploader("Subir Aclaración de la Firma del Director/Comandante", type=['png', 'jpg', 'jpeg'], key="fdir")

        # Mostrar imágenes actuales si existe el destino
        if cod_destino:
            try:
                dest_prev = destinos.obtener_destino(cod_destino)
                if dest_prev:
                    col_prev3, col_prev4 = st.columns(2)
                    with col_prev3:
                        if dest_prev.get('sello_director') and os.path.exists(dest_prev['sello_director']):
                            st.image(dest_prev['sello_director'], caption="Sello actual", width=120)
                    with col_prev4:
                        if dest_prev.get('firma_director') and os.path.exists(dest_prev['firma_director']):
                            st.image(dest_prev['firma_director'], caption="Firma actual", width=150)
            except Exception:
                pass
        
        if st.button("Guardar Destino"):
            try:
                dest_existe = destinos.obtener_destino(cod_destino)
                ruta_sdir = guardar_imagen_subida(sello_dir, f"dir_sello_{cod_destino}") if sello_dir else (dest_existe.get('sello_director', '') if dest_existe else '')
                ruta_fdir = guardar_imagen_subida(firma_dir, f"dir_firma_{cod_destino}") if firma_dir else (dest_existe.get('firma_director', '') if dest_existe else '')
                
                res = destinos.guardar_destino(cod_destino, desc_destino, ruta_sdir, ruta_fdir)
                st.success(f"Destino {res} correctamente.")
            except Exception as e:
                st.error(str(e))

    # --- TAB 3: HABERES ---
    with tab3:
        st.subheader("Sueldo Base (Almirante)")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            mes_haber = st.text_input("Mes (Ej. 2026-04)")
        with col_h2:
            sueldo_adm = st.number_input("Sueldo Base ($)", min_value=0.0, format="%.2f")
            
        if st.button("Guardar Sueldo"):
            if mes_haber.strip() == "":
                st.warning("Por favor, ingresa un mes válido.")
            else:
                try:
                    db.insert_mes(mes_haber, sueldo_adm)
                    st.success("Haberes actualizados.")
                except Exception as e:
                    st.error("Error al guardar haberes.")
        st.divider()
        st.subheader("Registros Cargados")
        st.caption("💡 Puedes editar los montos haciendo doble clic en la celda o eliminar filas seleccionándolas y presionando suprimir.")

        datos = db.get_all_meses() 
    
        if datos:
        # Convertimos a DataFrame y renombramos columnas para la vista
            df = pd.DataFrame(datos)
            df = df.rename(columns={"mes": "Mes", "sueldo_almirante": "Sueldo Base"})

        # Mostramos la grilla editable
            st.data_editor(
                df,
                num_rows="dynamic", # Habilita agregar y borrar filas desde la interfaz
                column_config={
                    "Mes": st.column_config.TextColumn("Mes", disabled=True), # Protegemos la clave primaria
                    "Sueldo Base": st.column_config.NumberColumn("Sueldo Base ($)", format="%.2f")
                },
                use_container_width=True,
                hide_index=True,
                key="editor_haberes" # Clave obligatoria para leer los cambios
            )

            # Botón para sincronizar los cambios de la grilla con la base de datos
            if st.button("💾 Guardar Cambios de la Tabla", type="primary"):
                try:
                    cambios = st.session_state["editor_haberes"]
                    cambios_realizados = False

                    # 1. Procesar modificaciones (Update)
                    for index_fila, modificaciones in cambios["edited_rows"].items():
                        mes_editado = df.iloc[index_fila]["Mes"]
                        nuevo_sueldo = modificaciones.get("Sueldo Base")
                        if nuevo_sueldo is not None:
                            db.update_mes(mes_editado, nuevo_sueldo)
                            cambios_realizados = True

                    # 2. Procesar eliminaciones (Delete)
                    for index_fila in cambios["deleted_rows"]:
                        mes_eliminado = df.iloc[index_fila]["Mes"]
                        db.delete_mes(mes_eliminado)
                        cambios_realizados = True

                    if cambios_realizados:
                        st.success("Base de datos sincronizada correctamente.")
                        st.rerun()
                    else:
                        st.info("No se detectaron cambios para guardar.")
                
                except Exception as e:
                    st.error(f"Error al sincronizar: {e}")
        else:
            st.info("No hay haberes cargados todavía en la base de datos.")