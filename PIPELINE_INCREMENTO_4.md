# 🚀 PIPELINE INCREMENTO 4 - Captura en Vivo con Webcam

Este documento detalla los pasos realizados para el Incremento 4, cumpliendo estricamente los objetivos de habilitar la cámara en vivo para la pestaña de "Asistencia por Captura Facial" y el "Registro de Alumno".

## 1. Integración de OpenCV
Para manipular el hardware de la webcam y obtener frames de video fluidos, se incorporó la librería **opencv-python** (cv2). 

## 2. Creación del Componente Reutilizable (CameraThread)
En lugar de repetir el código de la cámara, creamos un motor central llamado `CameraThread` (`src/ui/camera_thread.py`) que hereda de `QThread`. 
**Ventajas:**
- Lee la cámara en un hilo secundario, evitando que la interfaz gráfica (UI) se congele.
- Transforma los píxeles de BGR (OpenCV) a RGB y los emite en formato `QImage` listo para PySide6.
- Contiene un método `stop()` que libera el recurso de hardware (`capture.release()`) de forma segura, evitando fugas de memoria o luces encendidas eternamente en la webcam.

## 3. Workflow A: Registrar Alumno (Tomar Foto)
Se creó un componente `CamaraDialog` (`src/ui/camara_dialog.py`), una ventana flotante (Modal) dedicada exclusivamente a sacar fotos.
**Flujo logrado:**
1. Al hacer clic en **"Tomar Foto"**, se abre el Modal e instancia el `CameraThread`.
2. Se muestra la cámara en vivo y aparece el botón **"Capturar Fotografía"**.
3. Al capturar, el hilo de video se pausa, "congelando" el frame.
4. Aparecen los botones **"Reintentar"** (🗑️) para descartar y **"Guardar Foto"** (✅).
5. Al darle a Guardar, la ventana modal convierte esa imagen a formato binario (bytes JPG) y se la inyecta al widget de ángulo original (`AnguloFotoWidget`), mostrando la miniatura igual que cuando se carga por archivo.

## 4. Workflow B: Asistencia por Captura Facial
Se dotó de vida al panel oscuro (placeholder) de la vista de Asistencia.
**Flujo logrado:**
1. La validación original funciona intacta (exige tener una jornada configurada).
2. Al hacer clic en **"Abrir Cámara"**, en lugar de cambiar solo el texto, instancia el `CameraThread` y mapea los frames escalados al cuadro de video de la interfaz.
3. Al hacer clic en **"Cerrar Cámara"**, se detiene el hilo y se libera el recurso.
4. **Seguridad UX/UI:** Se interceptó el evento `hideEvent`. Si el usuario tiene la cámara encendida, pero cambia de opción en el menú (se va a otra pestaña), el sistema detecta que se ocultó el widget y apaga automáticamente la cámara, asegurando un control absoluto del hardware.

## Ejemplo Práctico de Uso
1. Inicie la aplicación e inicie sesión.
2. Vaya a **Registrar Alumno**.
3. Haga clic en **Tomar Foto** en el "Ángulo Frontal". Se abre un popup mostrando su rostro en vivo.
4. Sonría, haga clic en "Capturar", si no le convence presione el botón "Reintentar" (el tacho). Si le gusta, presione "Guardar". La ventana se cierra sola y su foto aparece en el recuadro.
5. Luego vaya a **Jornada** y configure un turno.
6. Finalmente vaya a **Captura Facial**. Presione "Abrir cámara". Se encenderá su luz de la webcam y se verá reflejado en la pantalla principal.
