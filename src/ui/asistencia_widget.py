from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt


class AsistenciaWidget(QWidget):
    """
    Vista de Asistencia por Captura Facial.

    Controles:
        - Botón toggle Abrir Cámara / Cerrar Cámara.
        - Panel de video (placeholder para el próximo incremento).

    Regla de negocio:
        No se puede abrir la cámara si la Jornada no fue configurada.
        Se valida consultando jornada_widget.esta_configurada().
    """

    # ── Textos del botón toggle ──────────────────────────────────────
    _TEXTO_ABRIR  = "▶   Abrir Cámara"
    _TEXTO_CERRAR = "⏹   Cerrar Cámara"

    def __init__(self, jornada_widget):
        super().__init__()
        self.jornada_widget = jornada_widget
        self._camara_abierta = False
        self._build_ui()

    # ── Construcción de la UI ────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("background-color: #f5f6fa;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(20)

        # Título
        title = QLabel("📷  Asistencia por Captura Facial")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50;"
        )
        outer.addWidget(title)

        # ── Fila de botones ──────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_camara = QPushButton(self._TEXTO_ABRIR)
        self.btn_camara.setFixedHeight(42)
        self.btn_camara.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_camara.setStyleSheet(self._estilo_btn_abrir())
        self.btn_camara.clicked.connect(self._toggle_camara)

        btn_row.addWidget(self.btn_camara)
        btn_row.addStretch()
        outer.addLayout(btn_row)

        # ── Panel de video (placeholder) ─────────────────────────────
        self.panel_video = QFrame()
        self.panel_video.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 8px;
                border: 2px solid #2c3e50;
            }
        """)
        self.panel_video.setMinimumHeight(380)

        # Label interior del panel
        panel_layout = QVBoxLayout(self.panel_video)
        self.lbl_estado_camara = QLabel("[ Cámara cerrada ]")
        self.lbl_estado_camara.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_estado_camara.setStyleSheet(
            "color: #7f8c8d; font-size: 15px; border: none;"
        )
        panel_layout.addWidget(self.lbl_estado_camara)

        outer.addWidget(self.panel_video)

    # ── Slot principal ───────────────────────────────────────────────

    def _toggle_camara(self):
        """Alterna el estado de la cámara con validación de jornada."""
        if not self._camara_abierta:
            self._intentar_abrir_camara()
        else:
            self._cerrar_camara()

    def _intentar_abrir_camara(self):
        """
        Valida que la Jornada esté configurada antes de abrir.
        Si no lo está, muestra alerta y no cambia el estado.
        """
        if not self.jornada_widget.esta_configurada():
            QMessageBox.warning(
                self,
                "Jornada no configurada",
                "Antes de abrir la Cámara del Sistema debe configurarse "
                "los parámetros de la Jornada "
                "(segunda opción del Menú Lateral)."
            )
            return

        # Jornada OK → abrir cámara (lógica real en próximo incremento)
        self._camara_abierta = True
        self.btn_camara.setText(self._TEXTO_CERRAR)
        self.btn_camara.setStyleSheet(self._estilo_btn_cerrar())
        self.lbl_estado_camara.setText("[ Cámara abierta — video en próximo incremento ]")
        self.lbl_estado_camara.setStyleSheet(
            "color: #27ae60; font-size: 15px; border: none;"
        )

    def _cerrar_camara(self):
        """Cierra la cámara y restaura el estado inicial del panel."""
        self._camara_abierta = False
        self.btn_camara.setText(self._TEXTO_ABRIR)
        self.btn_camara.setStyleSheet(self._estilo_btn_abrir())
        self.lbl_estado_camara.setText("[ Cámara cerrada ]")
        self.lbl_estado_camara.setStyleSheet(
            "color: #7f8c8d; font-size: 15px; border: none;"
        )

    # ── Estilos de botón ─────────────────────────────────────────────

    @staticmethod
    def _estilo_btn_abrir():
        return """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """

    @staticmethod
    def _estilo_btn_cerrar():
        return """
            QPushButton {
                background-color: #c0392b;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #a93226;
            }
        """
