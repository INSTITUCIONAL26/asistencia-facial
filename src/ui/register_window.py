"""
Ventana de Registro de Operadores del Sistema.
IES N.º 7 Populorum Progressio
"""
from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from PySide6.QtCore import Qt
from repositories.user_repository import UserRepository
import psycopg


class RegisterWindow(QWidget):
    """
    Registro de nuevo personal administrativo para operar la mesa de entrada.
    """

    def __init__(self):
        super().__init__()
        self.repo = UserRepository()
        self.setWindowTitle("IES N.º 7 Populorum Progressio - Registro de Operador")
        self.resize(380, 440)
        self.setStyleSheet("""
            QWidget {
                background-color: #111424;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
        """)

        lbl_inst = QLabel("IES N.º 7 POPULORUM PROGRESSIO")
        lbl_inst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_inst.setStyleSheet("color: #3498db; font-size: 11px; font-weight: bold; letter-spacing: 1.5px;")

        lbl_titulo = QLabel("Nuevo Operador de Mesa")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold; margin-bottom: 6px;")

        # Inputs
        self.username_input = self._crear_input("Nombre de usuario (*)")
        self.password_input = self._crear_input("Contraseña (*)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.email_input = self._crear_input("Correo electrónico institucional")
        self.dni_input = self._crear_input("DNI")
        self.cuil_input = self._crear_input("CUIL")

        self.register_button = QPushButton("Registrar Operador")
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                padding: 11px;
                font-weight: bold;
                border-radius: 6px;
                font-size: 14px;
                border: none;
                margin-top: 8px;
            }
            QPushButton:hover { background-color: #0b5ed7; }
        """)
        self.register_button.clicked.connect(self.registrar_usuario)

        layout = QVBoxLayout()
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(12)

        layout.addWidget(lbl_inst)
        layout.addWidget(lbl_titulo)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.dni_input)
        layout.addWidget(self.cuil_input)
        layout.addWidget(self.register_button)
        layout.addStretch()
        self.setLayout(layout)

    def _crear_input(self, placeholder: str) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet("""
            QLineEdit {
                background-color: #1a1e36;
                color: #ffffff;
                padding: 9px 12px;
                font-size: 13px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
            QLineEdit:focus { border: 1px solid #3498db; }
        """)
        return inp

    def registrar_usuario(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        email = self.email_input.text().strip() or None
        dni = self.dni_input.text().strip() or None
        cuil = self.cuil_input.text().strip() or None

        if not username or not password:
            QMessageBox.warning(self, "Campos obligatorios", "El nombre de usuario y la contraseña son obligatorios.")
            return

        try:
            self.repo.create_user(username, email, dni, cuil, password)
            QMessageBox.information(self, "Éxito", f"Operador '{username}' registrado correctamente.")
            self.close()
        except psycopg.IntegrityError:
            QMessageBox.critical(self, "Error", "El usuario, correo, DNI o CUIL ya se encuentran registrados.")
        except Exception as e:
            QMessageBox.critical(self, "Error inesperado", str(e))
