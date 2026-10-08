# 🚀 PIPELINE FASE 1 (INCREMENTO 5) - Ciclo de Vida de la Jornada

Este documento detalla la Fase 1 del Incremento 5, que introduce reglas de negocio estrictas para la gestión de las Jornadas y su impacto en la cámara de la interfaz.

## 1. Repositorio de Jornada (Persistencia Real)
Se creó `src/repositories/jornada_repository.py`. 
Ahora la jornada ya no es solo una validación visual en memoria, sino que cuenta con soporte en PostgreSQL para realizar operaciones concretas:
- `crear_jornada`: Hace el **INSERT** al iniciar una nueva jornada y retorna su ID.
- `actualizar_jornada`: Permite modificar los horarios de una jornada existente ejecutando un **UPDATE**, evitando la creación de filas duplicadas si el operador corrige un error de tipeo.

## 2. Rediseño del `JornadaWidget` (Gestión de Estados)
La pestaña de Jornada se rediseñó para incluir un sistema estricto de estados basado en botones de acción:

### Modo Edición (`en_edicion = True`)
- Es el estado inicial. Los campos de texto y hora están habilitados.
- **Botón visible:** `Guardar Jornada`.
- **Efecto en Asistencia:** La señal `esta_configurada()` devuelve `False`, lo que **bloquea la cámara** en la pestaña de Asistencia. (El profesor exigía impedir usar la cámara mientras se edita).

### Modo Guardado (`en_edicion = False`)
- Ocurre al presionar *Guardar*. El sistema inserta o actualiza la BD.
- Los inputs se bloquean (quedan en "solo lectura") para evitar accidentes.
- **Botones visibles:** `Editar Jornada` y `Terminar Jornada`.
- **Efecto en Asistencia:** La señal `esta_configurada()` devuelve `True`, habilitando el motor de reconocimiento.
- Si el usuario presiona *Editar*, la interfaz vuelve al Modo Edición y la cámara se apaga automáticamente gracias a nuestro sistema de Señales y Slots (Signal/Slots de PySide6).

### Terminar Jornada (Cierre Suave)
- Al presionar *Terminar Jornada*, el sistema lanza una alerta de confirmación.
- Al aceptar, **NO se elimina el registro** de PostgreSQL (para no corromper el historial de asistencias).
- Simplemente resetea los campos a sus valores por defecto (`--:--`), desvincula el `jornada_id` en memoria, y devuelve la interfaz al Modo Edición, lista para abrir un nuevo turno de portería.
