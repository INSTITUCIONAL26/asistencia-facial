import cv2
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QImage
from ui.camera_thread import CameraThread

class CamaraDialog(QDialog):
    """
    Ventana flotante (Modal) para capturar la fotografía en tiempo real.
    Reutiliza el CameraThread para la cámara y permite capturar, reintentar o aceptar la foto.
    """
    def __init__(self, titulo="Capturar Fotografía", parent=None):
        super().__init__(parent)
        self.setWindowTitle(titulo)
        self.setFixedSize(600, 550)
        self.setStyleSheet("background-color: #1a1a2e;")
        
        self.camera_thread = None
        self.captured_image_bytes = None
        self.current_qt_image = None
        self._is_review_mode = False
        
        self._build_ui()
        self._iniciar_camara()
        
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- Panel de Video ---
        self.panel_video = QLabel("Iniciando cámara...")
        self.panel_video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.panel_video.setStyleSheet("""
            QLabel {
                background-color: #0f0f1c;
                color: #7f8c8d;
                font-size: 16px;
                border: 2px solid #2c3e50;
                border-radius: 8px;
            }
        """)
        self.panel_video.setMinimumSize(560, 420)
        self.panel_video.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.panel_video)
        
        # --- Controles ---
        self.btn_layout = QHBoxLayout()
        self.btn_layout.setSpacing(10)
        
        # Botón Capturar (Modo En Vivo)
        self.btn_capturar = QPushButton(" Capturar Fotografía")
        self.btn_capturar.setIcon(QIcon("src/ui/assets/camera.svg"))
        self.btn_capturar.setIconSize(QSize(20, 20))
        self.btn_capturar.setFixedHeight(45)
        self.btn_capturar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_capturar.setStyleSheet(self._primary_btn_style())
        self.btn_capturar.clicked.connect(self._capturar_foto)
        
        # Botón Reintentar (Modo Revisión)
        self.btn_reintentar = QPushButton(" Reintentar")
        self.btn_reintentar.setIcon(QIcon("src/ui/assets/trash-2.svg"))
        self.btn_reintentar.setIconSize(QSize(20, 20))
        self.btn_reintentar.setFixedHeight(45)
        self.btn_reintentar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reintentar.setStyleSheet(self._danger_btn_style())
        self.btn_reintentar.clicked.connect(self._reintentar)
        self.btn_reintentar.hide()
        
        # Botón Aceptar (Modo Revisión)
        self.btn_aceptar = QPushButton(" Guardar Foto")
        self.btn_aceptar.setIcon(QIcon("src/ui/assets/check.svg"))
        self.btn_aceptar.setIconSize(QSize(20, 20))
        self.btn_aceptar.setFixedHeight(45)
        self.btn_aceptar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_aceptar.setStyleSheet(self._success_btn_style())
        self.btn_aceptar.clicked.connect(self.accept)
        self.btn_aceptar.hide()
        
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_reintentar)
        self.btn_layout.addWidget(self.btn_capturar)
        self.btn_layout.addWidget(self.btn_aceptar)
        self.btn_layout.addStretch()
        
        layout.addLayout(self.btn_layout)
        
    def _iniciar_camara(self):
        self._is_review_mode = False
        self.btn_capturar.show()
        self.btn_reintentar.hide()
        self.btn_aceptar.hide()
        
        if self.camera_thread is None:
            self.camera_thread = CameraThread(camera_index=0)
            self.camera_thread.frame_captured.connect(self._actualizar_frame)
            self.camera_thread.start()
            
    def _actualizar_frame(self, qt_image: QImage):
        if not self._is_review_mode:
            self.current_qt_image = qt_image
            # Escalar manteniendo la proporción
            pixmap = QPixmap.fromImage(qt_image).scaled(
                self.panel_video.width(), self.panel_video.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.panel_video.setPixmap(pixmap)
            
    def _capturar_foto(self):
        """Congela el frame y pasa al modo revisión."""
        if self.current_qt_image:
            self._is_review_mode = True
            
            # Detener el hilo de la cámara temporalmente para congelar la imagen
            if self.camera_thread is not None:
                self.camera_thread.stop()
                self.camera_thread = None
                
            self.btn_capturar.hide()
            self.btn_reintentar.show()
            self.btn_aceptar.show()

    def _reintentar(self):
        """Descarta la foto congelada y vuelve a encender la cámara."""
        self._iniciar_camara()
        
    def get_image_bytes(self) -> bytes:
        """Extrae la imagen en formato JPG en bytes."""
        if self.current_qt_image:
            # Para exportar los bytes necesitamos pasar QImage a un QByteArray
            from PySide6.QtCore import QByteArray, QBuffer, QIODevice
            ba = QByteArray()
            buffer = QBuffer(ba)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            self.current_qt_image.save(buffer, "JPG", quality=90)
            return ba.data()
        return None

    def closeEvent(self, event):
        """Asegura liberar la cámara si el usuario cierra la ventana con la X."""
        if self.camera_thread is not None:
            self.camera_thread.stop()
            self.camera_thread = None
        super().closeEvent(event)

    # --- Estilos ---
    def _primary_btn_style(self):
        return """
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 0 30px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #0b5ed7; }
        """
        
    def _danger_btn_style(self):
        return """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 0 30px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
        """
        
    def _success_btn_style(self):
        return """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 0 30px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #219a52; }
        """
