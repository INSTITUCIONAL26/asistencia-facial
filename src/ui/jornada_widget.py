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
        self.setStyleSheet("background-color: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(0)

        # Título
        title = QLabel("Configuración de la Jornada")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: white; margin-bottom: 24px; background-color: transparent;"
        )
        outer.addWidget(title)

        # Card contenedor
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

        # ── Fecha (solo lectura) ─────────────────────────────────────
        fecha_label = QLabel(date.today().strftime("%d/%m/%Y"))
        fecha_label.setStyleSheet("font-size: 14px; color: white; padding: 6px 0; border: none;")
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
        label.setStyleSheet("font-size: 14px; color: #a0a0a0; border: none;")
        label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        row.addWidget(label)
        row.addWidget(widget)
        row.addStretch()
        layout.addLayout(row)

    @staticmethod
    def _input_style():
        """Estilo base para QLineEdit."""
        return (
            "padding: 7px 10px;"
            "font-size: 14px;"
            "color: white;"
            "border: 1px solid #555;"
            "border-radius: 4px;"
            "background-color: transparent;"
        )

    @staticmethod
    def _time_edit_style():
        """Estilo para QTimeEdit con chevrons nativos simulados."""
        return """
            QTimeEdit {
                padding: 7px 10px;
                font-size: 14px;
                color: white;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: transparent;
            }
            QTimeEdit::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                border: none;
                background-color: transparent;
            }
            QTimeEdit::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                border: none;
                background-color: transparent;
            }
            QTimeEdit::up-arrow {
                image: url(src/ui/assets/chevron-up.svg);
                width: 16px;
                height: 16px;
            }
            QTimeEdit::down-arrow {
                image: url(src/ui/assets/chevron-down.svg);
                width: 16px;
                height: 16px;
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
