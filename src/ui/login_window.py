import os
from PySide6.QtWidgets import (
    QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from PySide6.QtGui import QIcon
from repositories.user_repository import UserRepository
from ui.main_window import MainWindow
from ui.register_window import RegisterWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = UserRepository()
        self.welcome_window = None
        self.register_window = None

        self.setWindowTitle("Inicio de sesión")
        self.resize(420, 260)

        # Inputs con diseño moderno
        self.identifier_input = QLineEdit()
        self.identifier_input.setPlaceholderText("Usuario / Email / DNI / CUIL")
        self.identifier_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px;")
        self.identifier_input.returnPressed.connect(self.iniciar_sesion)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px;")
        self.password_input.returnPressed.connect(self.iniciar_sesion)
        
        # Cargar los iconos SVG
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_eye = QIcon(os.path.join(base_dir, "assets", "eye.svg"))
        self.icon_eye_off = QIcon(os.path.join(base_dir, "assets", "eye-off.svg"))

        # Agregar la acción del ojito
        self.toggle_password_action = self.password_input.addAction(
            self.icon_eye,
            QLineEdit.ActionPosition.TrailingPosition
        )
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)

        # Botones modernos
        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        self.login_button.clicked.connect(self.iniciar_sesion)

        self.register_button = QPushButton("Crear nuevo usuario")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0d6efd;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #0d6efd;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
        """)
        self.register_button.clicked.connect(self.abrir_registro)

        # Layout sin el texto redundante y con márgenes
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(15)
        
        layout.addWidget(self.identifier_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)
        layout.addStretch()
        self.setLayout(layout)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_action.setIcon(self.icon_eye_off)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_action.setIcon(self.icon_eye)

    def iniciar_sesion(self):
        identificador = self.identifier_input.text().strip()
        contrasenia = self.password_input.text().strip()

        if identificador == "" or contrasenia == "":
            QMessageBox.warning(self, "Datos incompletos", "Ingrese usuario y contraseña.")
            return

        usuario = self.repo.find_by_credentials(identificador, contrasenia)

        if usuario is None:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas.")
            return

        self.main_window = MainWindow(usuario[0], usuario[1])
        self.main_window.show()
        self.close()

    def abrir_registro(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
