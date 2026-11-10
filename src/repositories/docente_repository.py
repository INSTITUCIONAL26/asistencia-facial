"""
Módulo de repositorio para la entidad Docente y sus imágenes biométricas.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from typing import Optional, List, Dict, Tuple, Any
from config.database import get_connection


class DocenteRepository:
    """
    Repositorio para operaciones CRUD sobre la tabla 'docente'
    y persistencia biométrica en 'foto_docente'.
    """

    def crear_docente(
        self,
        legajo: str,
        nombre: str,
        apellido: str,
        dni: str,
        cuil: str,
        correo_electronico: Optional[str] = None,
        telefono: Optional[str] = None,
        domicilio: Optional[str] = None,
    ) -> int:
        """
        Inserta un nuevo docente en la base de datos y retorna su ID generado.
        """
        query = """
        INSERT INTO docente (
            legajo, nombre, apellido, dni, cuil,
            correo_electronico, telefono, domicilio, activo
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        RETURNING id;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (
                        legajo.strip().upper(),
                        nombre.strip().title(),
                        apellido.strip().title(),
                        dni.strip(),
                        cuil.strip(),
                        correo_electronico.strip() if correo_electronico else None,
                        telefono.strip() if telefono else None,
                        domicilio.strip() if domicilio else None,
                    ),
                )
                docente_id = cur.fetchone()[0]
            conn.commit()
        return docente_id

    def obtener_docente_por_id(self, docente_id: int) -> Optional[Dict[str, Any]]:
        """
        Retorna la ficha completa del docente dado su ID.
        """
        query = """
        SELECT id, legajo, nombre, apellido, dni, cuil,
               correo_electronico, telefono, domicilio, activo
        FROM docente
        WHERE id = %s;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id,))
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "legajo": row[1],
                    "nombre": row[2],
                    "apellido": row[3],
                    "dni": row[4],
                    "cuil": row[5],
                    "correo_electronico": row[6],
                    "telefono": row[7],
                    "domicilio": row[8],
                    "activo": row[9],
                    "nombre_completo": f"{row[2]} {row[3]}",
                }

    def obtener_nombre_por_id(self, docente_id: int) -> Optional[str]:
        """
        Retorna únicamente el nombre y apellido del docente (optimizado para UI).
        """
        query = "SELECT nombre, apellido FROM docente WHERE id = %s;"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id,))
                row = cur.fetchone()
                if row:
                    return f"{row[0]} {row[1]}"
        return None

    def buscar_por_dni_o_cuil(self, identificador: str) -> Optional[Dict[str, Any]]:
        """
        Permite buscar un docente por su número de DNI, CUIL o Legajo.
        """
        query = """
        SELECT id, legajo, nombre, apellido, dni, cuil, activo
        FROM docente
        WHERE dni = %s OR cuil = %s OR legajo = %s
        LIMIT 1;
        """
        clean_id = identificador.strip()
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (clean_id, clean_id, clean_id.upper()))
                row = cur.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0],
                    "legajo": row[1],
                    "nombre": row[2],
                    "apellido": row[3],
                    "dni": row[4],
                    "cuil": row[5],
                    "activo": row[6],
                    "nombre_completo": f"{row[2]} {row[3]}",
                }

    def obtener_todos(self, solo_activos: bool = True) -> List[Dict[str, Any]]:
        """
        Lista todos los docentes registrados, ordenados alfabéticamente por apellido.
        """
        query = """
        SELECT id, legajo, nombre, apellido, dni, cuil, activo
        FROM docente
        """
        if solo_activos:
            query += " WHERE activo = TRUE"
        query += " ORDER BY apellido ASC, nombre ASC;"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [
                    {
                        "id": r[0],
                        "legajo": r[1],
                        "nombre": r[2],
                        "apellido": r[3],
                        "dni": r[4],
                        "cuil": r[5],
                        "activo": r[6],
                        "nombre_completo": f"{r[3]}, {r[2]}",
                    }
                    for r in rows
                ]

    # --- Persistencia Biométrica ---

    def guardar_foto(self, docente_id: int, angulo: str, imagen_bytes: bytes) -> int:
        """
        Inserta una muestra fotográfica facial para el docente.
        Ángulos soportados: 'frontal', 'izquierdo', 'derecho'.
        """
        query = """
        INSERT INTO foto_docente (docente_id, angulo, imagen)
        VALUES (%s, %s, %s)
        RETURNING id;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id, angulo.lower().strip(), imagen_bytes))
                foto_id = cur.fetchone()[0]
            conn.commit()
        return foto_id

    def obtener_todas_las_fotos(self) -> List[Tuple[int, str, bytes]]:
        """
        Retorna todas las muestras fotográficas de docentes activos
        para cargar en la memoria del hilo de reconocimiento facial.
        Retorna lista de tuplas: (docente_id, angulo, imagen_bytes).
        """
        query = """
        SELECT fd.docente_id, fd.angulo, fd.imagen
        FROM foto_docente fd
        JOIN docente d ON fd.docente_id = d.id
        WHERE d.activo = TRUE;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def eliminar_fotos_docente(self, docente_id: int) -> None:
        """
        Elimina las muestras faciales de un docente (ej: para re-enrolamiento).
        """
        query = "DELETE FROM foto_docente WHERE docente_id = %s;"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (docente_id,))
            conn.commit()
