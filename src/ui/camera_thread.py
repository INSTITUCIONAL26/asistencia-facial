import cv2
import time
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage
import numpy as np

class CameraThread(QThread):
    """
    Hilo de trabajo reutilizable para capturar frames de la webcam utilizando OpenCV.
    - Dibuja el rectángulo/óvalo de detección a 30 FPS.
    - Cada 2 segundos, si hay exactamente 1 rostro, emite el crop para reconocimiento.
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
        
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        self._is_processing = False
        self._last_recognition_time = 0.0
        self._recon_interval = 2.0  
        self._current_status = ""
        self._green_until = 0.0

    def set_match_success(self):
        """Pone el óvalo en verde por 2 segundos."""
        self._green_until = time.time() + 2.0

    def _emitir_estado(self, texto):
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
                # Detección facial optimizada
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=8, minSize=(120, 120)
                )
                
                # Imagen limpia (para almacenamiento y archivo biométrico sin dibujos)
                clean_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h_img, w_img, ch = clean_rgb.shape
                bytes_per_line = ch * w_img
                clean_qt_image = QImage(clean_rgb.data, w_img, h_img, bytes_per_line, QImage.Format.Format_RGB888).copy()
                self.clean_frame_captured.emit(clean_qt_image)

                # Imagen visual con interfaz biométrica interactiva estilo bancaria
                display_rgb = clean_rgb.copy()
                is_match = time.time() < self._green_until
                center_frame_x = w_img // 2
                center_frame_y = h_img // 2

                for (x, y, w, h) in faces:
                    face_cx = x + w // 2
                    face_cy = y + h // 2
                    axes = (int((w // 2) * 1.35), int((h // 2) * 1.45))

                    # Evaluación de encuadre (Centro y Proporción)
                    dx = abs(face_cx - center_frame_x)
                    dy = abs(face_cy - center_frame_y)
                    is_centered = (dx < w_img * 0.18) and (dy < h_img * 0.20) and (w >= w_img * 0.20) and (w <= w_img * 0.75)

                    if is_match or is_centered:
                        color = (0, 230, 115)       # Verde esmeralda (Encuadre perfecto)
                        glow_color = (0, 255, 128)
                    else:
                        color = (255, 50, 50)       # Rojo (Fuera de encuadre / buscando)
                        glow_color = (255, 90, 90)

                    # 1. Dibujar el óvalo guía suave
                    cv2.ellipse(display_rgb, (face_cx, face_cy), axes, 0, 0, 360, color, 2, cv2.LINE_AA)

                    # 2. Punto orbital interactivo que recorre el perímetro (Efecto biometría bancaria)
                    theta = (time.time() * 3.5) % (2 * np.pi)
                    orbit_x = int(face_cx + axes[0] * np.cos(theta))
                    orbit_y = int(face_cy + axes[1] * np.sin(theta))

                    cv2.circle(display_rgb, (orbit_x, orbit_y), 9, glow_color, 2, cv2.LINE_AA)
                    cv2.circle(display_rgb, (orbit_x, orbit_y), 5, (255, 255, 255), -1, cv2.LINE_AA)

                if not self._is_processing:
                    if len(faces) == 0:
                        self._emitir_estado("Esperando rostro...")
                    elif len(faces) > 1:
                        self._emitir_estado("Más de un rostro detectado")
                    elif len(faces) == 1:
                        current_time = time.time()
                        if current_time - self._last_recognition_time >= self._recon_interval:
                            self._last_recognition_time = current_time
                            self._is_processing = True
                            
                            self._emitir_estado("Procesando reconocimiento facial...")
                            
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
                            # Cooldown: avisamos qué está pasando visualmente
                            if is_match:
                                self._emitir_estado("¡Rostro Reconocido Exitosamente!")
                            else:
                                self._emitir_estado("Enfocando rostro (Espera de seguridad)...")

                qt_image = QImage(display_rgb.data, w_img, h_img, bytes_per_line, QImage.Format.Format_RGB888)
                self.frame_captured.emit(qt_image)
            else:
                self.msleep(10)
                
        # Liberar los recursos
        if self.capture is not None:
            self.capture.release()

    def set_processing(self, is_processing: bool):
        """Método para liberar el bloqueo desde afuera una vez terminado el reconocimiento."""
        self._is_processing = is_processing

    def stop(self):
        self._is_running = False
        self.wait()
