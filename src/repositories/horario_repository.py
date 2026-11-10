"""
Módulo de repositorio para Carreras, Cátedras y Obligaciones Horarias.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from datetime import date, time, datetime, timedelta
from typing import Optional, List, Dict, Any
from config.database import get_connection


class HorarioRepository:
    """
    Gestiona la estructura académica (Carreras, Cátedras)
    y las obligaciones horarias (Clases de 1h 20m, Mesas de Examen, Jornadas).
    """

    # --- Carreras y Cátedras ---

    def obtener_carreras(self) -> List[Dict[str, Any]]:
        """Retorna todas las carreras institucionales."""
        query = "SELECT id, nombre FROM carrera ORDER BY nombre ASC;"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return [{"id": r[0], "nombre": r[1]} for r in cur.fetchall()]

    def obtener_catedras(self, carrera_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retorna las cátedras, opcionalmente filtradas por carrera."""
        query = """
        SELECT cat.id, cat.nombre, car.id, car.nombre
        FROM catedra cat
        JOIN carrera car ON cat.carrera_id = car.id
        """
        params = []
        if carrera_id:
            query += " WHERE cat.carrera_id = %s"
            params.append(carrera_id)
        query += " ORDER BY car.nombre ASC, cat.nombre ASC;"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return [
                    {
                        "id": r[0],
                        "nombre": r[1],
                        "carrera_id": r[2],
                        "carrera_nombre": r[3],
                    }
                    for r in cur.fetchall()
                ]

    # --- Obligaciones Horarias ---

    def crear_obligacion(
        self,
        docente_id: int,
        tipo_actividad: str,
        horario_entrada: time,
        horario_salida: time,
        catedra_id: Optional[int] = None,
        dia_semana: Optional[str] = None,
        fecha_especifica: Optional[date] = None,
        rol_mesa: Optional[str] = None,
    ) -> int:
        """
        Registra una obligación horaria para el docente.
        - tipo_actividad: 'clase', 'jornada', 'mesa_examen'
        - dia_semana: 'lunes' .. 'sabado' (para clases semanales recurrentes)
        - fecha_especifica: date (para Mesas de Examen o Jornadas)
        - rol_mesa: 'presidente', 'vocal', 'auxiliar' (solo si tipo_actividad == 'mesa_examen')
        """
        query = """
        INSERT INTO obligacion_horaria (
            docente_id, catedra_id, tipo_actividad, dia_semana,
            fecha_especifica, horario_entrada, horario_salida, rol_mesa
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        dia = dia_semana.lower().strip() if dia_semana else None
        rol = rol_mesa.lower().strip() if rol_mesa else None

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        docente_id,
                        catedra_id,
                        tipo_actividad.lower().strip(),
                        dia,
                        fecha_especifica,
                        horario_entrada,
                        horario_salida,
                        rol,
                    ),
                )
                obligacion_id = cur.fetchone()[0]
            conn.commit()
        return obligacion_id

    def obtener_obligaciones_por_docente(self, docente_id: int) -> List[Dict[str, Any]]:
        """
        Retorna la grilla horaria completa asignada a un docente.
        """
        query = """
        SELECT 
            oh.id, oh.tipo_actividad, oh.dia_semana, oh.fecha_especifica,
            oh.horario_entrada, oh.horario_salida, oh.rol_mesa,
            COALESCE(cat.nombre, 'Jornada Institucional') as catedra_nombre,
            COALESCE(car.nombre, 'Institucional') as carrera_nombre
        FROM obligacion_horaria oh
        LEFT JOIN catedra cat ON oh.catedra_id = cat.id
        LEFT JOIN carrera car ON cat.carrera_id = car.id
        WHERE oh.docente_id = %s
        ORDER BY oh.fecha_especifica DESC NULLS LAST, oh.horario_entrada ASC;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id,))
                rows = cur.fetchall()
                return [
                    {
                        "id": r[0],
                        "tipo_actividad": r[1],
                        "dia_semana": r[2],
                        "fecha_especifica": r[3],
                        "horario_entrada": r[4],
                        "horario_salida": r[5],
                        "rol_mesa": r[6],
                        "catedra_nombre": r[7],
                        "carrera_nombre": r[8],
                    }
                    for r in rows
                ]

    def obtener_obligacion_actual(
        self,
        docente_id: int,
        fecha_actual: date,
        hora_actual: time,
        margen_anticipacion_minutos: int = 45,
    ) -> Optional[Dict[str, Any]]:
        """
        Determina qué obligación horaria le corresponde a un docente en el momento actual.
        
        Reglas de prioridad:
        1. Prioridad Máxima: Eventos puntuales de hoy (Mesa de Examen o Jornada con fecha_especifica = hoy).
        2. Clases semanales fijas (dia_semana coincidente con el día de hoy).
        3. Manejo de ventana temporal:
           - Permite marcar entrada desde 'margen_anticipacion_minutos' antes del horario_entrada.
           - Cubre toda la duración de la clase y hasta 30 minutos después de horario_salida para permitir salida tardía.
        4. Clases consecutivas: Si hay varias en curso o próximas, selecciona la que esté más cercana al horario_entrada.
        """
        dias_espanol = {
            0: "lunes",
            1: "martes",
            2: "miercoles",
            3: "jueves",
            4: "viernes",
            5: "sabado",
            6: "domingo",
        }
        dia_semana_nombre = dias_espanol[fecha_actual.weekday()]

        query = """
        SELECT 
            oh.id, oh.tipo_actividad, oh.dia_semana, oh.fecha_especifica,
            oh.horario_entrada, oh.horario_salida, oh.rol_mesa,
            COALESCE(cat.nombre, 'Jornada Institucional') as catedra_nombre,
            COALESCE(car.nombre, 'Institucional') as carrera_nombre
        FROM obligacion_horaria oh
        LEFT JOIN catedra cat ON oh.catedra_id = cat.id
        LEFT JOIN carrera car ON cat.carrera_id = car.id
        WHERE oh.docente_id = %s
          AND (
              (oh.fecha_especifica = %s)
              OR (oh.fecha_especifica IS NULL AND oh.dia_semana = %s)
          )
        ORDER BY 
          -- Priorizar eventos de fecha específica sobre clases semanales
          CASE WHEN oh.fecha_especifica IS NOT NULL THEN 0 ELSE 1 END,
          -- Ordenar por proximidad al horario de entrada
          ABS(EXTRACT(EPOCH FROM (oh.horario_entrada - %s::time)));
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id, fecha_actual, dia_semana_nombre, hora_actual))
                candidatos = cur.fetchall()

        if not candidatos:
            return None

        # Evaluar dentro de la ventana de validez de cada candidato
        dt_actual = datetime.combine(fecha_actual, hora_actual)

        for c in candidatos:
            h_entrada = c[4]
            h_salida = c[5]

            dt_inicio_valido = datetime.combine(fecha_actual, h_entrada) - timedelta(minutes=margen_anticipacion_minutos)
            dt_fin_valido = datetime.combine(fecha_actual, h_salida) + timedelta(minutes=45)

            if dt_inicio_valido <= dt_actual <= dt_fin_valido:
                return {
                    "id": c[0],
                    "tipo_actividad": c[1],
                    "dia_semana": c[2],
                    "fecha_especifica": c[3],
                    "horario_entrada": c[4],
                    "horario_salida": c[5],
                    "rol_mesa": c[6],
                    "catedra_nombre": c[7],
                    "carrera_nombre": c[8],
                }

        # Si ninguno calza en la ventana horaria, retorna None (Docente sin actividad en este horario)
        return None
