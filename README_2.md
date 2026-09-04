# Reporte de Avance — Incremento 3

Este documento detalla el progreso funcional y técnico de los **Pasos 1 al 5** del Incremento 3, destacando el fiel cumplimiento de los requisitos de negocio y las restricciones impuestas (consigna).

---

## 🏗️ Paso 1: Adecuación de Base de Datos y Repositorios
Se preparó el terreno de la base de datos para soportar los nuevos requerimientos.
- **Base de Datos:** Se actualizó el esquema DDL (`01-schema.sql`) para reflejar la realidad de PostgreSQL, agregando la columna `catedra` (VARCHAR) a la tabla `jornada` y asegurando que `foto_alumno` utilice tipo `bytea` para almacenar las imágenes directamente en la base.
- **Backend:** Se creó la capa de persistencia mediante la clase `AlumnoRepository`.
  - Método `crear_alumno()`: Inserta todos los datos personales exigidos y captura el ID generado mediante la cláusula `RETURNING id`.
  - Método `guardar_foto()`: Recibe el ID del alumno recién creado y almacena la captura en formato binario para los ángulos requeridos (`frontal`, `izquierdo`, `derecho`).

## 🪟 Paso 2: Creación de la Ventana Principal y Menú
Se estructuró la navegación base de la aplicación.
- Se eliminó la pantalla `WelcomeWindow` de prueba y se construyó `MainWindow`.
- **Estructura Requerida:** Se programó un menú lateral (Sidebar) utilizando componentes nativos y un área de contenido (`QStackedWidget`) que permite navegar entre las tres opciones (Captura, Jornada, Registrar Alumno) sin destruir la vista anterior, lo que garantiza que variables en memoria no se pierdan al navegar.
- **Integración:** El flujo desde el Login fue conectado de forma segura, transfiriendo el `usuario_id` y `nombre_usuario` para que el sistema salude al operador de turno y quede registrado internamente para usos futuros.

## 📅 Paso 3: Configuración de Jornada (`JornadaWidget`)
Se implementó el formulario inicial operativo para el uso diario.
- **Campos Solicitados:** Fecha automática en Label, Horarios de Entrada y Salida, y Cátedra como campo de texto.
- **Manejo de Tiempos:** Se usó `QTimeEdit` forzando el formato por defecto `--:--` (el cual no se confunde con `00:00`, dándole soporte robusto para turnos de madrugada).
- **Cumplimiento de Consigna:** Tal como fue dictado por las reglas, los valores **sólo viven en memoria** por ahora. No se persiste la jornada en la BD ni se incluyó botón "Guardar", dejando todo listo para el próximo incremento.

## 📷 Paso 4: Asistencia por Captura Facial (`AsistenciaWidget`)
Se construyó el motor que orquestará el futuro feed de video.
- **Manejo de Estado:** Se incluyó un botón tipo Toggle (▶ Abrir / ⏹ Cerrar).
- **Regla de Negocio Estricta:** Se respetó la lógica condicional prioritaria. Si un usuario intenta "Abrir Cámara", el sistema interactúa con el `JornadaWidget` en memoria (`esta_configurada()`). Si no hay jornada, salta inmediatamente el `QMessageBox` de advertencia prohibiendo el encendido.

## 👥 Paso 5: Registrar Alumno (`RegistrarAlumnoWidget`)
El módulo más complejo a nivel formulario de este incremento.
- **Grilla de Datos Personales:** 10 campos estrictos diseñados para validar el formato (`QRegularExpressionValidator` para evitar letras en DNI/Celular). Se combinó `QDateEdit` y `QSpinBox` para agilizar fechas.
- **Biometría Requerida:** Se creó un componente encapsulado y escalable llamado `AnguloFotoWidget` instanciado las 3 veces requeridas (Frontal, Izquierdo, Derecho). Permite cargar archivo de disco, previsualizarlo en miniatura y leer sus bytes.
- **Persistencia Directa:** Al presionar "Registrar Alumno", se validan los 10 textos y la presencia ineludible de las 3 imágenes. Una vez aprobado, guarda todo atómicamente en PostgreSQL y blanquea el formulario.

## ✨ Cierre Final: Interfaz Profesional Uniforme
- Lejos de usar herramientas web que rompan el paradigma PySide6, se construyó un tema oscuro profesional 100% nativo que continúa visualmente al diseño de la ventana de Inicio de Sesión original.
- Se adoptaron **íconos SVG puros (Lucide)** para el Sidebar y para controles de sistema (Selectores de Fechas y Valores), reemplazando los emojis primitivos y dándole una robustez de calidad corporativa a la herramienta.

---

> **Estatus:** El **Incremento 3** está finalizado, habiendo respetado minuciosamente las restricciones funcionales requeridas y logrando un producto final sumamente estable.
