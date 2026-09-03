from config.database import get_connection


class AlumnoRepository:

    def crear_alumno(
        self,
        nombre,
        apellido,
        dni,
        carrera,
        celular,
        correo_electronico,
        fecha_de_nacimiento,
        anio_de_ingreso,
        domicilio,
        libreta,
        telefono=None,
    ):
        """
        Inserta un nuevo alumno en la tabla alumno.
        Retorna el id generado, necesario para luego guardar sus fotos.
        """
        query = """
        INSERT INTO alumno (
            nombre,
            apellido,
            dni,
            carrera,
            celular,
            correo_electronico,
            fecha_de_nacimiento,
            anio_de_ingreso,
            domicilio,
            libreta,
            telefono
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        nombre,
                        apellido,
                        dni,
                        carrera,
                        celular,
                        correo_electronico,
                        fecha_de_nacimiento,
                        anio_de_ingreso,
                        domicilio,
                        libreta,
                        telefono,
                    ),
                )
                alumno_id = cur.fetchone()[0]
            conn.commit()
        return alumno_id

    def guardar_foto(self, alumno_id, angulo, imagen_bytes):
        """
        Inserta una foto de alumno en la tabla foto_alumno.

        Parámetros:
            alumno_id   : id del alumno ya registrado.
            angulo      : string con el valor del ángulo.
                          Valores esperados: 'frontal', 'izquierdo', 'derecho'.
            imagen_bytes: contenido binario de la imagen (bytes).
                          Se obtiene con: open(ruta, 'rb').read()
        """
        query = """
        INSERT INTO foto_alumno (alumno_id, angulo, imagen)
        VALUES (%s, %s, %s);
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (alumno_id, angulo, imagen_bytes))
            conn.commit()
