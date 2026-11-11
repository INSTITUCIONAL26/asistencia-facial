"""
Hilo de Captura de Video con OpenCV a 30 FPS.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
import time
import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage


class CameraThread(QThread):
    """
    Hilo de trabajo reutilizable para capturar frames de la webcam utilizando OpenCV.
    - Dibuja el óvalo de encuadre biométrico y retícula a 30 FPS.
    - Cada intervalo configurable, si hay exactamente 1 rostro centrado, emite el crop.
    - Soporta pausa temporal del reconocimiento (manteniendo la cámara en vivo)
      mientras se muestra el diálogo modal de confirmación obligatorio.
    """
    frame_captured = Signal(QImage)
    clean_frame_captured = Signal(QImage)
    face_to_recognize = Signal(np.ndarray)
    status_update = Signal(str)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self._is_running = False
        self.capture = None
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self._is_processing = False
        self._is_paused = False
        self._last_recognition_time = 0.0
        self._recon_interval = 2.0  
        self._current_status = ""
        self._green_until = 0.0

    def set_match_success(self):
        """Pone el óvalo en verde esmeralda por 2.5 segundos."""
        self._green_until = time.time() + 2.5

    def pausar_reconocimiento(self):
        """
        Pausa los intentos de reconocimiento facial.
        La cámara continúa transmitiendo video fluido a 30 FPS.
        """
        self._is_paused = True
        self._is_processing = True

    def reanudar_reconocimiento(self, cooldown_segundos: float = 3.0):
        """
        Reanuda el reconocimiento facial aplicando un enfriamiento preventivo
        para evitar solicitudes superpuestas inmediatas sobre la misma persona.
        """
        self._last_recognition_time = time.time() + (cooldown_segundos - self._recon_interval)
        self._is_paused = False
        self._is_processing = False

    def _emitir_estado(self, texto: str):
        if self._current_status != texto:
            self._current_status = texto
            self.status_update.emit(texto)

    def run(self):
        self._is_running = True
        self.capture = cv2.VideoCapture(self.camera_index)
        
        while self._is_running:
            ret, frame = self.capture.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Detección facial optimizada con Haar Cascade
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=8, minSize=(120, 120)
                )
                
                # Imagen limpia (para archivo biométrico)
                clean_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h_img, w_img, ch = clean_rgb.shape
                bytes_per_line = ch * w_img
                clean_qt_image = QImage(
                    clean_rgb.data, w_img, h_img, bytes_per_line, QImage.Format.Format_RGB888
                ).copy()
                self.clean_frame_captured.emit(clean_qt_image)

                # Imagen visual con interfaz biométrica interactiva
                display_rgb = clean_rgb.copy()
                is_match = time.time() < self._green_until
                center_frame_x = w_img // 2
                center_frame_y = h_img // 2

                for (x, y, w, h) in faces:
                    face_cx = x + w // 2
                    face_cy = y + h // 2
                    axes = (int((w // 2) * 1.35), int((h // 2) * 1.45))

                    dx = abs(face_cx - center_frame_x)
                    dy = abs(face_cy - center_frame_y)
                    is_centered = (
                        (dx < w_img * 0.18)
                        and (dy < h_img * 0.20)
                        and (w >= w_img * 0.20)
                        and (w <= w_img * 0.75)
                    )

                    if is_match or is_centered:
                        color = (0, 230, 115)       # Verde esmeralda (Encuadre calibrado)
                    else:
                        color = (255, 50, 50)       # Rojo de calibración

                    # Óvalo guía principal con anti-aliasing
                    cv2.ellipse(display_rgb, (face_cx, face_cy), axes, 0, 0, 360, color, 2, cv2.LINE_AA)

                    # Retícula biométrica de precisión en los 4 ejes
                    ax_w, ax_h = axes
                    tick_len = 10
                    cv2.line(display_rgb, (face_cx, face_cy - ax_h - tick_len), (face_cx, face_cy - ax_h + tick_len), color, 2, cv2.LINE_AA)
                    cv2.line(display_rgb, (face_cx, face_cy + ax_h - tick_len), (face_cx, face_cy + ax_h + tick_len), color, 2, cv2.LINE_AA)
                    cv2.line(display_rgb, (face_cx - ax_w - tick_len, face_cy), (face_cx - ax_w + tick_len, face_cy), color, 2, cv2.LINE_AA)
                    cv2.line(display_rgb, (face_cx + ax_w - tick_len, face_cy), (face_cx + ax_w + tick_len, face_cy), color, 2, cv2.LINE_AA)

                # Lógica de emisión de rostro para reconocimiento
                if self._is_paused:
                    self._emitir_estado("Esperando confirmación en pantalla...")
                elif not self._is_processing:
                    if len(faces) == 0:
                        self._emitir_estado("Esperando docente...")
                    elif len(faces) > 1:
                        self._emitir_estado("Más de un rostro detectado")
                    elif len(faces) == 1:
                        current_time = time.time()
                        if current_time - self._last_recognition_time >= self._recon_interval:
                            self._last_recognition_time = current_time
                            self._is_processing = True
                            
                            self._emitir_estado("Identificando docente...")
                            
                            x, y, w, h = faces[0]
                            margin_x = int(w * 0.1)
                            margin_y = int(h * 0.1)
                            x1 = max(0, x - margin_x)
                            y1 = max(0, y - margin_y)
                            x2 = min(frame.shape[1], x + w + margin_x)
                            y2 = min(frame.shape[0], y + h + margin_y)
                            
                            face_crop_bgr = frame[y1:y2, x1:x2].copy()
                            self.face_to_recognize.emit(face_crop_bgr)
                        else:
                            if is_match:
                                self._emitir_estado("¡Docente identificado exitosamente!")
                            else:
                                self._emitir_estado("Enfocando rostro...")

                qt_image = QImage(display_rgb.data, w_img, h_img, bytes_per_line, QImage.Format.Format_RGB888)
                self.frame_captured.emit(qt_image)
            else:
                self.msleep(10)
                
        # Liberar recursos de cámara
        if self.capture is not None:
            self.capture.release()

    def set_processing(self, is_processing: bool):
        """Libera o bloquea el procesamiento."""
        self._is_processing = is_processing

    def stop(self):
        self._is_running = False
        self.wait()
