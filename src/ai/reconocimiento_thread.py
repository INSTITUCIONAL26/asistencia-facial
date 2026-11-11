"""
Hilo de Reconocimiento Facial Asíncrono con DeepFace y Facenet512.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
import cv2
import numpy as np
from deepface import DeepFace
from PySide6.QtCore import QThread, Signal

from repositories.docente_repository import DocenteRepository


class ReconocimientoThread(QThread):
    """
    Hilo encargado de realizar el reconocimiento facial de manera asíncrona.
    - Calcula el embedding de la imagen de la cámara.
    - Calcula (y cachea) los embeddings de los docentes en la BD.
    - Realiza el Match usando distancia coseno con Facenet512.
    - Soporta pausa y reanudación durante la visualización del diálogo modal.
    """
    match_found = Signal(int, float)  # (docente_id, distancia)
    match_failed = Signal(float)      # (mejor_distancia)
    finished_processing = Signal()    # Para que la cámara vuelva a capturar

    def __init__(self, parent=None):
        super().__init__(parent)
        self.docente_repo = DocenteRepository()
        self.model_name = "Facenet512"
        self.threshold = 0.40
        self.face_crop = None
        
        self.embeddings_cache = {}
        self._num_fotos_cacheadas = 0
        self._is_warmup = False
        self._paused = False

    def pausar(self):
        """Pausa el procesamiento de nuevos matches mientras el modal está activo."""
        self._paused = True

    def reanudar(self):
        """Reanuda el procesamiento de matches al cerrarse el modal."""
        self._paused = False

    def start_warmup(self):
        """Inicia la carga de la BD y de los pesos de la IA en segundo plano."""
        self._is_warmup = True
        self.start()

    def recargar_cache(self):
        """Fuerza la recarga de fotos desde la BD (ej: luego de registrar un nuevo docente)."""
        self._num_fotos_cacheadas = -1
        self.cargar_cache_si_es_necesario()

    def cargar_cache_si_es_necesario(self):
        """Carga y procesa las imágenes de la BD solo si hubo cambios."""
        fotos = self.docente_repo.obtener_todas_las_fotos()
        
        if len(fotos) == self._num_fotos_cacheadas and self._num_fotos_cacheadas > 0:
            return

        print(f"[DeepFace] Cargando base de datos ({len(fotos)} fotos detectadas de docentes)...")
        self.embeddings_cache = {}
        self._num_fotos_cacheadas = len(fotos)
        
        for docente_id, angulo, imagen_bytes in fotos:
            nparr = np.frombuffer(imagen_bytes, np.uint8)
            img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            try:
                result = DeepFace.represent(
                    img_path=img_bgr,
                    model_name=self.model_name,
                    enforce_detection=False,
                )
                embedding = result[0]["embedding"]
                
                if docente_id not in self.embeddings_cache:
                    self.embeddings_cache[docente_id] = []
                
                self.embeddings_cache[docente_id].append({
                    "angulo": angulo,
                    "embedding": embedding,
                })
            except Exception as e:
                print(f"[DeepFace] Error procesando BD para docente {docente_id}: {e}")

        print("[DeepFace] Caché de docentes listo.")

    def set_face_crop(self, crop: np.ndarray):
        """Recibe el recorte enviado por la cámara."""
        self.face_crop = crop

    def run(self):
        """Lógica pesada de DeepFace que corre en segundo plano."""
        # Si está pausado (modal abierto), descartamos de inmediato
        if self._paused:
            self.face_crop = None
            self.finished_processing.emit()
            return

        # Modo warmup (precarga en segundo plano)
        if getattr(self, '_is_warmup', False):
            self.cargar_cache_si_es_necesario()
            try:
                dummy = np.zeros((100, 100, 3), dtype=np.uint8)
                DeepFace.represent(img_path=dummy, model_name=self.model_name, enforce_detection=False)
            except Exception:
                pass
            self._is_warmup = False
            self.finished_processing.emit()
            return
            
        # Modo reconocimiento normal
        if self.face_crop is None:
            self.finished_processing.emit()
            return

        self.cargar_cache_si_es_necesario()

        try:
            # Obtener embedding del rostro detectado por la cámara
            result = DeepFace.represent(
                img_path=self.face_crop,
                model_name=self.model_name,
                enforce_detection=False,
            )
            cam_embedding = np.array(result[0]["embedding"])

            mejor_distancia = 1.0
            mejor_docente_id = None

            # Buscar el mejor match en el caché
            for docente_id, referencias in self.embeddings_cache.items():
                for ref in referencias:
                    db_embedding = np.array(ref["embedding"])
                    
                    # Distancia Coseno
                    dot_product = np.dot(cam_embedding, db_embedding)
                    norm_a = np.linalg.norm(cam_embedding)
                    norm_b = np.linalg.norm(db_embedding)
                    dist = 1.0 - (dot_product / (norm_a * norm_b))
                    
                    if dist < mejor_distancia:
                        mejor_distancia = dist
                        mejor_docente_id = docente_id

            # Comprobar umbral estricto (<= 0.40) y que no se haya pausado durante el cálculo
            if not self._paused and mejor_distancia <= self.threshold and mejor_docente_id is not None:
                print(f"[Match] Docente ID: {mejor_docente_id} | Distancia: {mejor_distancia:.4f}")
                self.match_found.emit(mejor_docente_id, float(mejor_distancia))
            elif not self._paused:
                print(f"[No Match] Mejor distancia fue: {mejor_distancia:.4f}")
                self.match_failed.emit(float(mejor_distancia))

        except Exception as e:
            print(f"[DeepFace] Error en inferencia: {e}")
            if not self._paused:
                self.match_failed.emit(1.0)
        finally:
            self.face_crop = None
            self.finished_processing.emit()
