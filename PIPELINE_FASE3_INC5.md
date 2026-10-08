# 🚀 PIPELINE FASE 3 (INCREMENTO 5) - Reconocimiento Biométrico con DeepFace

Este documento detalla la Fase 3, donde implementamos el "cerebro" analítico de la aplicación utilizando los conceptos matemáticos del profesor: Extracción de Vectores (Embeddings) y cálculo de Distancias.

## 1. El Hilo Especializado (`ReconocimientoThread`)
Para evitar que la carga matemática pesada congele la interfaz de usuario, creamos un nuevo QThread dedicado exclusivamente a la Inteligencia Artificial (`src/ai/reconocimiento_thread.py`).
Este hilo recibe el "recorte de la cara" (crop) emitido por el `CameraThread` (Fase 2) y procede a analizarlo.

## 2. Caché y Carga Inicial de Embeddings
Extraer el vector de una foto usando `FaceNet512` es un proceso costoso. Si lo hiciéramos para todos los alumnos de la BD en cada validación, el sistema colapsaría.
Para solucionarlo, implementamos un **Caché en Memoria**:
1. Se agregó un método en `AlumnoRepository` para extraer todas las imágenes históricas.
2. La primera vez que el sistema se inicializa, recorre la BD, calcula los embeddings usando `DeepFace.represent` y los guarda en memoria RAM (diccionario).
3. A partir de allí, las consultas posteriores son ultra rápidas.

## 3. Matemática del Modelo (FaceNet512)
Cuando la webcam dispara un rostro, el hilo hace lo siguiente:
1. Extrae su vector usando: `DeepFace.represent(model_name="Facenet512", enforce_detection=False)` (se apaga el detector interno porque nuestro propio Haar Cascade ya hizo ese trabajo, ahorrando el 50% del tiempo de CPU).
2. Itera sobre todos los embeddings cacheados en memoria.
3. Utiliza `scipy.spatial.distance.cosine` para calcular la similitud matemática.
4. Identifica qué foto de la BD dio la distancia más baja (el mejor candidato).

## 4. El Umbral de Decisión (0.40)
Se codificó la regla estricta:
- `if mejor_distancia <= 0.40`: El hilo emite la señal `match_found(alumno_id)`.
- `else`: El hilo emite la señal `match_failed()`.
Finalmente, emite `finished_processing()` para decirle a la cámara que ya puede habilitar el escáner nuevamente.
