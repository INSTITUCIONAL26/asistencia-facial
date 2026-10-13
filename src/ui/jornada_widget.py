from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QLineEdit, QTimeEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QTime, Signal, QSize
from PySide6.QtGui import QIcon

from repositories.jornada_repository import JornadaRepository

class JornadaWidget(QWidget):
    """
    Vista de Configuración de Jornada.
    """
    estado_cambiado = Signal(bool)

    def __init__(self, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id
        self.jornada_repo = JornadaRepository()

        self._entrada_configurada = False
        self._salida_configurada  = False
        
        self.jornada_id = None
        self.en_edicion = True

        self._build_ui()
        self._actualizar_ui_estado()

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(0)

        title = QLabel("Configuración de la Jornada")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: white; margin-bottom: 24px; background-color: transparent;"
        )
        outer.addWidget(title)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(22)

        self.fecha_label = QLabel(date.today().strftime("%d/%m/%Y"))
        self.fecha_label.setStyleSheet("font-size: 14px; color: white; padding: 6px 0; border: none;")
        self._add_row(card_layout, "Fecha", self.fecha_label)

        from PySide6.QtWidgets import QCompleter, QMenu
        self._quick_buttons = []

        # Horario de entrada con botones de acceso rápido
        row_entrada = QHBoxLayout()
        row_entrada.setSpacing(8)

        self.entrada_edit = QTimeEdit()
        self.entrada_edit.setDisplayFormat("HH:mm")
        self.entrada_edit.setSpecialValueText("--:--")
        self.entrada_edit.setTime(self.entrada_edit.minimumTime())
        self.entrada_edit.setFixedWidth(110)
        self.entrada_edit.setStyleSheet(self._time_edit_style())
        self.entrada_edit.timeChanged.connect(self._on_entrada_changed)
        row_entrada.addWidget(self.entrada_edit)

        # Botones rápidos para entrada
        btn_ent_ahora = self._crear_btn_rapido("Ahora", lambda: self.entrada_edit.setTime(QTime.currentTime()))
        btn_ent_08 = self._crear_btn_rapido("08:00", lambda: self.entrada_edit.setTime(QTime(8, 0)))
        btn_ent_18 = self._crear_btn_rapido("18:00", lambda: self.entrada_edit.setTime(QTime(18, 0)))
        for b in [btn_ent_ahora, btn_ent_08, btn_ent_18]:
            row_entrada.addWidget(b)
            self._quick_buttons.append(b)

        row_entrada.addStretch()
        self._add_row(card_layout, "Horario de entrada", row_entrada)

        # Horario de salida con botones de acceso rápido
        row_salida = QHBoxLayout()
        row_salida.setSpacing(8)

        self.salida_edit = QTimeEdit()
        self.salida_edit.setDisplayFormat("HH:mm")
        self.salida_edit.setSpecialValueText("--:--")
        self.salida_edit.setTime(self.salida_edit.minimumTime())
        self.salida_edit.setFixedWidth(110)
        self.salida_edit.setStyleSheet(self._time_edit_style())
        self.salida_edit.timeChanged.connect(self._on_salida_changed)
        row_salida.addWidget(self.salida_edit)

        # Botones rápidos para salida (calcular respecto a entrada o tiempo actual)
        def _set_salida_offset(secs):
            base_time = self.entrada_edit.time() if self._entrada_configurada else QTime.currentTime()
            self.salida_edit.setTime(base_time.addSecs(secs))

        btn_sal_5m = self._crear_btn_rapido("+5 min", lambda: _set_salida_offset(300))
        btn_sal_1h = self._crear_btn_rapido("+1 h", lambda: _set_salida_offset(3600))
        btn_sal_4h = self._crear_btn_rapido("+4 h", lambda: _set_salida_offset(14400))
        for b in [btn_sal_5m, btn_sal_1h, btn_sal_4h]:
            row_salida.addWidget(b)
            self._quick_buttons.append(b)

        row_salida.addStretch()
        self._add_row(card_layout, "Horario de salida", row_salida)

        # Cátedra con buscador inteligente y autocompletado
        row_catedra = QHBoxLayout()
        row_catedra.setSpacing(8)

        self.catedra_input = QLineEdit()
        self.catedra_input.setPlaceholderText("Buscar o escribir cátedra...")
        self.catedra_input.setStyleSheet(self._input_style())
        self.catedra_input.textChanged.connect(self._verificar_cambio_estado)

        materias = [
            "Analítica Web",
            "Reconocimiento Visual",
            "Minería de Datos",
            "Proyectos",
            "Prácticas Profesionalizantes",
            "PNL",
            "Ciberseguridad"
        ]
        completer = QCompleter(materias, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.catedra_input.setCompleter(completer)
        row_catedra.addWidget(self.catedra_input)

        # Botón menú de selección rápida de materias
        btn_sugerencias = QPushButton(" ▾ Materias ")
        btn_sugerencias.setFixedHeight(34)
        btn_sugerencias.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_sugerencias.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: #e0e0e0;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        menu_materias = QMenu(self)
        menu_materias.setStyleSheet("""
            QMenu {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #555;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #0d6efd;
            }
        """)
        for m in materias:
            action = menu_materias.addAction(m)
            action.triggered.connect(lambda checked=False, mat=m: self.catedra_input.setText(mat))

        btn_sugerencias.setMenu(menu_materias)
        row_catedra.addWidget(btn_sugerencias)
        self._quick_buttons.append(btn_sugerencias)

        self._add_row(card_layout, "Cátedra", row_catedra)

        # Botones de Acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_guardar = QPushButton(" Guardar Jornada")
        self.btn_guardar.setIcon(QIcon("src/ui/assets/check.svg"))
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet(self._primary_btn_style())
        self.btn_guardar.clicked.connect(self._guardar_jornada)
        
        self.btn_editar = QPushButton(" Editar Jornada")
        self.btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_editar.setStyleSheet(self._secondary_btn_style())
        self.btn_editar.clicked.connect(self._editar_jornada)
        
        self.btn_terminar = QPushButton(" Terminar Jornada")
        self.btn_terminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_terminar.setStyleSheet(self._danger_btn_style())
        self.btn_terminar.clicked.connect(self._terminar_jornada)

        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_terminar)

        card_layout.addLayout(btn_layout)

        outer.addWidget(card)
        outer.addStretch()

    def _add_row(self, layout, label_text, widget):
        row = QHBoxLayout()
        row.setSpacing(16)
        label = QLabel(label_text)
        label.setFixedWidth(160)
        label.setStyleSheet("font-size: 14px; color: #a0a0a0; border: none;")
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(label)
        if isinstance(widget, QWidget):
            row.addWidget(widget)
        else:
            row.addLayout(widget)
        row.addStretch()
        layout.addLayout(row)

    @staticmethod
    def _input_style():
        return (
            "padding: 7px 10px; font-size: 14px; color: white;"
            "border: 1px solid #555; border-radius: 4px; background-color: transparent;"
        )

    @staticmethod
    def _time_edit_style():
        return """
            QTimeEdit { padding: 7px 10px; font-size: 14px; color: white; border: 1px solid #555; border-radius: 4px; background-color: transparent; }
            QTimeEdit::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 24px; border: none; background-color: transparent; }
            QTimeEdit::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 24px; border: none; background-color: transparent; }
            QTimeEdit::up-arrow { image: url(src/ui/assets/chevron-up.svg); width: 16px; height: 16px; }
            QTimeEdit::down-arrow { image: url(src/ui/assets/chevron-down.svg); width: 16px; height: 16px; }
        """
        
    @staticmethod
    def _primary_btn_style():
        return "QPushButton { background-color: #0d6efd; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; border: none; } QPushButton:hover { background-color: #0b5ed7; }"

    @staticmethod
    def _secondary_btn_style():
        return "QPushButton { background-color: #6c757d; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; border: none; } QPushButton:hover { background-color: #5a6268; }"

    @staticmethod
    def _danger_btn_style():
        return "QPushButton { background-color: #dc3545; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold; border: none; } QPushButton:hover { background-color: #c82333; }"

    def _crear_btn_rapido(self, texto, callback):
        btn = QPushButton(texto)
        btn.setFixedHeight(28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(13, 110, 253, 0.15);
                color: #70a1ff;
                border: 1px solid #0d6efd;
                border-radius: 4px;
                padding: 2px 10px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0d6efd;
                color: white;
            }
            QPushButton:disabled {
                border-color: #444;
                color: #666;
                background-color: transparent;
            }
        """)
        btn.clicked.connect(callback)
        return btn

    def _actualizar_ui_estado(self):
        """Actualiza la interfaz según si está en edición o guardada."""
        self.entrada_edit.setEnabled(self.en_edicion)
        self.salida_edit.setEnabled(self.en_edicion)
        self.catedra_input.setEnabled(self.en_edicion)
        
        for b in getattr(self, '_quick_buttons', []):
            b.setEnabled(self.en_edicion)

        self.btn_guardar.setVisible(self.en_edicion)
        self.btn_editar.setVisible(not self.en_edicion)
        self.btn_terminar.setVisible(not self.en_edicion)

    def _verificar_cambio_estado(self):
        estado_actual = self.esta_configurada()
        if estado_actual != getattr(self, '_ultimo_estado', False):
            self._ultimo_estado = estado_actual
            self.estado_cambiado.emit(estado_actual)

    def _on_entrada_changed(self, time: QTime):
        self._entrada_configurada = time != self.entrada_edit.minimumTime()
        self._verificar_cambio_estado()

    def _on_salida_changed(self, time: QTime):
        self._salida_configurada = time != self.salida_edit.minimumTime()
        self._verificar_cambio_estado()

    def _guardar_jornada(self):
        if not (self._entrada_configurada and self._salida_configurada and self.catedra_input.text().strip()):
            QMessageBox.warning(self, "Error", "Debe completar todos los campos.")
            return

        fecha_str = date.today().isoformat()
        entrada_str = self.entrada_edit.time().toString("HH:mm")
        salida_str = self.salida_edit.time().toString("HH:mm")
        catedra = self.catedra_input.text().strip()

        if self.jornada_id is None:
            self.jornada_id = self.jornada_repo.crear_jornada(fecha_str, entrada_str, salida_str, catedra, self.usuario_id)
        else:
            self.jornada_repo.actualizar_jornada(self.jornada_id, entrada_str, salida_str, catedra)

        self.en_edicion = False
        self._actualizar_ui_estado()
        self._verificar_cambio_estado()
        QMessageBox.information(self, "Éxito", "Jornada guardada correctamente.")

    def _editar_jornada(self):
        self.en_edicion = True
        self._actualizar_ui_estado()
        self._verificar_cambio_estado()

    def _terminar_jornada(self):
        respuesta = QMessageBox.question(
            self, "Terminar Jornada", "¿Está seguro que desea terminar la jornada actual?\nEsto cerrará la sesión sin borrar los registros.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            self.jornada_id = None
            self.en_edicion = True
            
            # Reset UI
            self.entrada_edit.setTime(self.entrada_edit.minimumTime())
            self.salida_edit.setTime(self.salida_edit.minimumTime())
            self.catedra_input.clear()
            
            self._actualizar_ui_estado()
            self._verificar_cambio_estado()

    def esta_configurada(self) -> bool:
        """La jornada se considera configurada solo si no está en edición y tiene ID."""
        return not self.en_edicion and self.jornada_id is not None
