from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class AsistenciaWidget(QWidget):
    """
    Vista de Asistencia por Captura Facial.
    Stub temporal — se implementa en el Paso 4.
    """

    def __init__(self, jornada_widget):
        super().__init__()
        self.jornada_widget = jornada_widget

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("📷  Asistencia por Captura Facial\n(Paso 4 — en desarrollo)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: #555;")
        layout.addWidget(lbl)

        self.setLayout(layout)
