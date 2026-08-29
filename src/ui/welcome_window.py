from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

class WelcomeWindow(QWidget):
    def __init__(self, nombre_usuario):
        super().__init__()
        self.setWindowTitle("Bienvenido")
        self.resize(400, 200)

        label = QLabel(f"Bienvenido, {nombre_usuario}")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
