"""
Módulo de repositorio para el registro y auditoría de Asistencias Docentes.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from config.database import get_connection


class AsistenciaRepository:
    """
    Gestiona la persistencia de entradas, salidas, tardanzas y salidas anticipadas.
    """

    def registrar_entrada(
        self,
        docente_id: int,
        obligacion_id: Optional[int],
        fecha: date,
        entrada: datetime,
        estado_entrada: str,
        minutos_tardanza: int = 0,
        observaciones: Optional[str] = None,
    ) -> int:
        """
        Inserta un nuevo registro de entrada presencial en la tabla 'asistencia'.
        estado_entrada: 'en_horario' o 'tardanza'
        Retorna el ID de asistencia generado.
        """
        query = """
        INSERT INTO asistencia (
            docente_id, obligacion_id, fecha, entrada,
            estado_entrada, minutos_tardanza, estado_salida,
            minutos_anticipada, observaciones
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'sin_salida', 0, %s)
        RETURNING id;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        docente_id,
                        obligacion_id,
                        fecha,
                        entrada,
                        estado_entrada.lower().strip(),
                        minutos_tardanza,
                        observaciones,
                    ),
                )
                asistencia_id = cur.fetchone()[0]
            conn.commit()
        return asistencia_id

    def registrar_salida(
        self,
        asistencia_id: int,
        salida: datetime,
        estado_salida: str,
        minutos_anticipada: int = 0,
        observaciones: Optional[str] = None,
    ) -> None:
        """
        Actualiza la marcación de salida de un registro de asistencia abierto.
        estado_salida: 'normal' o 'anticipada'
        """
        query = """
        UPDATE asistencia
        SET salida = %s,
            estado_salida = %s,
            minutos_anticipada = %s,
            observaciones = COALESCE(%s, observaciones)
        WHERE id = %s;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        salida,
                        estado_salida.lower().strip(),
                        minutos_anticipada,
                        observaciones,
                        asistencia_id,
                    ),
                )
            conn.commit()

    def obtener_asistencia_del_dia(
        self,
        docente_id: int,
        obligacion_id: int,
        fecha: date,
    ) -> Optional[Dict[str, Any]]:
        """
        Retorna el registro de asistencia del docente para una obligación horaria y fecha dada.
        Permite saber si ya marcó entrada y si la salida está pendiente.
        """
        query = """
        SELECT id, docente_id, obligacion_id, fecha, entrada, salida,
               estado_entrada, minutos_tardanza, estado_salida, minutos_anticipada,
               observaciones
        FROM asistencia
        WHERE docente_id = %s AND obligacion_id = %s AND fecha = %s
        ORDER BY entrada DESC
        LIMIT 1;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id, obligacion_id, fecha))
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "docente_id": row[1],
                    "obligacion_id": row[2],
                    "fecha": row[3],
                    "entrada": row[4],
                    "salida": row[5],
                    "estado_entrada": row[6],
                    "minutos_tardanza": row[7],
                    "estado_salida": row[8],
                    "minutos_anticipada": row[9],
                    "observaciones": row[10],
                }

    def obtener_historial_docente(
        self,
        docente_id: int,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retorna el historial de asistencias de un docente entre un rango de fechas.
        """
        query = """
        SELECT 
            asi.id, asi.fecha, asi.entrada, asi.salida,
            asi.estado_entrada, asi.minutos_tardanza,
            asi.estado_salida, asi.minutos_anticipada,
            COALESCE(cat.nombre, 'Jornada Institucional') as actividad_nombre,
            oh.tipo_actividad, oh.horario_entrada, oh.horario_salida
        FROM asistencia asi
        LEFT JOIN obligacion_horaria oh ON asi.obligacion_id = oh.id
        LEFT JOIN catedra cat ON oh.catedra_id = cat.id
        WHERE asi.docente_id = %s
        """
        params = [docente_id]
        if fecha_desde:
            query += " AND asi.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND asi.fecha <= %s"
            params.append(fecha_hasta)

        query += " ORDER BY asi.fecha DESC, asi.entrada DESC;"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                return [
                    {
                        "id": r[0],
                        "fecha": r[1],
                        "entrada": r[2],
                        "salida": r[3],
                        "estado_entrada": r[4],
                        "minutos_tardanza": r[5],
                        "estado_salida": r[6],
                        "minutos_anticipada": r[7],
                        "actividad_nombre": r[8],
                        "tipo_actividad": r[9],
                        "horario_esperado_entrada": r[10],
                        "horario_esperado_salida": r[11],
                    }
                    for r in rows
                ]
