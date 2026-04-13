import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.units import inch
from app.services.analisis import(
    get_periodos,
    get_resumen_periodo,
    get_rendimiento_por_materia,
    get_materias_criticas,
    get_masa_estudiantil,
    get_detalle_feedback,
    get_detalle_materia_secciones
)

# --- Helpers de Formato ---

def _get_excel_formats(wb):
    return {
        "header": wb.add_format({"bold": True, "bg_color": "#1A5C2E", "font_color":"#FFFFFF", "border":1, "align": "center", "valign": "vcenter"}),
        "title": wb.add_format({"bold": True, "font_size": 14, "font_color": "#1A5C2E"}),
        "label": wb.add_format({"bold": True, "font_color": "#444444"}),
        "value": wb.add_format({"align": "left"}),
        "red": wb.add_format({"bg_color": "#FAECE7", "font_color": "#712B13", "border": 1}),
        "green": wb.add_format({"bg_color": "#EAF3DE", "font_color": "#27500A", "border": 1}),
        "cell": wb.add_format({"border": 1, "align": "center"})
    }

def _get_pdf_base(buffer, title, subtitle, usuario_actual="ADMIN---UNPHU", report_code=None):
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Personalización de estilos
    styles["Title"].fontSize = 14
    styles["Title"].alignment = 1  # Centro
    styles["Title"].spaceBefore = 0
    styles["Title"].spaceAfter = 2
    
    story = []

    logo_path = "https://unphu.edu.do/favicon.ico"
    try:
        img = Image(logo_path, 0.8*inch, 0.8*inch)
    except:
        img = Paragraph("LOGO", styles["Normal"])

    # El código de reporte mostrará el código de escuela si se provee, sino uno genérico
    display_code = report_code if report_code else "ACAD---UNPHU---RPT"

    header_data = [
        [img, 
         [
             Paragraph("<b>UNIVERSIDAD NACIONAL PEDRO HENRÍQUEZ UREÑA (UNPHU)</b>", styles["Title"]),
             Paragraph(f"<b>{title}</b>", styles["Normal"]),
             Paragraph(subtitle, styles["Normal"])
         ],
         [
             Paragraph(f"Usuario: {usuario_actual}", styles["Normal"]),
             Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]),
             Paragraph(f"Cód: {display_code}", styles["Normal"])
         ]
        ]
    ]

    header_table = Table(header_data, colWidths=[1.2*inch, 4.0*inch, 2.0*inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*inch))
    
    return doc, story, styles

def _add_academic_summary(story, styles, periodo, codigo_materia=None):
    """
    Agrega una sección de resumen académico al final de los reportes PDF.
    Calcula los datos a partir del rendimiento por materia para garantizar consistencia con las tablas.
    """
    if not periodo:
        return

    # Si es para una materia específica, usamos su detalle de secciones
    if codigo_materia:
        data = get_detalle_materia_secciones(codigo_materia, periodo)
        total_secciones = len(data)
        secciones_criticas = sum(1 for d in data if d["estado"] == "Crítico")
        promedio_general = sum(d["promedio"] for d in data) / total_secciones if total_secciones > 0 else 0
        aprobacion_promedio = sum(d["porcentaje_aprobacion"] for d in data) / total_secciones if total_secciones > 0 else 0
    else:
        # Si es general, lo basamos en el rendimiento por materia (que es lo que muestran las tablas generales)
        rendimiento = get_rendimiento_por_materia(periodo)
        if not rendimiento:
            return
        
        total_secciones = len(rendimiento) # Aquí cada materia cuenta como una unidad de análisis en reportes generales
        secciones_criticas = sum(1 for r in rendimiento if r.get("porcentaje_reprobacion", 0) > 30)
        promedio_general = sum(r["promedio"] for r in rendimiento) / total_secciones if total_secciones > 0 else 0
        aprobacion_promedio = sum(r["porcentaje_aprobacion"] for r in rendimiento) / total_secciones if total_secciones > 0 else 0

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>Resumen académico del Periodo</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))

    resumen_data = [
        ["Total de unidades analizadas", str(total_secciones)],
        ["Unidades en estado crítico", str(secciones_criticas)],
        ["Promedio general", f"{promedio_general:.2f}"],
        ["Índice de aprobación promedio", f"{aprobacion_promedio:.2f}%"],
    ]

    resumen_tab = Table(resumen_data, colWidths=[3 * inch, 1.5 * inch], hAlign='LEFT')
    resumen_tab.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ]))
    story.append(resumen_tab)

