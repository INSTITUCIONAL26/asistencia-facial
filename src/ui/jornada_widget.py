from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTimeEdit, QFrame
)
from PySide6.QtCore import Qt, QTime


class JornadaWidget(QWidget):
    """
    Vista de Configuración de la Jornada.

    Campos:
        - Fecha          : automática del sistema (solo lectura).
        - Horario entrada: QTimeEdit, valor por defecto '--:--'.
        - Horario salida : QTimeEdit, valor por defecto '--:--'.
        - Cátedra        : QLineEdit, valor por defecto vacío.

    Los valores se conservan en memoria mientras la app esté abierta.
    En este incremento la jornada NO se persiste en la base de datos.
    """

    def __init__(self, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id

        # Flags internos: detectan si el usuario modificó cada hora.
        # Se usan porque QTimeEdit con specialValueText("--:--")
        # muestra '--:--' cuando el valor es igual al mínimo (00:00).
        # De este modo 00:00 nunca se confunde con "sin configurar".
        self._entrada_configurada = False
        self._salida_configurada  = False

        self._build_ui()

    # ── Construcción de la UI ────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("background-color: #f5f6fa;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(0)

        # Título
        title = QLabel("📅  Configuración de la Jornada")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 24px;"
        )
        outer.addWidget(title)

        # Card contenedor
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(22)

        # ── Fecha (solo lectura) ─────────────────────────────────────
        fecha_label = QLabel(date.today().strftime("%d/%m/%Y"))
        fecha_label.setStyleSheet("font-size: 14px; color: #2c3e50; padding: 6px 0;")
        self._add_row(card_layout, "Fecha", fecha_label)

        # ── Horario de entrada ───────────────────────────────────────
        self.entrada_edit = QTimeEdit()
        self.entrada_edit.setDisplayFormat("HH:mm")
        self.entrada_edit.setSpecialValueText("--:--")          # se muestra cuando valor == mínimo
        self.entrada_edit.setTime(self.entrada_edit.minimumTime())  # inicia en '--:--'
        self.entrada_edit.setFixedWidth(130)
        self.entrada_edit.setStyleSheet(self._time_edit_style())
        self.entrada_edit.timeChanged.connect(self._on_entrada_changed)
        self._add_row(card_layout, "Horario de entrada", self.entrada_edit)

        # ── Horario de salida ────────────────────────────────────────
        self.salida_edit = QTimeEdit()
        self.salida_edit.setDisplayFormat("HH:mm")
        self.salida_edit.setSpecialValueText("--:--")
        self.salida_edit.setTime(self.salida_edit.minimumTime())
        self.salida_edit.setFixedWidth(130)
        self.salida_edit.setStyleSheet(self._time_edit_style())
        self.salida_edit.timeChanged.connect(self._on_salida_changed)
        self._add_row(card_layout, "Horario de salida", self.salida_edit)

        # ── Cátedra ──────────────────────────────────────────────────
        self.catedra_input = QLineEdit()
        self.catedra_input.setPlaceholderText("Nombre de la cátedra")
        self.catedra_input.setStyleSheet(self._input_style())
        self._add_row(card_layout, "Cátedra", self.catedra_input)

        outer.addWidget(card)
        outer.addStretch()

    # ── Helpers de construcción ──────────────────────────────────────

    def _add_row(self, layout, label_text, widget):
        """Agrega una fila label + control al layout."""
        row = QHBoxLayout()
        row.setSpacing(16)

        label = QLabel(label_text)
        label.setFixedWidth(160)
        label.setStyleSheet("font-size: 14px; color: #636e72;")
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(label)
        row.addWidget(widget)
        row.addStretch()
        layout.addLayout(row)

    @staticmethod
    def _input_style():
        """
        Estilo base para QLineEdit.
        Se fuerza color: #2c3e50 para evitar que el tema oscuro de Windows
        pinte el texto de blanco sobre fondo claro.
        """
        return (
            "padding: 7px 10px;"
            "font-size: 14px;"
            "color: #2c3e50;"
            "border: 1px solid #dfe6e9;"
            "border-radius: 5px;"
            "background-color: #fdfdfd;"
        )

    @staticmethod
    def _time_edit_style():
        """
        Estilo para QTimeEdit.
        Incluye color explícito del texto (fix para tema oscuro de Windows)
        y estilo visible para las flechas de subir/bajar.
        """
        return """
            QTimeEdit {
                padding: 7px 10px;
                font-size: 14px;
                color: #2c3e50;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                background-color: #fdfdfd;
            }
            QTimeEdit::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #dfe6e9;
                background-color: #f0f2f5;
                border-top-right-radius: 5px;
            }
            QTimeEdit::up-button:hover {
                background-color: #dfe6e9;
            }
            QTimeEdit::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #dfe6e9;
                background-color: #f0f2f5;
                border-bottom-right-radius: 5px;
            }
            QTimeEdit::down-button:hover {
                background-color: #dfe6e9;
            }
            QTimeEdit::up-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 6px solid #636e72;
            }
            QTimeEdit::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #636e72;
            }
        """

    # ── Slots ────────────────────────────────────────────────────────

    def _on_entrada_changed(self, time: QTime):
        """Marca el campo como configurado si el valor difiere del mínimo ('--:--')."""
        self._entrada_configurada = time != self.entrada_edit.minimumTime()

    def _on_salida_changed(self, time: QTime):
        self._salida_configurada = time != self.salida_edit.minimumTime()

    # ── API pública ──────────────────────────────────────────────────

    def esta_configurada(self) -> bool:
        """
        Retorna True si los tres parámetros fueron completados con valores
        distintos a los defaults:
            - Horario de entrada distinto de '--:--'
            - Horario de salida  distinto de '--:--'
            - Cátedra no vacía
        """
        catedra_ok = self.catedra_input.text().strip() != ""
        return self._entrada_configurada and self._salida_configurada and catedra_ok
