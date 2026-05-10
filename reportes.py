import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

import viaticos


def _img(img_path, width, height):
    """Retorna Image si el archivo existe, sino un Spacer del mismo tamaño."""
    if img_path and os.path.exists(img_path):
        return Image(img_path, width=width, height=height)
    return Spacer(width, height)


def build_receipt_pdf(path: str, data: dict) -> None:
    """Genera el PDF con el formato exacto del Anexo 38 (703.e)."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        topMargin=2.0*cm, bottomMargin=2.0*cm,
        leftMargin=2.5*cm, rightMargin=2.5*cm
    )

    styles = getSampleStyleSheet()
    s_left     = ParagraphStyle("Left",     parent=styles["Normal"], fontName="Helvetica", fontSize=10, alignment=0)
    s_center   = ParagraphStyle("Center",   parent=styles["Normal"], fontName="Helvetica", fontSize=10, alignment=1)
    s_right    = ParagraphStyle("Right",    parent=styles["Normal"], fontName="Helvetica", fontSize=10, alignment=2)
    s_title    = ParagraphStyle("Title",    parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=12, alignment=1, leading=14)
    s_body     = ParagraphStyle("Body",     parent=styles["Normal"], fontName="Helvetica", fontSize=11, leading=18, alignment=4)
    s_sign     = ParagraphStyle("Sign",     parent=styles["Normal"], fontName="Helvetica", fontSize=9,  leading=13, alignment=1)
    s_causante = ParagraphStyle("Causante", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=15, alignment=0)

    def fecha_es(fecha_str):
        if not fecha_str:
            return ""
        dia, mes, anio = fecha_str.split("/")
        meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        return f"{dia} de {meses[int(mes)]} de {anio}"

    # ── Cálculos ──────────────────────────────────────────────────────────────
    total_float  = data.get("total_calculado", 0.0)
    total_txt    = viaticos.format_money(total_float)
    total_letras = viaticos.importe_a_letras(total_float)
    pct_aplicado = data.get("porcentaje_aplicado", 100.0)
    texto_pct_nota = f" (al {pct_aplicado}%)" if pct_aplicado != 100.0 else ""
    
    texto_cuerpo = (
        f"--------- Recibí de la <b>JEFATURA ADMINISTRATIVA FINANCIERA DE LA ARMADA</b> "
        f"la suma de {total_letras} ({total_txt}), correspondiente a "
        f"{data.get('detalle_breakdown', '')} del viático diario de "
        f"{viaticos.format_money(data.get('importe_diario', 0.0))} – "
        f"({data.get('categoria', '')}){texto_pct_nota}. " 
        f"Desde {data.get('lugar_origen', '')} el día {data.get('fecha_salida', '')} a las {data.get('hora_salida', '')} "
        f"hasta {data.get('destino_comision', '')} el día {data.get('fecha_regreso', '')} a las {data.get('hora_regreso', '')}, "
        f"con motivo de {data.get('motivo', '')}. Por orden {data.get('orden', '')}."
    )

    # ── Encabezado: "ARMADA ARGENTINA" izq / "ANEXO 38 (703.e)" der ──────────
    t_header = Table([
    [Paragraph("ARMADA ARGENTINA", s_left)],
    [Paragraph("ANEXO 38<br/>(703.e)", s_center)]
    ], colWidths=[16*cm])

    elems = [
        t_header,
        Spacer(1, 1*cm),
        Paragraph("RECIBO POR VIÁTICOS POR COMISIONES DEL SERVICIO<br/>PERSONAL MILITAR", s_title),
        Spacer(1, 0.5*cm),
        Paragraph(texto_cuerpo, s_body),
        Spacer(1, 0.5*cm),
    ]

    # ── Fecha de emisión (derecha) ────────────────────────────────────────────
    lugar_emision = data.get("lugar_emision", "Buenos Aires")
    fecha_fmt     = fecha_es(data.get("fecha_emision_recibo", ""))
    elems.append(Paragraph(f"{lugar_emision}, {fecha_fmt}.", s_right))
    elems.append(Spacer(1, 1*cm))

    # ── Bloque causante (mitad derecha) ───────────────────────────────────────
    causante_txt = (
        f"Firma: .................................................<br/>"
        f"Aclaración: {data.get('nombre', '')} {data.get('apellido', '')}<br/>"
        f"M.R. {data.get('mr', '')} – {data.get('jerarquia_desc', '')}<br/>"
        f"DNI: {data.get('dni', '')}<br/>"
        f"COD. Alfa/Numérico: {data.get('cod_destino', '')}<br/>"
        f"Destino de Revista: {data.get('destino_revista_desc', '')}"
    )
    t_causante = Table(
        [[Paragraph("", s_causante), Paragraph(causante_txt, s_causante)]],
        colWidths=[10*cm, 8*cm]
    )
    t_causante.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    elems.append(t_causante)
    elems.append(Spacer(0.1, 0.5*cm))

    # ── Bloque de autoridades (FORMATO ESCALONADO) ────────────────────────────
    #
    #  FILA 1 (Arriba):   [ Sello Detall (Izq) ]    [ Firma + Aclaración (Centro-Izq) ]
    #  FILA 2 (Abajo):                              [ Sello Director (Centro) ]    [ Firma + Aclaración (Der) ]
    #
    nombre_jefe = data.get("nombre_jefe_personal", "")
    cargo_jefe  = data.get("cargo_jefe_personal",  "")
    nombre_dir  = data.get("nombre_director", "")
    cargo_dir   = data.get("cargo_director",  "")

    # Imágenes (Ajustamos el tamaño para que entren perfectas sin deformar la tabla)
    sello_detall_img = _img(data.get("sello_detall_path"),   5.0*cm, 4.0*cm)
    firma_detall_img = _img(data.get("firma_detall_path"),   4.0*cm, 1.5*cm)
    sello_dir_img    = _img(data.get("sello_director_path"), 4.0*cm, 5.0*cm)
    firma_dir_img    = _img(data.get("firma_director_path"), 4.0*cm, 1.5*cm)

    # -------------------------------------------------------------------------
    # 1. BLOQUE DETALL (Margen izquierdo)
    # -------------------------------------------------------------------------
    # Agrupamos la firma, el nombre y el cargo en una sola celda vertical
    col_firma_detall = [
        firma_detall_img,
        #Paragraph(nombre_jefe, s_sign),
        #Paragraph(cargo_jefe,  s_sign),
    ]

    # Creamos la tabla horizontal: [ Sello | Texto ]
    t_detall = Table(
        [[sello_detall_img, col_firma_detall]],
        colWidths=[4.5*cm, 4.0*cm, 1*cm],
        rowHeights=[3*cm],
        hAlign='LEFT'
    )
    t_detall.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("VALIGN", (1, 0), (1, 0), "BOTTOM"),
        ("ALIGN",  (0, 0), (-1, -1), "LEFT"),
        ("ALIGN",  (1, 0), (1, 0), "LEFT"), # Firma pegada al sello
        ("LEFTPADDING", (0, 0), (0, 0), -1.5*cm), # Eliminar espacio interno
        ("LEFTPADDING", (1, 0), (1, 0), -1.2*cm), # Eliminar espacio interno
    ]))

    elems.append(t_detall)
    
    # Agregamos el espacio vertical equivalente a dos "enters"
    elems.append(Spacer(1, 1.5*cm))

    # -------------------------------------------------------------------------
    # 2. BLOQUE DIRECTOR (Centro - Derecha)
    # -------------------------------------------------------------------------
    # Agrupamos la firma, el nombre y el cargo en una sola celda vertical
    col_firma_dir = [
        firma_dir_img,
       # Paragraph(nombre_dir, s_sign),
       # Paragraph(cargo_dir,  s_sign),
    ]

    # Para centrar el sello y mandar la firma a la derecha, usamos 3 columnas:
    # [ Espacio Vacío (4.5cm) | Sello (6cm) | Firma (6.5cm) ] = 17cm total de hoja
    t_director = Table(
        [[Spacer(5.5*cm, 1*cm), sello_dir_img, col_firma_dir]],
        colWidths=[5.5*cm, 4.3*cm, 0.5*cm],
        hAlign='LEFT'
    )
    t_director.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",  (1, 0), (1, 0), "LEFT"),
        ("ALIGN",  (2, 0), (2, 0), "LEFT"), # Firma pegada al sello
        ("LEFTPADDING", (2, 0), (2, 0), 0), # Eliminar espacio interno
    ]))

    elems.append(t_director)

    # Construir el PDF
    doc.build(elems)