"""
Vista de Gestión de Licencias y Días Particulares.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QComboBox, QDateEdit,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QIcon

from repositories.docente_repository import DocenteRepository
from repositories.licencia_repository import LicenciaRepository


class LicenciasWidget(QWidget):
    """
    Panel administrativo para gestionar:
    - Cupo reglamentario de 6 días particulares anuales por docente (sin certificado).
    - Licencias médicas con seguimiento de certificado (Pendiente -> Confirmada).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.docente_repo = DocenteRepository()
        self.licencia_repo = LicenciaRepository()
        self._build_ui()
        self.recargar_datos()

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(20)

        # 1. Cabecera
        card_header = QFrame()
        card_header.setStyleSheet("background-color: transparent; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);")
        header_layout = QVBoxLayout(card_header)
        header_layout.setContentsMargins(36, 16, 36, 16)
        
        lbl_inst = QLabel("IES N.º 7 POPULORUM PROGRESSIO")
        lbl_inst.setStyleSheet("font-size: 11px; font-weight: bold; color: #3498db; letter-spacing: 1px; border: none;")
        
        title = QLabel("Gestión de Licencias y Días Particulares")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: none;")
        
        header_layout.addWidget(lbl_inst)
        header_layout.addWidget(title)
        main_layout.addWidget(card_header)

        # 2. Formulario de Carga
        form_card = QFrame()
        form_card.setStyleSheet("background-color: #1a1e36; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 20, 24, 20)
        form_layout.setSpacing(16)

        lbl_secc = QLabel("Registrar Licencia / Inasistencia Justificada")
        lbl_secc.setStyleSheet("color: #3498db; font-size: 15px; font-weight: bold; border: none;")
        form_layout.addWidget(lbl_secc)

        grid = QGridLayout()
        grid.setSpacing(14)

        # Combo Docente
        self.cmb_docente = QComboBox()
        self.cmb_docente.setStyleSheet(self._estilo_combo())
        self.cmb_docente.currentIndexChanged.connect(self._actualizar_badge_cupo)

        # Badge de Cupo de Particulares
        self.lbl_cupo = QLabel("Particulares: 6 disponibles de 6")
        self.lbl_cupo.setStyleSheet("""
            background-color: #27ae60;
            color: white;
            font-size: 12px;
            font-weight: bold;
            padding: 6px 14px;
            border-radius: 5px;
        """)

        # Combo Tipo Licencia
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["Día Particular (Sin certificado)", "Licencia Médica (Requiere certificado)"])
        self.cmb_tipo.setStyleSheet(self._estilo_combo())

        # Fechas Desde y Hasta
        self.date_desde = QDateEdit(QDate.currentDate())
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setStyleSheet(self._estilo_date())

        self.date_hasta = QDateEdit(QDate.currentDate())
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setStyleSheet(self._estilo_date())

        # Motivo
        self.txt_motivo = QLineEdit()
        self.txt_motivo.setPlaceholderText("Diagnóstico o motivo de inasistencia...")
        self.txt_motivo.setStyleSheet("""
            QLineEdit {
                background-color: #242946;
                color: #ffffff;
                font-size: 13px;
                padding: 8px 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)

        grid.addWidget(self._crear_label("Docente:"), 0, 0)
        grid.addWidget(self.cmb_docente, 0, 1)
        grid.addWidget(self.lbl_cupo, 0, 2)

        grid.addWidget(self._crear_label("Tipo de Novedad:"), 1, 0)
        grid.addWidget(self.cmb_tipo, 1, 1, 1, 2)

        grid.addWidget(self._crear_label("Fecha Desde:"), 2, 0)
        grid.addWidget(self.date_desde, 2, 1)

        grid.addWidget(self._crear_label("Fecha Hasta:"), 2, 2)
        grid.addWidget(self.date_hasta, 2, 3)

        grid.addWidget(self._crear_label("Motivo / Observación:"), 3, 0)
        grid.addWidget(self.txt_motivo, 3, 1, 1, 3)

        form_layout.addLayout(grid)

        # Botones de Acción
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_guardar = QPushButton("  Registrar Licencia")
        self.btn_guardar.setIcon(QIcon("src/ui/assets/calendar.svg"))
        self.btn_guardar.setIconSize(QSize(16, 16))
        self.btn_guardar.setFixedHeight(40)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #0b5ed7; }
        """)
        self.btn_guardar.clicked.connect(self._guardar_licencia)

        btn_row.addWidget(self.btn_guardar)
        form_layout.addLayout(btn_row)
        main_layout.addWidget(form_card)

        # 3. Grilla de Licencias y Botón de Confirmación Médica
        tabla_card = QFrame()
        tabla_card.setStyleSheet("background-color: #1a1e36; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);")
        tabla_layout = QVBoxLayout(tabla_card)
        tabla_layout.setContentsMargins(20, 16, 20, 16)
        tabla_layout.setSpacing(12)

        tabla_header = QHBoxLayout()
        lbl_tbl_title = QLabel("Historial de Licencias y Certificados Médicos")
        lbl_tbl_title.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        tabla_header.addWidget(lbl_tbl_title)
        tabla_header.addStretch()

        self.btn_confirmar_medico = QPushButton(" Confirmar Presentación de Certificado Médico")
        self.btn_confirmar_medico.setIcon(QIcon("src/ui/assets/check.svg"))
        self.btn_confirmar_medico.setIconSize(QSize(16, 16))
        self.btn_confirmar_medico.setFixedHeight(36)
        self.btn_confirmar_medico.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirmar_medico.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 18px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_confirmar_medico.clicked.connect(self._confirmar_certificado_seleccionado)
        tabla_header.addWidget(self.btn_confirmar_medico)
        tabla_layout.addLayout(tabla_header)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Docente", "Tipo", "Desde", "Hasta", "Estado", "Certificado"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: #111424;
                color: #ffffff;
                gridline-color: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #1a1e36;
                color: #3498db;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
        """)
        tabla_layout.addWidget(self.tabla)
        main_layout.addWidget(tabla_card)

    def recargar_datos(self):
        self.cmb_docente.clear()
        docentes = self.docente_repo.obtener_todos(solo_activos=True)
        for doc in docentes:
            self.cmb_docente.addItem(f"{doc['nombre_completo']} ({doc['legajo']})", doc["id"])
        self._actualizar_badge_cupo()
        self._cargar_tabla()

    def _actualizar_badge_cupo(self):
        docente_id = self.cmb_docente.currentData()
        if not docente_id:
            return
        anio_actual = date.today().year
        disponibles = self.licencia_repo.cupo_particular_disponible(docente_id, anio_actual)
        self.lbl_cupo.setText(f"Particulares {anio_actual}: {disponibles} disponibles de 6")
        if disponibles == 0:
            self.lbl_cupo.setStyleSheet("background-color: #c0392b; color: white; font-size: 12px; font-weight: bold; padding: 6px 14px; border-radius: 5px;")
        elif disponibles <= 2:
            self.lbl_cupo.setStyleSheet("background-color: #e67e22; color: white; font-size: 12px; font-weight: bold; padding: 6px 14px; border-radius: 5px;")
        else:
            self.lbl_cupo.setStyleSheet("background-color: #27ae60; color: white; font-size: 12px; font-weight: bold; padding: 6px 14px; border-radius: 5px;")

    def _cargar_tabla(self):
        self.tabla.setRowCount(0)
        from repositories.informe_repository import InformeRepository
        inf_repo = InformeRepository()
        licencias = inf_repo.obtener_informe_licencias_y_particulares(anio=date.today().year)

        for fila, lic in enumerate(licencias):
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(str(lic["licencia_id"])))
            self.tabla.setItem(fila, 1, QTableWidgetItem(lic["docente_nombre"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(lic["tipo"].upper()))
            self.tabla.setItem(fila, 3, QTableWidgetItem(lic["fecha_desde"].strftime("%d/%m/%Y")))
            self.tabla.setItem(fila, 4, QTableWidgetItem(lic["fecha_hasta"].strftime("%d/%m/%Y")))
            
            estado_item = QTableWidgetItem(lic["estado"].upper())
            if lic["estado"] == "confirmada":
                estado_item.setForeground(Qt.GlobalColor.green)
            elif lic["estado"] == "pendiente":
                estado_item.setForeground(Qt.GlobalColor.yellow)
            else:
                estado_item.setForeground(Qt.GlobalColor.red)
            self.tabla.setItem(fila, 5, estado_item)

            cert_str = "Presentado" if lic["certificado_presentado"] else "No requerido" if lic["tipo"] == "particular" else "Pendiente"
            self.tabla.setItem(fila, 6, QTableWidgetItem(cert_str))

    def _guardar_licencia(self):
        docente_id = self.cmb_docente.currentData()
        if not docente_id:
            QMessageBox.warning(self, "Atención", "Debe seleccionar un docente.")
            return

        tipo = "particular" if self.cmb_tipo.currentIndex() == 0 else "medica"
        f_desde = self.date_desde.date().toPython()
        f_hasta = self.date_hasta.date().toPython()

        if f_hasta < f_desde:
            QMessageBox.warning(self, "Fecha Inválida", "La fecha 'Hasta' no puede ser anterior a 'Desde'.")
            return

        anio = f_desde.year
        # Validar cupo de particulares
        if tipo == "particular":
            disponibles = self.licencia_repo.cupo_particular_disponible(docente_id, anio)
            if disponibles <= 0:
                QMessageBox.critical(
                    self, "Cupo Agotado",
                    "El docente ya ha consumido sus 6 días particulares reglamentarios para este año."
                )
                return

        try:
            self.licencia_repo.crear_licencia(
                docente_id=docente_id,
                tipo=tipo,
                fecha_desde=f_desde,
                fecha_hasta=f_hasta,
                anio=anio,
                motivo=self.txt_motivo.text().strip() or None,
            )
            QMessageBox.information(self, "Éxito", f"Licencia ({tipo.upper()}) registrada correctamente.")
            self.txt_motivo.clear()
            self._actualizar_badge_cupo()
            self._cargar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la licencia:\n{e}")

    def _confirmar_certificado_seleccionado(self):
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Selección Requerida", "Seleccione una licencia médica de la tabla para confirmar la recepción del certificado.")
            return

        lic_id = int(self.tabla.item(fila, 0).text())
        tipo = self.tabla.item(fila, 2).text().lower()

        if tipo != "medica":
            QMessageBox.information(self, "Información", "Los días particulares no requieren presentación de certificado médico.")
            return

        try:
            self.licencia_repo.confirmar_certificado_medico(lic_id, date.today())
            QMessageBox.information(self, "Certificado Confirmado", "La licencia médica ha sido promovida a estado CONFIRMADA tras la entrega del certificado.")
            self._cargar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el certificado:\n{e}")

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
