-- ============================================================
-- TRABAJO FINAL DE CURSADA - RECONOCIMIENTO VISUAL
-- Contexto A: Asistencia para docentes del IES N.º 7 Populorum Progressio
-- Motor: PostgreSQL 15+
-- Archivo: database/initdb/01-schema.sql
-- ============================================================

-- ------------------------------------------------------------
-- Tabla: usuario
-- Descripción: Operadores del sistema en mesa de entrada / bedelía
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
    id                  SERIAL PRIMARY KEY,
    nombre_usuario      VARCHAR(50)  UNIQUE NOT NULL,
    contrasenia         VARCHAR(255) NOT NULL,
    correo_electronico  VARCHAR(100) UNIQUE,
    dni                 VARCHAR(20)  UNIQUE,
    cuil                VARCHAR(20)  UNIQUE,
    rol                 VARCHAR(50)  NOT NULL DEFAULT 'administrativo'
);

-- ------------------------------------------------------------
-- Tabla: docente
-- Descripción: Profesores del instituto identificados por biometría
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS docente (
    id                   SERIAL PRIMARY KEY,
    legajo               VARCHAR(50)  UNIQUE NOT NULL,
    nombre               VARCHAR(100) NOT NULL,
    apellido             VARCHAR(100) NOT NULL,
    dni                  VARCHAR(20)  UNIQUE NOT NULL,
    cuil                 VARCHAR(20)  UNIQUE NOT NULL,
    correo_electronico   VARCHAR(100),
    telefono             VARCHAR(30),
    domicilio            VARCHAR(255),
    activo               BOOLEAN NOT NULL DEFAULT TRUE
);

-- ------------------------------------------------------------
-- Tabla: foto_docente
-- Descripción: Vectores e imágenes biométricas por ángulo
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS foto_docente (
    id          SERIAL PRIMARY KEY,
    docente_id  INTEGER NOT NULL REFERENCES docente(id) ON DELETE CASCADE,
    angulo      VARCHAR(20) NOT NULL, -- 'frontal', 'izquierdo', 'derecho'
    imagen      BYTEA NOT NULL
);

-- ------------------------------------------------------------
-- Tabla: carrera
-- Descripción: Carreras de nivel terciario del IES N.º 7
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS carrera (
    id      SERIAL PRIMARY KEY,
    nombre  VARCHAR(150) UNIQUE NOT NULL
);

-- ------------------------------------------------------------
-- Tabla: catedra
-- Descripción: Materias/cátedras asociadas a una carrera
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS catedra (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(150) NOT NULL,
    carrera_id  INTEGER NOT NULL REFERENCES carrera(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Tabla: obligacion_horaria
-- Descripción: Asignaciones de clases (1h 20m), Jornadas y Mesas
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS obligacion_horaria (
    id                SERIAL PRIMARY KEY,
    docente_id        INTEGER NOT NULL REFERENCES docente(id) ON DELETE CASCADE,
    catedra_id        INTEGER REFERENCES catedra(id) ON DELETE SET NULL, -- Nullable para Jornadas Institucionales
    tipo_actividad    VARCHAR(30) NOT NULL CHECK (tipo_actividad IN ('clase', 'jornada', 'mesa_examen')),
    dia_semana        VARCHAR(20) CHECK (dia_semana IN ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado')),
    fecha_especifica  DATE, -- Para eventos puntuales (Mesas de examen o Jornadas)
    horario_entrada   TIME NOT NULL,
    horario_salida    TIME NOT NULL,
    rol_mesa          VARCHAR(30) CHECK (rol_mesa IN ('presidente', 'vocal', 'auxiliar'))
);

-- ------------------------------------------------------------
-- Tabla: asistencia
-- Descripción: Registro de entrada y salida presencial confirmado
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS asistencia (
    id                 SERIAL PRIMARY KEY,
    docente_id         INTEGER NOT NULL REFERENCES docente(id) ON DELETE CASCADE,
    obligacion_id      INTEGER REFERENCES obligacion_horaria(id) ON DELETE SET NULL,
    fecha              DATE NOT NULL,
    entrada            TIMESTAMP NOT NULL,
    salida             TIMESTAMP,
    estado_entrada     VARCHAR(20) NOT NULL CHECK (estado_entrada IN ('en_horario', 'tardanza')),
    minutos_tardanza   INTEGER NOT NULL DEFAULT 0,
    estado_salida      VARCHAR(20) NOT NULL DEFAULT 'sin_salida' CHECK (estado_salida IN ('normal', 'anticipada', 'sin_salida')),
    minutos_anticipada INTEGER NOT NULL DEFAULT 0,
    observaciones      VARCHAR(255)
);

-- ------------------------------------------------------------
-- Tabla: licencia_docente
-- Descripción: Días particulares (máx 6 anuales) y licencias médicas
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS licencia_docente (
    id                              SERIAL PRIMARY KEY,
    docente_id                      INTEGER NOT NULL REFERENCES docente(id) ON DELETE CASCADE,
    tipo                            VARCHAR(20) NOT NULL CHECK (tipo IN ('particular', 'medica')),
    fecha_desde                     DATE NOT NULL,
    fecha_hasta                     DATE NOT NULL,
    anio                            INTEGER NOT NULL,
    estado                          VARCHAR(20) NOT NULL DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'confirmada', 'rechazada')),
    certificado_presentado          BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_presentacion_certificado  DATE,
    motivo                          VARCHAR(255),
    CONSTRAINT chk_licencia_fechas CHECK (fecha_hasta >= fecha_desde)
);

-- ============================================================
-- DATOS INICIALES (SEMILLA / FIXTURES) PARA EL IES N.º 7
-- ============================================================

-- Carreras de ejemplo
INSERT INTO carrera (nombre) VALUES 
('Tecnicatura Superior en Desarrollo de Software'),
('Tecnicatura Superior en Enfermería')
ON CONFLICT (nombre) DO NOTHING;

-- Cátedras de ejemplo
INSERT INTO catedra (nombre, carrera_id) VALUES 
('Programación Visual', 1),
('Bases de Datos II', 1),
('Práctica Profesionalizante I', 1),
('Anatomía y Fisiología', 2)
ON CONFLICT DO NOTHING;
