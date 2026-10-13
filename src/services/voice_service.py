import time
import threading
import queue


class VoiceService:
    """
    Servicio de síntesis de voz asíncrono y robusto (Grado Industrial).
    - Utiliza un hilo de trabajo dedicado (worker thread) y cola FIFO.
    - El objeto COM SAPI.SpVoice permanece vivo durante toda la sesión, evitando
      cortes prematuros por recolección de basura.
    - La interfaz y la cámara continúan a 30 FPS sin ningún retraso.
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
        try:
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Buscar voz en español nativa (Microsoft Helena)
            for v in speaker.GetVoices():
                desc = v.GetDescription().lower()
                if "helena" in desc or "spanish" in desc or "es-es" in desc:
                    speaker.Voice = v
                    break
                    
            speaker.Rate = 1     # Ritmo natural y claro
            speaker.Volume = 100 # Volumen al 100%
        except Exception as e:
            print(f"[VoiceService] Error inicializando SAPI en hilo de voz: {e}")
            speaker = None

        while self._is_running:
            try:
                texto = self._queue.get(timeout=0.5)
                if texto and speaker:
                    # Habla síncrona dentro del hilo de fondo: garantiza que la frase se emita completa
                    speaker.Speak(texto, 0)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[VoiceService] Error en reproducción de voz: {e}")

    def hablar(self, texto: str, cooldown: float = 0.0):
        """
        Envía una frase a la cola de voz. Retorna de inmediato para no frenar la UI.
        
        Parámetros:
            texto: Frase a reproducir.
            cooldown: Segundos mínimos antes de permitir repetir la misma frase.
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
        """Limpia frases pendientes si es necesario."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except queue.Empty:
                break


# Instancia única lista para usar
voice_service = VoiceService()
