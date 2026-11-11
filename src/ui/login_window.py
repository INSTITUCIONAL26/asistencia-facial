"""
Ventana de Inicio de Sesión Institucional.
IES N.º 7 Populorum Progressio
"""
import os
from PySide6.QtWidgets import (
    QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QLabel, QFrame
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from repositories.user_repository import UserRepository
from ui.main_window import MainWindow
from ui.register_window import RegisterWindow


class LoginWindow(QWidget):
    """
    Control de acceso institucional para el personal de mesa de entrada y bedelía.
    """

    def __init__(self):
        super().__init__()
        self.repo = UserRepository()
        self.main_window = None
        self.register_window = None

        self.setWindowTitle("IES N.º 7 Populorum Progressio - Acceso al Sistema")
        self.resize(440, 360)
        self.setStyleSheet("""
            QWidget {
                background-color: #111424;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
        """)

        # Cabecera institucional
        lbl_siglas = QLabel("IES N.º 7 POPULORUM PROGRESSIO")
        lbl_siglas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_siglas.setStyleSheet("color: #3498db; font-size: 11px; font-weight: bold; letter-spacing: 1.5px;")

        lbl_titulo = QLabel("Sistema de Asistencia Docente")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("color: #ffffff; font-size: 19px; font-weight: bold; margin-bottom: 8px;")

        # Inputs con diseño moderno
        self.identifier_input = QLineEdit()
        self.identifier_input.setPlaceholderText("Usuario / Email / DNI / CUIL")
        self.identifier_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1e36;
                color: #ffffff;
                padding: 10px 14px;
                font-size: 13px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
        """)
        self.identifier_input.returnPressed.connect(self.iniciar_sesion)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1e36;
                color: #ffffff;
                padding: 10px 14px;
                font-size: 13px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
        """)
        self.password_input.returnPressed.connect(self.iniciar_sesion)

        # Iconos de ojito
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_eye = QIcon(os.path.join(base_dir, "assets", "eye.svg"))
        self.icon_eye_off = QIcon(os.path.join(base_dir, "assets", "eye-off.svg"))

        self.toggle_password_action = self.password_input.addAction(
            self.icon_eye,
            QLineEdit.ActionPosition.TrailingPosition
        )
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)

        # Botones
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 11px;
                font-weight: bold;
                border-radius: 6px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover { background-color: #0b5ed7; }
        """)
        self.login_button.clicked.connect(self.iniciar_sesion)

        self.register_button = QPushButton("Crear nuevo operador")
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                padding: 8px;
                font-weight: bold;
                border: 1px solid rgba(52, 152, 219, 0.4);
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: rgba(52, 152, 219, 0.1);
            }
        """)
        self.register_button.clicked.connect(self.abrir_registro)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(14)

        layout.addWidget(lbl_siglas)
        layout.addWidget(lbl_titulo)
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

        if not identificador or not contrasenia:
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
