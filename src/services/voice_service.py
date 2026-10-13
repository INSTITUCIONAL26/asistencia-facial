import time
import threading


class VoiceService:
    """
    Servicio de síntesis de voz asíncrono y ultra-robusto para Windows.
    Utiliza directamente la API nativa SAPI.SpVoice con modo asíncrono puro (SVSFlagsAsync).
    Garantiza:
    1. Cero bloqueos en los hilos de la UI y cámara.
    2. No sufre de los bloqueos de bucle de pyttsx3.
    3. Habla con voz nativa en español (Microsoft Helena).
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
        self._last_spoken = {}
        self._speaker = None
        self._init_speaker()

    def _init_speaker(self):
        try:
            import pythoncom
            import win32com.client
            pythoncom.CoInitialize()
            self._speaker = win32com.client.Dispatch("SAPI.SpVoice")
            
            # Buscar voz en español
            for v in self._speaker.GetVoices():
                desc = v.GetDescription()
                if "helena" in desc.lower() or "spanish" in desc.lower():
                    self._speaker.Voice = v
                    break
            # Velocidad natural y fluida
            self._speaker.Rate = 1
            self._speaker.Volume = 100
        except Exception as e:
            print(f"[VoiceService] Error al conectar SAPI SpVoice: {e}")
            self._speaker = None

    def hablar(self, texto: str, cooldown: float = 0.0, purge: bool = False):
        """
        Reproduce un mensaje de voz en segundo plano de manera asíncrona.
        
        Parámetros:
            texto: Frase a pronunciar.
            cooldown: Segundos a esperar antes de repetir este mismo mensaje.
            purge: Si es True, interrumpe cualquier locución previa y habla de inmediato.
        """
        if not texto:
            return

        ahora = time.time()
        ultimo_tiempo = self._last_spoken.get(texto, 0.0)

        if ahora - ultimo_tiempo < cooldown:
            return

        self._last_spoken[texto] = ahora

        def _async_speak():
            try:
                import pythoncom
                import win32com.client
                pythoncom.CoInitialize()
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                for v in speaker.GetVoices():
                    desc = v.GetDescription()
                    if "helena" in desc.lower() or "spanish" in desc.lower():
                        speaker.Voice = v
                        break
                speaker.Rate = 1
                speaker.Volume = 100
                # 1 = SVSFlagsAsync, 2 = SVSFPurgeBeforeSpeak
                flags = 1 | (2 if purge else 0)
                speaker.Speak(texto, flags)
            except Exception as err:
                print(f"[VoiceService] Fallo al reproducir voz: {err}")

        # Ejecutamos la llamada en un hilo ultra-liviano para evitar cualquier bloqueo COM
        t = threading.Thread(target=_async_speak, daemon=True)
        t.start()


# Instancia única lista para usar
voice_service = VoiceService()
