import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from tkcalendar import DateEntry
from PIL import Image
import os
import sys
import shutil
from datetime import datetime

# Módulos de tu sistema
import database as db
import personas
import destinos
import viaticos
import reportes

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class SistemaViaticosNaval(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Armada Argentina - Gestión de Viáticos v2.0")
        self.geometry("1200x850")
        
        db.init_db()
        self.rutas_temporales = {"sello": "", "firma": ""} # Para guardar rutas antes de confirmar destino

        # Layout Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Panel Lateral
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Opcional: Logo Ancla (Si tenés la imagen)
        ruta_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "referencias", "Escudo_Armada_Argentina.png")
        if os.path.exists(ruta_logo):
            img_logo = ctk.CTkImage(Image.open(ruta_logo), size=(140, 140))
            ctk.CTkLabel(self.sidebar, image=img_logo, text="").pack(pady=20)
        else:
            ctk.CTkLabel(self.sidebar, text="⚓ VIÁTICOS", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=30)

        self.btn_dash = ctk.CTkButton(self.sidebar, text="📊 Dashboard", command=self.show_dashboard)
        self.btn_dash.pack(pady=10, padx=20)

        self.btn_conf = ctk.CTkButton(self.sidebar, text="⚙️ Configuración", command=self.show_config)
        self.btn_conf.pack(pady=10, padx=20)

        self.content_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1a1a1a")
        self.content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.show_dashboard()

    def clear_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # DASHBOARD PRINCIPAL
    # ==========================================
    def show_dashboard(self):
        self.clear_frame()
        ctk.CTkLabel(self.content_frame, text="Generación de Recibo (Anexo 38)", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        # Cargar datos para menús
        jerarquias_db = db.get_all_jerarquias()
        self.lista_jerarquias = [f"{j['cod_jerarquia']} - {j['descripcion']}" for j in jerarquias_db] if jerarquias_db else []
        
        lista_destinos_db = destinos.listar_destinos()
        self.dict_destinos = {d['descripcion']: d['cod_destino'] for d in lista_destinos_db} if lista_destinos_db else {}
        self.lista_desc_destinos = list(self.dict_destinos.keys())

        # --- SECCIÓN PERSONAL ---
        frame_p = ctk.CTkFrame(self.content_frame)
        frame_p.pack(fill="x", padx=20, pady=5)
        
        row1 = ctk.CTkFrame(frame_p, fg_color="transparent")
        row1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row1, text="M.R.:").pack(side="left", padx=5)
        self.ent_mr = ctk.CTkEntry(row1, width=120)
        self.ent_mr.pack(side="left", padx=5)
        ctk.CTkButton(row1, text="🔍 Buscar", width=80, command=self.buscar_militar_gui).pack(side="left", padx=10)

        row2 = ctk.CTkFrame(frame_p, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row2, text="DNI:").pack(side="left", padx=5)
        self.ent_dni = ctk.CTkEntry(row2, width=110)
        self.ent_dni.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Nombre:").pack(side="left", padx=10)
        self.ent_nombre = ctk.CTkEntry(row2, width=180)
        self.ent_nombre.pack(side="left", padx=5)
        ctk.CTkLabel(row2, text="Apellido:").pack(side="left", padx=10)
        self.ent_apellido = ctk.CTkEntry(row2, width=180)
        self.ent_apellido.pack(side="left", padx=5)

        row3 = ctk.CTkFrame(frame_p, fg_color="transparent")
        row3.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row3, text="Jerarquía:").pack(side="left", padx=5)
        self.combo_jerarquia = ctk.CTkComboBox(row3, values=self.lista_jerarquias, width=220)
        self.combo_jerarquia.pack(side="left", padx=5)
        ctk.CTkLabel(row3, text="Destino Revista:").pack(side="left", padx=10)
        self.combo_destino_revista = ctk.CTkComboBox(row3, values=self.lista_desc_destinos, width=220)
        self.combo_destino_revista.pack(side="left", padx=5)

        ctk.CTkButton(frame_p, text="💾 Guardar Personal", fg_color="green", command=self.guardar_personal_gui).pack(pady=10)

        # --- SECCIÓN COMISIÓN ---
        frame_c = ctk.CTkFrame(self.content_frame)
        frame_c.pack(fill="x", padx=20, pady=5)
        
        row_c1 = ctk.CTkFrame(frame_c, fg_color="transparent")
        row_c1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row_c1, text="Origen:").pack(side="left", padx=5)
        self.ent_origen = ctk.CTkEntry(row_c1, width=220)
        self.ent_origen.pack(side="left", padx=5)
        ctk.CTkLabel(row_c1, text="Destino Comisión:").pack(side="left", padx=10)
        self.ent_dest_com = ctk.CTkEntry(row_c1, width=220)
        self.ent_dest_com.pack(side="left", padx=5)

        row_c2 = ctk.CTkFrame(frame_c, fg_color="transparent")
        row_c2.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(row_c2, text="Motivo:").pack(side="left", padx=5)
        self.ent_motivo = ctk.CTkEntry(row_c2, width=220)
        self.ent_motivo.pack(side="left", padx=5)
        
        ctk.CTkLabel(row_c2, text="Orden de:").pack(side="left", padx=10)
        self.ent_orden = ctk.CTkEntry(row_c2, width=150)
        self.ent_orden.pack(side="left", padx=5)
        
        ctk.CTkLabel(row_c2, text="Porcentaje (%):").pack(side="left", padx=15)
        self.ent_porcentaje = ctk.CTkEntry(row_c2, width=60)
        self.ent_porcentaje.insert(0, "100") # Queda en 100% por defecto
        self.ent_porcentaje.pack(side="left", padx=5)
        
        # Fila Fechas y Horas
        row_c3 = ctk.CTkFrame(frame_c, fg_color="transparent")
        row_c3.pack(fill="x", padx=10, pady=5)
        
        # Generamos las listas de horas y minutos automáticamente
        lista_horas = [f"{i:02d}" for i in range(24)]
        lista_minutos = [f"{i:02d}" for i in range(0, 60, 5)] # Saltos de 5 minutos

        # --- BLOQUE SALIDA ---
        ctk.CTkLabel(row_c3, text="Salida:").pack(side="left", padx=5)
        self.cal_salida = DateEntry(row_c3, date_pattern='dd/mm/yyyy', width=12)
        self.cal_salida.pack(side="left", padx=5)
        
        self.combo_h_salida = ctk.CTkComboBox(row_c3, values=lista_horas, width=65, state="readonly")
        self.combo_h_salida.set("08") # Hora por defecto
        self.combo_h_salida.pack(side="left", padx=2)
        
        ctk.CTkLabel(row_c3, text=":").pack(side="left")
        
        self.combo_m_salida = ctk.CTkComboBox(row_c3, values=lista_minutos, width=65, state="readonly")
        self.combo_m_salida.set("00") # Minuto por defecto
        self.combo_m_salida.pack(side="left", padx=2)

        # --- BLOQUE REGRESO ---
        ctk.CTkLabel(row_c3, text="Regreso:").pack(side="left", padx=15)
        self.cal_regreso = DateEntry(row_c3, date_pattern='dd/mm/yyyy', width=12)
        self.cal_regreso.pack(side="left", padx=5)
        
        self.combo_h_regreso = ctk.CTkComboBox(row_c3, values=lista_horas, width=65, state="readonly")
        self.combo_h_regreso.set("14") # Hora por defecto
        self.combo_h_regreso.pack(side="left", padx=2)
        
        ctk.CTkLabel(row_c3, text=":").pack(side="left")
        
        self.combo_m_regreso = ctk.CTkComboBox(row_c3, values=lista_minutos, width=65, state="readonly")
        self.combo_m_regreso.set("00") # Minuto por defecto
        self.combo_m_regreso.pack(side="left", padx=2)

        # --- SECCIÓN EMISIÓN ---
        frame_e = ctk.CTkFrame(self.content_frame)
        frame_e.pack(fill="x", padx=20, pady=5)
        row_e1 = ctk.CTkFrame(frame_e, fg_color="transparent")
        row_e1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(row_e1, text="Lugar Emisión:").pack(side="left", padx=5)
        self.ent_lugar_emision = ctk.CTkEntry(row_e1, width=150)
        self.ent_lugar_emision.insert(0, "Buenos Aires")
        self.ent_lugar_emision.pack(side="left", padx=5)
        ctk.CTkLabel(row_e1, text="Fecha Recibo:").pack(side="left", padx=15)
        self.cal_emision = DateEntry(row_e1, date_pattern='dd/mm/yyyy', width=12)
        self.cal_emision.pack(side="left", padx=5)

        ctk.CTkButton(self.content_frame, text="📄 GENERAR PDF", fg_color="#2c3e50", height=45, command=self.ejecutar_pdf_gui).pack(pady=10)

    # ==========================================
    # CONFIGURACIÓN Y PESTAÑAS
    # ==========================================
    def show_config(self):
        self.clear_frame()
        tabview = ctk.CTkTabview(self.content_frame)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        tab_detall = tabview.add("🏛️ Detall / Firmas")
        tab_destinos = tabview.add("📍 Destinos")
        tab_haberes = tabview.add("💰 Haberes")

        self.setup_tab_detall(tab_detall)
        self.setup_tab_destinos(tab_destinos)
        self.setup_tab_haberes(tab_haberes)

    def setup_tab_detall(self, tab):
        detall_data = db.get_config_detall()
        col = ctk.CTkFrame(tab, fg_color="transparent")
        col.pack(pady=10)

        # Sello
        self.f_sello_det = ctk.CTkFrame(col, width=200, height=140)
        self.f_sello_det.grid(row=0, column=0, padx=10)
        self.f_sello_det.pack_propagate(False)
        self.actualizar_previsualizacion(self.f_sello_det, detall_data.get('sello_detall') if detall_data else None, "Sello")
        ctk.CTkButton(col, text="Cargar Sello", command=lambda: self.procesar_subida_detall("sello")).grid(row=1, column=0, pady=5)

        # Firma
        self.f_firma_det = ctk.CTkFrame(col, width=200, height=140)
        self.f_firma_det.grid(row=0, column=1, padx=10)
        self.f_firma_det.pack_propagate(False)
        self.actualizar_previsualizacion(self.f_firma_det, detall_data.get('firma_detall') if detall_data else None, "Firma")
        ctk.CTkButton(col, text="Cargar Firma", command=lambda: self.procesar_subida_detall("firma")).grid(row=1, column=1, pady=5)

    def setup_tab_destinos(self, tab):
        frame_form = ctk.CTkFrame(tab)
        frame_form.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(frame_form, text="Código:").grid(row=0, column=0, padx=5)
        self.ent_cod_dest = ctk.CTkEntry(frame_form, width=100)
        self.ent_cod_dest.grid(row=0, column=1, padx=5)
        ctk.CTkButton(frame_form, text="🔍", width=40, command=self.cargar_datos_destino).grid(row=0, column=2, padx=5)
        
        ctk.CTkLabel(frame_form, text="Descripción:").grid(row=0, column=3, padx=5)
        self.ent_desc_dest = ctk.CTkEntry(frame_form, width=200)
        self.ent_desc_dest.grid(row=0, column=4, padx=5)

        frame_imgs = ctk.CTkFrame(tab, fg_color="transparent")
        frame_imgs.pack(pady=10)

        self.f_sello_dir = ctk.CTkFrame(frame_imgs, width=200, height=140)
        self.f_sello_dir.grid(row=0, column=0, padx=20)
        self.f_sello_dir.pack_propagate(False)
        self.actualizar_previsualizacion(self.f_sello_dir, None, "Sello")
        ctk.CTkButton(frame_imgs, text="Cargar Sello Destino", command=lambda: self.subir_imagen_destino("sello")).grid(row=1, column=0, pady=5)

        self.f_firma_dir = ctk.CTkFrame(frame_imgs, width=200, height=140)
        self.f_firma_dir.grid(row=0, column=1, padx=20)
        self.f_firma_dir.pack_propagate(False)
        self.actualizar_previsualizacion(self.f_firma_dir, None, "Firma")
        ctk.CTkButton(frame_imgs, text="Cargar Firma Destino", command=lambda: self.subir_imagen_destino("firma")).grid(row=1, column=1, pady=5)

        ctk.CTkButton(tab, text="💾 GUARDAR DESTINO", fg_color="green", command=self.guardar_destino_completo).pack(pady=10)

    def setup_tab_haberes(self, tab):
        frame_form = ctk.CTkFrame(tab)
        frame_form.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(frame_form, text="Mes:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_mes = ctk.CTkEntry(frame_form, placeholder_text="Ej: 2026-04", width=120)
        self.ent_mes.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_form, text="Sueldo Base ($):").grid(row=0, column=2, padx=5, pady=5)
        self.ent_monto = ctk.CTkEntry(frame_form, placeholder_text="Ej: 1500000.50", width=150)
        self.ent_monto.grid(row=0, column=3, padx=5, pady=5)

        ctk.CTkButton(frame_form, text="💾 Guardar", fg_color="green", command=self.guardar_haber_gui).grid(row=0, column=4, padx=15, pady=5)

        frame_tabla = ctk.CTkFrame(tab)
        frame_tabla.pack(fill="both", expand=True, padx=20, pady=5)
        
        scroll_y = ttk.Scrollbar(frame_tabla)
        scroll_y.pack(side="right", fill="y")

        self.tabla_haberes = ttk.Treeview(frame_tabla, columns=("Mes", "Monto"), show="headings", yscrollcommand=scroll_y.set)
        self.tabla_haberes.heading("Mes", text="Mes (AAAA-MM)")
        self.tabla_haberes.heading("Monto", text="Sueldo Base ($)")
        self.tabla_haberes.column("Mes", anchor="center", width=150)
        self.tabla_haberes.column("Monto", anchor="e", width=200)
        self.tabla_haberes.pack(fill="both", expand=True)
        scroll_y.config(command=self.tabla_haberes.yview)

        frame_acciones = ctk.CTkFrame(tab, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(frame_acciones, text="✏️ Editar", command=self.cargar_haber_para_edicion).pack(side="left", padx=10)
        ctk.CTkButton(frame_acciones, text="🗑️ Eliminar", fg_color="#c0392b", hover_color="#e74c3c", command=self.eliminar_haber_gui).pack(side="right", padx=10)

        self.cargar_tabla_haberes()

    # ==========================================
    # LÓGICA GENERAL
    # ==========================================
    def actualizar_previsualizacion(self, frame, ruta, texto):
        for w in frame.winfo_children(): w.destroy()
        if ruta and os.path.exists(ruta):
            img = ctk.CTkImage(Image.open(ruta), size=(180, 100))
            ctk.CTkLabel(frame, image=img, text="").pack(expand=True)
        else:
            ctk.CTkLabel(frame, text=f"Sin {texto}").pack(expand=True)

    def copiar_imagen_local(self, archivo_origen, prefijo):
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        dest_dir = os.path.join(base_dir, "uploads")
        if not os.path.exists(dest_dir): os.makedirs(dest_dir)
        nombre = f"{prefijo}_{datetime.now().strftime('%H%M%S')}{os.path.splitext(archivo_origen)[1]}"
        ruta_final = os.path.join(dest_dir, nombre)
        shutil.copy2(archivo_origen, ruta_final)
        return ruta_final

    def procesar_subida_detall(self, tipo):
        archivo = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if archivo:
            ruta_destino = self.copiar_imagen_local(archivo, f"detall_{tipo}")
            detall_actual = db.get_config_detall()
            s_path = ruta_destino if tipo == "sello" else (detall_actual['sello_detall'] if detall_actual else "")
            f_path = ruta_destino if tipo == "firma" else (detall_actual['firma_detall'] if detall_actual else "")
            db.save_config_detall(s_path, f_path, "", "")
            target_frame = self.f_sello_det if tipo == "sello" else self.f_firma_det
            self.actualizar_previsualizacion(target_frame, ruta_destino, tipo)
            messagebox.showinfo("Éxito", f"{tipo.capitalize()} guardado.")

    def subir_imagen_destino(self, tipo):
        archivo = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg")])
        if archivo:
            ruta_final = self.copiar_imagen_local(archivo, f"dest_{tipo}")
            self.rutas_temporales[tipo] = ruta_final
            target_frame = self.f_sello_dir if tipo == "sello" else self.f_firma_dir
            self.actualizar_previsualizacion(target_frame, ruta_final, tipo)

    def guardar_destino_completo(self):
        cod = self.ent_cod_dest.get()
        desc = self.ent_desc_dest.get()
        if not cod or not desc: return messagebox.showerror("Error", "Complete código y descripción")
        actual = destinos.obtener_destino(cod)
        s_path = self.rutas_temporales["sello"] or (actual['sello_director'] if actual else "")
        f_path = self.rutas_temporales["firma"] or (actual['firma_director'] if actual else "")
        db.update_destino(int(cod), desc, s_path, f_path, "", "") if actual else db.insert_destino(int(cod), desc, s_path, f_path, "", "")
        messagebox.showinfo("Éxito", "Destino guardado en la Base de Datos.")
        self.rutas_temporales = {"sello": "", "firma": ""}

    def cargar_datos_destino(self):
        dest = destinos.obtener_destino(self.ent_cod_dest.get())
        if dest:
            self.ent_desc_dest.delete(0, 'end'); self.ent_desc_dest.insert(0, dest['descripcion'])
            self.actualizar_previsualizacion(self.f_sello_dir, dest['sello_director'], "Sello")
            self.actualizar_previsualizacion(self.f_firma_dir, dest['firma_director'], "Firma")
            self.rutas_temporales = {"sello": "", "firma": ""}
        else:
            messagebox.showwarning("Aviso", "Código no encontrado.")

    # --- LÓGICA HABERES ---
    def cargar_tabla_haberes(self):
        for item in self.tabla_haberes.get_children(): self.tabla_haberes.delete(item)
        lista_haberes = db.get_all_meses()
        if lista_haberes:
            for h in lista_haberes:
                monto = f"$ {h['sueldo_almirante']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                self.tabla_haberes.insert("", "end", values=(h['mes'], monto))

    def guardar_haber_gui(self):
        mes = self.ent_mes.get().strip()
        monto_str = self.ent_monto.get().strip().replace(",", ".")
        if not mes or not monto_str: return messagebox.showwarning("Atención", "Complete mes y monto.")
        try:
            db.insert_mes(mes, float(monto_str))
            messagebox.showinfo("Éxito", "Haber guardado.")
            self.ent_mes.delete(0, 'end'); self.ent_monto.delete(0, 'end')
            self.cargar_tabla_haberes()
        except ValueError: messagebox.showerror("Error", "Monto inválido.")

    def cargar_haber_para_edicion(self):
        seleccion = self.tabla_haberes.selection()
        if not seleccion: return
        mes, monto_str = self.tabla_haberes.item(seleccion[0])['values']
        self.ent_mes.delete(0, 'end'); self.ent_mes.insert(0, mes)
        self.ent_monto.delete(0, 'end'); self.ent_monto.insert(0, monto_str.replace("$ ", "").replace(".", "").replace(",", "."))

    def eliminar_haber_gui(self):
        seleccion = self.tabla_haberes.selection()
        if not seleccion: return
        mes = self.tabla_haberes.item(seleccion[0])['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar mes {mes}?"):
            db.delete_mes(mes)
            self.cargar_tabla_haberes()

    # --- LÓGICA PERSONAL Y PDF ---
    def buscar_militar_gui(self):
        p = personas.obtener_persona(self.ent_mr.get())
        if p:
            self.ent_dni.delete(0, 'end'); self.ent_dni.insert(0, str(p['dni']))
            self.ent_nombre.delete(0, 'end'); self.ent_nombre.insert(0, p['nombre'])
            self.ent_apellido.delete(0, 'end'); self.ent_apellido.insert(0, p['apellido'])
            
            # Sincronizar Combos
            for val in self.lista_jerarquias:
                if val.startswith(f"{p.get('cod_jerarquia', '')} -"):
                    self.combo_jerarquia.set(val)
                    break
            self.combo_destino_revista.set(next((k for k, v in self.dict_destinos.items() if v == p.get('cod_destino')), ""))
        else:
            self.ent_dni.delete(0, 'end'); self.ent_nombre.delete(0, 'end'); self.ent_apellido.delete(0, 'end')

    def guardar_personal_gui(self):
        mr = self.ent_mr.get().strip(); dni = self.ent_dni.get().strip()
        nom = self.ent_nombre.get().strip(); ape = self.ent_apellido.get().strip()
        jer = self.combo_jerarquia.get(); dest = self.combo_destino_revista.get()
        
        if not mr or not dni or not nom or not ape: return messagebox.showerror("Error", "Complete MR, DNI, Nombre y Apellido.")
        cod_jer = jer.split(" - ")[0] if " - " in jer else ""
        cod_dest = self.dict_destinos.get(dest)
        
        try:
            personas.guardar_persona(mr, dni, nom, ape, cod_jer, cod_dest)
            messagebox.showinfo("Éxito", "Personal guardado correctamente.")
        except Exception as e: messagebox.showerror("Error", str(e))

    def ejecutar_pdf_gui(self):
        try:
            # 1. Validaciones
            mr = self.ent_mr.get().strip()
            if not mr: return messagebox.showerror("Error", "Ingrese MR")

            desc_revista = self.combo_destino_revista.get()
            cod_dest = self.dict_destinos.get(desc_revista)
            dest_info = destinos.obtener_destino(cod_dest)
            detall_info = db.get_config_detall()
                        
            # 2. Sueldo base
            f_salida_obj = datetime.strptime(self.cal_salida.get(), "%d/%m/%Y")
            sueldo_adm = db.get_sueldo_mes(f_salida_obj.strftime("%Y-%m"))
            if not sueldo_adm: return messagebox.showerror("Error", "Falta haber cargado para este mes.")
            
            # Leemos el porcentaje (si lo borran o ponen letras, usa 100% por seguridad)
            try:
                pct = float(self.ent_porcentaje.get().replace(",", "."))
            except ValueError:
                pct = 100.0
                
            # Achicamos el sueldo base según el porcentaje de la comisión
            sueldo_ajustado = sueldo_adm * (pct / 100.0)
            
            # 3. Categoría real
            cod_jer = self.combo_jerarquia.get().split(" - ")[0]
            cat_row = db.execute_query("SELECT c.categoria FROM jerarquias j JOIN categorias c ON j.id_cat = c.id_cat WHERE j.cod_jerarquia = ?", (cod_jer,), fetch=True)
            cat_nombre = cat_row["categoria"] if cat_row else "VOLUNTARIOS Y ASPIRANTES"

           # Unimos lo que el usuario seleccionó en los nuevos combos
            hora_salida_armada = f"{self.combo_h_salida.get()}:{self.combo_m_salida.get()}"
            hora_regreso_armada = f"{self.combo_h_regreso.get()}:{self.combo_m_regreso.get()}"

            # 4. Liquidar (Pasamos las horas armadas)
            liquidacion = viaticos.liquidar_viatico(sueldo_ajustado, cat_nombre, self.cal_salida.get(), hora_salida_armada, self.cal_regreso.get(), hora_regreso_armada)
            
            # 5. Generar PDF
            data_pdf = {
            "mr": mr, 
            "dni": self.ent_dni.get(), 
            "nombre": self.ent_nombre.get(), 
            "apellido": self.ent_apellido.get(),
            "jerarquia_desc": self.combo_jerarquia.get().split(" - ")[1], 
            "destino_revista_desc": desc_revista, 
            "cod_destino": cod_dest,
            "lugar_origen": self.ent_origen.get(), 
            "destino_comision": self.ent_dest_com.get(), 
            "motivo": self.ent_motivo.get(), 
            "orden": self.ent_orden.get(),
            "fecha_salida": self.cal_salida.get(),
            "fecha_regreso": self.cal_regreso.get(),
            "lugar_emision": self.ent_lugar_emision.get(), 
            "fecha_emision_recibo": self.cal_emision.get(),
            "hora_salida": hora_salida_armada,
            "hora_regreso": hora_regreso_armada,
            
            "porcentaje_aplicado": pct, 

            "sello_detall_path": detall_info['sello_detall'] if detall_info else "",
            "firma_detall_path": detall_info['firma_detall'] if detall_info else "",
            "sello_director_path": dest_info['sello_director'] if dest_info else "",
            "firma_director_path": dest_info['firma_director'] if dest_info else "",
            "total_calculado": liquidacion["total_calculado"], 
            "detalle_breakdown": liquidacion["detalle_breakdown"],
            "importe_diario": liquidacion["importe_diario"], 
            "categoria": cat_nombre
        }
            nombre_archivo = f"Recibo_{self.ent_apellido.get()}_{mr}.pdf"
            reportes.build_receipt_pdf(nombre_archivo, data_pdf)
            messagebox.showinfo("Éxito", f"PDF generado correctamente.\nPorcentaje de comisión aplicado: {pct}%\nTotal: $ {liquidacion['total_calculado']:,.2f}")
        except Exception as e: 
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = SistemaViaticosNaval()
    app.mainloop()