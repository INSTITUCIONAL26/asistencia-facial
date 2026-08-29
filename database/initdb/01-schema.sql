-- Este script es de respaldo/documentación. 
-- La base de datos ya fue inicializada.

CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    correo_electronico VARCHAR(100),
    dni VARCHAR(20),
    cuil VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS jornada (
    id SERIAL PRIMARY KEY,
    fecha DATE,
    horario_salida TIME,
    horario_entrada TIME,
    usuario_id INTEGER REFERENCES usuario(id)
);

-- Aquí se agregarían las demás tablas (alumno, asistencia, foto_alumno)
-- según el diagrama completo.
