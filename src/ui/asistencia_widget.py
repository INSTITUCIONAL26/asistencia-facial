from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QMessageBox, QGridLayout
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
        outer.setSpacing(15)

        title_card = QFrame()
        title_card.setStyleSheet("background-color: transparent; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);")
        title_layout = QVBoxLayout(title_card)
        title_layout.setContentsMargins(36, 16, 36, 16)
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

        # Panel de Información Detallada (Dashboard de Reconocimiento)
        self.panel_info = QFrame()
        self.panel_info.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.2);
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        grid_info = QGridLayout(self.panel_info)
        grid_info.setContentsMargins(20, 15, 20, 15)
        
        # Labels estáticos
        l1 = QLabel("Estado Visual:")
        l2 = QLabel("ID Reconocido:")
        l3 = QLabel("Distancia (<=0.40):")
        l4 = QLabel("Acción en BD:")
        
        for l in [l1, l2, l3, l4]:
            l.setStyleSheet("color: #a0a0a0; font-size: 14px; font-weight: bold; border: none;")

        # Labels dinámicos
        self.lbl_val_estado = QLabel("Cámara cerrada")
        self.lbl_val_id = QLabel("-")
        self.lbl_val_distancia = QLabel("-")
        self.lbl_val_accion = QLabel("-")
        
        for l in [self.lbl_val_estado, self.lbl_val_id, self.lbl_val_distancia, self.lbl_val_accion]:
            l.setStyleSheet("color: #ecf0f1; font-size: 14px; border: none;")

        grid_info.addWidget(l1, 0, 0)
        grid_info.addWidget(self.lbl_val_estado, 0, 1)
        
        grid_info.addWidget(l2, 1, 0)
        grid_info.addWidget(self.lbl_val_id, 1, 1)
        
        grid_info.addWidget(l3, 2, 0)
        grid_info.addWidget(self.lbl_val_distancia, 2, 1)
        
        grid_info.addWidget(l4, 3, 0)
        grid_info.addWidget(self.lbl_val_accion, 3, 1)
        
        # Ajustar anchos
        grid_info.setColumnStretch(1, 1)

        outer.addWidget(self.panel_info)
        outer.addStretch()

    def _actualizar_datos_modelo(self, alumno_id, distancia, color_id="#ecf0f1", color_dist="#ecf0f1"):
        """Actualiza los labels de ID y distancia."""
        self.lbl_val_id.setText(str(alumno_id) if alumno_id else "-")
        self.lbl_val_id.setStyleSheet(f"color: {color_id}; font-size: 14px; font-weight: bold; border: none;")
        
        if distancia is not None:
            self.lbl_val_distancia.setText(f"{distancia:.4f}")
            self.lbl_val_distancia.setStyleSheet(f"color: {color_dist}; font-size: 14px; font-weight: bold; border: none;")
        else:
            self.lbl_val_distancia.setText("-")
            self.lbl_val_distancia.setStyleSheet("color: #ecf0f1; font-size: 14px; border: none;")

    def _actualizar_accion(self, texto, color="#0d6efd"):
        """Actualiza la acción realizada en base de datos."""
        self.lbl_val_accion.setText(texto)
        self.lbl_val_accion.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold; border: none;")

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
            # Iniciamos la pre-carga (Warmup) de los pesos e imágenes en segundo plano silenciosamente
            self.reconocimiento_thread.start_warmup()
        else:
            # Si ya existía, enviamos un warmup rápido (solo cargará BD si se detectan fotos nuevas)
            self.reconocimiento_thread.start_warmup()

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
        
        self.lbl_val_estado.setText("Inicializando...")
        self._actualizar_datos_modelo("-", None)
        self._actualizar_accion("-")

    def _actualizar_estado_camara(self, texto):
        # Evitar sobreescribir el estado "Procesando"
        self.lbl_val_estado.setText(texto)
        if "Procesando" in texto:
            self.lbl_val_estado.setStyleSheet("color: #f1c40f; font-size: 14px; font-weight: bold; border: none;")
        elif "Exitosamente" in texto:
            self.lbl_val_estado.setStyleSheet("color: #2ecc71; font-size: 14px; font-weight: bold; border: none;")
        else:
            self.lbl_val_estado.setStyleSheet("color: #ecf0f1; font-size: 14px; border: none;")

    def _procesar_match(self, alumno_id, distancia):
        self._actualizar_datos_modelo(alumno_id, distancia, color_id="#2ecc71", color_dist="#2ecc71")
        
        # Pintar el óvalo de verde por 2 segundos
        if hasattr(self, 'camera_thread') and self.camera_thread is not None:
            self.camera_thread.set_match_success()
            
        jornada_id = self.jornada_widget.jornada_id
        if jornada_id is None:
            return

        asistencia = self.asistencia_repo.obtener_asistencia_activa(alumno_id, jornada_id)
        
        if asistencia is None:
            self.asistencia_repo.registrar_entrada(alumno_id, jornada_id)
            self._actualizar_accion(f"Entrada registrada", "#2ecc71")
        else:
            asist_id, entrada, salida = asistencia
            if salida is not None:
                self._actualizar_accion("Asistencia completada (Entrada y Salida)", "#3498db")
                return
            
            hora_salida_jornada = self.jornada_widget.salida_edit.time()
            ahora = QTime.currentTime()
            segundos_diff = ahora.secsTo(hora_salida_jornada)
            
            if segundos_diff <= 300:
                self.asistencia_repo.registrar_salida(asist_id)
                self._actualizar_accion(f"Salida registrada", "#2ecc71")
            else:
                self._actualizar_accion("Esperando horario de salida", "#e67e22")

    def _procesar_rechazo(self, distancia):
        self._actualizar_datos_modelo("Desconocido", distancia, color_id="#e74c3c", color_dist="#e74c3c")
        self._actualizar_accion("Rostro no reconocido (ignorado)", "#e74c3c")

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
        
        self.lbl_val_estado.setText("Cámara cerrada")
        self.lbl_val_estado.setStyleSheet("color: #ecf0f1; font-size: 14px; border: none;")
        self._actualizar_datos_modelo("-", None)
        self._actualizar_accion("-")

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
