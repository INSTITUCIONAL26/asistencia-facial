# 🚀 PIPELINE FASE 2 (INCREMENTO 5) - Motor de Detección Liviana

Este documento detalla los avances logrados en la Fase 2, donde reconstruimos el hilo de la cámara (`CameraThread`) para prepararlo para el procesamiento de Inteligencia Artificial pesada, aplicando estrictamente el concepto de "Separar Detección de Reconocimiento".

## 1. Integración de Haar Cascade (Detección a 30 FPS)
Se cargó el clasificador por defecto de OpenCV (`haarcascade_frontalface_default.xml`).
Este algoritmo de Machine Learning tradicional es extremadamente rápido. Ahora, en el método `run()` del hilo de la cámara, OpenCV busca rostros en cada *frame* (30 veces por segundo) y dibuja automáticamente un óvalo verde sobre ellos. Esto le da al usuario retroalimentación visual ("feedback") inmediata, fluida y sin consumir recursos del procesador.

## 2. Regla del Rostro Único
Se implementó la validación estricta exigida en las reglas de negocio:
`if len(faces) == 1:`
Si la cámara detecta dos o más rostros a la vez, o si no detecta ninguno, el sistema anula silenciosamente el paso al reconocimiento. Esto garantiza que la IA no intente asociar la asistencia de dos personas a la vez.

## 3. Temporizador e Intervalos de 2 Segundos
Ejecutar DeepFace 30 veces por segundo congelaría la computadora por completo. Para solucionarlo, se implementó la arquitectura de bloqueos:
- Se declararon las variables `_is_processing` y `_last_recognition_time`.
- Cuando se detecta exactamente 1 rostro, el sistema se fija hace cuánto fue la última captura.
- Si pasaron más de 2 segundos, levanta la bandera (`_is_processing = True`), recorta el cuadrado exacto donde está el rostro y lo emite a través de la nueva señal `face_to_recognize`.

## 4. Nuevo Puente (Signal) de Emisión
Se creó `face_to_recognize = Signal(np.ndarray)`. En lugar de hacer el reconocimiento adentro del hilo de la cámara (lo cual la trabaría), el hilo simplemente "dispara" el recorte (crop) de la cara hacia afuera y bloquea su propia compuerta.
En la **Fase 3**, el formulario principal (o un hilo especializado) recibirá este rostro recortado, ejecutará el modelo `FaceNet512`, calculará la distancia coseno y, al terminar, llamará al método `set_processing(False)` para abrir nuevamente la compuerta de la cámara.
