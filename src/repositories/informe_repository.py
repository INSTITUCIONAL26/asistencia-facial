"""
Módulo de repositorio para Consultas e Informes Administrativos.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from datetime import date
from typing import Optional, List, Dict, Any
from config.database import get_connection


class InformeRepository:
    """
    Proporciona consultas consolidadas para el personal de secretaría y bedelía:
    - Cruce automático de marcaciones biométricas vs horarios esperados.
    - Auditoría de tardanzas (minutos de demora) y salidas anticipadas.
    - Detección de salidas sin registrar (pendientes de revisión).
    - Monitoreo del cupo anual de 6 particulares y seguimiento de certificados médicos.
    """

    def obtener_informe_asistencias(
        self,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        docente_id: Optional[int] = None,
        carrera_id: Optional[int] = None,
        catedra_id: Optional[int] = None,
        solo_anomalias: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Retorna la planilla analítica de asistencias cruzada contra las obligaciones horarias.
        Si 'solo_anomalias' es True, filtra únicamente registros con Tardanza, Salida Anticipada o Sin Salida.
        """
        query = """
        SELECT 
            asi.id,
            d.id as docente_id,
            d.legajo,
            d.apellido || ', ' || d.nombre as docente_nombre,
            COALESCE(car.nombre, 'Institucional') as carrera_nombre,
            COALESCE(cat.nombre, 'Jornada Institucional') as actividad_nombre,
            oh.tipo_actividad,
            oh.rol_mesa,
            asi.fecha,
            oh.horario_entrada as horario_previsto_entrada,
            oh.horario_salida as horario_previsto_salida,
            asi.entrada as hora_marcada_entrada,
            asi.estado_entrada,
            asi.minutos_tardanza,
            asi.salida as hora_marcada_salida,
            asi.estado_salida,
            asi.minutos_anticipada,
            asi.observaciones
        FROM asistencia asi
        JOIN docente d ON asi.docente_id = d.id
        LEFT JOIN obligacion_horaria oh ON asi.obligacion_id = oh.id
        LEFT JOIN catedra cat ON oh.catedra_id = cat.id
        LEFT JOIN carrera car ON cat.carrera_id = car.id
        WHERE 1=1
        """
        params = []
        if fecha_desde:
            query += " AND asi.fecha >= %s"
            params.append(fecha_desde)
        if fecha_hasta:
            query += " AND asi.fecha <= %s"
            params.append(fecha_hasta)
        if docente_id:
            query += " AND d.id = %s"
            params.append(docente_id)
        if carrera_id:
            query += " AND car.id = %s"
            params.append(carrera_id)
        if catedra_id:
            query += " AND cat.id = %s"
            params.append(catedra_id)
        if solo_anomalias:
            query += " AND (asi.estado_entrada = 'tardanza' OR asi.estado_salida IN ('anticipada', 'sin_salida'))"

        query += " ORDER BY asi.fecha DESC, asi.entrada DESC;"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                return [
                    {
                        "asistencia_id": r[0],
                        "docente_id": r[1],
                        "legajo": r[2],
                        "docente_nombre": r[3],
                        "carrera_nombre": r[4],
                        "actividad_nombre": r[5],
                        "tipo_actividad": r[6],
                        "rol_mesa": r[7],
                        "fecha": r[8],
                        "horario_previsto_entrada": r[9],
                        "horario_previsto_salida": r[10],
                        "hora_marcada_entrada": r[11],
                        "estado_entrada": r[12],
                        "minutos_tardanza": r[13],
                        "hora_marcada_salida": r[14],
                        "estado_salida": r[15],
                        "minutos_anticipada": r[16],
                        "observaciones": r[17],
                    }
                    for r in rows
                ]

    def obtener_informe_licencias_y_particulares(
        self,
        anio: int,
        docente_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retorna la relación de licencias del año, indicando para cada docente
        el uso de días particulares (sobre el cupo de 6) y el estado de justificaciones médicas.
        """
        query = """
        SELECT 
            lic.id,
            d.id as docente_id,
            d.legajo,
            d.apellido || ', ' || d.nombre as docente_nombre,
            lic.tipo,
            lic.fecha_desde,
            lic.fecha_hasta,
            lic.anio,
            lic.estado,
            lic.certificado_presentado,
            lic.fecha_presentacion_certificado,
            lic.motivo
        FROM licencia_docente lic
        JOIN docente d ON lic.docente_id = d.id
        WHERE lic.anio = %s
        """
        params = [anio]
        if docente_id:
            query += " AND d.id = %s"
            params.append(docente_id)

        query += " ORDER BY lic.fecha_desde DESC;"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                return [
                    {
                        "licencia_id": r[0],
                        "docente_id": r[1],
                        "legajo": r[2],
                        "docente_nombre": r[3],
                        "tipo": r[4],
                        "fecha_desde": r[5],
                        "fecha_hasta": r[6],
                        "anio": r[7],
                        "estado": r[8],
                        "certificado_presentado": r[9],
                        "fecha_presentacion_certificado": r[10],
                        "motivo": r[11],
                    }
                    for r in rows
                ]

    def obtener_resumen_docente(
        self,
        docente_id: int,
        fecha_desde: date,
        fecha_hasta: date,
    ) -> Dict[str, Any]:
        """
        Calcula indicadores ejecutivos para la ficha del docente en un rango de fechas:
        - Total de marcaciones
        - Total de entradas en horario vs tardanzas
        - Total de salidas normales vs anticipadas vs sin registrar
        - Días particulares consumidos y disponibles
        - Licencias médicas pendientes vs confirmadas
        """
        query_asistencia = """
        SELECT 
            COUNT(*) as total_asistencias,
            COUNT(*) FILTER (WHERE estado_entrada = 'en_horario') as en_horario,
            COUNT(*) FILTER (WHERE estado_entrada = 'tardanza') as tardanzas,
            COUNT(*) FILTER (WHERE estado_salida = 'normal') as salidas_normales,
            COUNT(*) FILTER (WHERE estado_salida = 'anticipada') as salidas_anticipadas,
            COUNT(*) FILTER (WHERE estado_salida = 'sin_salida') as sin_salida
        FROM asistencia
        WHERE docente_id = %s AND fecha BETWEEN %s AND %s;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query_asistencia, (docente_id, fecha_desde, fecha_hasta))
                r = cur.fetchone()
                resumen_asi = {
                    "total_asistencias": r[0] or 0,
                    "en_horario": r[1] or 0,
                    "tardanzas": r[2] or 0,
                    "salidas_normales": r[3] or 0,
                    "salidas_anticipadas": r[4] or 0,
                    "sin_salida": r[5] or 0,
                }

                # Consulta de particulares del año
                anio_actual = fecha_desde.year
                cur.execute(
                    """
                    SELECT COUNT(*) FROM licencia_docente 
                    WHERE docente_id = %s AND tipo = 'particular' AND anio = %s AND estado = 'confirmada';
                    """,
                    (docente_id, anio_actual),
                )
                particulares_usados = cur.fetchone()[0]

                # Consulta de licencias médicas
                cur.execute(
                    """
                    SELECT 
                        COUNT(*) FILTER (WHERE estado = 'pendiente') as medicas_pendientes,
                        COUNT(*) FILTER (WHERE estado = 'confirmada') as medicas_confirmadas
                    FROM licencia_docente
                    WHERE docente_id = %s AND tipo = 'medica' AND anio = %s;
                    """,
                    (docente_id, anio_actual),
                )
                m = cur.fetchone()
                resumen_lic = {
                    "particulares_consumidos": particulares_usados,
                    "particulares_disponibles": max(0, 6 - particulares_usados),
                    "medicas_pendientes": m[0] or 0,
                    "medicas_confirmadas": m[1] or 0,
                }

        return {**resumen_asi, **resumen_lic}
