"""
Test de validación del Paso 4:
Verifica la instanciación e integración de todas las vistas de interfaz de usuario
adaptadas al IES N.º 7 Populorum Progressio.
"""
import sys
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(base_dir, 'src'))

from PySide6.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.register_window import RegisterWindow
from ui.registrar_docente_widget import RegistrarDocenteWidget
from ui.horarios_widget import HorariosWidget
from ui.licencias_widget import LicenciasWidget
from ui.main_window import MainWindow

def test_paso4():
    app = QApplication.instance() or QApplication(sys.argv)

    print("=" * 60)
    print("VALIDACIÓN INDUSTRIAL - PASO 4 (INTERFAZ DE USUARIO)")
    print("=" * 60)

    # 1. LoginWindow
    print("\n1. Probando LoginWindow...")
    login = LoginWindow()
    assert "Populorum" in login.windowTitle(), "El título de Login debe reflejar la institución"
    print("   [OK] LoginWindow institucional instanciado")

    # 2. RegisterWindow
    print("\n2. Probando RegisterWindow...")
    reg = RegisterWindow()
    assert "Populorum" in reg.windowTitle()
    print("   [OK] RegisterWindow institucional instanciado")

    # 3. RegistrarDocenteWidget
    print("\n3. Probando RegistrarDocenteWidget...")
    doc_widget = RegistrarDocenteWidget()
    assert doc_widget.foto_frontal is not None
    assert doc_widget.foto_izq is not None
    assert doc_widget.foto_der is not None
    print("   [OK] RegistrarDocenteWidget con 3 ángulos biométricos instanciado")

    # 4. HorariosWidget
    print("\n4. Probando HorariosWidget (Planificación y 80 min)...")
    horarios = HorariosWidget()
    horarios.recargar_datos()
    assert horarios.cmb_docente is not None
    assert horarios.cmb_tipo is not None
    print("   [OK] HorariosWidget instanciado y datos recargados")

    # 5. LicenciasWidget
    print("\n5. Probando LicenciasWidget (Particulares y Médicas)...")
    licencias = LicenciasWidget()
    licencias.recargar_datos()
    assert licencias.lbl_cupo is not None
    assert licencias.btn_confirmar_medico is not None
    print("   [OK] LicenciasWidget instanciado con control de cupo y confirmación médica")

    # 6. MainWindow
    print("\n6. Probando MainWindow con Sidebar de 5 Módulos...")
    main_win = MainWindow(usuario_id=1, nombre_usuario="admin_populorum")
    assert main_win.stack.count() == 5, f"Debe tener 5 vistas en el stack, tiene {main_win.stack.count()}"
    assert len(main_win.sidebar_buttons) == 5, "Debe tener 5 botones en el sidebar"
    print(f"   [OK] MainWindow integrado con {main_win.stack.count()} vistas y navegación institucional")

    print("\n" + "=" * 60)
    print("TODAS LAS PRUEBAS DEL PASO 4 PASARON EXITOSAMENTE (100%)")
    print("=" * 60)

if __name__ == "__main__":
    test_paso4()
