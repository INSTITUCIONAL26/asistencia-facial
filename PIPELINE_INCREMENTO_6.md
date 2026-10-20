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

### ⏳ Fase 2: Motores de Exportación (Excel y PDF)
- [ ] Creación de `ExcelExportService` (`src/services/excel_export_service.py`) usando `openpyxl`:
  - Encabezado de la Jornada y estilos tipográficos.
  - Tabla de alumnos con bordes, anchos de columna dinámicos y formatos de hora.
  - Gestión de `Sin registrar`, jornadas vacías y contador singular/plural.
- [ ] Creación de `PdfExportService` (`src/services/pdf_export_service.py`) usando `reportlab`:
  - Documento `SimpleDocTemplate` con `Table`, `TableStyle` y `ParagraphStyle`.
  - Estructuración de encabezado, tabla y leyenda final.

### ⏳ Fase 3: Interfaz de Usuario e Integración en Menú Lateral
- [ ] Creación de `InformesWidget` (`src/ui/informes_widget.py`) con `QTableWidget`:
  - Columnas: `Fecha`, `Cátedra`, `Horario` (`HH:MM - HH:MM`), botón `Excel` y botón `PDF`.
  - Método `recargar_datos()` para refresco dinámico al entrar.
- [ ] Integración en `MainWindow`:
  - Cuarto botón en Menú lateral: `Exportar Informes`.
  - Conexión con `QFileDialog` para selección de carpeta/nombre sugerido.

### ⏳ Fase 4: Pruebas Integrales y Casos Especiales
- [ ] Validación de los 10 casos de prueba obligatorios de la rúbrica.
- [ ] Pruebas de seguridad multisesión y no filtrado por jornada terminada.
