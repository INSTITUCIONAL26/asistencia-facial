# Sistema de Asistencia por Reconocimiento Facial

Este repositorio contiene la estructura base y el módulo de inicio de sesión de un sistema de asistencia basado en reconocimiento facial.

## Pipeline del Proceso Realizado

A continuación se detallan los pasos y configuraciones implementadas durante el desarrollo de esta etapa:

### 1. Estructura del Proyecto
- Se definió y construyó una arquitectura limpia separando responsabilidades en carpetas específicas (`src/config`, `src/repositories`, `src/ui`, `database/initdb`).
- Se aplicaron reglas de nomenclatura estrictas (minúsculas y guiones).

### 2. Entorno Aislado y Dependencias
- Se creó un entorno virtual (`.venv`) para aislar las dependencias del sistema.
- Se instalaron librerías clave mediante `requirements.txt`: 
  - **PySide6** (Interfaz gráfica).
  - **OpenCV, DeepFace, TensorFlow, Keras** (Motor de reconocimiento facial e IA para uso futuro).
  - **psycopg, python-dotenv** (Conexión a base de datos y variables de entorno).

### 3. Configuración de Base de Datos
- Se configuró la conexión a PostgreSQL utilizando Docker (`compose.yaml`).
- Se implementó el archivo `.env` para proteger las credenciales de acceso a la base de datos (ignorado en el control de versiones).
- Se creó la conexión centralizada a la base de datos mediante Python (`src/config/database.py`).

### 4. Lógica de Repositorio (Capa de Datos)
- Se desarrolló el `user_repository.py` con dos responsabilidades principales:
  - **Consulta:** Búsqueda de credenciales (permitiendo inicio de sesión con Usuario, Email, DNI o CUIL).
  - **Escritura:** Registro de nuevos usuarios insertando los datos directamente en PostgreSQL.

### 5. Interfaz de Usuario (UI)
- **Login:** Se diseñó una ventana de inicio de sesión (`login_window.py`) limpia, con soporte para teclado (tecla Enter).
- **Ojito de Contraseña:** Se integraron iconos SVG interactivos dentro del campo de la contraseña que permiten alternar su visibilidad en tiempo real.
- **Registro:** Se implementó una ventana de registro (`register_window.py`) con validación de campos obligatorios (Usuario y Contraseña) y opcionales (Email, DNI, CUIL, los cuales impactan como NULL en la base de datos si quedan vacíos).
- **Bienvenida:** Se configuró una ventana de aterrizaje (`welcome_window.py`) que saluda al usuario logueado exitosamente.

### 6. Seguridad y Control de Versiones
- Se configuró el archivo `.gitignore` para bloquear la subida de datos sensibles (`.env`), archivos compilados de Python y entornos virtuales (`.venv`).
- Se generó un `.env.example` a modo de plantilla pública.

## Pruebas Realizadas y Resultados
El módulo superó exitosamente las siguientes pruebas funcionales:
- **Login Correcto:** Validación de acceso utilizando diferentes métodos de identificación (Nombre de usuario, Correo, DNI y CUIL).
- **Login Rechazado:** Respuesta correcta del sistema (mensaje de alerta) ante el envío de formularios vacíos o contraseñas incorrectas.
- **Creación de Usuario:** Inserción exitosa de nuevos usuarios a la base de datos desde la interfaz de registro, comprobando el correcto manejo de campos nulos y evitando duplicidades.
- **Visibilidad de Contraseña:** Cambio de estado perfecto del `EchoMode` de la contraseña al pulsar el botón del "ojito".

---

## Guía de Comandos de Operación

Para mantener el sistema optimizado cuando no se está desarrollando, se recomienda pausar los servicios. 

### Base de Datos (Docker)
- **Encender la base de datos:** `docker compose start` (o `docker compose up -d`)
- **Apagar la base de datos:** `docker compose stop`

### Entorno Virtual (.venv)
Dependiendo de tu terminal, los comandos para acceder a la "burbuja" del proyecto son:

**Si usas Símbolo del Sistema (CMD):**
- Activar: `.venv\Scripts\activate.bat`
- Desactivar: `deactivate`

**Si usas PowerShell:**
- Activar: `.\.venv\Scripts\Activate.ps1`
- Desactivar: `deactivate`
