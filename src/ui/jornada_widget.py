from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class JornadaWidget(QWidget):
    """
    Vista de Configuración de la Jornada.
    Stub temporal — se implementa en el Paso 3.
    """

    def __init__(self, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("⚙️  Configuración de la Jornada\n(Paso 3 — en desarrollo)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 16px; color: #555;")
        layout.addWidget(lbl)

        self.setLayout(layout)

    def esta_configurada(self):
        """
        Retorna True si los parámetros de jornada fueron completados.
        Stub: siempre retorna False hasta que se implemente en el Paso 3.
        """
        return False
