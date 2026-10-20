from datetime import date, datetime, time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from repositories.informe_repository import InformeRepository
from services.excel_export_service import ExcelExportService, generar_nombre_sugerido
from services.pdf_export_service import PdfExportService


class InformesWidget(QWidget):
    """
    Vista de Exportar Informes de Asistencia.
    Lista todas las Jornadas del usuario autenticado ordenadas por fecha y hora descendente,
    permitiendo exportar cada una a formato Excel (.xlsx) o PDF (.pdf).
    """

    def __init__(self, usuario_id: int):
        super().__init__()
        self.usuario_id = usuario_id
        self.repo = InformeRepository()

        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(20)

        # ── Encabezado / Título ─────────────────────────────────────
        title_card = QFrame()
        title_card.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        title_layout = QVBoxLayout(title_card)
        title_layout.setContentsMargins(36, 18, 36, 18)
        title = QLabel("Exportar Informes de Asistencia")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: none;")
        subtitle = QLabel("Consulte sus Jornadas registradas y descargue las planillas en formato Excel o PDF.")
        subtitle.setStyleSheet("font-size: 13px; color: #a0a0a0; border: none; margin-top: 4px;")
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        outer.addWidget(title_card)

        # ── Tabla de Jornadas ────────────────────────────────────────
        self.tabla_frame = QFrame()
        self.tabla_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.02);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        tabla_layout = QVBoxLayout(self.tabla_frame)
        tabla_layout.setContentsMargins(20, 20, 20, 20)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Cátedra", "Horario", "Excel", "PDF"])
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.tabla.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabla.setStyleSheet(self._tabla_style())

        # Ajuste de tamaño de columnas
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        self.tabla.setColumnWidth(0, 130)  # Fecha
        self.tabla.setColumnWidth(2, 170)  # Horario (HH:MM - HH:MM)
        self.tabla.setColumnWidth(3, 110)  # Excel
        self.tabla.setColumnWidth(4, 110)  # PDF

        tabla_layout.addWidget(self.tabla)

        # Label de estado vacío
        self.lbl_vacio = QLabel("No se encontraron Jornadas registradas para su usuario.")
        self.lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_vacio.setStyleSheet("font-size: 14px; color: #7f8c8d; padding: 30px; border: none;")
        self.lbl_vacio.hide()
        tabla_layout.addWidget(self.lbl_vacio)

        outer.addWidget(self.tabla_frame)

    def showEvent(self, event):
        """Refresca automáticamente el listado al navegar hacia esta vista."""
        super().showEvent(event)
        self.cargar_jornadas()

    def cargar_jornadas(self):
        """Consulta PostgreSQL y puebla la tabla de Jornadas del usuario."""
        try:
            jornadas = self.repo.obtener_jornadas_por_usuario(self.usuario_id)
        except Exception as e:
            print(f"[InformesWidget] Error consultando jornadas: {e}")
            self.tabla.hide()
            self.lbl_vacio.setText("No se pudo conectar a la base de datos para cargar las Jornadas.")
            self.lbl_vacio.show()
            return

        self.tabla.setRowCount(0)

        if not jornadas:
            self.lbl_vacio.setText("No se encontraron Jornadas registradas para su usuario.")
            self.tabla.hide()
            self.lbl_vacio.show()
            return

        self.lbl_vacio.hide()
        self.tabla.show()
        self.tabla.setRowCount(len(jornadas))

        for row_idx, j in enumerate(jornadas):
            jornada_id, fecha_val, catedra_val, ent_val, sal_val = j

            # Formateo de fecha: DD/MM/YYYY
            fecha_str = fecha_val.strftime("%d/%m/%Y") if isinstance(fecha_val, (date, datetime)) else str(fecha_val or "")

            # Formateo de horario: HH:MM - HH:MM
            def _fmt_hora(h):
                if isinstance(h, (time, datetime)):
                    return h.strftime("%H:%M")
                return str(h or "")

            ent_str = _fmt_hora(ent_val)
            sal_str = _fmt_hora(sal_val)
            horario_str = f"{ent_str} - {sal_str}" if ent_str or sal_str else "-"

            # Item Fecha
            item_fecha = QTableWidgetItem(fecha_str)
            item_fecha.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_fecha.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla.setItem(row_idx, 0, item_fecha)

            # Item Cátedra
            item_catedra = QTableWidgetItem(str(catedra_val or ""))
            item_catedra.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            item_catedra.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla.setItem(row_idx, 1, item_catedra)

            # Item Horario
            item_horario = QTableWidgetItem(horario_str)
            item_horario.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_horario.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabla.setItem(row_idx, 2, item_horario)

            # Botón Acción Excel
            btn_excel = QPushButton("  Excel")
            btn_excel.setIcon(QIcon("src/ui/assets/file-text.svg"))
            btn_excel.setIconSize(QSize(14, 14))
            btn_excel.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_excel.setStyleSheet(self._excel_btn_style())
            btn_excel.clicked.connect(
                lambda _, jid=jornada_id, f=fecha_val, c=catedra_val: self._exportar_excel(jid, f, c)
            )
            self.tabla.setCellWidget(row_idx, 3, self._centrar_widget(btn_excel))

            # Botón Acción PDF
            btn_pdf = QPushButton("  PDF")
            btn_pdf.setIcon(QIcon("src/ui/assets/file-text.svg"))
            btn_pdf.setIconSize(QSize(14, 14))
            btn_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_pdf.setStyleSheet(self._pdf_btn_style())
            btn_pdf.clicked.connect(
                lambda _, jid=jornada_id, f=fecha_val, c=catedra_val: self._exportar_pdf(jid, f, c)
            )
            self.tabla.setCellWidget(row_idx, 4, self._centrar_widget(btn_pdf))

            self.tabla.setRowHeight(row_idx, 52)

    def _exportar_excel(self, jornada_id: int, fecha_val, catedra_val):
        """Flujo de exportación a Excel con diálogo Guardar como."""
        nombre_sugerido = generar_nombre_sugerido(fecha_val, str(catedra_val or ""), "xlsx")

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar planilla de asistencia en Excel",
            nombre_sugerido,
            "Planillas de Excel (*.xlsx)"
        )

        if not ruta:
            # Si el usuario cancela, no generar archivo ni mostrar error
            return

        # Consultar y validar propiedad en PostgreSQL
        detalle = self.repo.obtener_detalle_jornada(jornada_id, self.usuario_id)
        if not detalle:
            QMessageBox.critical(self, "Error de seguridad", "No se encontró la Jornada o no pertenece al usuario autenticado.")
            return

        asistencias = self.repo.obtener_asistencias_jornada(jornada_id, self.usuario_id)

        try:
            ExcelExportService.exportar(ruta, detalle, asistencias)
            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"El archivo Excel fue creado correctamente:\n\n{ruta}"
            )
            from services.voice_service import voice_service
            voice_service.hablar("Planilla de Excel exportada correctamente.", cooldown=2.0)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error de exportación",
                f"Ocurrió un error al generar la planilla Excel:\n{str(e)}"
            )

    def _exportar_pdf(self, jornada_id: int, fecha_val, catedra_val):
        """Flujo de exportación a PDF con diálogo Guardar como."""
        nombre_sugerido = generar_nombre_sugerido(fecha_val, str(catedra_val or ""), "pdf")

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar planilla de asistencia en PDF",
            nombre_sugerido,
            "Documentos PDF (*.pdf)"
        )

        if not ruta:
            return

        detalle = self.repo.obtener_detalle_jornada(jornada_id, self.usuario_id)
        if not detalle:
            QMessageBox.critical(self, "Error de seguridad", "No se encontró la Jornada o no pertenece al usuario autenticado.")
            return

        asistencias = self.repo.obtener_asistencias_jornada(jornada_id, self.usuario_id)

        try:
            PdfExportService.exportar(ruta, detalle, asistencias)
            QMessageBox.information(
                self,
                "Exportación exitosa",
                f"El archivo PDF fue creado correctamente:\n\n{ruta}"
            )
            from services.voice_service import voice_service
            voice_service.hablar("Documento PDF exportado correctamente.", cooldown=2.0)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error de exportación",
                f"Ocurrió un error al generar el documento PDF:\n{str(e)}"
            )

    @staticmethod
    def _centrar_widget(widget: QWidget) -> QWidget:
        """Envuelve un botón en un contenedor centrado para celdas de QTableWidget."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(widget)
        return container

    # ── Estilos Visuales ─────────────────────────────────────────────

    @staticmethod
    def _tabla_style() -> str:
        return """
            QTableWidget {
                background-color: transparent;
                border: none;
                color: white;
                font-size: 13px;
                gridline-color: rgba(255, 255, 255, 0.08);
            }
            QTableWidget::item {
                padding: 6px 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            }
            QHeaderView::section {
                background-color: rgba(255, 255, 255, 0.06);
                color: #bdc3c7;
                font-size: 13px;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #0d6efd;
            }
        """

    @staticmethod
    def _excel_btn_style() -> str:
        return """
            QPushButton {
                background-color: #198754;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #157347;
            }
        """

    @staticmethod
    def _pdf_btn_style() -> str:
        return """
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background-color: #bb2d3b;
            }
        """
