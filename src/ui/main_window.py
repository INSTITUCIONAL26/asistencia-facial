from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from ui.asistencia_widget import AsistenciaWidget
from ui.jornada_widget import JornadaWidget
from ui.registrar_alumno_widget import RegistrarAlumnoWidget


class MainWindow(QMainWindow):
    def __init__(self, usuario_id, nombre_usuario):
        super().__init__()
        self.usuario_id = usuario_id
        self.nombre_usuario = nombre_usuario

        self.setWindowTitle(f"Sistema de Asistencia Facial — {nombre_usuario}")
        self.resize(1100, 680)

        # ── Widget central ──────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        # Se elimina el color de fondo para heredar el tema oscuro nativo

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ─────────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet("background-color: rgba(255, 255, 255, 0.03); border-right: 1px solid rgba(255, 255, 255, 0.1);")

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 20)
        sidebar_layout.setSpacing(0)

        # Logo / título del sidebar
        title_label = QLabel("Asistencia\nFacial")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: white;
            font-size: 15px;
            font-weight: bold;
            padding: 28px 10px 24px 10px;
            border: none;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        """)
        sidebar_layout.addWidget(title_label)

        # ── Stack de contenido ──────────────────────────────────────
        # JornadaWidget se crea primero porque AsistenciaWidget lo necesita
        self.jornada_widget = JornadaWidget(usuario_id)
        self.asistencia_widget = AsistenciaWidget(self.jornada_widget)
        self.registrar_alumno_widget = RegistrarAlumnoWidget()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.asistencia_widget)        # índice 0
        self.stack.addWidget(self.jornada_widget)           # índice 1
        self.stack.addWidget(self.registrar_alumno_widget)  # índice 2

        # ── Botones del sidebar ─────────────────────────────────────
        opciones = [
            ("  Captura Facial",      "src/ui/assets/camera.svg",    0),
            ("  Configurar Jornada",  "src/ui/assets/calendar.svg",  1),
            ("  Registrar Alumno",    "src/ui/assets/user-plus.svg", 2),
        ]

        self.sidebar_buttons = []
        for texto, icono_path, indice in opciones:
            btn = QPushButton(texto)
            btn.setIcon(QIcon(icono_path))
            btn.setIconSize(QSize(18, 18))
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(52)
            btn.setStyleSheet(self._estilo_boton(activo=False))
            btn.clicked.connect(lambda _, i=indice: self.cambiar_vista(i))
            self.sidebar_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Usuario en pie del sidebar
        user_label = QLabel(nombre_usuario)
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 8px;")
        user_label.setWordWrap(True)
        sidebar_layout.addWidget(user_label)

        # ── Ensamblado ──────────────────────────────────────────────
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        # Vista por defecto: Captura Facial (índice 0)
        self.cambiar_vista(0)

    # ── Métodos ─────────────────────────────────────────────────────

    def cambiar_vista(self, indice):
        """Cambia el panel de contenido y actualiza el estilo del botón activo."""
        self.stack.setCurrentIndex(indice)
        for i, btn in enumerate(self.sidebar_buttons):
            activo = (i == indice)
            btn.setChecked(activo)
            btn.setStyleSheet(self._estilo_boton(activo=activo))

    @staticmethod
    def _estilo_boton(activo: bool) -> str:
        """Retorna el stylesheet del botón según si está activo o no."""
        if activo:
            return """
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    text-align: left;
                    padding-left: 24px;
                    border: none;
                    border-left: 4px solid #86b7fe;
                }
            """
        return """
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                font-size: 13px;
                font-weight: normal;
                text-align: left;
                padding-left: 28px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
            }
        """
