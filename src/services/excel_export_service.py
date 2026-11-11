"""
Servicio de Exportación a Excel (.xlsx) con openpyxl.
Sistema de Asistencia Docente - IES N.º 7 Populorum Progressio
"""
from datetime import date, datetime, time
from typing import List, Dict, Any, Optional
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExcelExportService:
    """
    Genera planillas de asistencia docente para Secretaría y Bedelía del IES N.º 7.
    Cruza horarios esperados, marcaciones reales, demoras y salidas anticipadas.
    """

    @staticmethod
    def exportar_informe(
        ruta_archivo: str,
        registros: List[Dict[str, Any]],
        filtros_desc: str = "General",
        operador_nombre: str = "Administración",
    ) -> None:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Asistencia Docente"

        # Paleta institucional IES N.º 7
        COLOR_CABECERA_BG = "0D3B66"   # Azul institucional oscuro
        COLOR_CABECERA_TXT = "FFFFFF"  # Blanco
        COLOR_SUB_BG = "F4F4F6"
        COLOR_ZEBRA = "F9FAFC"
        COLOR_TARDANZA = "FDEED9"      # Naranja suave
        COLOR_ANTICIPADA = "FDE8E8"    # Rojo suave

        font_titulo = Font(name="Calibri", size=15, bold=True, color="0D3B66")
        font_sub = Font(name="Calibri", size=10, italic=True, color="555555")
        font_header = Font(name="Calibri", size=10, bold=True, color=COLOR_CABECERA_TXT)
        font_data = Font(name="Calibri", size=10)
        font_bold = Font(name="Calibri", size=10, bold=True)

        fill_header = PatternFill("solid", fgColor=COLOR_CABECERA_BG)
        fill_zebra = PatternFill("solid", fgColor=COLOR_ZEBRA)
        fill_tardanza = PatternFill("solid", fgColor=COLOR_TARDANZA)
        fill_anticipada = PatternFill("solid", fgColor=COLOR_ANTICIPADA)

        border_thin = Side(border_style="thin", color="D0D0D0")
        border_all = Border(left=border_thin, right=border_thin, top=border_thin, bottom=border_thin)

        # 1. Títulos y Membrete Institucional
        ws["A1"] = "IES N.º 7 POPULORUM PROGRESSIO"
        ws["A1"].font = font_titulo
        ws["A2"] = "SISTEMA DE ASISTENCIA Y CONTROL HORARIO DOCENTE"
        ws["A2"].font = Font(name="Calibri", size=12, bold=True, color="333333")

        fecha_emision = datetime.now().strftime("%d/%m/%Y %H:%M")
        ws["A3"] = f"Filtro aplicado: {filtros_desc} | Emitido: {fecha_emision} | Operador: {operador_nombre}"
        ws["A3"].font = font_sub

        ws.row_dimensions[1].height = 24
        ws.row_dimensions[2].height = 18
        ws.row_dimensions[3].height = 18
        ws.row_dimensions[4].height = 10

        # 2. Encabezados de Columna
        columnas = [
            ("Fecha", 12),
            ("Legajo", 12),
            ("Docente (Apellido, Nombre)", 28),
            ("Carrera", 32),
            ("Cátedra / Actividad", 28),
            ("Tipo", 12),
            ("Horario Previsto", 18),
            ("Entrada", 14),
            ("Estado Entrada", 16),
            ("Salida", 14),
            ("Estado Salida", 16),
            ("Observaciones", 24),
        ]

        row_header = 5
        ws.row_dimensions[row_header].height = 26

        for col_idx, (col_name, _) in enumerate(columnas, start=1):
            cell = ws.cell(row=row_header, column=col_idx, value=col_name)
            cell.font = font_header
            cell.fill = fill_header
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = border_all

        # 3. Filas de Datos
        fila_actual = 6
        for r in registros:
            ws.row_dimensions[fila_actual].height = 20

            fecha_str = r["fecha"].strftime("%d/%m/%Y") if isinstance(r["fecha"], (date, datetime)) else str(r["fecha"])
            
            # Formato de horas
            h_prev_in = r["horario_previsto_entrada"].strftime("%H:%M") if r["horario_previsto_entrada"] else "-"
            h_prev_out = r["horario_previsto_salida"].strftime("%H:%M") if r["horario_previsto_salida"] else "-"
            previsto_str = f"{h_prev_in} - {h_prev_out}"

            ent_str = r["hora_marcada_entrada"].strftime("%H:%M") if r["hora_marcada_entrada"] else "-"
            sal_str = r["hora_marcada_salida"].strftime("%H:%M") if r["hora_marcada_salida"] else "Sin Salida"

            # Estado Entrada
            if r["estado_entrada"] == "tardanza":
                est_in_str = f"Tardanza (+{r['minutos_tardanza']}m)"
            else:
                est_in_str = "En Horario"

            # Estado Salida
            if r["estado_salida"] == "anticipada":
                est_out_str = f"Anticipada (-{r['minutos_anticipada']}m)"
            elif r["estado_salida"] == "sin_salida":
                est_out_str = "Sin Registrar"
            else:
                est_out_str = "Normal"

            valores = [
                fecha_str,
                r["legajo"],
                r["docente_nombre"],
                r["carrera_nombre"],
                r["actividad_nombre"],
                r["tipo_actividad"].upper(),
                previsto_str,
                ent_str,
                est_in_str,
                sal_str,
                est_out_str,
                r.get("observaciones") or "",
            ]

            es_zebra = (fila_actual % 2 == 0)
            fill_fila = fill_zebra if es_zebra else PatternFill(fill_type=None)

            for col_idx, val in enumerate(valores, start=1):
                cell = ws.cell(row=fila_actual, column=col_idx, value=val)
                cell.font = font_data
                cell.border = border_all
                cell.fill = fill_fila

                # Alineaciones
                if col_idx in (1, 2, 6, 7, 8, 9, 10, 11):
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                else:
                    cell.alignment = Alignment(horizontal="left", vertical="center")

                # Resaltar anomalías
                if col_idx == 9 and r["estado_entrada"] == "tardanza":
                    cell.fill = fill_tardanza
                    cell.font = font_bold
                elif col_idx == 11 and r["estado_salida"] in ("anticipada", "sin_salida"):
                    cell.fill = fill_anticipada
                    cell.font = font_bold

            fila_actual += 1

        # 4. Resumen Ejecutivo al Pie
        fila_actual += 1
        ws.cell(row=fila_actual, column=1, value="RESUMEN ESTADÍSTICO DE SECRETARÍA").font = font_bold
        fila_actual += 1

        total_reg = len(registros)
        tardanzas = sum(1 for r in registros if r["estado_entrada"] == "tardanza")
        en_horario = sum(1 for r in registros if r["estado_entrada"] == "en_horario")
        anticipadas = sum(1 for r in registros if r["estado_salida"] == "anticipada")
        sin_salida = sum(1 for r in registros if r["estado_salida"] == "sin_salida")

        resumen_datos = [
            ("Total de Registros Evaluados:", total_reg),
            ("Entradas en Horario:", en_horario),
            ("Entradas con Tardanza:", tardanzas),
            ("Salidas Anticipadas:", anticipadas),
            ("Salidas Sin Registrar (Pendientes):", sin_salida),
        ]

        for etiqueta, cant in resumen_datos:
            ws.cell(row=fila_actual, column=1, value=etiqueta).font = font_data
            ws.cell(row=fila_actual, column=3, value=cant).font = font_bold
            fila_actual += 1

        # Ajuste de ancho de columnas
        for col_idx, (_, ancho) in enumerate(columnas, start=1):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = max(ancho, 12)

        wb.save(ruta_archivo)
