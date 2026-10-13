# 🚀 PIPELINE FASE 4 (INCREMENTO 5) - Reglas de Negocio de Asistencia

Este documento detalla la Fase 4 y final del Incremento 5, en la cual unimos todos los subsistemas (Jornada, Detección y Reconocimiento) e implementamos las reglas de tolerancia de horarios ordenadas por el profesor.

## 1. Conexión Total (Wiring)
En la pestaña de Asistencia (`AsistenciaWidget`), inyectamos los tres componentes principales:
1. `CameraThread` (Fase 2)
2. `ReconocimientoThread` (Fase 3)
3. `AsistenciaRepository` (Recién creado en esta fase).

Ahora, cuando `CameraThread` recorta un rostro válido, emite una señal que automáticamente despierta al `ReconocimientoThread`. Al terminar, este hilo responde con `match_found` o `match_failed` hacia la interfaz, y libera el bloqueo de la cámara.

## 2. Lógica de Tolerancia y Doble Marcado
Se programó el árbol de decisiones exacto solicitado en el audio para proteger los datos en PostgreSQL:
- **Primer Escaneo (Entrada):** Cuando hay un Match, consultamos la BD. Si no existe un registro para ese alumno en esa jornada, se ejecuta el `INSERT` grabando su `entrada` (la salida queda en `NULL`).
- **Escaneo Prematuro (Falso Egreso):** Si el alumno vuelve a pasar y su salida sigue en `NULL`, comparamos la hora actual contra la hora de fin de turno configurada en la jornada. Si faltan **más de 5 minutos** (300 segundos), el sistema lo rebota con el aviso: *"Entrada ya registrada, espere a su horario de salida"*.
- **Escaneo Final (Egreso Exitoso):** Si pasa por la cámara y faltan **5 minutos exactos o menos** (o si ya pasó la hora de salida), el sistema lo aprueba y lanza el `UPDATE asistencia SET salida = AHORA`.

## 3. Manejo de Errores Silencioso
Si una persona que no está en la base de datos pasa por la cámara (o si el modelo devuelve una distancia $> 0.40$), el sistema ignora el evento de forma silenciosa para no interrumpir el flujo constante de estudiantes reales pasando por el molinete.

## 4. Script de Limpieza y Reset de Base de Datos (PowerShell)
Para realizar pruebas limpias desde cero sin perder las credenciales del usuario administrador, se utiliza el script `reset_db.py` ubicado en la raíz del proyecto. Este script borra todos los datos **y reinicia los IDs a 1** (`RESTART IDENTITY`):

```powershell
.\.venv\Scripts\python.exe reset_db.py
```

> [!NOTE]
## 5. Módulo Adicional de Accesibilidad: Síntesis de Voz Asíncrona (TTS)
Se integró `VoiceService` (`pyttsx3` con voz nativa en español SAPI5) para brindar retroalimentación por voz en tiempo real:
- **Asistencia Biométrica:**
  - *"Entrada registrada. Bienvenido, [Nombre Alumno]."*
  - *"Salida registrada. Hasta luego, [Nombre Alumno]."*
  - *"Entrada ya registrada. Por favor, espere a su horario de salida."*
  - *"Rostro no reconocido."*
- **Registro de Alumnos:**
  - Instrucciones de pose para cada ángulo: *"Por favor, mire de frente a la cámara"*, *"Gire hacia su izquierda"*, *"Gire hacia su derecha"*.
  - Confirmación de captura: *"Fotografía capturada"*.
## 6. Módulo UX/Biometría: Retícula de Precisión e Industrialización de Voz
- **Retícula Biométrica Industrial:**
  - Se eliminaron elementos toscos o giratorios sustituyéndolos por una **retícula de precisión** con miras en los 4 ejes cardinales y óvalo anti-aliasing.
  - **Calibración:** Si el rostro está centrado en el encuadre y a la distancia óptima (o match verificado), la retícula conmuta a **Verde Esmeralda (`#00E673`)**. Fuera de posición, se mantiene en **Rojo de Calibración (`#FF3232`)**.
- **Captura Pura (Clean Frame):**
  - Desacoplamiento total entre visor y base de datos: las imágenes en PostgreSQL se almacenan 100% limpias sin sobreimpresión gráfica.
- **Motor de Audio Persistente:**
  - El hilo de voz mantiene el objeto COM SAPI activo en memoria para garantizar salida de audio continua, sin recortes por garbage collection ni silencios posteriores.

## 🎉 ¡FIN DEL INCREMENTO 5!
Con estas 4 fases terminadas, la síntesis de voz continua y la retícula biométrica de precisión, la aplicación alcanza estándar industrial robusto.




