"""
Vista de Asistencia Docente por Captura Facial.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QMessageBox, QGridLayout, QDialog
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap

from services.asistencia_service import AsistenciaService
from repositories.docente_repository import DocenteRepository
from ui.confirmacion_marcacion_dialog import ConfirmacionMarcacionDialog
from services.voice_service import voice_service


class AsistenciaWidget(QWidget):
    """
    Vista principal de marcación biométrica para docentes:
    - Transmisión de webcam a 30 FPS con retícula biométrica.
    - Reconocimiento asíncrono con DeepFace (Facenet512).
    - Evaluación de obligaciones horarias (clases 80m, mesas, jornadas).
    - Despliegue de diálogo modal obligatorio (OK/Cancelar).
    - Pausa y reanudación transparente del reconocimiento durante el modal.
    """

    _TEXTO_ABRIR = "  Abrir Cámara"
    _TEXTO_CERRAR = "  Cerrar Cámara"

    def __init__(self, parent=None, jornada_widget=None):
        super().__init__(parent)
        self.jornada_widget = jornada_widget
        self._camara_abierta = False

        self.asistencia_service = AsistenciaService()
        self.docente_repo = DocenteRepository()
        self.camera_thread = None
        self.reconocimiento_thread = None

        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(60, 40, 60, 40)
        outer.setSpacing(15)

        # 1. Tarjeta de Título
        title_card = QFrame()
        title_card.setStyleSheet(
            "background-color: transparent; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);"
        )
        title_layout = QVBoxLayout(title_card)
        title_layout.setContentsMargins(36, 16, 36, 16)
        
        lbl_inst = QLabel("IES N.º 7 POPULORUM PROGRESSIO")
        lbl_inst.setStyleSheet("font-size: 11px; font-weight: bold; color: #3498db; letter-spacing: 1px; border: none;")
        
        title = QLabel("Control de Asistencia Docente por Reconocimiento Facial")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: none;")
        
        title_layout.addWidget(lbl_inst)
        title_layout.addWidget(title)
        outer.addWidget(title_card)

        # 2. Barra de Control
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

        # 3. Panel de Video
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

        # 4. Panel de Información Detallada (Dashboard)
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
        grid_info.setSpacing(10)

        l1 = QLabel("Estado del Sistema:")
        l2 = QLabel("Docente Identificado:")
        l3 = QLabel("Distancia Biométrica:")
        l4 = QLabel("Operación Propuesta:")

        for l in [l1, l2, l3, l4]:
            l.setStyleSheet("color: #a0a0a0; font-size: 14px; font-weight: bold; border: none;")

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

        grid_info.setColumnStretch(1, 1)
        outer.addWidget(self.panel_info)
        outer.addStretch()

    def _actualizar_datos_modelo(self, docente_nombre, distancia, color_id="#ecf0f1", color_dist="#ecf0f1"):
        self.lbl_val_id.setText(str(docente_nombre) if docente_nombre else "-")
        self.lbl_val_id.setStyleSheet(f"color: {color_id}; font-size: 14px; font-weight: bold; border: none;")

        if distancia is not None:
            self.lbl_val_distancia.setText(f"{distancia:.4f} (<= 0.40)")
            self.lbl_val_distancia.setStyleSheet(f"color: {color_dist}; font-size: 14px; font-weight: bold; border: none;")
        else:
            self.lbl_val_distancia.setText("-")
            self.lbl_val_distancia.setStyleSheet("color: #ecf0f1; font-size: 14px; border: none;")

    def _actualizar_accion(self, texto, color="#0d6efd"):
        self.lbl_val_accion.setText(texto)
        self.lbl_val_accion.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold; border: none;")

    def _toggle_camara(self):
        if not self._camara_abierta:
            self._abrir_camara()
        else:
            self._cerrar_camara()

    def _abrir_camara(self):
        from ui.camera_thread import CameraThread
        from ai.reconocimiento_thread import ReconocimientoThread

        # 1. Hilo de Reconocimiento Facial (DeepFace)
        if self.reconocimiento_thread is None:
            self.reconocimiento_thread = ReconocimientoThread(self)
            self.reconocimiento_thread.match_found.connect(self._procesar_match)
            self.reconocimiento_thread.match_failed.connect(self._procesar_rechazo)
            self.reconocimiento_thread.start_warmup()

        # 2. Hilo de Captura de Video (OpenCV)
        self.camera_thread = CameraThread(camera_index=0, parent=self)
        self.camera_thread.frame_captured.connect(self._actualizar_frame_camara)
        self.camera_thread.face_to_recognize.connect(self._enviar_a_reconocimiento)
        self.camera_thread.status_update.connect(self.lbl_val_estado.setText)

        # Handoff entre hilos
        self.reconocimiento_thread.finished_processing.connect(
            lambda: self.camera_thread.set_processing(False) if self.camera_thread else None
        )

        self.camera_thread.start()
        self._camara_abierta = True
        self.btn_camara.setText(self._TEXTO_CERRAR)
        self.btn_camara.setIcon(QIcon("src/ui/assets/square.svg"))
        self.btn_camara.setStyleSheet(self._estilo_btn_cerrar())
        self._actualizar_accion("En espera de docente...", "#3498db")

    def _enviar_a_reconocimiento(self, face_crop):
        if self.reconocimiento_thread and self.reconocimiento_thread.isRunning():
            self.reconocimiento_thread.set_face_crop(face_crop)
            self.reconocimiento_thread.start()

    def _procesar_match(self, docente_id: int, distancia: float):
        """
        Ejecutado al identificar a un docente por biometría.
        Aplica el flujo exigido en las Secciones 4 y 5.3 del reglamento:
        1. Evalúa la actividad actual del docente.
        2. Pausa nuevos intentos de reconocimiento mientras la cámara sigue viva.
        3. Muestra el modal de confirmación obligatorio (OK/Cancelar).
        4. Solo persiste si presiona OK.
        5. Reanuda el reconocimiento al cerrarse el diálogo.
        """
        docente = self.docente_repo.obtener_docente_por_id(docente_id)
        docente_nombre = docente["nombre_completo"] if docente else f"ID {docente_id}"

        # 1. Evaluar reglas de negocio mediante el servicio
        evaluacion = self.asistencia_service.evaluar_marcacion(docente_id)

        # Si no puede marcar (docente inactivo, licencia activa, sin cátedra ahora, etc.)
        if not evaluacion["puede_marcar"]:
            motivo = evaluacion.get("motivo_rechazo")
            mensaje = evaluacion.get("mensaje", "No es posible registrar marcación.")
            
            if motivo == "SIN_ACTIVIDAD_PROGRAMADA":
                self._actualizar_datos_modelo(docente_nombre, distancia, color_id="#f39c12", color_dist="#2ecc71")
                self._actualizar_accion("Sin actividad programada en este horario", "#f39c12")
                voice_service.hablar(f"{docente_nombre}, no posee actividades programadas en este horario.", cooldown=4.0)
            elif motivo == "ASISTENCIA_YA_COMPLETADA":
                self._actualizar_datos_modelo(docente_nombre, distancia, color_id="#3498db", color_dist="#2ecc71")
                self._actualizar_accion("Asistencia ya completada para hoy", "#3498db")
                voice_service.hablar(f"Asistencia ya completada para el día de hoy, {docente_nombre}.", cooldown=4.0)
            elif motivo == "LICENCIA_ACTIVA":
                self._actualizar_datos_modelo(docente_nombre, distancia, color_id="#9b59b6", color_dist="#2ecc71")
                self._actualizar_accion(mensaje, "#9b59b6")
                voice_service.hablar(f"{docente_nombre} posee una licencia activa para el día de hoy.", cooldown=4.0)
            else:
                self._actualizar_datos_modelo(docente_nombre, distancia, color_id="#e74c3c", color_dist="#2ecc71")
                self._actualizar_accion(mensaje, "#e74c3c")

            if self.camera_thread:
                self.camera_thread.reanudar_reconocimiento(cooldown_segundos=3.0)
            return

        # 2. Caso Válido: Corresponde mostrar el modal de confirmación obligatorio
        self._actualizar_datos_modelo(docente_nombre, distancia, color_id="#2ecc71", color_dist="#2ecc71")
        if self.camera_thread:
            self.camera_thread.set_match_success()
            # Pausar nuevos intentos de reconocimiento mientras el modal está abierto
            self.camera_thread.pausar_reconocimiento()

        if self.reconocimiento_thread:
            self.reconocimiento_thread.pausar()

        # 3. Desplegar Diálogo Modal de Confirmación
        dialog = ConfirmacionMarcacionDialog(evaluacion, parent=self)
        resultado = dialog.exec()

        # 4. Procesar decisión del docente
        if resultado == QDialog.DialogCode.Accepted:
            # Presionó OK -> Persistir en la base de datos
            res = self.asistencia_service.confirmar_marcacion(evaluacion)
            op = evaluacion["tipo_operacion"]
            clasif = evaluacion["clasificacion"]

            self._actualizar_accion(f"{op} registrada ({clasif.upper()})", "#2ecc71")
            
            # Anuncio por voz
            if op == "ENTRADA":
                voice_service.hablar(f"Entrada confirmada. Bienvenido al instituto, {docente_nombre}.", cooldown=3.0)
            else:
                voice_service.hablar(f"Salida confirmada. Hasta luego, {docente_nombre}.", cooldown=3.0)

        else:
            # Presionó Cancelar o cerró el modal -> NO modificar la base de datos
            self._actualizar_accion("Marcación cancelada por el docente (Descartada)", "#e74c3c")
            voice_service.hablar("Operación cancelada.", cooldown=3.0)

        # 5. Reanudar el reconocimiento facial
        if self.reconocimiento_thread:
            self.reconocimiento_thread.reanudar()

        if self.camera_thread:
            self.camera_thread.reanudar_reconocimiento(cooldown_segundos=3.5)

    def _procesar_rechazo(self, distancia: float):
        self._actualizar_datos_modelo("Desconocido", distancia, color_id="#e74c3c", color_dist="#e74c3c")
        self._actualizar_accion("Rostro no reconocido", "#e74c3c")

    def _actualizar_frame_camara(self, qt_image):
        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.panel_video.width(), self.panel_video.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_estado_camara.setPixmap(pixmap)
        self.lbl_estado_camara.show()

    def _cerrar_camara(self):
        if self.camera_thread is not None:
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
