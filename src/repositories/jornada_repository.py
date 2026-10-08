from config.database import get_connection

class JornadaRepository:
    def crear_jornada(self, fecha, horario_entrada, horario_salida, catedra, usuario_id):
        """Inserta una nueva jornada y retorna su ID."""
        query = """
        INSERT INTO jornada (fecha, horario_entrada, horario_salida, catedra, usuario_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (fecha, horario_entrada, horario_salida, catedra, usuario_id))
                jornada_id = cur.fetchone()[0]
            conn.commit()
        return jornada_id

    def actualizar_jornada(self, jornada_id, horario_entrada, horario_salida, catedra):
        """Actualiza una jornada existente en estado de edición (UPDATE)."""
        query = """
        UPDATE jornada
        SET horario_entrada = %s,
            horario_salida = %s,
            catedra = %s
        WHERE id = %s;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (horario_entrada, horario_salida, catedra, jornada_id))
            conn.commit()
