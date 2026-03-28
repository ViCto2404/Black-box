import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from app.services.analisis import(
    get_resumen_periodo,
    get_rendimiento_por_materia,
    get_materias_criticas,
    get_masa_estudiantil
)

def exportar_excel(periodo: str):
    resumen = get_resumen_periodo(periodo)
    rendimiento = get_rendimiento_por_materia(periodo)
    criticas = get_materias_criticas(periodo)
    masa = get_masa_estudiantil(periodo)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        wb = writer.book

        fmt_header = wb.add_format({
            "bold": True, "bg_color": "#1A55C2E", "font_color":"#FFFFFF", 
            "border":1, "align": "center", "valing": "vcenter"
        })

        fmt_title = wb.add_format({
            "bold": True, "font-size": 14, "font-color": "#1A5C2E"
        })

        fmt_label = wb.add_format({"bold": True, "font_color": "#444441"})
        fmt_value = wb.add_format({"align": "left"})
        fmt_red   = wb.add_format({
            "bg_color": "#FAECE7", "font_color": "#712B13", "border": 1
        })
        fmt_green = wb.add_format({
            "bg_color": "#EAF3DE", "font_color": "#27500A", "border": 1
        })
        fmt_cell  = wb.add_format({"border": 1, "align": "center"})

        ws1 = writer.sheets.get("Resumen") or wb.add_worksheet("Resumen")
        writer.sheets["Resumen"] = ws1
        ws1.set_column("A:A", 35)
        ws1.set_column("B:B", 20)

        ws1.write("A1", f"Reporte Académico — Periodo {periodo}", fmt_title)
        ws1.write("A2", f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}", fmt_value)
        ws1.write("A4", "Indicador", fmt_header)
        ws1.write("B4", "Valor", fmt_header)

        filas_resumen = [
            ("Total estudiantes analizados", resumen.get("total_estudiantes_analizados", 0)),
            ("Total materias",               resumen.get("total_materias", 0)),
            ("Índice de aprobación global",  f"{resumen.get('indice_aprobacion_global', 0)}%"),
            ("Materias críticas",            resumen.get("cantidad_materias_criticas", 0)),
        ]
        for i, (label, value) in enumerate(filas_resumen, start=4):
            ws1.write(i, 0, label, fmt_label)
            ws1.write(i, 1, value, fmt_value)

        if rendimiento:
            df_rend = pd.DataFrame(rendimiento)
            df_rend = df_rend[[
                "codigo_materia", "nombre_materia", "codigo_carrera",
                "total_estudiantes", "promedio",
                "porcentaje_aprobacion", "porcentaje_reprobacion"
            ]]
            df_rend.columns = [
                "Código", "Materia", "Carrera",
                "Total estudiantes", "Promedio",
                "% Aprobación", "% Reprobación"
            ]
            df_rend.to_excel(writer, sheet_name="Rendimiento", index=False, startrow=1)
            ws2 = writer.sheets["Rendimiento"]
            ws2.set_column("A:A", 12)
            ws2.set_column("B:B", 35)
            ws2.set_column("C:G", 18)
            ws2.write("A1", f"Rendimiento por materia — Periodo {periodo}", fmt_title)
            for col_num, col_name in enumerate(df_rend.columns):
                ws2.write(1, col_num, col_name, fmt_header)
            # Colorear filas críticas
            for row_num, row in enumerate(df_rend.itertuples(), start=2):
                fmt = fmt_red if row._7 > 30 else fmt_green
                ws2.write(row_num, 5, row._6, fmt)
                ws2.write(row_num, 6, row._7, fmt)

        # ── Hoja 3: Materias críticas ────────────────────────────────
        if criticas:
            df_crit = pd.DataFrame(criticas)
            df_crit = df_crit[[
                "codigo_materia", "nombre_materia",
                "total_estudiantes", "promedio",
                "porcentaje_aprobacion", "porcentaje_reprobacion"
            ]]
            df_crit.columns = [
                "Código", "Materia",
                "Total estudiantes", "Promedio",
                "% Aprobación", "% Reprobación"
            ]
            df_crit.to_excel(writer, sheet_name="Materias Críticas", index=False, startrow=1)
            ws3 = writer.sheets["Materias Críticas"]
            ws3.set_column("A:A", 12)
            ws3.set_column("B:B", 35)
            ws3.set_column("C:F", 18)
            ws3.write("A1", f"Materias con reprobación > 30% — Periodo {periodo}", fmt_title)
            for col_num, col_name in enumerate(df_crit.columns):
                ws3.write(1, col_num, col_name, fmt_header)

        # ── Hoja 4: Masa estudiantil ─────────────────────────────────
        if masa:
            df_masa = pd.DataFrame(masa)
            df_masa.columns = [
                "Código carrera", "Carrera",
                "Activos", "Inactivos", "Total"
            ]
            df_masa.to_excel(writer, sheet_name="Masa Estudiantil", index=False, startrow=1)
            ws4 = writer.sheets["Masa Estudiantil"]
            ws4.set_column("A:A", 15)
            ws4.set_column("B:B", 40)
            ws4.set_column("C:E", 15)
            ws4.write("A1", "Masa estudiantil por carrera", fmt_title)
            for col_num, col_name in enumerate(df_masa.columns):
                ws4.write(1, col_num, col_name, fmt_header)

    return buffer.getvalue()