def _add_feedback_summary(story, styles, codigo_carrera, feedback_data):
    """
    Calcula y agrega un resumen de feedback al final del reporte PDF.
    """
    if not feedback_data:
        return

    # 1. Estudiantes participantes (ID únicos) y Contadores
    participantes_unicos = set()
    quejas = 0
    sugerencias = 0

    for f in feedback_data:
        # Usar id_estudiante para identificar participación única
        id_est = f.get("id_estudiante")
        if id_est:
            participantes_unicos.add(id_est)
        
        # Analizar 'queja/sugerencia' para clasificar
        tipo = str(f.get("queja/sugerencia", "")).lower()
        if "queja" in tipo:
            quejas += 1
        elif "sugerencia" in tipo:
            sugerencias += 1

    cant_participantes = len(participantes_unicos)

    # 2. % de participación
    # get_masa_estudiantil(codigo_carrera=codigo_carrera) devuelve lista de dicts por carrera
    masa = get_masa_estudiantil(codigo_carrera=codigo_carrera)
    total_estudiantes_masa = sum(m.get("total_general", 0) for m in masa)
    
    porcentaje_participacion = (cant_participantes / total_estudiantes_masa * 100) if total_estudiantes_masa > 0 else 0

    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>Resumen de Feedback</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))

    resumen_data = [
        ["Estudiantes participantes", str(cant_participantes)],
        ["Cantidad de Quejas", str(quejas)],
        ["Cantidad de Sugerencias", str(sugerencias)],
        ["% de participación", f"{porcentaje_participacion:.2f}%"],
    ]

    resumen_tab = Table(resumen_data, colWidths=[3 * inch, 1.5 * inch], hAlign='LEFT')
    resumen_tab.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
    ]))
    story.append(resumen_tab)

# --- Reporte 1: Resumen del periodo académico ---

def exportar_resumen_periodo_excel(periodo: str):
    resumen = get_resumen_periodo(periodo)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        wb = writer.book
        fmt = _get_excel_formats(wb)
        ws = wb.add_worksheet("Resumen")
        ws.set_column("A:A", 35); ws.set_column("B:B", 20)
        ws.write("A1", f"Resumen Académico — Periodo {periodo}", fmt["title"])
        ws.write("A2", f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}", fmt["value"])
        ws.write("A4", "Indicador", fmt["header"]); ws.write("B4", "Valor", fmt["header"])
        filas = [
            ("Total unidades analizadas",   resumen.get("total_secciones_analizadas", 0)),
            ("Unidades en estado crítico",  resumen.get("secciones_criticas", 0)),
            ("Promedio general",             resumen.get("promedio_general", 0)),
            ("Índice de aprobación promedio", f"{resumen.get('indice_aprobacion', 0)}%"),
        ]
        for i, (label, value) in enumerate(filas, start=4):
            ws.write(i, 0, label, fmt["label"]); ws.write(i, 1, value, fmt["value"])
    return buffer.getvalue()

