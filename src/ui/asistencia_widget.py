from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QSize, QTime
from PySide6.QtGui import QIcon


class AsistenciaWidget(QWidget):
    """
    Vista de Asistencia por Captura Facial.

    Controles:
        - Botón toggle Abrir Cámara / Cerrar Cámara.
        - Panel de video (placeholder para el próximo incremento).

    Regla de negocio:
        No se puede abrir la cámara si la Jornada no fue configurada.
        Se valida consultando jornada_widget.esta_configurada().
    """

    # ── Textos del botón toggle ──────────────────────────────────────
    _TEXTO_ABRIR  = "  Abrir Cámara"
    _TEXTO_CERRAR = "  Cerrar Cámara"

    def __init__(self, jornada_widget):
        super().__init__()
        self.jornada_widget = jornada_widget
        self._camara_abierta = False
        self._build_ui()

    # ── Construcción de la UI ────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(20)

        # ── Card para el Título (similar a las otras vistas) ─────────
        title_card = QFrame()
        title_card.setStyleSheet("background-color: transparent; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);")
        title_layout = QVBoxLayout(title_card)
        title_layout.setContentsMargins(36, 32, 36, 32)
        title = QLabel("Asistencia por Captura Facial")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: none;")
        title_layout.addWidget(title)
        outer.addWidget(title_card)

        # ── Fila de botones ──────────────────────────────────────────
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

        # ── Panel de video (placeholder) ─────────────────────────────
        self.panel_video = QFrame()
        self.panel_video.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border-radius: 8px;
                border: 2px solid #2c3e50;
            }
        """)
        self.panel_video.setMinimumHeight(380)

        # Label interior del panel
        panel_layout = QVBoxLayout(self.panel_video)
        self.lbl_estado_camara = QLabel("[ Cámara cerrada ]")
        self.lbl_estado_camara.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_estado_camara.setStyleSheet(
            "color: #7f8c8d; font-size: 15px; border: none;"
        )
        panel_layout.addWidget(self.lbl_estado_camara)

        outer.addWidget(self.panel_video)

    # ── Slot principal ───────────────────────────────────────────────

    def _toggle_camara(self):
        """Alterna el estado de la cámara con validación de jornada."""
        if not self._camara_abierta:
            self._intentar_abrir_camara()
        else:
            self._cerrar_camara()

    def _intentar_abrir_camara(self):
        """
        Valida que la Jornada esté configurada antes de abrir.
        Si no lo está, muestra alerta y no cambia el estado.
        """
        if not self.jornada_widget.esta_configurada():
            QMessageBox.warning(
                self,
                "Jornada no configurada",
                "Antes de abrir la Cámara del Sistema debe configurarse "
                "los parámetros de la Jornada "
                "(segunda opción del Menú Lateral)."
            )
            return

        # Jornada OK —> iniciar el CameraThread
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
            
            # Conectar la cámara con la IA
            self.camera_thread.face_to_recognize.connect(self.reconocimiento_thread.set_face_crop)
            self.camera_thread.face_to_recognize.connect(self.reconocimiento_thread.start)
            
            # Al terminar la IA, desbloqueamos la cámara
            self.reconocimiento_thread.finished_processing.connect(
                lambda: self.camera_thread.set_processing(False)
            )

            self.camera_thread.start()

        self._camara_abierta = True
        self.btn_camara.setText(self._TEXTO_CERRAR)
        self.btn_camara.setIcon(QIcon("src/ui/assets/square.svg"))
        self.btn_camara.setStyleSheet(self._estilo_btn_cerrar())
        self.lbl_estado_camara.hide()

    def _procesar_match(self, alumno_id, distancia):
        """Regla de Negocio: 5 minutos de tolerancia para marcar salida."""
        jornada_id = self.jornada_widget.jornada_id
        if jornada_id is None:
            return

        asistencia = self.asistencia_repo.obtener_asistencia_activa(alumno_id, jornada_id)
        
        if asistencia is None:
            # 1. Primer Reconocimiento -> Entrada
            self.asistencia_repo.registrar_entrada(alumno_id, jornada_id)
            QMessageBox.information(self, "Match Exitoso", f"Entrada registrada (ID: {alumno_id})")
        else:
            asist_id, entrada, salida = asistencia
            if salida is not None:
                # Ya registró salida
                return
            
            # 2. Evaluar tiempo de salida (tolerancia 5 mins antes del horario configurado)
            hora_salida_jornada = self.jornada_widget.salida_edit.time()
            ahora = QTime.currentTime()
            
            # Segundos entre ahora y la hora de salida de la jornada
            segundos_diff = ahora.secsTo(hora_salida_jornada)
            
            # Si faltan 5 minutos (300 segundos) o menos, O si ya pasó la hora -> Puede Salir
            if segundos_diff <= 300:
                self.asistencia_repo.registrar_salida(asist_id)
                QMessageBox.information(self, "Match Exitoso", f"Salida registrada (ID: {alumno_id})")
            else:
                QMessageBox.warning(self, "Aviso", f"Entrada ya registrada. Espere a su horario de salida.")

    def _procesar_rechazo(self):
        """Lógica opcional: qué hacer si el rostro no hace match."""
        # Podría mostrar un pequeño popup que se auto-cierre, o simplemente ignorarlo.
        pass

    def _actualizar_frame_camara(self, qt_image):
        from PySide6.QtGui import QPixmap
        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.panel_video.width(), self.panel_video.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        # Reutilizamos el lbl_estado_camara para mostrar el video
        self.lbl_estado_camara.setPixmap(pixmap)
        self.lbl_estado_camara.show()

    def _cerrar_camara(self):
        """Cierra la cámara y restaura el estado inicial del panel."""
        if hasattr(self, 'camera_thread') and self.camera_thread is not None:
            self.camera_thread.stop()
            self.camera_thread = None

        self._camara_abierta = False
        self.btn_camara.setText(self._TEXTO_ABRIR)
        self.btn_camara.setIcon(QIcon("src/ui/assets/play.svg"))
        self.btn_camara.setStyleSheet(self._estilo_btn_abrir())
        
        # Restaurar placeholder
        self.lbl_estado_camara.clear()
        self.lbl_estado_camara.setText("[ Cámara cerrada ]")
        self.lbl_estado_camara.setStyleSheet(
            "color: #7f8c8d; font-size: 15px; border: none;"
        )
        self.lbl_estado_camara.show()

    def hideEvent(self, event):
        """Si la ventana se oculta (cambio de pestaña), cerrar cámara por seguridad."""
        if self._camara_abierta:
            self._cerrar_camara()
        super().hideEvent(event)

    def on_jornada_estado_cambiado(self, configurada: bool):
        """Slot que reacciona a los cambios en la Jornada. Si se desconfigura y la cámara está abierta, la cierra."""
        if not configurada and self._camara_abierta:
            self._cerrar_camara()

    # ── Estilos de botón ─────────────────────────────────────────────

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
