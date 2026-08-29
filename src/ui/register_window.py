from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from repositories.user_repository import UserRepository
import psycopg

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = UserRepository()
        self.setWindowTitle("Crear nuevo usuario")
        self.resize(350, 400)

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de usuario (Obligatorio)")
        self.username_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px;")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña (Obligatorio)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px;")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo electrónico (Opcional)")
        self.email_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px;")

        self.dni_input = QLineEdit()
        self.dni_input.setPlaceholderText("DNI (Opcional)")
        self.dni_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px;")

        self.cuil_input = QLineEdit()
        self.cuil_input.setPlaceholderText("CUIL (Opcional)")
        self.cuil_input.setStyleSheet("padding: 8px; font-size: 14px; border: 1px solid #ccc; border-radius: 4px;")

        # Botón
        self.register_button = QPushButton("Registrar")
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #198754;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #157347;
            }
        """)
        self.register_button.clicked.connect(self.registrar_usuario)

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.dni_input)
        layout.addWidget(self.cuil_input)
        layout.addWidget(self.register_button)
        layout.addStretch()
        
        self.setLayout(layout)

    def registrar_usuario(self):
        usuario = self.username_input.text().strip()
        contra = self.password_input.text().strip()
        
        # Si están vacíos, se convierten en None para que en SQL sean NULL
        correo = self.email_input.text().strip() or None
        dni = self.dni_input.text().strip() or None
        cuil = self.cuil_input.text().strip() or None

        if not usuario or not contra:
            QMessageBox.warning(self, "Datos incompletos", "El nombre de usuario y contraseña son obligatorios.")
            return

        try:
            self.repo.create_user(usuario, correo, dni, cuil, contra)
            QMessageBox.information(self, "Éxito", "Usuario creado correctamente.")
            self.close()
        except psycopg.errors.UniqueViolation:
            QMessageBox.critical(self, "Error", "El usuario, correo, DNI o CUIL ya existe en la base de datos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al guardar: {str(e)}")
