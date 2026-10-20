# 🚀 PIPELINE INCREMENTO 6 - Exportación de Informes de Asistencia en Excel y PDF

Este documento detalla la planificación técnica, los requisitos obligatorios de la cátedra y las fases de implementación del **Sexto Incremento** del Sistema de Asistencia por Reconocimiento Facial.

---

## 🎯 Objetivo General
Incorporar una nueva sección **Exportar Informes** que permita consultar el historial de Jornadas registradas por el usuario autenticado y generar, para cada Jornada, una planilla de asistencia formal en formato **Excel (.xlsx)** o **PDF (.pdf)**.

---

## 📌 Requisitos y Reglas de Negocio Obligatorias
1. **Nuevas Dependencias Oficiales:**
   - `openpyxl`: Generación y formateo de planillas Excel (.xlsx).
   - `reportlab`: Construcción del documento PDF (.pdf) y sus tablas.
2. **Propiedad y Seguridad de Datos (Regla Funcional Estricta):**
   - Un usuario sólo puede listar y exportar **sus propias Jornadas** (`WHERE usuario_id = %s`).
   - Al exportar, la consulta a base de datos vuelve a validar `jornada.usuario_id = %s` (seguridad en la capa de datos, no solo visual).
3. **Ordenamiento Obligatorio:**
   - Listado de Jornadas: `ORDER BY fecha DESC, horario_entrada DESC`.
   - Listado de Alumnos en el Informe: `ORDER BY apellido ASC, nombre ASC`.
4. **Estructura del Informe (Excel y PDF):**
   - **Datos de la Jornada:** Fecha, Cátedra, Horario de entrada, Horario de salida, Nombre del Usuario docente.
   - **Tabla de Alumnos Presentes:** Columnas `#` (índice 1, 2, 3...), `Apellido`, `Nombre`, `DNI`, `Libreta`, `Entrada`, `Salida`.
   - **Salida Faltante:** Si `salida IS NULL`, mostrar exactamente el texto `Sin registrar`.
   - **Jornada sin asistencias:** Generar el archivo igualmente, mostrando el mensaje `No se registraron asistencias para esta Jornada.` y contador en 0.
   - **Contador Final:**
     - Singular: `Se registró 1 alumno presente en total.`
     - Plural: `Se registraron X alumnos presentes en total.`
5. **Workflow de Exportación:**
   - Diálogo nativo `Guardar como...` (`QFileDialog.getSaveFileName`).
   - Nombre sugerido por defecto: `asistencia_YYYY-MM-DD_catedra-slug.xlsx` / `.pdf`.
   - Si el usuario cancela el diálogo, no generar archivo ni mostrar error.
   - Refresco dinámico: Al ingresar a la sección de Informes, recargar datos desde PostgreSQL para incluir jornadas creadas en la misma sesión.

---

## 🗺️ Fases de Implementación

### ✅ Fase 1: Entorno, Dependencias y Capa de Datos (Completada)
- [x] Instalación de `openpyxl` y `reportlab` en `.venv`.
- [x] Actualización de `requirements.txt`.
- [x] Creación de `InformeRepository` (`src/repositories/informe_repository.py`) con validación estricta de `usuario_id` en consultas:
  - `obtener_jornadas_por_usuario(usuario_id)`
  - `obtener_detalle_jornada(jornada_id, usuario_id)`
  - `obtener_asistencias_jornada(jornada_id, usuario_id)`

### ✅ Fase 2: Motores de Exportación (Excel y PDF) (Completada)
- [x] Creación de `ExcelExportService` (`src/services/excel_export_service.py`) usando `openpyxl`:
  - Encabezado con datos completos de la Jornada (Fecha, Cátedra, Horarios y Usuario docente).
  - Tabla de alumnos con índices, alineación diferenciada, fondos cebra y bordes finos.
  - Ajuste automático de anchos de columna para evitar textos truncados (`###`).
  - Caso especial: Salida NULL representada como `Sin registrar`.
  - Caso especial: Jornadas sin asistencias (`No se registraron asistencias para esta Jornada.`).
  - Contador final con gramática estricta (singular/plural y 0 alumnos).
  - Función generadora de nombre sugerido oficial: `asistencia_YYYY-MM-DD_<catedra-slug>.xlsx`.
- [x] Creación de `PdfExportService` (`src/services/pdf_export_service.py`) usando `reportlab`:
  - Maquetado en hoja A4 con márgenes de 36 pt y anchos proporcionales exactos (520 pt).
  - Tabla estilizada con cabecera en azul corporativo (`#1F497D`), texto blanco y bordes sutiles.
  - Tratamiento idéntico de casos especiales (`Sin registrar`, 0 asistencias y contadores).
  - Función generadora de nombre sugerido oficial: `asistencia_YYYY-MM-DD_<catedra-slug>.pdf`.

### ✅ Fase 3: Interfaz de Usuario e Integración en Menú Lateral (Completada)
- [x] Creación de `InformesWidget` (`src/ui/informes_widget.py`) con `QTableWidget`:
  - Columnas oficiales: `Fecha`, `Cátedra`, `Horario` (`HH:MM - HH:MM`), botón `Excel` y botón `PDF`.
  - Botones de acción independientes por fila con iconos y colores corporativos (verde Excel y rojo PDF).
  - Integración nativa de `QFileDialog.getSaveFileName` con nombres sugeridos oficiales.
  - Refresco automático al ingresar a la pestaña (`showEvent` y hook en `cambiar_vista`).
  - Manejo de estado vacío ("No se encontraron Jornadas registradas...") y protección ante fallos de conexión.
- [x] Integración en `MainWindow`:
  - Cuarto botón en Menú lateral: `Exportar Informes` con icono `file-text.svg`.
  - Incorporación en el `QStackedWidget` (índice 3).
  - Vinculación con `usuario_id` del docente autenticado.

### ⏳ Fase 4: Pruebas Integrales y Casos Especiales
- [ ] Validación de los 10 casos de prueba obligatorios de la rúbrica.
- [ ] Pruebas de seguridad multisesión y no filtrado por jornada terminada.
