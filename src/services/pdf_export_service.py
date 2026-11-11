"""
Servicio de Exportación a PDF (.pdf) con ReportLab.
Sistema de Asistencia Docente - IES N.º 7 Populorum Progressio
"""
from datetime import date, datetime, time
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class PdfExportService:
    """
    Genera el informe formal en PDF para presentación a Secretaría y Dirección.
    Diseñado en formato A4 horizontal (Landscape) para máxima legibilidad.
    """

    @staticmethod
    def exportar_informe(
        ruta_archivo: str,
        registros: List[Dict[str, Any]],
        filtros_desc: str = "General",
        operador_nombre: str = "Administración",
    ) -> None:
        doc = SimpleDocTemplate(
            ruta_archivo,
            pagesize=landscape(A4),
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Estilos personalizados
        style_inst = ParagraphStyle(
            "InstHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            textColor=colors.HexColor("#0D3B66"),
            alignment=1, # Centrado
            spaceAfter=2,
        )

        style_titulo = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=colors.HexColor("#333333"),
            alignment=1,
            spaceAfter=6,
        )

        style_meta = ParagraphStyle(
            "MetaText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=colors.HexColor("#666666"),
            alignment=1,
            spaceAfter=12,
        )

        style_cell = ParagraphStyle(
            "CellText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#222222"),
        )

        style_cell_bold = ParagraphStyle(
            "CellTextBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#222222"),
        )

        style_cell_center = ParagraphStyle(
            "CellCenter",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            alignment=1,
        )

        style_cell_header = ParagraphStyle(
            "CellHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            alignment=1,
            textColor=colors.white,
        )

        elementos = []

        # 1. Cabecera Institucional
        elementos.append(Paragraph("IES N.º 7 POPULORUM PROGRESSIO", style_inst))
        elementos.append(Paragraph("INFORME OFICIAL DE ASISTENCIA Y CONTROL HORARIO DOCENTE", style_titulo))
        
        fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")
        meta_str = f"Filtros: {filtros_desc} &nbsp;|&nbsp; Fecha de Emisión: {fecha_emision} &nbsp;|&nbsp; Operador: {operador_nombre}"
        elementos.append(Paragraph(meta_str, style_meta))

        # 2. Tabla de Datos
        headers = [
            Paragraph("Fecha", style_cell_header),
            Paragraph("Legajo", style_cell_header),
            Paragraph("Docente", style_cell_header),
            Paragraph("Cátedra / Actividad", style_cell_header),
            Paragraph("Horario Previsto", style_cell_header),
            Paragraph("Entrada", style_cell_header),
            Paragraph("Estado Entrada", style_cell_header),
            Paragraph("Salida", style_cell_header),
            Paragraph("Estado Salida", style_cell_header),
            Paragraph("Observaciones", style_cell_header),
        ]

        data = [headers]

        for r in registros:
            fecha_str = r["fecha"].strftime("%d/%m/%Y") if isinstance(r["fecha"], (date, datetime)) else str(r["fecha"])
            
            h_prev_in = r["horario_previsto_entrada"].strftime("%H:%M") if r["horario_previsto_entrada"] else "-"
            h_prev_out = r["horario_previsto_salida"].strftime("%H:%M") if r["horario_previsto_salida"] else "-"
            previsto_str = f"{h_prev_in} - {h_prev_out}"

            ent_str = r["hora_marcada_entrada"].strftime("%H:%M") if r["hora_marcada_entrada"] else "-"
            sal_str = r["hora_marcada_salida"].strftime("%H:%M") if r["hora_marcada_salida"] else "Sin Salida"

            # Estado Entrada
            if r["estado_entrada"] == "tardanza":
                est_in_str = f"<font color='#d35400'><b>Tardanza (+{r['minutos_tardanza']}m)</b></font>"
            else:
                est_in_str = "<font color='#27ae60'><b>En Horario</b></font>"

            # Estado Salida
            if r["estado_salida"] == "anticipada":
                est_out_str = f"<font color='#c0392b'><b>Anticipada (-{r['minutos_anticipada']}m)</b></font>"
            elif r["estado_salida"] == "sin_salida":
                est_out_str = "<font color='#7f8c8d'><i>Sin Salida</i></font>"
            else:
                est_out_str = "<font color='#2980b9'><b>Normal</b></font>"

            fila = [
                Paragraph(fecha_str, style_cell_center),
                Paragraph(r["legajo"], style_cell_center),
                Paragraph(r["docente_nombre"], style_cell_bold),
                Paragraph(r["actividad_nombre"], style_cell),
                Paragraph(previsto_str, style_cell_center),
                Paragraph(ent_str, style_cell_center),
                Paragraph(est_in_str, style_cell_center),
                Paragraph(sal_str, style_cell_center),
                Paragraph(est_out_str, style_cell_center),
                Paragraph(r.get("observaciones") or "-", style_cell),
            ]
            data.append(fila)

        # Anchos de columna en Landscape A4 (Total ~ 770 pt)
        col_widths = [55, 55, 120, 130, 75, 55, 80, 55, 75, 70]
        tabla = Table(data, colWidths=col_widths, repeatRows=1)

        t_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D3B66")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D0D0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]

        # Zebra striping
        for i in range(1, len(data)):
            if i % 2 == 0:
                t_style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8F9FA")))

        tabla.setStyle(TableStyle(t_style))
        elementos.append(tabla)
        elementos.append(Spacer(1, 16))

        # 3. Resumen y Firmas
        total_reg = len(registros)
        tardanzas = sum(1 for r in registros if r["estado_entrada"] == "tardanza")
        en_horario = sum(1 for r in registros if r["estado_entrada"] == "en_horario")
        anticipadas = sum(1 for r in registros if r["estado_salida"] == "anticipada")
        sin_salida = sum(1 for r in registros if r["estado_salida"] == "sin_salida")

        resumen_html = (
            f"<b>Resumen Estadístico:</b> &nbsp; Total Clases/Marcaciones: <b>{total_reg}</b> &nbsp;|&nbsp; "
            f"En Horario: <b>{en_horario}</b> &nbsp;|&nbsp; Tardanzas: <b>{tardanzas}</b> &nbsp;|&nbsp; "
            f"Salidas Anticipadas: <b>{anticipadas}</b> &nbsp;|&nbsp; Pendientes de Revisión: <b>{sin_salida}</b>"
        )
        style_resumen = ParagraphStyle("ResumenStyle", parent=styles["Normal"], fontSize=8, textColor=colors.HexColor("#333333"))
        elementos.append(Paragraph(resumen_html, style_resumen))
        elementos.append(Spacer(1, 32))

        # Bloque de Firmas Institucionales
        firmas_data = [
            [
                Paragraph("___________________________________<br/><b>Firma Bedelía / Mesa de Entrada</b>", style_cell_center),
                Paragraph("___________________________________<br/><b>Firma Secretaría Académica</b>", style_cell_center),
            ]
        ]
        tabla_firmas = Table(firmas_data, colWidths=[385, 385])
        tabla_firmas.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elementos.append(KeepTogether(tabla_firmas))

        doc.build(elementos)
