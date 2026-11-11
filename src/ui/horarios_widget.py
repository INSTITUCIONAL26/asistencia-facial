"""
Vista de Gestión de Cátedras y Obligaciones Horarias.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from datetime import time, date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QComboBox, QTimeEdit,
    QDateEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QTime, QDate, QSize
from PySide6.QtGui import QIcon

from repositories.docente_repository import DocenteRepository
from repositories.horario_repository import HorarioRepository


class HorariosWidget(QWidget):
    """
    Panel administrativo para planificar y asignar:
    - Clases Regulares de 1 hora y 20 minutos reloj (80 min).
    - Mesas de Examen con asignación de roles (Presidente, Vocal, Auxiliar).
    - Jornadas Institucionales.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.docente_repo = DocenteRepository()
        self.horario_repo = HorarioRepository()
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
        
        title = QLabel("Planificación de Cátedras y Obligaciones Horarias")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: none;")
        
        header_layout.addWidget(lbl_inst)
        header_layout.addWidget(title)
        main_layout.addWidget(card_header)

        # 2. Formulario de Asignación
        form_card = QFrame()
        form_card.setStyleSheet("background-color: #1a1e36; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);")
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(24, 20, 24, 20)
        form_layout.setSpacing(16)

        lbl_secc = QLabel("Asignar Nueva Obligación Horaria")
        lbl_secc.setStyleSheet("color: #3498db; font-size: 15px; font-weight: bold; border: none;")
        form_layout.addWidget(lbl_secc)

        grid = QGridLayout()
        grid.setSpacing(14)

        # Combo Docente
        self.cmb_docente = QComboBox()
        self.cmb_docente.setStyleSheet(self._estilo_combo())

        # Combo Tipo Actividad
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["Clase Regular (1h 20m)", "Mesa de Examen", "Jornada Institucional"])
        self.cmb_tipo.setStyleSheet(self._estilo_combo())
        self.cmb_tipo.currentIndexChanged.connect(self._on_tipo_actividad_cambiado)

        # Carrera y Cátedra
        self.cmb_carrera = QComboBox()
        self.cmb_carrera.setStyleSheet(self._estilo_combo())
        self.cmb_carrera.currentIndexChanged.connect(self._on_carrera_cambiada)

        self.cmb_catedra = QComboBox()
        self.cmb_catedra.setStyleSheet(self._estilo_combo())

        # Día de la semana o Fecha específica
        self.cmb_dia = QComboBox()
        self.cmb_dia.addItems(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"])
        self.cmb_dia.setStyleSheet(self._estilo_combo())

        self.date_especifica = QDateEdit(QDate.currentDate())
        self.date_especifica.setCalendarPopup(True)
        self.date_especifica.setStyleSheet(self._estilo_date())
        self.date_especifica.setEnabled(False)

        # Rol de Mesa
        self.cmb_rol_mesa = QComboBox()
        self.cmb_rol_mesa.addItems(["Ninguno", "Presidente", "Vocal", "Auxiliar"])
        self.cmb_rol_mesa.setStyleSheet(self._estilo_combo())
        self.cmb_rol_mesa.setEnabled(False)

        # Horarios (Entrada y Salida)
        self.time_entrada = QTimeEdit(QTime(18, 30))
        self.time_entrada.setStyleSheet(self._estilo_date())
        self.time_entrada.timeChanged.connect(self._auto_calcular_fin_clase)

        self.time_salida = QTimeEdit(QTime(19, 50))
        self.time_salida.setStyleSheet(self._estilo_date())

        # Añadir al grid
        grid.addWidget(self._crear_label("Docente Titular:"), 0, 0)
        grid.addWidget(self.cmb_docente, 0, 1)

        grid.addWidget(self._crear_label("Tipo de Actividad:"), 0, 2)
        grid.addWidget(self.cmb_tipo, 0, 3)

        grid.addWidget(self._crear_label("Carrera:"), 1, 0)
        grid.addWidget(self.cmb_carrera, 1, 1)

        grid.addWidget(self._crear_label("Cátedra / Materia:"), 1, 2)
        grid.addWidget(self.cmb_catedra, 1, 3)

        grid.addWidget(self._crear_label("Día de la Semana:"), 2, 0)
        grid.addWidget(self.cmb_dia, 2, 1)

        grid.addWidget(self._crear_label("Fecha (Mesa/Jornada):"), 2, 2)
        grid.addWidget(self.date_especifica, 2, 3)

        grid.addWidget(self._crear_label("Horario de Inicio:"), 3, 0)
        grid.addWidget(self.time_entrada, 3, 1)

        grid.addWidget(self._crear_label("Horario de Fin (80m):"), 3, 2)
        grid.addWidget(self.time_salida, 3, 3)

        grid.addWidget(self._crear_label("Rol en Mesa:"), 4, 0)
        grid.addWidget(self.cmb_rol_mesa, 4, 1)

        form_layout.addLayout(grid)

        # Botón Guardar
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_guardar = QPushButton("  Asignar Horario al Docente")
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
        self.btn_guardar.clicked.connect(self._guardar_obligacion)
        btn_row.addWidget(self.btn_guardar)
        form_layout.addLayout(btn_row)

        main_layout.addWidget(form_card)

        # 3. Grilla / Tabla de Obligaciones Registradas
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(7)
        self.tabla.setHorizontalHeaderLabels([
            "Docente", "Tipo", "Cátedra / Actividad", "Carrera", "Día / Fecha", "Horario", "Rol Mesa"
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

    def _auto_calcular_fin_clase(self, qtime_in: QTime):
        """Para clases regulares, auto-calcula los 80 minutos reglamentarios."""
        if self.cmb_tipo.currentIndex() == 0: # Clase regular
            fin = qtime_in.addSecs(80 * 60)
            self.time_salida.setTime(fin)

    def _on_tipo_actividad_cambiado(self, index: int):
        if index == 0:  # Clase regular
            self.cmb_dia.setEnabled(True)
            self.date_especifica.setEnabled(False)
            self.cmb_rol_mesa.setEnabled(False)
            self.cmb_carrera.setEnabled(True)
            self.cmb_catedra.setEnabled(True)
            self._auto_calcular_fin_clase(self.time_entrada.time())
        elif index == 1:  # Mesa de Examen
            self.cmb_dia.setEnabled(False)
            self.date_especifica.setEnabled(True)
            self.cmb_rol_mesa.setEnabled(True)
            self.cmb_carrera.setEnabled(True)
            self.cmb_catedra.setEnabled(True)
        else:  # Jornada Institucional
            self.cmb_dia.setEnabled(False)
            self.date_especifica.setEnabled(True)
            self.cmb_rol_mesa.setEnabled(False)
            self.cmb_carrera.setEnabled(False)
            self.cmb_catedra.setEnabled(False)

    def _on_carrera_cambiada(self):
        carrera_id = self.cmb_carrera.currentData()
        self.cmb_catedra.clear()
        if carrera_id:
            catedras = self.horario_repo.obtener_catedras(carrera_id)
            for cat in catedras:
                self.cmb_catedra.addItem(cat["nombre"], cat["id"])

    def recargar_datos(self):
        """Carga los docentes, carreras y la grilla de horarios."""
        # Cargar docentes
        self.cmb_docente.clear()
        docentes = self.docente_repo.obtener_todos(solo_activos=True)
        for doc in docentes:
            self.cmb_docente.addItem(f"{doc['nombre_completo']} ({doc['legajo']})", doc["id"])

        # Cargar carreras
        self.cmb_carrera.clear()
        carreras = self.horario_repo.obtener_carreras()
        for car in carreras:
            self.cmb_carrera.addItem(car["nombre"], car["id"])

        self._on_carrera_cambiada()
        self._cargar_tabla()

    def _cargar_tabla(self):
        """Carga todas las obligaciones en la tabla."""
        self.tabla.setRowCount(0)
        docentes = self.docente_repo.obtener_todos(solo_activos=False)

        fila = 0
        for doc in docentes:
            obligaciones = self.horario_repo.obtener_obligaciones_por_docente(doc["id"])
            for ob in obligaciones:
                self.tabla.insertRow(fila)
                self.tabla.setItem(fila, 0, QTableWidgetItem(doc["nombre_completo"]))
                self.tabla.setItem(fila, 1, QTableWidgetItem(ob["tipo_actividad"].upper()))
                self.tabla.setItem(fila, 2, QTableWidgetItem(ob["catedra_nombre"]))
                self.tabla.setItem(fila, 3, QTableWidgetItem(ob["carrera_nombre"]))

                dia_fecha = ob["fecha_especifica"].strftime("%d/%m/%Y") if ob["fecha_especifica"] else str(ob["dia_semana"]).capitalize()
                self.tabla.setItem(fila, 4, QTableWidgetItem(dia_fecha))
                
                horario_str = f"{ob['horario_entrada'].strftime('%H:%M')} a {ob['horario_salida'].strftime('%H:%M')}"
                self.tabla.setItem(fila, 5, QTableWidgetItem(horario_str))
                
                rol = str(ob["rol_mesa"]).upper() if ob["rol_mesa"] else "-"
                self.tabla.setItem(fila, 6, QTableWidgetItem(rol))
                fila += 1

    def _guardar_obligacion(self):
        docente_id = self.cmb_docente.currentData()
        if not docente_id:
            QMessageBox.warning(self, "Atención", "Debe seleccionar un docente.")
            return

        tipo_idx = self.cmb_tipo.currentIndex()
        tipos_map = {0: "clase", 1: "mesa_examen", 2: "jornada"}
        tipo_actividad = tipos_map[tipo_idx]

        catedra_id = self.cmb_catedra.currentData() if tipo_actividad != "jornada" else None
        
        dias_map = {0: "lunes", 1: "martes", 2: "miercoles", 3: "jueves", 4: "viernes", 5: "sabado"}
        dia_semana = dias_map[self.cmb_dia.currentIndex()] if tipo_actividad == "clase" else None
        
        fecha_especifica = self.date_especifica.date().toPython() if tipo_actividad != "clase" else None

        rol_mesa = self.cmb_rol_mesa.currentText().lower() if tipo_actividad == "mesa_examen" and self.cmb_rol_mesa.currentIndex() > 0 else None

        h_in = time(self.time_entrada.time().hour(), self.time_entrada.time().minute())
        h_out = time(self.time_salida.time().hour(), self.time_salida.time().minute())

        try:
            self.horario_repo.crear_obligacion(
                docente_id=docente_id,
                tipo_actividad=tipo_actividad,
                horario_entrada=h_in,
                horario_salida=h_out,
                catedra_id=catedra_id,
                dia_semana=dia_semana,
                fecha_especifica=fecha_especifica,
                rol_mesa=rol_mesa,
            )
            QMessageBox.information(self, "Éxito", "Obligación horaria asignada correctamente.")
            self._cargar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la obligación horaria:\n{e}")

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
            QDateEdit, QTimeEdit {
                background-color: #242946;
                color: #ffffff;
                font-size: 13px;
                padding: 6px 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """
