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

## 🎉 ¡FIN DEL INCREMENTO 5!
Con estas 4 fases terminadas, la aplicación es capaz de gestionar jornadas y realizar reconocimiento biométrico industrial en tiempo real con ventanas de tolerancia temporales, todo sin congelar la pantalla.
