from datetime import date, datetime, time
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


class PdfExportService:
    """
    Servicio de exportación a PDF (.pdf) usando ReportLab.
    Cumple con el diseño, ordenamiento y casos especiales de la rúbrica del Incremento 6.
    """

    @staticmethod
    def exportar(ruta_archivo: str, detalle_jornada: tuple, asistencias: list):
        """
        Genera el documento PDF de asistencia.

        detalle_jornada: (id, fecha, catedra, horario_entrada, horario_salida, nombre_usuario)
        asistencias: lista de tuplas (apellido, nombre, dni, libreta, entrada, salida)
        """
        # Desempaquetar metadatos
        _, fecha_val, catedra, h_entrada, h_salida, usuario_docente = detalle_jornada

        fecha_str = fecha_val.strftime("%d/%m/%Y") if isinstance(fecha_val, (date, datetime)) else str(fecha_val or "")
        
        def _fmt_hora(h):
            if isinstance(h, (time, datetime)):
                return h.strftime("%H:%M")
            return str(h or "")

        entrada_str = _fmt_hora(h_entrada)
        salida_str = _fmt_hora(h_salida)

        # Configuración del documento A4 (595.27 x 841.89 pt)
        doc = SimpleDocTemplate(
            ruta_archivo,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=40,
            bottomMargin=40
        )

        elements = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        style_title = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=18,
            leading=22,
            textColor=colors.HexColor('#1F497D'),
            spaceAfter=15
        )

        style_meta_label = ParagraphStyle(
            'MetaLabel',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#333333')
        )

        style_meta_val = ParagraphStyle(
            'MetaVal',
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#111111')
        )

        style_cell = ParagraphStyle(
            'CellText',
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#222222')
        )

        style_cell_center = ParagraphStyle(
            'CellTextCenter',
            parent=style_cell,
            alignment=1  # Centrado
        )

        style_contador = ParagraphStyle(
            'ContadorFinal',
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#1F497D'),
            spaceBefore=12
        )

        # ── 1. Título ────────────────────────────────────────────────
        elements.append(Paragraph("PLANILLA DE ASISTENCIA", style_title))

        # ── 2. Encabezado de la Jornada (Metadatos) ───────────────────
        meta_data = [
            [Paragraph("Fecha:", style_meta_label), Paragraph(fecha_str, style_meta_val)],
            [Paragraph("Cátedra:", style_meta_label), Paragraph(str(catedra or ""), style_meta_val)],
            [Paragraph("Horario de entrada:", style_meta_label), Paragraph(entrada_str, style_meta_val)],
            [Paragraph("Horario de salida:", style_meta_label), Paragraph(salida_str, style_meta_val)],
            [Paragraph("Usuario:", style_meta_label), Paragraph(str(usuario_docente or ""), style_meta_val)],
        ]

        t_meta = Table(meta_data, colWidths=[120, 400])
        t_meta.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 18))

        # ── 3. Tabla de Alumnos Presentes ────────────────────────────
        # Anchos de columna que suman 520 pt (área imprimible de A4)
        col_widths = [28, 96, 96, 75, 75, 75, 75]
        headers = ["#", "Apellido", "Nombre", "DNI", "Libreta", "Entrada", "Salida"]
        table_rows = [headers]

        total_alumnos = len(asistencias)

        if total_alumnos == 0:
            # Caso especial 7.2: Jornada sin asistencias
            msg_p = Paragraph(
                "<i>No se registraron asistencias para esta Jornada.</i>",
                style_cell_center
            )
            # Fila combinada
            table_rows.append([msg_p, "", "", "", "", "", ""])
            
            t_asist = Table(table_rows, colWidths=col_widths)
            t_asist.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F497D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('SPAN', (0, 1), (-1, 1)),  # Combinar toda la fila de mensaje
                ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
                ('BOTTOMPADDING', (0, 1), (-1, 1), 10),
                ('TOPPADDING', (0, 1), (-1, 1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D9D9D9')),
            ]))
        else:
            for idx, alu in enumerate(asistencias, start=1):
                apellido, nombre, dni, libreta, f_ent, f_sal = alu

                ent_str = f_ent.strftime("%H:%M") if isinstance(f_ent, (datetime, time)) else (str(f_ent) if f_ent else "")
                sal_str = f_sal.strftime("%H:%M") if isinstance(f_sal, (datetime, time)) else ("Sin registrar" if f_sal is None else str(f_sal))

                row = [
                    Paragraph(str(idx), style_cell_center),
                    Paragraph(str(apellido), style_cell),
                    Paragraph(str(nombre), style_cell),
                    Paragraph(str(dni), style_cell_center),
                    Paragraph(str(libreta), style_cell_center),
                    Paragraph(ent_str, style_cell_center),
                    Paragraph(sal_str, style_cell_center),
                ]
                table_rows.append(row)

            t_asist = Table(table_rows, colWidths=col_widths)
            
            t_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F497D')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D9D9D9')),
            ]

            # Fondo cebra alternado para legibilidad
            for r in range(1, len(table_rows)):
                bg = colors.HexColor('#F8F9FA') if r % 2 == 0 else colors.white
                t_style.append(('BACKGROUND', (0, r), (-1, r), bg))

            t_asist.setStyle(TableStyle(t_style))

        elements.append(t_asist)
        elements.append(Spacer(1, 14))

        # ── 4. Contador Final con Singular y Plural ───────────────────
        if total_alumnos == 0:
            texto_contador = "0 alumnos presentes."
        elif total_alumnos == 1:
            texto_contador = "Se registró 1 alumno presente en total."
        else:
            texto_contador = f"Se registraron {total_alumnos} alumnos presentes en total."

        elements.append(Paragraph(texto_contador, style_contador))

        # Construir el PDF
        doc.build(elements)
