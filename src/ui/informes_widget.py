"""
Vista de Informes, Auditoría y Exportación de Asistencia Docente.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from datetime import date, datetime
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QComboBox, QDateEdit,
    QCheckBox, QFileDialog, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QIcon

from repositories.informe_repository import InformeRepository
from repositories.docente_repository import DocenteRepository
from repositories.horario_repository import HorarioRepository
from services.excel_export_service import ExcelExportService
from services.pdf_export_service import PdfExportService
from services.voice_service import voice_service


class InformesWidget(QWidget):
    """
    Panel de auditoría y reportes para Secretaría y Bedelía del IES N.º 7:
    - Filtros por Docente, Carrera, Cátedra, Rango de Fechas y Anomalías.
    - Dashboard de KPIs ejecutivos en tiempo real.
    - Tabla interactiva con cruce automático de horarios previstos vs reales.
    - Exportación a planillas oficiales en Excel (.xlsx) y PDF (.pdf).
    """

    def __init__(self, usuario_id: int = 1, parent=None):
        super().__init__(parent)
        self.usuario_id = usuario_id
        self.informe_repo = InformeRepository()
        self.docente_repo = DocenteRepository()
        self.horario_repo = HorarioRepository()
        self._registros_actuales = []

        self._build_ui()
        self.recargar_filtros()
        self.consultar_informe()

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 36, 60, 36)
        main_layout.setSpacing(16)

        # 1. Cabecera Institucional
        card_header = QFrame()
        card_header.setStyleSheet("background-color: transparent; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);")
        h_layout = QVBoxLayout(card_header)
        h_layout.setContentsMargins(32, 14, 32, 14)
        
        lbl_inst = QLabel("IES N.º 7 POPULORUM PROGRESSIO")
        lbl_inst.setStyleSheet("font-size: 11px; font-weight: bold; color: #3498db; letter-spacing: 1.5px; border: none;")
        
        lbl_title = QLabel("Informes de Asistencia y Auditoría Horaria")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: none;")
        
        h_layout.addWidget(lbl_inst)
        h_layout.addWidget(lbl_title)
        main_layout.addWidget(card_header)

        # 2. Panel de Filtros
        filter_card = QFrame()
        filter_card.setStyleSheet("background-color: #1a1e36; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08);")
        f_layout = QVBoxLayout(filter_card)
        f_layout.setContentsMargins(20, 16, 20, 16)
        f_layout.setSpacing(12)

        grid_filtros = QGridLayout()
        grid_filtros.setSpacing(12)

        self.cmb_docente = QComboBox()
        self.cmb_docente.setStyleSheet(self._estilo_combo())

        self.cmb_carrera = QComboBox()
        self.cmb_carrera.setStyleSheet(self._estilo_combo())
        self.cmb_carrera.currentIndexChanged.connect(self._on_carrera_cambiada)

        self.cmb_catedra = QComboBox()
        self.cmb_catedra.setStyleSheet(self._estilo_combo())

        # Fechas (Por defecto, primer y último día del mes actual)
        hoy = QDate.currentDate()
        primer_dia = QDate(hoy.year(), hoy.month(), 1)
        self.date_desde = QDateEdit(primer_dia)
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setStyleSheet(self._estilo_date())

        self.date_hasta = QDateEdit(hoy)
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setStyleSheet(self._estilo_date())

        self.chk_solo_anomalias = QCheckBox("Solo anomalías (Tardanzas / Salidas anticipadas / Sin salida)")
        self.chk_solo_anomalias.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 12px;")

        grid_filtros.addWidget(self._crear_label("Docente:"), 0, 0)
        grid_filtros.addWidget(self.cmb_docente, 0, 1)

        grid_filtros.addWidget(self._crear_label("Carrera:"), 0, 2)
        grid_filtros.addWidget(self.cmb_carrera, 0, 3)

        grid_filtros.addWidget(self._crear_label("Cátedra:"), 1, 0)
        grid_filtros.addWidget(self.cmb_catedra, 1, 1)

        grid_filtros.addWidget(self._crear_label("Fecha Desde:"), 1, 2)
        grid_filtros.addWidget(self.date_desde, 1, 3)

        grid_filtros.addWidget(self._crear_label("Fecha Hasta:"), 2, 2)
        grid_filtros.addWidget(self.date_hasta, 2, 3)

        grid_filtros.addWidget(self.chk_solo_anomalias, 2, 0, 1, 2)

        f_layout.addLayout(grid_filtros)

        # Botones de Filtrado y Exportación
        actions_row = QHBoxLayout()
        self.btn_filtrar = QPushButton("  Filtrar Planilla")
        self.btn_filtrar.setIcon(QIcon("src/ui/assets/play.svg"))
        self.btn_filtrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_filtrar.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-weight: bold;
                padding: 8px 22px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #0b5ed7; }
        """)
        self.btn_filtrar.clicked.connect(self.consultar_informe)
        actions_row.addWidget(self.btn_filtrar)

        actions_row.addStretch()

        self.btn_excel = QPushButton("  Exportar a Excel (.xlsx)")
        self.btn_excel.setIcon(QIcon("src/ui/assets/file-text.svg"))
        self.btn_excel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_excel.setStyleSheet("""
            QPushButton {
                background-color: #198754;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #157347; }
        """)
        self.btn_excel.clicked.connect(self._exportar_excel)
        actions_row.addWidget(self.btn_excel)

        self.btn_pdf = QPushButton("  Exportar a PDF (.pdf)")
        self.btn_pdf.setIcon(QIcon("src/ui/assets/file-text.svg"))
        self.btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pdf.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #bb2d3b; }
        """)
        self.btn_pdf.clicked.connect(self._exportar_pdf)
        actions_row.addWidget(self.btn_pdf)

        f_layout.addLayout(actions_row)
        main_layout.addWidget(filter_card)

        # 3. Dashboard de Métricas Resumen
        metrics_card = QFrame()
        metrics_card.setStyleSheet("background-color: #111424; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08);")
        m_layout = QHBoxLayout(metrics_card)
        m_layout.setContentsMargins(18, 12, 18, 12)
        m_layout.setSpacing(18)

        self.lbl_m_total = self._crear_kpi("Total Clases", "0", "#3498db")
        self.lbl_m_en_horario = self._crear_kpi("En Horario", "0", "#2ecc71")
        self.lbl_m_tardanzas = self._crear_kpi("Tardanzas", "0", "#f39c12")
        self.lbl_m_anticipadas = self._crear_kpi("Salidas Anticipadas", "0", "#e67e22")
        self.lbl_m_sin_salida = self._crear_kpi("Pendientes Revisión", "0", "#e74c3c")

        m_layout.addLayout(self.lbl_m_total)
        m_layout.addLayout(self.lbl_m_en_horario)
        m_layout.addLayout(self.lbl_m_tardanzas)
        m_layout.addLayout(self.lbl_m_anticipadas)
        m_layout.addLayout(self.lbl_m_sin_salida)
        main_layout.addWidget(metrics_card)

        # 4. Tabla de Registros
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Docente", "Cátedra / Actividad", "Previsto",
            "Entrada", "Estado Entrada", "Salida", "Estado Salida"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: #1a1e36;
                color: #ffffff;
                gridline-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #111424;
                color: #3498db;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """)
        main_layout.addWidget(self.tabla)

    def _crear_kpi(self, titulo: str, valor: str, color_val: str):
        v_box = QVBoxLayout()
        v_box.setSpacing(2)
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet("color: #7f8c8d; font-size: 11px; font-weight: bold;")
        lbl_v = QLabel(valor)
        lbl_v.setStyleSheet(f"color: {color_val}; font-size: 18px; font-weight: bold;")
        v_box.addWidget(lbl_t)
        v_box.addWidget(lbl_v)
        return v_box

    def recargar_filtros(self):
        # Docentes
        self.cmb_docente.clear()
        self.cmb_docente.addItem("Todos los docentes", None)
        docentes = self.docente_repo.obtener_todos(solo_activos=False)
        for doc in docentes:
            self.cmb_docente.addItem(f"{doc['nombre_completo']} ({doc['legajo']})", doc["id"])

        # Carreras
        self.cmb_carrera.clear()
        self.cmb_carrera.addItem("Todas las carreras", None)
        carreras = self.horario_repo.obtener_carreras()
        for car in carreras:
            self.cmb_carrera.addItem(car["nombre"], car["id"])

        self._on_carrera_cambiada()

    def _on_carrera_cambiada(self):
        carrera_id = self.cmb_carrera.currentData()
        self.cmb_catedra.clear()
        self.cmb_catedra.addItem("Todas las cátedras", None)
        catedras = self.horario_repo.obtener_catedras(carrera_id)
        for cat in catedras:
            self.cmb_catedra.addItem(cat["nombre"], cat["id"])

    def consultar_informe(self):
        f_desde = self.date_desde.date().toPython()
        f_hasta = self.date_hasta.date().toPython()
        doc_id = self.cmb_docente.currentData()
        car_id = self.cmb_carrera.currentData()
        cat_id = self.cmb_catedra.currentData()
        solo_anomalias = self.chk_solo_anomalias.isChecked()

        registros = self.informe_repo.obtener_informe_asistencias(
            fecha_desde=f_desde,
            fecha_hasta=f_hasta,
            docente_id=doc_id,
            carrera_id=car_id,
            catedra_id=cat_id,
            solo_anomalias=solo_anomalias,
        )
        self._registros_actuales = registros

        # Actualizar métricas
        total = len(registros)
        en_horario = sum(1 for r in registros if r["estado_entrada"] == "en_horario")
        tardanzas = sum(1 for r in registros if r["estado_entrada"] == "tardanza")
        anticipadas = sum(1 for r in registros if r["estado_salida"] == "anticipada")
        sin_salida = sum(1 for r in registros if r["estado_salida"] == "sin_salida")

        self.lbl_m_total.itemAt(1).widget().setText(str(total))
        self.lbl_m_en_horario.itemAt(1).widget().setText(str(en_horario))
        self.lbl_m_tardanzas.itemAt(1).widget().setText(str(tardanzas))
        self.lbl_m_anticipadas.itemAt(1).widget().setText(str(anticipadas))
        self.lbl_m_sin_salida.itemAt(1).widget().setText(str(sin_salida))

        # Poblar tabla
        self.tabla.setRowCount(0)
        for fila, r in enumerate(registros):
            self.tabla.insertRow(fila)

            f_str = r["fecha"].strftime("%d/%m/%Y") if isinstance(r["fecha"], (date, datetime)) else str(r["fecha"])
            h_prev_in = r["horario_previsto_entrada"].strftime("%H:%M") if r["horario_previsto_entrada"] else "-"
            h_prev_out = r["horario_previsto_salida"].strftime("%H:%M") if r["horario_previsto_salida"] else "-"
            prev_str = f"{h_prev_in} - {h_prev_out}"

            ent_str = r["hora_marcada_entrada"].strftime("%H:%M") if r["hora_marcada_entrada"] else "-"
            sal_str = r["hora_marcada_salida"].strftime("%H:%M") if r["hora_marcada_salida"] else "-"

            self.tabla.setItem(fila, 0, QTableWidgetItem(f_str))
            self.tabla.setItem(fila, 1, QTableWidgetItem(r["docente_nombre"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(r["actividad_nombre"]))
            self.tabla.setItem(fila, 3, QTableWidgetItem(prev_str))
            self.tabla.setItem(fila, 4, QTableWidgetItem(ent_str))

            # Estado Entrada
            item_in = QTableWidgetItem(r["estado_entrada"].upper() if r["estado_entrada"] != "tardanza" else f"TARDANZA (+{r['minutos_tardanza']}m)")
            item_in.setForeground(Qt.GlobalColor.green if r["estado_entrada"] == "en_horario" else Qt.GlobalColor.yellow)
            self.tabla.setItem(fila, 5, item_in)

            self.tabla.setItem(fila, 6, QTableWidgetItem(sal_str))

            # Estado Salida
            if r["estado_salida"] == "anticipada":
                item_out = QTableWidgetItem(f"ANTICIPADA (-{r['minutos_anticipada']}m)")
                item_out.setForeground(Qt.GlobalColor.yellow)
            elif r["estado_salida"] == "sin_salida":
                item_out = QTableWidgetItem("SIN REGISTRAR")
                item_out.setForeground(Qt.GlobalColor.red)
            else:
                item_out = QTableWidgetItem("NORMAL")
                item_out.setForeground(Qt.GlobalColor.green)
            self.tabla.setItem(fila, 7, item_out)

    def _exportar_excel(self):
        if not self._registros_actuales:
            QMessageBox.warning(self, "Sin datos", "No hay registros en la planilla para exportar.")
            return

        fecha_hoy = date.today().strftime("%Y-%m-%d")
        sugerido = f"asistencia_docentes_{fecha_hoy}.xlsx"
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Planilla Excel", sugerido, "Archivos Excel (*.xlsx)")
        if not ruta:
            return

        try:
            ExcelExportService.exportar_informe(
                ruta_archivo=ruta,
                registros=self._registros_actuales,
                filtros_desc=f"{self.date_desde.date().toString('dd/MM/yyyy')} a {self.date_hasta.date().toString('dd/MM/yyyy')}",
            )
            QMessageBox.information(self, "Exportación Exitosa", f"Planilla Excel generada correctamente en:\n{ruta}")
            voice_service.hablar("Planilla Excel exportada exitosamente.", cooldown=2.0)
        except Exception as e:
            QMessageBox.critical(self, "Error de Exportación", f"No se pudo generar el archivo Excel:\n{e}")

    def _exportar_pdf(self):
        if not self._registros_actuales:
            QMessageBox.warning(self, "Sin datos", "No hay registros en la planilla para exportar.")
            return

        fecha_hoy = date.today().strftime("%Y-%m-%d")
        sugerido = f"informe_docentes_{fecha_hoy}.pdf"
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar Informe PDF", sugerido, "Documentos PDF (*.pdf)")
        if not ruta:
            return

        try:
            PdfExportService.exportar_informe(
                ruta_archivo=ruta,
                registros=self._registros_actuales,
                filtros_desc=f"{self.date_desde.date().toString('dd/MM/yyyy')} a {self.date_hasta.date().toString('dd/MM/yyyy')}",
            )
            QMessageBox.information(self, "Exportación Exitosa", f"Informe PDF generado correctamente en:\n{ruta}")
            voice_service.hablar("Informe PDF generado exitosamente.", cooldown=2.0)
        except Exception as e:
            QMessageBox.critical(self, "Error de Exportación", f"No se pudo generar el archivo PDF:\n{e}")

    @staticmethod
    def _crear_label(texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet("color: #bdc3c7; font-size: 13px; font-weight: bold; border: none;")
        return lbl

    @staticmethod
    def _estilo_combo() -> str:
        return """
            QComboBox {
                background-color: #242946;
                color: #ffffff;
                font-size: 13px;
                padding: 6px 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #1a1e36;
                color: white;
                selection-background-color: #0d6efd;
            }
        """

    @staticmethod
    def _estilo_date() -> str:
        return """
            QDateEdit {
                background-color: #242946;
                color: #ffffff;
                font-size: 13px;
                padding: 6px 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """
