"""
Ventana Principal de Navegación del Sistema.
IES N.º 7 Populorum Progressio
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QSizePolicy, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from ui.asistencia_widget import AsistenciaWidget
from ui.registrar_docente_widget import RegistrarDocenteWidget
from ui.horarios_widget import HorariosWidget
from ui.licencias_widget import LicenciasWidget
from ui.informes_widget import InformesWidget


class MainWindow(QMainWindow):
    """
    Ventana contenedora principal con barra de navegación lateral (Sidebar)
    e identidad visual institucional del IES N.º 7 Populorum Progressio.
    """

    def __init__(self, usuario_id: int, nombre_usuario: str):
        super().__init__()
        self.usuario_id = usuario_id
        self.nombre_usuario = nombre_usuario

        self.setWindowTitle("Sistema de Asistencia Docente - IES N.º 7 Populorum Progressio")
        self.resize(1180, 720)

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar Lateral Institucional ---
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #111424;
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 20)
        sidebar_layout.setSpacing(4)

        # Logo / Título del Sidebar
        header_box = QFrame()
        header_box.setStyleSheet("border: none; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding: 18px 10px;")
        h_layout = QVBoxLayout(header_box)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(4)

        lbl_siglas = QLabel("IES N.º 7")
        lbl_siglas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_siglas.setStyleSheet("color: #3498db; font-size: 13px; font-weight: bold; letter-spacing: 2px;")

        lbl_nombre_inst = QLabel("POPULORUM\nPROGRESSIO")
        lbl_nombre_inst.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nombre_inst.setStyleSheet("color: #ffffff; font-size: 15px; font-weight: bold; line-height: 1.2;")

        lbl_sub = QLabel("Asistencia Docente")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_sub.setStyleSheet("color: #7f8c8d; font-size: 11px;")

        h_layout.addWidget(lbl_siglas)
        h_layout.addWidget(lbl_nombre_inst)
        h_layout.addWidget(lbl_sub)
        sidebar_layout.addWidget(header_box)

        # --- Instanciación de Vistas ---
        self.asistencia_widget = AsistenciaWidget(parent=self)
        self.docentes_widget = RegistrarDocenteWidget(parent=self)
        self.horarios_widget = HorariosWidget(parent=self)
        self.licencias_widget = LicenciasWidget(parent=self)
        self.informes_widget = InformesWidget(usuario_id=self.usuario_id)

        # Conectar señales entre vistas: cuando se guarda un nuevo docente, recargar combos
        self.docentes_widget.docente_guardado.connect(self._on_docente_agregado)

        # Stack de contenido
        self.stack = QStackedWidget()
        self.stack.addWidget(self.asistencia_widget)  # Índice 0
        self.stack.addWidget(self.docentes_widget)    # Índice 1
        self.stack.addWidget(self.horarios_widget)    # Índice 2
        self.stack.addWidget(self.licencias_widget)   # Índice 3
        self.stack.addWidget(self.informes_widget)    # Índice 4

        # --- Botones del Sidebar ---
        opciones = [
            ("  Captura Facial",        "src/ui/assets/camera.svg",    0),
            ("  Gestión de Docentes",   "src/ui/assets/user-plus.svg", 1),
            ("  Horarios y Cátedras",   "src/ui/assets/calendar.svg",  2),
            ("  Licencias / Particulares", "src/ui/assets/check.svg", 3),
            ("  Informes y Auditoría",  "src/ui/assets/file-text.svg", 4),
        ]

        self.sidebar_buttons = []
        for texto, icono_path, indice in opciones:
            btn = QPushButton(texto)
            btn.setIcon(QIcon(icono_path))
            btn.setIconSize(QSize(18, 18))
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(50)
            btn.setStyleSheet(self._estilo_boton(activo=False))
            btn.clicked.connect(lambda _, i=indice: self.cambiar_vista(i))
            self.sidebar_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        # Usuario autenticado en pie del sidebar
        user_card = QFrame()
        user_card.setStyleSheet("background-color: rgba(255, 255, 255, 0.03); border-radius: 6px; margin: 0 10px; padding: 6px;")
        uc_layout = QVBoxLayout(user_card)
        uc_layout.setContentsMargins(6, 4, 6, 4)

        lbl_rol = QLabel("Operador de Mesa de Entrada:")
        lbl_rol.setStyleSheet("color: #7f8c8d; font-size: 10px; font-weight: bold;")
        
        lbl_user = QLabel(nombre_usuario)
        lbl_user.setStyleSheet("color: #3498db; font-size: 12px; font-weight: bold;")
        lbl_user.setWordWrap(True)

        uc_layout.addWidget(lbl_rol)
        uc_layout.addWidget(lbl_user)
        sidebar_layout.addWidget(user_card)

        # Ensamblado
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        # Vista por defecto: Captura Facial (Índice 0)
        self.cambiar_vista(0)

    def cambiar_vista(self, indice: int):
        """Cambia el panel de contenido y actualiza el botón activo."""
        self.stack.setCurrentIndex(indice)
        
        # Si entra a Horarios o Licencias, refrescar datos
        if indice == 2:
            self.horarios_widget.recargar_datos()
        elif indice == 3:
            self.licencias_widget.recargar_datos()

        for i, btn in enumerate(self.sidebar_buttons):
            activo = (i == indice)
            btn.setChecked(activo)
            btn.setStyleSheet(self._estilo_boton(activo=activo))

    def _on_docente_agregado(self, docente_id: int):
        """Disparado cuando se enrola un nuevo docente."""
        self.horarios_widget.recargar_datos()
        self.licencias_widget.recargar_datos()
        if hasattr(self.asistencia_widget, 'reconocimiento_thread') and self.asistencia_widget.reconocimiento_thread:
            self.asistencia_widget.reconocimiento_thread.recargar_cache()

    @staticmethod
    def _estilo_boton(activo: bool) -> str:
        if activo:
            return """
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    font-size: 13px;
                    font-weight: bold;
                    text-align: left;
                    padding-left: 20px;
                    border: none;
                    border-left: 4px solid #3498db;
                }
            """
        return """
            QPushButton {
                background-color: transparent;
                color: #bdc3c7;
                font-size: 13px;
                font-weight: normal;
                text-align: left;
                padding-left: 24px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.05);
                color: white;
            }
        """
