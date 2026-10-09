import cv2
import numpy as np
from deepface import DeepFace
from PySide6.QtCore import QThread, Signal

from repositories.alumno_repository import AlumnoRepository

class ReconocimientoThread(QThread):
    """
    Hilo encargado de realizar el reconocimiento facial de manera asíncrona.
    - Calcula el embedding de la imagen de la cámara.
    - Calcula (y cachea) los embeddings de las imágenes de la BD.
    - Realiza el Match usando distancia coseno.
    """
    # Señales que emitirá hacia la UI
    match_found = Signal(int, float)  # (alumno_id, distancia)
    match_failed = Signal(float)      # (mejor_distancia)
    finished_processing = Signal()    # Para que la cámara vuelva a capturar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.alumno_repo = AlumnoRepository()
        self.model_name = "Facenet512"
        self.threshold = 0.40
        self.face_crop = None
        
        self.embeddings_cache = {}
        self._num_fotos_cacheadas = 0
        self._is_warmup = False

    def start_warmup(self):
        """Inicia la carga de la BD y de los pesos de la IA en segundo plano."""
        self._is_warmup = True
        self.start()

    def cargar_cache_si_es_necesario(self):
        """Carga y procesa las imágenes de la BD solo si hubo cambios."""
        fotos = self.alumno_repo.obtener_todas_las_fotos()
        
        # Si la cantidad de fotos no cambió, no recargamos nada (Velocidad instantánea)
        if len(fotos) == self._num_fotos_cacheadas and self._num_fotos_cacheadas > 0:
            return

        print(f"[DeepFace] Cargando base de datos ({len(fotos)} fotos detectadas)...")
        self.embeddings_cache = {}
        self._num_fotos_cacheadas = len(fotos)
        
        for alumno_id, angulo, imagen_bytes in fotos:
            nparr = np.frombuffer(imagen_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            try:
                result = DeepFace.represent(img_path=img_bgr, model_name=self.model_name, enforce_detection=False)
                embedding = result[0]["embedding"]
                
                if alumno_id not in self.embeddings_cache:
                    self.embeddings_cache[alumno_id] = []
                
                self.embeddings_cache[alumno_id].append({
                    "angulo": angulo,
                    "embedding": embedding
                })
            except Exception as e:
                print(f"[DeepFace] Error procesando BD para alumno {alumno_id}: {e}")

        print("[DeepFace] Caché listo.")

    def set_face_crop(self, crop: np.ndarray):
        """Recibe el recorte enviado por la cámara."""
        self.face_crop = crop

    def run(self):
        """Lógica pesada de DeepFace que corre en segundo plano."""
        # --- MODO WARMUP (PRECARGA EN SEGUNDO PLANO) ---
        if getattr(self, '_is_warmup', False):
            self.cargar_cache_si_es_necesario()
            try:
                # Disparo en vacío para pre-calentar los tensores de TensorFlow/Keras
                dummy = np.zeros((100, 100, 3), dtype=np.uint8)
                DeepFace.represent(img_path=dummy, model_name=self.model_name, enforce_detection=False)
            except:
                pass
            self._is_warmup = False
            self.finished_processing.emit()
            return
            
        # --- MODO RECONOCIMIENTO NORMAL ---
        if self.face_crop is None:
            self.finished_processing.emit()
            return

        self.cargar_cache_si_es_necesario()

        try:
            # 2. Obtener embedding de la cámara
            result = DeepFace.represent(img_path=self.face_crop, model_name=self.model_name, enforce_detection=False)
            cam_embedding = np.array(result[0]["embedding"])

            mejor_distancia = 1.0
            mejor_alumno_id = None

            # 3. Buscar el mejor match en el caché
            for alumno_id, referencias in self.embeddings_cache.items():
                for ref in referencias:
                    db_embedding = np.array(ref["embedding"])
                    
                    # Calcular Distancia Coseno manualmente con numpy
                    dot_product = np.dot(cam_embedding, db_embedding)
                    norm_a = np.linalg.norm(cam_embedding)
                    norm_b = np.linalg.norm(db_embedding)
                    dist = 1.0 - (dot_product / (norm_a * norm_b))
                    
                    if dist < mejor_distancia:
                        mejor_distancia = dist
                        mejor_alumno_id = alumno_id

            # 4. Aplicar el umbral estricto (<= 0.40)
            if mejor_distancia <= self.threshold and mejor_alumno_id is not None:
                print(f"[Match] Alumno ID: {mejor_alumno_id} | Distancia: {mejor_distancia:.4f}")
                self.match_found.emit(mejor_alumno_id, float(mejor_distancia))
            else:
                print(f"[No Match] Mejor distancia fue: {mejor_distancia:.4f}")
                self.match_failed.emit(float(mejor_distancia))

        except Exception as e:
            print(f"[DeepFace] Error en inferencia: {e}")
            self.match_failed.emit(1.0)
        finally:
            self.face_crop = None
            self.finished_processing.emit()
