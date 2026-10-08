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
    face_to_recognize = Signal(np.ndarray)  # Emite el crop del rostro (numpy array)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self._is_running = False
        self.capture = None
        
        # Clasificador para Detección Liviana
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Control de intervalos y estado (Fase 2)
        self._is_processing = False
        self._last_recognition_time = 0.0
        self._recon_interval = 2.0  # 2 segundos

    def run(self):
        self._is_running = True
        self.capture = cv2.VideoCapture(self.camera_index)
        
        while self._is_running:
            ret, frame = self.capture.read()
            if ret:
                # 1. Convertir a grises para el detector Haar Cascade
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
                )

                # Convertir a RGB para la interfaz gráfica
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # 2. Dibujar recuadros en TODOS los rostros detectados (UI fluida a 30fps)
                for (x, y, w, h) in faces:
                    # Dibujar óvalo/rectángulo verde
                    center_x, center_y = x + w // 2, y + h // 2
                    axes = (w // 2, h // 2)
                    cv2.ellipse(frame_rgb, (center_x, center_y), axes, 0, 0, 360, (0, 255, 0), 2)

                # 3. Lógica de Disparo de Reconocimiento (Fase 2)
                # Solo si hay EXACTAMENTE 1 rostro y no estamos ya procesando algo pesado
                if len(faces) == 1 and not self._is_processing:
                    current_time = time.time()
                    if current_time - self._last_recognition_time >= self._recon_interval:
                        self._last_recognition_time = current_time
                        self._is_processing = True  # Bloqueamos nuevos escaneos hasta que vuelva
                        
                        # Recortar (Crop) el rostro en RGB
                        x, y, w, h = faces[0]
                        face_crop = frame_rgb[y:y+h, x:x+w].copy()
                        
                        # Emitir el rostro para que la Fase 3 lo procese
                        self.face_to_recognize.emit(face_crop)

                # Emitir el Frame procesado a la interfaz
                h_img, w_img, ch = frame_rgb.shape
                bytes_per_line = ch * w_img
                qt_image = QImage(frame_rgb.data, w_img, h_img, bytes_per_line, QImage.Format.Format_RGB888)
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
