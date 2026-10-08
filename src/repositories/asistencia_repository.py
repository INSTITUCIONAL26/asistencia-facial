from config.database import get_connection

class AsistenciaRepository:
    def registrar_entrada(self, alumno_id, jornada_id):
        """Registra la hora de entrada dejando la salida en NULL."""
        query = """
        INSERT INTO asistencia (alumno_id, jornada_id, entrada) 
        VALUES (%s, %s, CURRENT_TIMESTAMP) RETURNING id;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (alumno_id, jornada_id))
                asistencia_id = cur.fetchone()[0]
            conn.commit()
        return asistencia_id

    def registrar_salida(self, asistencia_id):
        """Registra la hora de salida de una asistencia existente."""
        query = "UPDATE asistencia SET salida = CURRENT_TIMESTAMP WHERE id = %s;"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (asistencia_id,))
            conn.commit()

    def obtener_asistencia_activa(self, alumno_id, jornada_id):
        """Devuelve (id, entrada, salida) si el alumno ya tiene un registro en esta jornada."""
        query = """
        SELECT id, entrada, salida 
        FROM asistencia 
        WHERE alumno_id = %s AND jornada_id = %s;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (alumno_id, jornada_id))
                row = cur.fetchone()
        return row