def exportar_pdf(periodo: str) -> bytes:
    resumen     = get_resumen_periodo(periodo)
    criticas    = get_materias_criticas(periodo)
    rendimiento = get_rendimiento_por_materia(periodo)

    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=letter,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story  = []

    verde  = colors.HexColor("#1A5C2E")
    blanco = colors.white
    rojo   = colors.HexColor("#FAECE7")
    verde_claro = colors.HexColor("#EAF3DE")

    # Título
    story.append(Paragraph(
        f"<font color='#1A5C2E'><b>Reporte Académico UNPHU</b></font>",
        styles["Title"]
    ))
    story.append(Paragraph(
        f"Periodo: {periodo} — Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        styles["Normal"]
    ))
    story.append(Spacer(1, 0.3*inch))

    # Resumen ejecutivo
    story.append(Paragraph("<b>Resumen ejecutivo</b>", styles["Heading2"]))
    story.append(Spacer(1, 0.1*inch))

    data_resumen = [
        ["Indicador", "Valor"],
        ["Total estudiantes analizados", str(resumen.get("total_estudiantes_analizados", 0))],
        ["Total materias",               str(resumen.get("total_materias", 0))],
        ["Índice de aprobación global",  f"{resumen.get('indice_aprobacion_global', 0)}%"],
        ["Materias críticas",            str(resumen.get("cantidad_materias_criticas", 0))],
    ]
    tabla_resumen = Table(data_resumen, colWidths=[4*inch, 2.5*inch])
    tabla_resumen.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  verde),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  blanco),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#AAAAAA")),
        ("PADDING",     (0, 0), (-1, -1), 8),
    ]))
    story.append(tabla_resumen)
    story.append(Spacer(1, 0.3*inch))

    # Rendimiento por materia
    if rendimiento:
        story.append(Paragraph("<b>Rendimiento por materia</b>", styles["Heading2"]))
        story.append(Spacer(1, 0.1*inch))

        data_rend = [["Materia", "Total", "Promedio", "% Aprobación", "% Reprobación"]]
        for r in rendimiento:
            data_rend.append([
                r["nombre_materia"],
                str(r["total_estudiantes"]),
                str(r["promedio"]),
                f"{r['porcentaje_aprobacion']}%",
                f"{r['porcentaje_reprobacion']}%",
            ])

        tabla_rend = Table(data_rend, colWidths=[2.5*inch, 0.8*inch, 0.9*inch, 1.1*inch, 1.2*inch])
        style_rend = [
            ("BACKGROUND",  (0, 0), (-1, 0),  verde),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  blanco),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 9),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#AAAAAA")),
            ("PADDING",     (0, 0), (-1, -1), 6),
            ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ]
        # Colorear filas críticas en rojo
        for i, r in enumerate(rendimiento, start=1):
            if r["porcentaje_reprobacion"] > 30:
                style_rend.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FAECE7")))
            else:
                style_rend.append(("BACKGROUND", (0, i), (-1, i),
                    colors.white if i % 2 == 0 else colors.HexColor("#F5F5F5")))

        tabla_rend.setStyle(TableStyle(style_rend))
        story.append(tabla_rend)
        story.append(Spacer(1, 0.3*inch))

    # Materias críticas
    if criticas:
        story.append(Paragraph(
            "<b>Materias críticas</b> <font color='#993C1D'>(reprobación &gt; 30%)</font>",
            styles["Heading2"]
        ))
        story.append(Spacer(1, 0.1*inch))

        data_crit = [["Materia", "Promedio", "% Reprobación"]]
        for c in criticas:
            data_crit.append([
                c["nombre_materia"],
                str(c["promedio"]),
                f"{c['porcentaje_reprobacion']}%"
            ])

        tabla_crit = Table(data_crit, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
        tabla_crit.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0),  verde),
            ("TEXTCOLOR",   (0, 0), (-1, 0),  blanco),
            ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("BACKGROUND",  (0, 1), (-1, -1), colors.HexColor("#FAECE7")),
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#AAAAAA")),
            ("PADDING",     (0, 0), (-1, -1), 6),
            ("ALIGN",       (1, 0), (-1, -1), "CENTER"),
        ]))
        story.append(tabla_crit)

    doc.build(story)
    return buffer.getvalue()