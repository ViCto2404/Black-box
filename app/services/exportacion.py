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
    get_detalle_feedback
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

def _get_pdf_base(buffer, title, subtitle, usuario_actual="ADMIN---UNPHU", report_code="ACAD---RPT"):
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
             Paragraph(f"Cód: {report_code}", styles["Normal"])
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

def _add_academic_summary(story, styles, periodo):
    """
    Agrega una sección de resumen académico al final de los reportes PDF.
    """
    if not periodo:
        periodos = get_periodos()
        if not periodos:
            return
        periodo = periodos[0]

    resumen = get_resumen_periodo(periodo)
    rendimiento = get_rendimiento_por_materia(periodo)
    
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("<b>Resumen académico del Periodo</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))

    # Cálculo de materias críticas (reprobación > 30%)
    materias_criticas = 0
    if rendimiento:
        for r in rendimiento:
            if r.get("porcentaje_reprobacion", 0) > 30:
                materias_criticas += 1

    resumen_data = [
        ["Total de estudiantes analizados", str(resumen.get("total_estudiantes", 0))],
        ["Total de materias del periodo", str(len(rendimiento)) if rendimiento else "0"],
        ["Índice de aprobación global", f"{resumen.get('indice_aprobacion', 0):.2f}%"],
        ["Cantidad de materias críticas", str(materias_criticas)],
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
        
        # Analizar aspectos_evaluar para clasificar
        aspectos = f.get("aspectos_evaluar", "").upper()
        if "QUEJA" in aspectos:
            quejas += 1
        elif "SUGERENCIA" in aspectos:
            sugerencias += 1

    cant_participantes = len(participantes_unicos)

    # 2. % de participación
    # get_masa_estudiantil(codigo_carrera) devuelve lista de dicts por carrera
    masa = get_masa_estudiantil(codigo_carrera)
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
            ("Total secciones analizadas",   resumen.get("total_secciones_analizadas", 0)),
            ("Secciones en estado crítico",  resumen.get("secciones_criticas", 0)),
            ("Promedio general",             resumen.get("promedio_general", 0)),
            ("Índice de aprobación",         f"{resumen.get('indice_aprobacion', 0)}%"),
        ]
        for i, (label, value) in enumerate(filas, start=4):
            ws.write(i, 0, label, fmt["label"]); ws.write(i, 1, value, fmt["value"])
    return buffer.getvalue()

def exportar_resumen_periodo_pdf(periodo: str, usuario_actual: str = "ADMIN---UNPHU"):
    resumen = get_resumen_periodo(periodo)
    buffer = BytesIO()
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Reporte de Resumen Académico", 
        f"Periodo: {periodo}", 
        usuario_actual,
        "ACAD---RES---RPT"
    )
    
    story.append(Paragraph("<b>Indicadores Generales</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    data = [
        ["Indicador", "Valor"],
        ["Total secciones analizadas",   str(resumen.get("total_secciones_analizadas", 0))],
        ["Secciones en estado crítico",  str(resumen.get("secciones_criticas", 0))],
        ["Promedio general",             str(resumen.get("promedio_general", 0))],
        ["Índice de aprobación",         f"{resumen.get('indice_aprobacion', 0)}%"],
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

def exportar_rendimiento_pdf(periodo: str, usuario_actual: str = "ADMIN---UNPHU"):
    rendimiento = get_rendimiento_por_materia(periodo)
    buffer = BytesIO()
    
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Reporte de Desempeño Académico", 
        f"Al {periodo}", 
        usuario_actual,
        "ACAD---PER---RPT"
    )

    story.append(Paragraph("<b>Detalle de Rendimiento por Asignatura</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    if not rendimiento:
        story.append(Paragraph("No hay datos disponibles.", styles["Normal"]))
    else:
        data = [["Código", "Materia", "Estudiante\nActivos", "Promedio\ngeneral", "%Aprobación", "Estado"]]
        
        total_estudiantes = 0
        materias_criticas = 0
        suma_aprobacion = 0

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
            
            total_estudiantes += r["total_estudiantes"]
            suma_aprobacion += r['porcentaje_aprobacion']
            if r.get("porcentaje_reprobacion", 0) > 30:
                materias_criticas += 1

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

def exportar_materias_criticas_pdf(periodo: str, usuario_actual: str = "ADMIN---UNPHU"):
    criticas = get_materias_criticas(periodo)
    buffer = BytesIO()
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Detalle de Materias Críticas", 
        f"Periodo: {periodo}", 
        usuario_actual,
        "ACAD---CRI---RPT"
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
    masa = get_masa_estudiantil(periodo)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        wb = writer.book
        fmt = _get_excel_formats(wb)
        if not masa:
            ws = wb.add_worksheet("Masa Estudiantil"); ws.write("A1", "No hay datos"); return buffer.getvalue()
        df = pd.DataFrame(masa)
        df.columns = ["Código carrera", "Carrera", "Activos", "Inactivos", "Total"]
        df.to_excel(writer, sheet_name="Masa Estudiantil", index=False, startrow=1)
        ws = writer.sheets["Masa Estudiantil"]
        ws.set_column("A:A", 15); ws.set_column("B:B", 40); ws.set_column("C:E", 15)
        ws.write("A1", "Detalle de masa estudiantil", fmt["title"])
        for col_num, col_name in enumerate(df.columns): ws.write(1, col_num, col_name, fmt["header"])
    return buffer.getvalue()

def exportar_masa_estudiantil_pdf(periodo: str, usuario_actual: str = "ADMIN---UNPHU"):
    masa = get_masa_estudiantil(periodo)
    buffer = BytesIO()
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Detalle de Masa Estudiantil", 
        f"Periodo: {periodo}", 
        usuario_actual,
        "ACAD---MAS---RPT"
    )

    story.append(Paragraph("<b>Distribución de Estudiantes por Carrera</b>", styles["Normal"]))
    story.append(Spacer(1, 0.1*inch))

    if not masa:
        story.append(Paragraph("No hay datos disponibles.", styles["Normal"]))
    else:
        data = [["Carrera", "Activos", "Inactivos", "Total"]]
        for m in masa:
            data.append([m["nombre_carrera"][:40], str(m["activos"]), str(m["inactivos"]), str(m["total"])])
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
        # Seleccionar solo las columnas necesarias para el Excel
        df = df[["fecha_envio", "codigo_carrera", "aspectos_evaluar", "es_anonimo_str", "comentario"]]
        df.columns = ["Fecha", "Carrera", "Tipo de queja", "Anónimo", "Comentario"]
        df.to_excel(writer, sheet_name="Feedback", index=False, startrow=1)
        ws = writer.sheets["Feedback"]
        ws.set_column("A:A", 20); ws.set_column("B:B", 15); ws.set_column("C:C", 25); ws.set_column("D:D", 10); ws.set_column("E:E", 50)
        ws.write("A1", "Detalle de Feedback Estudiantil", fmt["title"])
        for col_num, col_name in enumerate(df.columns): ws.write(1, col_num, col_name, fmt["header"])
    return buffer.getvalue()

def exportar_feedback_pdf(codigo_carrera: str = None, usuario_actual: str = "ADMIN---UNPHU", periodo: str = None):
    feedback = get_detalle_feedback(codigo_carrera)
    buffer = BytesIO()
    doc, story, styles = _get_pdf_base(
        buffer, 
        "Detalle de Feedback Estudiantil", 
        f"Carrera: {codigo_carrera if codigo_carrera else 'Todas'}", 
        usuario_actual,
        "ACAD---FDB---RPT"
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

# --- Consolidado (Legacy support) ---

def exportar_excel(periodo: str):
    return exportar_resumen_periodo_excel(periodo)

def exportar_pdf(periodo: str) -> bytes:
    return exportar_resumen_periodo_pdf(periodo)
