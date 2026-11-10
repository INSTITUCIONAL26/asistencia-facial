"""
Servicio central de Reglas de Negocio para la Marcación Docente.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from datetime import datetime, date, time, timedelta
from typing import Dict, Any, Optional

from repositories.docente_repository import DocenteRepository
from repositories.horario_repository import HorarioRepository
from repositories.asistencia_repository import AsistenciaRepository
from repositories.licencia_repository import LicenciaRepository


class AsistenciaService:
    """
    Orquesta las reglas de negocio institucionales del IES N.º 7:
    - Evaluación de obligaciones horarias (clases 1h 20m, mesas de examen, jornadas).
    - Tolerancia de 5 minutos para determinar Tardanza.
    - Detección de salidas anticipadas.
    - Soporte para confirmación explícita mediante diálogo modal (OK/Cancelar).
    - Detección de inasistencias y licencias particulares/médicas.
    """

    TOLERANCIA_TARDANZA_MINUTOS = 5

    def __init__(
        self,
        docente_repo: Optional[DocenteRepository] = None,
        horario_repo: Optional[HorarioRepository] = None,
        asistencia_repo: Optional[AsistenciaRepository] = None,
        licencia_repo: Optional[LicenciaRepository] = None,
    ):
        self.docente_repo = docente_repo or DocenteRepository()
        self.horario_repo = horario_repo or HorarioRepository()
        self.asistencia_repo = asistencia_repo or AsistenciaRepository()
        self.licencia_repo = licencia_repo or LicenciaRepository()

    def evaluar_marcacion(
        self,
        docente_id: int,
        momento_actual: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Analiza la situación del docente frente a la cámara en el momento actual.
        No persiste ningún cambio en la base de datos: solo determina la operación propuesta
        para presentar al docente en el diálogo modal de confirmación obligatorio.
        """
        momento = momento_actual or datetime.now()
        fecha_actual = momento.date()
        hora_actual = momento.time()

        # 1. Validar existencia y vigencia del docente
        docente = self.docente_repo.obtener_docente_por_id(docente_id)
        if not docente:
            return {
                "puede_marcar": False,
                "motivo_rechazo": "DOCENTE_NO_REGISTRADO",
                "mensaje": "El rostro reconocido no pertenece a un docente registrado.",
            }

        if not docente["activo"]:
            return {
                "puede_marcar": False,
                "motivo_rechazo": "DOCENTE_INACTIVO",
                "mensaje": f"El docente {docente['nombre_completo']} se encuentra inactivo.",
            }

        # 2. Verificar si el docente tiene una licencia activa hoy
        licencia_activa = self.licencia_repo.obtener_licencia_activa_fecha(docente_id, fecha_actual)
        if licencia_activa:
            tipo_lic = licencia_activa["tipo"].capitalize()
            return {
                "puede_marcar": False,
                "motivo_rechazo": "LICENCIA_ACTIVA",
                "mensaje": f"El docente {docente['nombre_completo']} posee una licencia ({tipo_lic}) registrada para hoy.",
            }

        # 3. Consultar la obligación horaria correspondiente al momento actual
        obligacion = self.horario_repo.obtener_obligacion_actual(docente_id, fecha_actual, hora_actual)
        if not obligacion:
            return {
                "puede_marcar": False,
                "motivo_rechazo": "SIN_ACTIVIDAD_PROGRAMADA",
                "docente_nombre": docente["nombre_completo"],
                "mensaje": f"{docente['nombre_completo']} no tiene ninguna actividad o cátedra programada en este horario.",
            }

        # 4. Verificar el estado de marcaciones del docente para esta obligación hoy
        asistencia_previa = self.asistencia_repo.obtener_asistencia_del_dia(
            docente_id, obligacion["id"], fecha_actual
        )

        h_inicio_esperado = obligacion["horario_entrada"]
        h_fin_esperado = obligacion["horario_salida"]
        dt_inicio = datetime.combine(fecha_actual, h_inicio_esperado)
        dt_fin = datetime.combine(fecha_actual, h_fin_esperado)

        # CASO A: No marcó entrada todavía -> Corresponde registrar ENTRADA
        if not asistencia_previa:
            dt_limite_tolerancia = dt_inicio + timedelta(minutes=self.TOLERANCIA_TARDANZA_MINUTOS)

            if momento > dt_limite_tolerancia:
                minutos_demora = int((momento - dt_inicio).total_seconds() // 60)
                clasificacion = "tardanza"
                desc_clasificacion = f"Tardanza ({minutos_demora} min de demora)"
            else:
                minutos_demora = 0
                clasificacion = "en_horario"
                desc_clasificacion = "En horario normal"

            texto_propuesta = (
                f"¿Confirmar ENTRADA ({desc_clasificacion}) de {docente['nombre_completo']} "
                f"a {obligacion['catedra_nombre']} ({h_inicio_esperado.strftime('%H:%M')} a {h_fin_esperado.strftime('%H:%M')})?"
            )

            return {
                "puede_marcar": True,
                "tipo_operacion": "ENTRADA",
                "docente_id": docente_id,
                "docente_nombre": docente["nombre_completo"],
                "docente_legajo": docente["legajo"],
                "obligacion_id": obligacion["id"],
                "actividad_nombre": obligacion["catedra_nombre"],
                "carrera_nombre": obligacion["carrera_nombre"],
                "tipo_actividad": obligacion["tipo_actividad"],
                "rol_mesa": obligacion.get("rol_mesa"),
                "horario_esperado": f"{h_inicio_esperado.strftime('%H:%M')} a {h_fin_esperado.strftime('%H:%M')}",
                "clasificacion": clasificacion,
                "minutos_diferencia": minutos_demora,
                "momento_evaluacion": momento,
                "texto_propuesta": texto_propuesta,
            }

        # CASO B: Ya tiene entrada, pero no tiene salida -> Corresponde registrar SALIDA
        if asistencia_previa["salida"] is None:
            # Evaluar si se retira antes del horario previsto
            if momento < dt_fin:
                minutos_anticipada = int((dt_fin - momento).total_seconds() // 60)
                clasificacion = "anticipada"
                desc_clasificacion = f"Salida anticipada ({minutos_anticipada} min antes)"
            else:
                minutos_anticipada = 0
                clasificacion = "normal"
                desc_clasificacion = "Salida en horario habitual"

            texto_propuesta = (
                f"¿Confirmar SALIDA ({desc_clasificacion}) de {docente['nombre_completo']} "
                f"de {obligacion['catedra_nombre']}?"
            )

            return {
                "puede_marcar": True,
                "tipo_operacion": "SALIDA",
                "asistencia_id": asistencia_previa["id"],
                "docente_id": docente_id,
                "docente_nombre": docente["nombre_completo"],
                "docente_legajo": docente["legajo"],
                "obligacion_id": obligacion["id"],
                "actividad_nombre": obligacion["catedra_nombre"],
                "carrera_nombre": obligacion["carrera_nombre"],
                "tipo_actividad": obligacion["tipo_actividad"],
                "horario_esperado": f"{h_inicio_esperado.strftime('%H:%M')} a {h_fin_esperado.strftime('%H:%M')}",
                "clasificacion": clasificacion,
                "minutos_diferencia": minutos_anticipada,
                "momento_evaluacion": momento,
                "texto_propuesta": texto_propuesta,
            }

        # CASO C: Ya completó ENTRADA y SALIDA para esta obligación hoy
        return {
            "puede_marcar": False,
            "motivo_rechazo": "ASISTENCIA_YA_COMPLETADA",
            "docente_nombre": docente["nombre_completo"],
            "mensaje": (
                f"{docente['nombre_completo']} ya registró su ENTRADA y SALIDA "
                f"para la cátedra {obligacion['catedra_nombre']} el día de hoy."
            ),
        }

    def confirmar_marcacion(self, datos_evaluacion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Se invoca ÚNICAMENTE cuando el docente pulsa [OK] en el diálogo modal.
        Efectiviza la persistencia en PostgreSQL según la operación determinada.
        Si el docente pulsa [Cancelar], este método nunca es llamado y la base de datos queda intacta.
        """
        tipo_op = datos_evaluacion.get("tipo_operacion")
        docente_id = datos_evaluacion["docente_id"]
        momento = datos_evaluacion["momento_evaluacion"]
        clasificacion = datos_evaluacion["clasificacion"]
        minutos = datos_evaluacion["minutos_diferencia"]

        if tipo_op == "ENTRADA":
            asistencia_id = self.asistencia_repo.registrar_entrada(
                docente_id=docente_id,
                obligacion_id=datos_evaluacion["obligacion_id"],
                fecha=momento.date(),
                entrada=momento,
                estado_entrada=clasificacion,
                minutos_tardanza=minutos,
                observaciones=f"Entrada registrada por biometría ({clasificacion})",
            )
            return {
                "exito": True,
                "operacion": "ENTRADA",
                "asistencia_id": asistencia_id,
                "mensaje": f"Entrada registrada exitosamente: {datos_evaluacion['docente_nombre']}",
            }

        elif tipo_op == "SALIDA":
            asistencia_id = datos_evaluacion["asistencia_id"]
            self.asistencia_repo.registrar_salida(
                asistencia_id=asistencia_id,
                salida=momento,
                estado_salida=clasificacion,
                minutos_anticipada=minutos,
                observaciones=f"Salida registrada por biometría ({clasificacion})",
            )
            return {
                "exito": True,
                "operacion": "SALIDA",
                "asistencia_id": asistencia_id,
                "mensaje": f"Salida registrada exitosamente: {datos_evaluacion['docente_nombre']}",
            }

        return {
            "exito": False,
            "mensaje": f"Operación desconocida: {tipo_op}",
        }
