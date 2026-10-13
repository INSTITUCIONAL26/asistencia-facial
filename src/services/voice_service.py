import threading
import queue
import time
import pyttsx3


class VoiceService:
    """
    Servicio de síntesis de voz asíncrono y no bloqueante.
    Permite enviar mensajes de voz sin congelar la cámara ni la interfaz PySide6.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_service()
            return cls._instance

    def _init_service(self):
        self._queue = queue.Queue()
        self._last_spoken = {}
        self._is_running = True
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def _worker(self):
        # En Windows, pyttsx3 requiere inicializar COM en el mismo hilo
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass

        try:
            engine = pyttsx3.init()
            # Ajustar velocidad a un ritmo natural en español
            engine.setProperty('rate', 170)
            engine.setProperty('volume', 1.0)

            # Buscar y seleccionar voz en español
            voices = engine.getProperty('voices')
            for v in voices:
                nombre = v.name.lower()
                vid = v.id.lower()
                if 'spanish' in nombre or 'es-es' in vid or 'helena' in nombre or 'sabina' in nombre:
                    engine.setProperty('voice', v.id)
                    break
        except Exception as e:
            print(f"[VoiceService] Error inicializando motor TTS: {e}")
            engine = None

        while self._is_running:
            try:
                texto = self._queue.get(timeout=0.5)
                if texto and engine:
                    engine.say(texto)
                    engine.runAndWait()
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VoiceService] Error al reproducir audio: {e}")

    def hablar(self, texto: str, cooldown: float = 0.0):
        """
        Envía un texto a la cola de voz de forma asíncrona.
        
        Parámetros:
            texto: Frase a reproducir.
            cooldown: Segundos mínimos a esperar antes de volver a repetir esta misma frase.
        """
        if not texto:
            return

        ahora = time.time()
        ultimo_tiempo = self._last_spoken.get(texto, 0.0)

        if ahora - ultimo_tiempo < cooldown:
            return

        self._last_spoken[texto] = ahora
        self._queue.put(texto)

    def vaciar_cola(self):
        """Descarta mensajes pendientes en la cola."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break


# Instancia única lista para importar
voice_service = VoiceService()
