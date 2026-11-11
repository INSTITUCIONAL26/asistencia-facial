"""
Test de validación del Paso 5:
Verifica los servicios de exportación (Excel, PDF) y el widget de informes para secretaría.
"""
import sys
import os
import tempfile
from datetime import datetime, date, time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'src'))

from PySide6.QtWidgets import QApplication
from services.excel_export_service import ExcelExportService
from services.pdf_export_service import PdfExportService
from repositories.informe_repository import InformeRepository
from ui.informes_widget import InformesWidget


def test_paso5():
    app = QApplication.instance() or QApplication(sys.argv)

    print("=" * 60)
    print("VALIDACIÓN INDUSTRIAL - PASO 5 (INFORMES Y EXPORTACIÓN)")
    print("=" * 60)

    # Datos mock representativos del IES N.º 7 Populorum Progressio
    registros_mock = [
        {
            "asistencia_id": 1,
            "docente_id": 10,
            "legajo": "DOC-101",
            "docente_nombre": "Gómez, Carlos",
            "carrera_nombre": "Tecnicatura Superior en Desarrollo de Software",
            "actividad_nombre": "Programación Visual",
            "tipo_actividad": "clase",
            "rol_mesa": None,
            "fecha": date.today(),
            "horario_previsto_entrada": time(18, 30),
            "horario_previsto_salida": time(19, 50),
            "hora_marcada_entrada": datetime.now(),
            "estado_entrada": "en_horario",
            "minutos_tardanza": 0,
            "hora_marcada_salida": datetime.now(),
            "estado_salida": "normal",
            "minutos_anticipada": 0,
            "observaciones": "Marcación biométrica normal",
        },
        {
            "asistencia_id": 2,
            "docente_id": 11,
            "legajo": "DOC-102",
            "docente_nombre": "Mamani, Elena",
            "carrera_nombre": "Tecnicatura Superior en Desarrollo de Software",
            "actividad_nombre": "Bases de Datos II",
            "tipo_actividad": "clase",
            "rol_mesa": None,
            "fecha": date.today(),
            "horario_previsto_entrada": time(19, 50),
            "horario_previsto_salida": time(21, 10),
            "hora_marcada_entrada": datetime.now(),
            "estado_entrada": "tardanza",
            "minutos_tardanza": 8,
            "hora_marcada_salida": datetime.now(),
            "estado_salida": "anticipada",
            "minutos_anticipada": 10,
            "observaciones": "Llegó con demora y salida temprana",
        },
        {
            "asistencia_id": 3,
            "docente_id": 12,
            "legajo": "DOC-103",
            "docente_nombre": "Torres, Raúl",
            "carrera_nombre": "Tecnicatura Superior en Enfermería",
            "actividad_nombre": "Mesa de Examen Final",
            "tipo_actividad": "mesa_examen",
            "rol_mesa": "presidente",
            "fecha": date.today(),
            "horario_previsto_entrada": time(8, 30),
            "horario_previsto_salida": time(11, 30),
            "hora_marcada_entrada": datetime.now(),
            "estado_entrada": "en_horario",
            "minutos_tardanza": 0,
            "hora_marcada_salida": None,
            "estado_salida": "sin_salida",
            "minutos_anticipada": 0,
            "observaciones": "Mesa de examen - Salida pendiente de revisión",
        },
    ]

    # 1. Probar ExcelExportService
    print("\n1. Probando ExcelExportService...")
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f_excel:
        ruta_excel = f_excel.name

    try:
        ExcelExportService.exportar_informe(
            ruta_archivo=ruta_excel,
            registros=registros_mock,
            filtros_desc="Prueba Automatizada Paso 5",
            operador_nombre="Admin Test",
        )
        assert os.path.exists(ruta_excel), "El archivo Excel no fue generado"
        tam_excel = os.path.getsize(ruta_excel)
        assert tam_excel > 1000, f"El archivo Excel es sospechosamente pequeño: {tam_excel} bytes"
        print(f"   [OK] Planilla Excel generada exitosamente ({tam_excel} bytes)")
    finally:
        if os.path.exists(ruta_excel):
            os.remove(ruta_excel)

    # 2. Probar PdfExportService
    print("\n2. Probando PdfExportService...")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f_pdf:
        ruta_pdf = f_pdf.name

    try:
        PdfExportService.exportar_informe(
            ruta_archivo=ruta_pdf,
            registros=registros_mock,
            filtros_desc="Prueba Automatizada Paso 5",
            operador_nombre="Admin Test",
        )
        assert os.path.exists(ruta_pdf), "El archivo PDF no fue generado"
        tam_pdf = os.path.getsize(ruta_pdf)
        assert tam_pdf > 1000, f"El archivo PDF es sospechosamente pequeño: {tam_pdf} bytes"
        print(f"   [OK] Informe oficial PDF generado exitosamente ({tam_pdf} bytes)")
    finally:
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)

    # 3. Probar InformesWidget
    print("\n3. Probando InformesWidget (Interfaz de Secretaría)...")
    widget = InformesWidget(usuario_id=1)
    assert widget.tabla.columnCount() == 8, "La tabla debe tener 8 columnas"
    assert widget.btn_excel is not None, "Debe tener botón de exportar Excel"
    assert widget.btn_pdf is not None, "Debe tener botón de exportar PDF"
    print("   [OK] InformesWidget inicializado con filtros y dashboard de KPIs")

    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS DEL PASO 5 PASARON EXITOSAMENTE (100%)")
    print("=" * 60)


if __name__ == "__main__":
    test_paso5()
