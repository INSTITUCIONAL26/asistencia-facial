from config.database import get_connection


class InformeRepository:
    """
    Repositorio para consultas de Jornadas y Asistencias requeridas en Exportar Informes.
    Implementa validación estricta de propiedad (usuario_id) en todas las consultas.
    """

    def obtener_jornadas_por_usuario(self, usuario_id: int):
        """
        Retorna las jornadas registradas por el usuario autenticado,
        ordenadas por fecha descendente y horario de entrada descendente.
        Retorna lista de tuplas: (id, fecha, catedra, horario_entrada, horario_salida)
        """
        query = """
        SELECT id, fecha, catedra, horario_entrada, horario_salida
        FROM jornada
        WHERE usuario_id = %s
        ORDER BY fecha DESC, horario_entrada DESC;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (usuario_id,))
                return cur.fetchall()

    def obtener_detalle_jornada(self, jornada_id: int, usuario_id: int):
        """
        Retorna los metadatos de la jornada y el nombre de usuario que la registró,
        validando estrictamente que la jornada pertenezca al usuario autenticado.
        Retorna tupla: (id, fecha, catedra, horario_entrada, horario_salida, nombre_usuario) o None.
        """
        query = """
        SELECT j.id, j.fecha, j.catedra, j.horario_entrada, j.horario_salida, u.nombre_usuario
        FROM jornada j
        JOIN usuario u ON j.usuario_id = u.id
        WHERE j.id = %s AND j.usuario_id = %s;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (jornada_id, usuario_id))
                return cur.fetchone()

    def obtener_asistencias_jornada(self, jornada_id: int, usuario_id: int):
        """
        Retorna los alumnos que registraron asistencia en la jornada indicada,
        ordenados alfabéticamente por Apellido y luego por Nombre.
        Valida que la jornada pertenezca al usuario autenticado.
        Retorna lista de tuplas: (apellido, nombre, dni, libreta, entrada, salida)
        """
        query = """
        SELECT 
            al.apellido,
            al.nombre,
            COALESCE(al.dni, ''),
            COALESCE(al.libreta, ''),
            asi.entrada,
            asi.salida
        FROM asistencia asi
        JOIN alumno al ON asi.alumno_id = al.id
        JOIN jornada j ON asi.jornada_id = j.id
        WHERE asi.jornada_id = %s AND j.usuario_id = %s
        ORDER BY al.apellido ASC, al.nombre ASC;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (jornada_id, usuario_id))
                return cur.fetchall()
