import cv2
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QImage

class CameraThread(QThread):
    """
    Hilo de trabajo reutilizable para capturar frames de la webcam utilizando OpenCV.
    Se ejecuta en background para no bloquear la interfaz principal (UI).
    Emite cada frame procesado como una señal de QImage.
    """
    frame_captured = Signal(QImage)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self._is_running = False
        self.capture = None

    def run(self):
        self._is_running = True
        self.capture = cv2.VideoCapture(self.camera_index)
        
        while self._is_running:
            ret, frame = self.capture.read()
            if ret:
                # Convertir la imagen de OpenCV (BGR) a QImage (RGB) para PySide6
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                
                # Crear la imagen QImage
                qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                
                # Emitir la señal con el frame escalado y procesado
                self.frame_captured.emit(qt_image)
            else:
                self.msleep(10)
                
        # Liberar los recursos de forma segura cuando el hilo termina
        if self.capture is not None:
            self.capture.release()

    def stop(self):
        """Detiene la captura y solicita la finalización del hilo."""
        self._is_running = False
        self.wait()
