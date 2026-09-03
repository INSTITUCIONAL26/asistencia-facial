-- ============================================================
-- SCHEMA COMPLETO DEL PROYECTO ASISTENCIA FACIAL
-- Última actualización: Incremento 4
-- Motor: PostgreSQL
-- ============================================================

-- ------------------------------------------------------------
-- Tabla: usuario
-- Descripción: Usuarios del sistema (docentes/administradores)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
    id                  SERIAL PRIMARY KEY,
    nombre_usuario      VARCHAR(50)  UNIQUE NOT NULL,
    contrasenia         VARCHAR(255) NOT NULL,
    correo_electronico  VARCHAR(100) UNIQUE,
    dni                 VARCHAR(20)  UNIQUE,
    cuil                VARCHAR(20)  UNIQUE
);

-- ------------------------------------------------------------
-- Tabla: jornada
-- Descripción: Jornada académica del día, asociada a un usuario
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS jornada (
    id              SERIAL PRIMARY KEY,
    fecha           DATE,
    horario_entrada TIME,
    horario_salida  TIME,
    catedra         VARCHAR(150),
    usuario_id      INTEGER REFERENCES usuario(id)
);

-- ------------------------------------------------------------
-- Tabla: alumno
-- Descripción: Datos personales de los alumnos registrados
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alumno (
    id                   SERIAL PRIMARY KEY,
    nombre               VARCHAR(100) NOT NULL,
    apellido             VARCHAR(100) NOT NULL,
    dni                  VARCHAR(20),
    carrera              VARCHAR(150),
    celular              VARCHAR(30),
    telefono             VARCHAR(30),
    correo_electronico   VARCHAR(100),
    fecha_de_nacimiento  DATE,
    anio_de_ingreso      INTEGER,
    domicilio            VARCHAR(255),
    libreta              VARCHAR(50)
);

-- ------------------------------------------------------------
-- Tabla: foto_alumno
-- Descripción: Imágenes biométricas del alumno por ángulo.
--              La columna 'angulo' almacena un string con uno
--              de los valores: 'frontal', 'izquierdo', 'derecho'.
--              La imagen se almacena como binario (bytea).
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS foto_alumno (
    id          SERIAL PRIMARY KEY,
    alumno_id   INTEGER REFERENCES alumno(id),
    angulo      VARCHAR(20),
    imagen      BYTEA
);

-- ------------------------------------------------------------
-- Tabla: asistencia
-- Descripción: Registro de entrada/salida de alumnos por jornada
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS asistencia (
    id          SERIAL PRIMARY KEY,
    alumno_id   INTEGER REFERENCES alumno(id),
    jornada_id  INTEGER REFERENCES jornada(id),
    entrada     TIMESTAMP NOT NULL,
    salida      TIMESTAMP
);
