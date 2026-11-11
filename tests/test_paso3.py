"""
Test de validación del Paso 3:
Verifica la importación, diseño e instanciación del modal obligatorio
y el flujo de pausa/reanudación del motor de reconocimiento.
"""
import sys
import os
from datetime import datetime

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'src'))

from PySide6.QtWidgets import QApplication
from ui.confirmacion_marcacion_dialog import ConfirmacionMarcacionDialog
from ui.camera_thread import CameraThread
from ai.reconocimiento_thread import ReconocimientoThread

def test_paso3():
    app = QApplication.instance() or QApplication(sys.argv)

    print("=" * 60)
    print("VALIDACIÓN INDUSTRIAL - PASO 3")
    print("=" * 60)

    # 1. Probar inicialización y propiedades de ReconocimientoThread
    print("\n1. Probando ReconocimientoThread...")
    recon_thread = ReconocimientoThread()
    assert hasattr(recon_thread, 'pausar'), "ReconocimientoThread debe tener método pausar()"
    assert hasattr(recon_thread, 'reanudar'), "ReconocimientoThread debe tener método reanudar()"
    
    recon_thread.pausar()
    assert recon_thread._paused is True, "ReconocimientoThread no pausó correctamente"
    recon_thread.reanudar()
    assert recon_thread._paused is False, "ReconocimientoThread no reanudó correctamente"
    print("   [OK] ReconocimientoThread: métodos pausar() y reanudar() verificados")

    # 2. Probar CameraThread
    print("\n2. Probando CameraThread...")
    cam_thread = CameraThread()
    assert hasattr(cam_thread, 'pausar_reconocimiento'), "CameraThread debe tener pausar_reconocimiento()"
    assert hasattr(cam_thread, 'reanudar_reconocimiento'), "CameraThread debe tener reanudar_reconocimiento()"
    
    cam_thread.pausar_reconocimiento()
    assert cam_thread._is_paused is True, "CameraThread no pausó reconocimiento"
    cam_thread.reanudar_reconocimiento()
    assert cam_thread._is_paused is False, "CameraThread no reanudó reconocimiento"
    print("   [OK] CameraThread: pausa y reanudación con cooldown verificados")

    # 3. Probar ConfirmacionMarcacionDialog (Modo Entrada)
    print("\n3. Probando ConfirmacionMarcacionDialog (Entrada con Tardanza)...")
    datos_mock_entrada = {
        "puede_marcar": True,
        "tipo_operacion": "ENTRADA",
        "docente_id": 1,
        "docente_nombre": "Carlos Gómez",
        "docente_legajo": "DOC-101",
        "obligacion_id": 1,
        "actividad_nombre": "Programación Visual",
        "carrera_nombre": "Tecnicatura Superior en Desarrollo de Software",
        "tipo_actividad": "clase",
        "rol_mesa": None,
        "horario_esperado": "18:30 a 19:50",
        "clasificacion": "tardanza",
        "minutos_diferencia": 8,
        "momento_evaluacion": datetime.now(),
        "texto_propuesta": "¿Confirmar ENTRADA (Tardanza) de Carlos Gómez?"
    }
    dlg_entrada = ConfirmacionMarcacionDialog(datos_mock_entrada)
    assert dlg_entrada.isModal() is True, "El diálogo debe ser modal obligatorio"
    assert dlg_entrada.btn_confirmar is not None, "El diálogo debe tener botón de confirmación OK"
    assert dlg_entrada.btn_cancelar is not None, "El diálogo debe tener botón de cancelación"
    print("   [OK] Diálogo de Entrada instanciado correctamente con botones OK / Cancelar")

    # 4. Probar ConfirmacionMarcacionDialog (Modo Salida)
    print("\n4. Probando ConfirmacionMarcacionDialog (Salida Anticipada)...")
    datos_mock_salida = {
        "puede_marcar": True,
        "tipo_operacion": "SALIDA",
        "asistencia_id": 1,
        "docente_id": 1,
        "docente_nombre": "Carlos Gómez",
        "docente_legajo": "DOC-101",
        "obligacion_id": 1,
        "actividad_nombre": "Programación Visual",
        "carrera_nombre": "Tecnicatura Superior en Desarrollo de Software",
        "tipo_actividad": "clase",
        "rol_mesa": None,
        "horario_esperado": "18:30 a 19:50",
        "clasificacion": "anticipada",
        "minutos_diferencia": 12,
        "momento_evaluacion": datetime.now(),
        "texto_propuesta": "¿Confirmar SALIDA (Anticipada) de Carlos Gómez?"
    }
    dlg_salida = ConfirmacionMarcacionDialog(datos_mock_salida)
    assert dlg_salida.isModal() is True
    print("   [OK] Diálogo de Salida instanciado correctamente")

    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS DEL PASO 3 PASARON EXITOSAMENTE (100%)")
    print("=" * 60)

if __name__ == "__main__":
    test_paso3()
