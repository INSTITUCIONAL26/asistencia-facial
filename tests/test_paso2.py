"""
Script de validación industrial para el Paso 2:
Verifica repositorios, servicios y reglas de negocio del IES N.º 7 Populorum Progressio.
"""
import sys
import os
from datetime import datetime, date, time, timedelta

# Asegurar path a src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from repositories.docente_repository import DocenteRepository
from repositories.horario_repository import HorarioRepository
from repositories.asistencia_repository import AsistenciaRepository
from repositories.licencia_repository import LicenciaRepository
from repositories.informe_repository import InformeRepository
from services.asistencia_service import AsistenciaService

def run_tests():
    print("=" * 60)
    print("INICIANDO PRUEBAS INDUSTRIALES - PASO 2")
    print("=" * 60)

    docente_repo = DocenteRepository()
    horario_repo = HorarioRepository()
    asistencia_repo = AsistenciaRepository()
    licencia_repo = LicenciaRepository()
    informe_repo = InformeRepository()
    asistencia_service = AsistenciaService(
        docente_repo, horario_repo, asistencia_repo, licencia_repo
    )

    # 1. Test DocenteRepository
    print("\n1. Probando DocenteRepository...")
    legajo_test = f"DOC-TEST-{datetime.now().strftime('%H%M%S')}"
    doc_id = docente_repo.crear_docente(
        legajo=legajo_test,
        nombre="Carlos",
        apellido="Gómez",
        dni=f"DNI{datetime.now().strftime('%H%M%S')}",
        cuil=f"20-DNI{datetime.now().strftime('%H%M%S')}-3",
        correo_electronico="cgomez@populorum.edu.ar",
        telefono="388-1234567"
    )
    assert doc_id > 0, "Error: No se generó ID de docente"
    doc_info = docente_repo.obtener_docente_por_id(doc_id)
    assert doc_info["nombre"] == "Carlos", "Error al recuperar datos del docente"
    print(f"   [OK] Docente creado exitosamente: ID={doc_id}, Nombre={doc_info['nombre_completo']}")

    # 2. Test HorarioRepository (Carreras y Cátedras)
    print("\n2. Probando HorarioRepository...")
    carreras = horario_repo.obtener_carreras()
    assert len(carreras) > 0, "Error: No hay carreras precargadas"
    catedras = horario_repo.obtener_catedras(carreras[0]["id"])
    assert len(catedras) > 0, "Error: No hay cátedras precargadas"
    cat_id = catedras[0]["id"]
    print(f"   [OK] Carreras encontradas: {len(carreras)}, Cátedras: {len(catedras)} (usando '{catedras[0]['nombre']}')")

    # Crear una obligación horaria tipo CLASE de 1h 20m (ej: 18:30 a 19:50)
    # y asignarla al día de hoy para poder probar la evaluación en tiempo real
    hoy = date.today()
    dias_nombres = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    dia_hoy_str = dias_nombres[hoy.weekday()]

    hora_inicio = time(18, 30)
    hora_fin = time(19, 50) # Exactamente 1 hora y 20 minutos (80 min)

    ob_id = horario_repo.crear_obligacion(
        docente_id=doc_id,
        tipo_actividad="clase",
        horario_entrada=hora_inicio,
        horario_salida=hora_fin,
        catedra_id=cat_id,
        dia_semana=dia_hoy_str
    )
    assert ob_id > 0, "Error al crear obligación horaria"
    print(f"   [OK] Obligación horaria creada (Clase 80 min): ID={ob_id}, Día={dia_hoy_str}, {hora_inicio}-{hora_fin}")

    # 3. Test AsistenciaService: Evaluación de Entrada EN HORARIO
    print("\n3. Probando AsistenciaService - Entrada EN HORARIO...")
    # Simular que el docente llega a las 18:32 (dentro de los 5 min de tolerancia)
    momento_en_horario = datetime.combine(hoy, time(18, 32))
    eval_entrada = asistencia_service.evaluar_marcacion(doc_id, momento_en_horario)
    assert eval_entrada["puede_marcar"] is True
    assert eval_entrada["tipo_operacion"] == "ENTRADA"
    assert eval_entrada["clasificacion"] == "en_horario"
    assert eval_entrada["minutos_diferencia"] == 0
    print(f"   [OK] Clasificación correcta: {eval_entrada['clasificacion']} (Tolerancia respetada)")

    # 4. Test AsistenciaService: Evaluación de Entrada con TARDANZA (> 5 min)
    print("\n4. Probando AsistenciaService - Entrada con TARDANZA...")
    # Simular que el docente llega a las 18:39 (9 minutos tarde)
    momento_tardanza = datetime.combine(hoy, time(18, 39))
    eval_tardanza = asistencia_service.evaluar_marcacion(doc_id, momento_tardanza)
    assert eval_tardanza["puede_marcar"] is True
    assert eval_tardanza["tipo_operacion"] == "ENTRADA"
    assert eval_tardanza["clasificacion"] == "tardanza"
    assert eval_tardanza["minutos_diferencia"] == 9
    print(f"   [OK] Detección de tardanza correcta: {eval_tardanza['minutos_diferencia']} minutos de demora")

    # 5. Confirmación de Entrada mediante Modal (Simulación de presionar OK)
    print("\n5. Probando confirmación de Entrada...")
    res_confirmacion_in = asistencia_service.confirmar_marcacion(eval_tardanza)
    assert res_confirmacion_in["exito"] is True
    asistencia_id = res_confirmacion_in["asistencia_id"]
    print(f"   [OK] Entrada persistida en PostgreSQL: Asistencia ID={asistencia_id}")

    # 6. Test AsistenciaService: Evaluación de Salida ANTICIPADA
    print("\n6. Probando AsistenciaService - Salida ANTICIPADA...")
    # La clase termina 19:50; simular salida a las 19:35 (15 min antes)
    momento_anticipada = datetime.combine(hoy, time(19, 35))
    eval_salida_ant = asistencia_service.evaluar_marcacion(doc_id, momento_anticipada)
    assert eval_salida_ant["puede_marcar"] is True
    assert eval_salida_ant["tipo_operacion"] == "SALIDA"
    assert eval_salida_ant["clasificacion"] == "anticipada"
    assert eval_salida_ant["minutos_diferencia"] == 15
    print(f"   [OK] Detección de salida anticipada correcta: {eval_salida_ant['minutos_diferencia']} min antes")

    # 7. Confirmación de Salida mediante Modal
    print("\n7. Probando confirmación de Salida...")
    res_confirmacion_out = asistencia_service.confirmar_marcacion(eval_salida_ant)
    assert res_confirmacion_out["exito"] is True
    print(f"   [OK] Salida persistida exitosamente")

    # 8. Test AsistenciaService: Intento de volver a marcar tras haber completado
    print("\n8. Probando caso especial: Re-intento de marcación ya completada...")
    eval_repetida = asistencia_service.evaluar_marcacion(doc_id, momento_anticipada)
    assert eval_repetida["puede_marcar"] is False
    assert eval_repetida["motivo_rechazo"] == "ASISTENCIA_YA_COMPLETADA"
    print(f"   [OK] Bloqueo correcto de marcación duplicada: '{eval_repetida['motivo_rechazo']}'")

    # 9. Test LicenciaRepository: Control de cupo anual de Particulares (máximo 6)
    print("\n9. Probando LicenciaRepository - Cupo de Particulares (máx 6)...")
    anio_actual = hoy.year
    cupo_inicial = licencia_repo.cupo_particular_disponible(doc_id, anio_actual)
    assert cupo_inicial == 6, f"Error: Cupo inicial debería ser 6, obtenido {cupo_inicial}"
    
    # Consumir 1 particular
    lic_id = licencia_repo.crear_licencia(
        docente_id=doc_id,
        tipo="particular",
        fecha_desde=hoy + timedelta(days=1),
        fecha_hasta=hoy + timedelta(days=1),
        anio=anio_actual,
        motivo="Trámite bancario personal"
    )
    cupo_despues = licencia_repo.cupo_particular_disponible(doc_id, anio_actual)
    assert cupo_despues == 5, f"Error: Cupo posterior debería ser 5, obtenido {cupo_despues}"
    print(f"   [OK] Cupo anual calculado correctamente: Inicial=6, Utilizado=1, Disponible={cupo_despues}")

    # 10. Test LicenciaRepository: Ciclo de vida de Licencia Médica (Pendiente -> Confirmada)
    print("\n10. Probando LicenciaRepository - Ciclo de Licencia Médica...")
    lic_med_id = licencia_repo.crear_licencia(
        docente_id=doc_id,
        tipo="medica",
        fecha_desde=hoy + timedelta(days=3),
        fecha_hasta=hoy + timedelta(days=5),
        anio=anio_actual,
        motivo="Gripe estacional / reposo 48hs"
    )
    # Por defecto debe nacer en estado 'pendiente' y con certificado = False
    lic_doc = licencia_repo.obtener_licencia_activa_fecha(doc_id, hoy + timedelta(days=3))
    assert lic_doc["estado"] == "pendiente"
    assert lic_doc["certificado_presentado"] is False
    print("   [OK] Licencia médica iniciada en estado 'pendiente' a la espera de certificado")

    # Presentación formal del certificado
    licencia_repo.confirmar_certificado_medico(lic_med_id, hoy + timedelta(days=4))
    lic_doc_conf = licencia_repo.obtener_licencia_activa_fecha(doc_id, hoy + timedelta(days=3))
    assert lic_doc_conf["estado"] == "confirmada"
    assert lic_doc_conf["certificado_presentado"] is True
    print("   [OK] Certificado médico validado y promovido a estado 'confirmada'")

    # 11. Test InformeRepository: Reportes Analíticos Consolidados
    print("\n11. Probando InformeRepository - Consultas consolidadas para secretaría...")
    informe_asistencias = informe_repo.obtener_informe_asistencias(docente_id=doc_id)
    assert len(informe_asistencias) >= 1
    reg = informe_asistencias[0]
    print(f"   [OK] Planilla de Asistencias generada:")
    print(f"        Docente: {reg['docente_nombre']} | Actividad: {reg['actividad_nombre']}")
    print(f"        Entrada: {reg['hora_marcada_entrada'].strftime('%H:%M')} ({reg['estado_entrada']}) | Demora: {reg['minutos_tardanza']} min")
    print(f"        Salida:  {reg['hora_marcada_salida'].strftime('%H:%M')} ({reg['estado_salida']}) | Anticipada: {reg['minutos_anticipada']} min")

    resumen = informe_repo.obtener_resumen_docente(doc_id, hoy - timedelta(days=1), hoy + timedelta(days=1))
    print(f"   [OK] Resumen ejecutivo del docente:")
    print(f"        Total: {resumen['total_asistencias']} | Tardanzas: {resumen['tardanzas']} | Salidas Anticipadas: {resumen['salidas_anticipadas']}")
    print(f"        Particulares usados: {resumen['particulares_consumidos']} (Disponibles: {resumen['particulares_disponibles']})")

    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS INDUSTRIALES DEL PASO 2 PASARON EXITOSAMENTE (100%)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