def exportar_resumen_periodo_pdf(periodo: str, usuario_actual: str = "ADMIN---UNPHU", codigo_escuela: str = None):
    resumen = get_resumen_periodo(periodo)
    buffer = BytesIO()
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Reporte de Resumen Académico", 
        f"Periodo: {periodo}", 
        usuario_actual,
        codigo_escuela if codigo_escuela else "ACAD---RES---RPT"
    )
    
    story.append(Paragraph("<b>Indicadores Generales</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    data = [
        ["Indicador", "Valor"],
        ["Total de unidades analizadas", str(resumen.get("total_secciones_analizadas", 0))],
        ["Unidades en estado crítico", str(resumen.get("secciones_criticas", 0))],
        ["Promedio general", f"{resumen.get('promedio_general', 0):.2f}"],
        ["Índice de aprobación promedio", f"{resumen.get('indice_aprobacion', 0):.2f}%"],
    ]
    t = Table(data, colWidths=[4*inch, 2.5*inch], hAlign='CENTER')
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    
    _add_academic_summary(story, styles, periodo)
    
    doc.build(story)
    return buffer.getvalue()

# --- Reporte 2: Rendimiento por asignatura ---

def exportar_rendimiento_excel(periodo: str):
    rendimiento = get_rendimiento_por_materia(periodo)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        wb = writer.book
        fmt = _get_excel_formats(wb)
        if not rendimiento:
            ws = wb.add_worksheet("Rendimiento"); ws.write("A1", "No hay datos"); return buffer.getvalue()
        df = pd.DataFrame(rendimiento)[["codigo_materia", "nombre_materia", "codigo_carrera", "total_estudiantes", "promedio", "porcentaje_aprobacion", "porcentaje_reprobacion"]]
        df.columns = ["Código", "Materia", "Carrera", "Total estudiantes", "Promedio", "% Aprobación", "% Reprobación"]
        df.to_excel(writer, sheet_name="Rendimiento", index=False, startrow=1)
        ws = writer.sheets["Rendimiento"]
        ws.set_column("A:A", 12); ws.set_column("B:B", 35); ws.set_column("C:G", 18)
        ws.write("A1", f"Rendimiento por asignatura — Periodo {periodo}", fmt["title"])
        for col_num, col_name in enumerate(df.columns): ws.write(1, col_num, col_name, fmt["header"])
        for row_num, row in enumerate(df.itertuples(), start=2):
            f_cell = fmt["red"] if row._7 > 30 else fmt["green"]
            ws.write(row_num, 5, row._6, f_cell); ws.write(row_num, 6, row._7, f_cell)
    return buffer.getvalue()

def exportar_rendimiento_pdf(periodo: str, usuario_actual: str = "ADMIN---UNPHU", codigo_escuela: str = None):
    rendimiento = get_rendimiento_por_materia(periodo)
    buffer = BytesIO()
    
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Reporte de Desempeño Académico", 
        f"Al {periodo}", 
        usuario_actual,
        codigo_escuela if codigo_escuela else "ACAD---PER---RPT"
    )

    story.append(Paragraph("<b>Detalle de Rendimiento por Asignatura</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    if not rendimiento:
        story.append(Paragraph("No hay datos disponibles.", styles["Normal"]))
    else:
        data = [["Código", "Materia", "Estudiante\nActivos", "Promedio\ngeneral", "%Aprobación", "Estado"]]
        for r in rendimiento:
            estado_bd = r.get("estado_materia", "N/A")
            data.append([
                r["codigo_materia"],
                r["nombre_materia"][:30],
                str(r["total_estudiantes"]),
                f"{r['promedio']:.2f}",
                f"{r['porcentaje_aprobacion']}%",
                estado_bd
            ])

        t = Table(data, colWidths=[0.8*inch, 2.4*inch, 1.0*inch, 1.0*inch, 1.0*inch, 0.8*inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(t)
        
        _add_academic_summary(story, styles, periodo)

    doc.build(story)
    return buffer.getvalue()

# --- Reporte 3: Detalle de materias críticas ---

def exportar_materias_criticas_excel(periodo: str):
    criticas = get_materias_criticas(periodo)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        wb = writer.book
        fmt = _get_excel_formats(wb)
        if not criticas:
            ws = wb.add_worksheet("Materias Críticas"); ws.write("A1", "No hay datos"); return buffer.getvalue()
        
        df = pd.DataFrame(criticas)[["codigo_materia", "nombre_materia", "codigo_carrera", "total_estudiantes", "promedio", "porcentaje_reprobacion"]]
        df.columns = ["Código", "Materia", "Carrera", "Estudiantes", "Promedio", "% Reprobación"]
        
        df.to_excel(writer, sheet_name="Materias Críticas", index=False, startrow=1)
        ws = writer.sheets["Materias Críticas"]
        ws.set_column("A:A", 12); ws.set_column("B:B", 35); ws.set_column("C:C", 15); ws.set_column("D:F", 18)
        ws.write("A1", f"Detalle de materias críticas — Periodo {periodo}", fmt["title"])
        for col_num, col_name in enumerate(df.columns): ws.write(1, col_num, col_name, fmt["header"])
    return buffer.getvalue()

def exportar_materias_criticas_pdf(periodo: str, usuario_actual: str = "ADMIN---UNPHU", codigo_escuela: str = None):
    criticas = get_materias_criticas(periodo)
    buffer = BytesIO()
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Detalle de Materias Críticas", 
        f"Periodo: {periodo}", 
        usuario_actual,
        codigo_escuela if codigo_escuela else "ACAD---CRI---RPT"
    )

    story.append(Paragraph("<b>Listado de Asignaturas en Estado Crítico</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    if not criticas:
        story.append(Paragraph("No se encontraron materias críticas.", styles["Normal"]))
    else:
        data = [["Código", "Materia", "Carrera", "Cant.", "Prom.", "% Reprob."]]
        for c in criticas:
            data.append([
                c["codigo_materia"],
                c["nombre_materia"][:25],
                c["codigo_carrera"],
                str(c["total_estudiantes"]),
                str(c["promedio"]),
                f"{c['porcentaje_reprobacion']}%"
            ])
        t = Table(data, colWidths=[0.8*inch, 2.2*inch, 1.0*inch, 0.6*inch, 0.8*inch, 1.1*inch], hAlign='CENTER')
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(t)
    
    _add_academic_summary(story, styles, periodo)
    
    doc.build(story)
    return buffer.getvalue()

# --- Reporte 4: Detalle de masa estudiantil ---

def exportar_masa_estudiantil_excel(periodo: str):
    masa = get_masa_estudiantil(periodo=periodo)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        wb = writer.book
        fmt = _get_excel_formats(wb)
        if not masa:
            ws = wb.add_worksheet("Masa Estudiantil"); ws.write("A1", "No hay datos"); return buffer.getvalue()
        df = pd.DataFrame(masa)
        # Ajustamos columnas según lo que devuelve get_masa_estudiantil
        df = df[["codigo_carrera", "nombre_carrera", "total_activos", "total_inactivos", "total_general"]]
        df.columns = ["Código carrera", "Carrera", "Activos", "Inactivos", "Total"]
        
        df.to_excel(writer, sheet_name="Masa Estudiantil", index=False, startrow=1)
        ws = writer.sheets["Masa Estudiantil"]
        ws.set_column("A:A", 15); ws.set_column("B:B", 40); ws.set_column("C:E", 15)
        ws.write("A1", f"Detalle de masa estudiantil — {periodo}", fmt["title"])
        for col_num, col_name in enumerate(df.columns): ws.write(1, col_num, col_name, fmt["header"])
    return buffer.getvalue()

def exportar_masa_estudiantil_pdf(periodo: str, usuario_actual: str = "ADMIN---UNPHU", codigo_escuela: str = None):
    masa = get_masa_estudiantil(periodo=periodo)
    buffer = BytesIO()
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Detalle de Masa Estudiantil", 
        f"Periodo: {periodo}", 
        usuario_actual,
        codigo_escuela if codigo_escuela else "ACAD---MAS---RPT"
    )

    story.append(Paragraph("<b>Distribución de Estudiantes por Carrera</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    if not masa:
        story.append(Paragraph("No hay datos disponibles.", styles["Normal"]))
    else:
        data = [["Carrera", "Activos", "Inactivos", "Total"]]
        for m in masa:
            data.append([
                m["nombre_carrera"][:40], 
                str(m["total_activos"]), 
                str(m["total_inactivos"]), 
                str(m["total_general"])
            ])
        t = Table(data, colWidths=[3.5*inch, 1*inch, 1*inch, 1*inch], hAlign='CENTER')
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(t)
    
    _add_academic_summary(story, styles, periodo)
    
    doc.build(story)
    return buffer.getvalue()

# --- Reporte 5: Detalle de feedback estudiantil ---

def exportar_feedback_excel(codigo_carrera: str = None):
    feedback = get_detalle_feedback(codigo_carrera)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        wb = writer.book
        fmt = _get_excel_formats(wb)
        if not feedback:
            ws = wb.add_worksheet("Feedback"); ws.write("A1", "No hay datos"); return buffer.getvalue()
        df = pd.DataFrame(feedback)
        df = df[["fecha_envio", "codigo_carrera", "aspectos_evaluar", "es_anonimo_str", "comentario"]]
        df.columns = ["Fecha", "Carrera", "Tipo de queja", "Anónimo", "Comentario"]
        df.to_excel(writer, sheet_name="Feedback", index=False, startrow=1)
        ws = writer.sheets["Feedback"]
        ws.set_column("A:A", 20); ws.set_column("B:B", 15); ws.set_column("C:C", 25); ws.set_column("D:D", 10); ws.set_column("E:E", 50)
        ws.write("A1", "Detalle de Feedback Estudiantil", fmt["title"])
        for col_num, col_name in enumerate(df.columns): ws.write(1, col_num, col_name, fmt["header"])
    return buffer.getvalue()

def exportar_feedback_pdf(codigo_carrera: str = None, usuario_actual: str = "ADMIN---UNPHU", codigo_escuela: str = None):
    feedback = get_detalle_feedback(codigo_carrera)
    buffer = BytesIO()
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Detalle de Feedback Estudiantil", 
        f"Carrera: {codigo_carrera if codigo_carrera else 'Todas'}", 
        usuario_actual,
        codigo_escuela if codigo_escuela else "ACAD---FDB---RPT"
    )

    story.append(Paragraph("<b>Comentarios y Evaluaciones Recibidas</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    if not feedback:
        story.append(Paragraph("No hay feedback registrado.", styles["Normal"]))
    else:
        data = [["Fecha", "Carrera", "Aspectos", "Anón.", "Comentario"]]
        for f in feedback:
            fecha = f["fecha_envio"][:10] if f["fecha_envio"] else "N/A"
            data.append([
                fecha,
                f["codigo_carrera"],
                f["aspectos_evaluar"][:20],
                f["es_anonimo_str"],
                Paragraph(f["comentario"][:150], styles["Normal"]) if f["comentario"] else ""
            ])
            
        t = Table(data, colWidths=[0.9*inch, 0.8*inch, 1.5*inch, 0.6*inch, 3.2*inch], hAlign='CENTER')
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
    
    _add_feedback_summary(story, styles, codigo_carrera, feedback)
    
    doc.build(story)
    return buffer.getvalue()

# --- Reporte 6: Detalle por Materia y Secciones ---

def exportar_materia_detalle_excel(codigo_materia: str, periodo: str):
    data = get_detalle_materia_secciones(codigo_materia, periodo)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        wb = writer.book
        fmt = _get_excel_formats(wb)
        if not data:
            ws = wb.add_worksheet("Detalle Materia"); ws.write("A1", "No hay datos"); return buffer.getvalue()
        
        df = pd.DataFrame(data)
        nombre_materia = df["nombre_materia"].iloc[0] if not df.empty else codigo_materia
        
        df = df[["id_seccion_display", "nombre_profesor", "total_estudiantes", "promedio", "porcentaje_aprobacion", "estado"]]
        df.columns = ["Sección", "Profesor", "Estudiantes", "Promedio", "% Aprobación", "Estado"]
        
        df.to_excel(writer, sheet_name="Detalle Materia", index=False, startrow=1)
        ws = writer.sheets["Detalle Materia"]
        ws.set_column("A:A", 12); ws.set_column("B:B", 35); ws.set_column("C:F", 15)
        ws.write("A1", f"Análisis de {nombre_materia} ({codigo_materia}) — {periodo}", fmt["title"])
        for col_num, col_name in enumerate(df.columns): ws.write(1, col_num, col_name, fmt["header"])
        
        for row_num, row in enumerate(df.itertuples(), start=2):
            f_cell = fmt["red"] if row.Estado == "Crítico" else fmt["green"]
            ws.write(row_num, 5, row.Estado, f_cell)
            
    return buffer.getvalue()

def exportar_materia_detalle_pdf(codigo_materia: str, periodo: str, usuario_actual: str = "ADMIN---UNPHU", codigo_escuela: str = None):
    data = get_detalle_materia_secciones(codigo_materia, periodo)
    buffer = BytesIO()
    nombre_materia = data[0]["nombre_materia"] if data else codigo_materia
    
    doc, story, styles = _get_pdf_base(
        buffer, 
        f"Análisis Detallado de Asignatura", 
        f"Materia: {nombre_materia} ({codigo_materia}) | Periodo: {periodo}", 
        usuario_actual,
        codigo_escuela if codigo_escuela else "ACAD---MAT---RPT"
    )

    story.append(Paragraph(f"<b>Desglose por Secciones</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    if not data:
        story.append(Paragraph("No hay información disponible para esta materia.", styles["Normal"]))
    else:
        header = [["Sección", "Profesor", "Cant. Estudiantes", "Prom.", "% Aprob.", "Estado"]]
        rows = []
        for d in data:
            rows.append([
                d["id_seccion_display"],
                d["nombre_profesor"][:30],
                str(d["total_estudiantes"]),
                f"{d['promedio']:.2f}",
                f"{d['porcentaje_aprobacion']}%",
                d["estado"]
            ])
            
        t = Table(header + rows, colWidths=[0.8*inch, 2.0*inch, 1.2*inch, 0.7*inch, 0.9*inch, 0.9*inch], hAlign='CENTER')
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        for i, d in enumerate(data):
            color = colors.red if d["estado"] == "Crítico" else colors.green
            t.setStyle(TableStyle([
                ('TEXTCOLOR', (5, i+1), (5, i+1), color),
                ('FONTNAME', (5, i+1), (5, i+1), 'Helvetica-Bold'),
            ]))
            
        story.append(t)
    
        _add_academic_summary(story, styles, periodo, codigo_materia=codigo_materia)
    
    doc.build(story)
    return buffer.getvalue()

# --- Consolidado (Legacy support) ---

def exportar_excel(periodo: str):
    return exportar_resumen_periodo_excel(periodo)

def exportar_pdf(periodo: str) -> bytes:
    return exportar_resumen_periodo_pdf(periodo)
