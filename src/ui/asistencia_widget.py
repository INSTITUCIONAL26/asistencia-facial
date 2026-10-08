from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QTime
from PySide6.QtGui import QIcon


class AsistenciaWidget(QWidget):
    """
    Vista de Asistencia por Captura Facial.
    """

    _TEXTO_ABRIR  = "  Abrir Cámara"
    _TEXTO_CERRAR = "  Cerrar Cámara"

    def __init__(self, jornada_widget):
        super().__init__()
        self.jornada_widget = jornada_widget
        self._camara_abierta = False
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(20)

        title_card = QFrame()
        title_card.setStyleSheet("background-color: transparent; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);")
        title_layout = QVBoxLayout(title_card)
        title_layout.setContentsMargins(36, 32, 36, 32)
        title = QLabel("Asistencia por Captura Facial")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: none;")
        title_layout.addWidget(title)
        outer.addWidget(title_card)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.btn_camara = QPushButton(self._TEXTO_ABRIR)
        self.btn_camara.setIcon(QIcon("src/ui/assets/play.svg"))
        self.btn_camara.setIconSize(QSize(18, 18))
        self.btn_camara.setFixedHeight(42)
        self.btn_camara.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_camara.setStyleSheet(self._estilo_btn_abrir())
        self.btn_camara.clicked.connect(self._toggle_camara)

        btn_row.addWidget(self.btn_camara)
        btn_row.addStretch()
        outer.addLayout(btn_row)

        self.panel_video = QFrame()
        self.panel_video.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 8px;
                border: 2px solid #2c3e50;
            }
        """)
        self.panel_video.setMinimumHeight(380)

        panel_layout = QVBoxLayout(self.panel_video)
        self.lbl_estado_camara = QLabel("[ Cámara cerrada ]")
        self.lbl_estado_camara.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_estado_camara.setStyleSheet(
            "color: #7f8c8d; font-size: 15px; border: none;"
        )
        panel_layout.addWidget(self.lbl_estado_camara)

        outer.addWidget(self.panel_video)

        # Label de Feedback inferior (Reemplaza a QMessageBox)
        self.lbl_feedback = QLabel("Cámara cerrada")
        self.lbl_feedback.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_feedback.setStyleSheet("color: #7f8c8d; font-size: 16px; font-weight: bold; border: none;")
        outer.addWidget(self.lbl_feedback)

    def _actualizar_feedback(self, texto, color="#0d6efd"):
        self.lbl_feedback.setText(texto)
        self.lbl_feedback.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold; border: none;")

    def _toggle_camara(self):
        if not self._camara_abierta:
            self._intentar_abrir_camara()
        else:
            self._cerrar_camara()

    def _intentar_abrir_camara(self):
        if not self.jornada_widget.esta_configurada():
            QMessageBox.warning(
                self,
                "Jornada no configurada",
                "Antes de abrir la Cámara del Sistema debe configurarse "
                "los parámetros de la Jornada."
            )
            return

        from ui.camera_thread import CameraThread
        from ai.reconocimiento_thread import ReconocimientoThread
        from repositories.asistencia_repository import AsistenciaRepository

        if not hasattr(self, 'asistencia_repo'):
            self.asistencia_repo = AsistenciaRepository()

        if not hasattr(self, 'reconocimiento_thread') or self.reconocimiento_thread is None:
            self.reconocimiento_thread = ReconocimientoThread(self)
            self.reconocimiento_thread.match_found.connect(self._procesar_match)
            self.reconocimiento_thread.match_failed.connect(self._procesar_rechazo)

        if not hasattr(self, 'camera_thread') or self.camera_thread is None:
            self.camera_thread = CameraThread(camera_index=0)
            self.camera_thread.frame_captured.connect(self._actualizar_frame_camara)
            self.camera_thread.status_update.connect(self._actualizar_estado_camara)
            
            self.camera_thread.face_to_recognize.connect(self.reconocimiento_thread.set_face_crop)
            self.camera_thread.face_to_recognize.connect(self.reconocimiento_thread.start)
            
            self.reconocimiento_thread.finished_processing.connect(
                lambda: self.camera_thread.set_processing(False)
            )

            self.camera_thread.start()

        self._camara_abierta = True
        self.btn_camara.setText(self._TEXTO_CERRAR)
        self.btn_camara.setIcon(QIcon("src/ui/assets/square.svg"))
        self.btn_camara.setStyleSheet(self._estilo_btn_cerrar())
        self.lbl_estado_camara.hide()
        self._actualizar_feedback("Esperando rostro...", "#f1c40f")

    def _actualizar_estado_camara(self, texto):
        # Evitar sobreescribir los mensajes de reconocimiento persistentes si la IA está activa
        if not self.reconocimiento_thread.isRunning():
            self._actualizar_feedback(texto, "#f1c40f")

    def _procesar_match(self, alumno_id, distancia):
        jornada_id = self.jornada_widget.jornada_id
        if jornada_id is None:
            return

        asistencia = self.asistencia_repo.obtener_asistencia_activa(alumno_id, jornada_id)
        
        if asistencia is None:
            self.asistencia_repo.registrar_entrada(alumno_id, jornada_id)
            self._actualizar_feedback(f"Entrada registrada (ID: {alumno_id})", "#2ecc71")
        else:
            asist_id, entrada, salida = asistencia
            if salida is not None:
                self._actualizar_feedback("Entrada y salida ya registradas para esa Jornada.", "#3498db")
                return
            
            hora_salida_jornada = self.jornada_widget.salida_edit.time()
            ahora = QTime.currentTime()
            segundos_diff = ahora.secsTo(hora_salida_jornada)
            
            if segundos_diff <= 300:
                self.asistencia_repo.registrar_salida(asist_id)
                self._actualizar_feedback(f"Salida registrada (ID: {alumno_id})", "#2ecc71")
            else:
                self._actualizar_feedback("Entrada ya registrada; todavía no puede registrar salida.", "#e67e22")

    def _procesar_rechazo(self):
        self._actualizar_feedback("Rostro no reconocido", "#e74c3c")

    def _actualizar_frame_camara(self, qt_image):
        from PySide6.QtGui import QPixmap
        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.panel_video.width(), self.panel_video.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_estado_camara.setPixmap(pixmap)
        self.lbl_estado_camara.show()

    def _cerrar_camara(self):
        if hasattr(self, 'camera_thread') and self.camera_thread is not None:
            self.camera_thread.stop()
            self.camera_thread = None

        self._camara_abierta = False
        self.btn_camara.setText(self._TEXTO_ABRIR)
        self.btn_camara.setIcon(QIcon("src/ui/assets/play.svg"))
        self.btn_camara.setStyleSheet(self._estilo_btn_abrir())
        
        self.lbl_estado_camara.clear()
        self.lbl_estado_camara.setText("[ Cámara cerrada ]")
        self.lbl_estado_camara.setStyleSheet(
            "color: #7f8c8d; font-size: 15px; border: none;"
        )
        self.lbl_estado_camara.show()
        self._actualizar_feedback("Cámara cerrada", "#7f8c8d")

    def hideEvent(self, event):
        if self._camara_abierta:
            self._cerrar_camara()
        super().hideEvent(event)

    def on_jornada_estado_cambiado(self, configurada: bool):
        if not configurada and self._camara_abierta:
            self._cerrar_camara()

    @staticmethod
    def _estilo_btn_abrir():
        return """
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """

    @staticmethod
    def _estilo_btn_cerrar():
        return """
            QPushButton {
                background-color: #c0392b;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 24px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #a93226;
            }
        """
