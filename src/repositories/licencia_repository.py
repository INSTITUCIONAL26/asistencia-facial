"""
Módulo de repositorio para el control de Días Particulares y Licencias Médicas.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from datetime import date
from typing import Optional, List, Dict, Any
from config.database import get_connection


class LicenciaRepository:
    """
    Gestiona el cupo anual de 6 días particulares y el seguimiento
    del ciclo de vida de los certificados médicos.
    """

    MAX_PARTICULARES_ANUALES = 6

    def crear_licencia(
        self,
        docente_id: int,
        tipo: str,
        fecha_desde: date,
        fecha_hasta: date,
        anio: int,
        motivo: Optional[str] = None,
        estado_inicial: Optional[str] = None,
    ) -> int:
        """
        Registra una nueva licencia o inasistencia justificada.
        tipo: 'particular' o 'medica'
        - Para 'particular': se crea automáticamente en estado 'confirmada' (no requiere certificado).
        - Para 'medica': por defecto inicia en estado 'pendiente' a la espera del certificado.
        """
        tipo_clean = tipo.lower().strip()
        if not estado_inicial:
            estado_inicial = "confirmada" if tipo_clean == "particular" else "pendiente"

        query = """
        INSERT INTO licencia_docente (
            docente_id, tipo, fecha_desde, fecha_hasta, anio,
            estado, certificado_presentado, motivo
        )
        VALUES (%s, %s, %s, %s, %s, %s, FALSE, %s)
        RETURNING id;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        docente_id,
                        tipo_clean,
                        fecha_desde,
                        fecha_hasta,
                        anio,
                        estado_inicial,
                        motivo,
                    ),
                )
                licencia_id = cur.fetchone()[0]
            conn.commit()
        return licencia_id

    def contar_particulares_consumidos(self, docente_id: int, anio: int) -> int:
        """
        Retorna la cantidad de días particulares utilizados por un docente en el año.
        El máximo institucional reglamentario es 6.
        """
        query = """
        SELECT COUNT(*)
        FROM licencia_docente
        WHERE docente_id = %s
          AND tipo = 'particular'
          AND anio = %s
          AND estado = 'confirmada';
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id, anio))
                return cur.fetchone()[0]

    def cupo_particular_disponible(self, docente_id: int, anio: int) -> int:
        """
        Retorna cuántos días particulares le quedan disponibles al docente en el año.
        """
        consumidos = self.contar_particulares_consumidos(docente_id, anio)
        return max(0, self.MAX_PARTICULARES_ANUALES - consumidos)

    def confirmar_certificado_medico(
        self,
        licencia_id: int,
        fecha_presentacion: date,
    ) -> None:
        """
        Valida y confirma una licencia médica tras la recepción formal del certificado médico.
        Pasa el estado a 'confirmada' y marca 'certificado_presentado = TRUE'.
        """
        query = """
        UPDATE licencia_docente
        SET estado = 'confirmada',
            certificado_presentado = TRUE,
            fecha_presentacion_certificado = %s
        WHERE id = %s AND tipo = 'medica';
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (fecha_presentacion, licencia_id))
            conn.commit()

    def rechazar_licencia_medica(self, licencia_id: int, motivo_rechazo: Optional[str] = None) -> None:
        """
        Marca una licencia médica como 'rechazada' si no se presentó el certificado reglamentario.
        """
        query = """
        UPDATE licencia_docente
        SET estado = 'rechazada',
            motivo = COALESCE(%s, motivo)
        WHERE id = %s AND tipo = 'medica';
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (motivo_rechazo, licencia_id))
            conn.commit()

    def obtener_licencia_activa_fecha(self, docente_id: int, fecha: date) -> Optional[Dict[str, Any]]:
        """
        Determina si un docente tiene una licencia activa (particular o médica) en la fecha dada.
        """
        query = """
        SELECT id, docente_id, tipo, fecha_desde, fecha_hasta,
               estado, certificado_presentado, motivo
        FROM licencia_docente
        WHERE docente_id = %s
          AND %s BETWEEN fecha_desde AND fecha_hasta
          AND estado IN ('confirmada', 'pendiente')
        LIMIT 1;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id, fecha))
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "docente_id": row[1],
                    "tipo": row[2],
                    "fecha_desde": row[3],
                    "fecha_hasta": row[4],
                    "estado": row[5],
                    "certificado_presentado": row[6],
                    "motivo": row[7],
                }

    def obtener_licencias_docente(self, docente_id: int, anio: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retorna todas las licencias del docente, ordenadas por fecha más reciente.
        """
        query = """
        SELECT id, tipo, fecha_desde, fecha_hasta, anio, estado,
               certificado_presentado, fecha_presentacion_certificado, motivo
        FROM licencia_docente
        WHERE docente_id = %s
        """
        params = [docente_id]
        if anio:
            query += " AND anio = %s"
            params.append(anio)
        query += " ORDER BY fecha_desde DESC;"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                return [
                    {
                        "id": r[0],
                        "tipo": r[1],
                        "fecha_desde": r[2],
                        "fecha_hasta": r[3],
                        "anio": r[4],
                        "estado": r[5],
                        "certificado_presentado": r[6],
                        "fecha_presentacion_certificado": r[7],
                        "motivo": r[8],
                    }
                    for r in rows
                ]
