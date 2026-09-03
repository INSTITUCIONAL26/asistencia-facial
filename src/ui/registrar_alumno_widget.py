from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class RegistrarAlumnoWidget(QWidget):
    """
    Vista de Registrar Alumno.
    Stub temporal — se implementa en el Paso 5.
    """

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("👤  Registrar Alumno\n(Paso 5 — en desarrollo)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: #555;")
        layout.addWidget(lbl)

        self.setLayout(layout)
