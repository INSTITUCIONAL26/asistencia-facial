"""
Vista de Registro y Enrolamiento Biométrico de Docentes.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QScrollArea, QFileDialog, QMessageBox, QSizePolicy, QDialog
)
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QPixmap, QIcon

from repositories.docente_repository import DocenteRepository
from ui.camara_dialog import CamaraDialog


class AnguloDocenteWidget(QWidget):
    """
    Componente para captura/carga de una muestra fotográfica del docente.
    Se utiliza para los 3 ángulos biométricos: Frontal, Izquierdo y Derecho.
    """

    def __init__(self, titulo: str, angulo_key: str):
        super().__init__()
        self.titulo = titulo
        self.angulo_key = angulo_key
        self._imagen_bytes = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        lbl_titulo = QLabel(self.titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        layout.addWidget(lbl_titulo)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_cargar = QPushButton(" Cargar Foto")
        self.btn_cargar.setIcon(QIcon("src/ui/assets/upload.svg"))
        self.btn_cargar.setIconSize(QSize(14, 14))
        self.btn_cargar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cargar.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #0b5ed7; }
        """)
        self.btn_cargar.clicked.connect(self._cargar_archivo)
        btn_row.addWidget(self.btn_cargar)

        self.btn_camara = QPushButton(" Cámara")
        self.btn_camara.setIcon(QIcon("src/ui/assets/camera.svg"))
        self.btn_camara.setIconSize(QSize(14, 14))
        self.btn_camara.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_camara.setStyleSheet("""
            QPushButton {
                background-color: #198754;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #157347; }
        """)
        self.btn_camara.clicked.connect(self._abrir_camara)
        btn_row.addWidget(self.btn_camara)

        layout.addLayout(btn_row)

        self.contenedor_preview = QFrame()
        self.contenedor_preview.setFixedSize(140, 160)
        self.contenedor_preview.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border: 2px dashed #4a4a6a;
                border-radius: 8px;
            }
        """)
        preview_layout = QVBoxLayout(self.contenedor_preview)
        preview_layout.setContentsMargins(4, 4, 4, 4)

        self.lbl_preview = QLabel("Sin foto")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet("color: #7f8c8d; font-size: 12px; border: none;")
        preview_layout.addWidget(self.lbl_preview)

        layout.addWidget(self.contenedor_preview, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_nombre_archivo = QLabel("")
        self.lbl_nombre_archivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_nombre_archivo.setStyleSheet("color: #a0a0a0; font-size: 11px;")
        layout.addWidget(self.lbl_nombre_archivo)

    def _abrir_camara(self):
        dialog = CamaraDialog(f"Capturar Ángulo {self.titulo}", parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if dialog.captured_image_bytes:
                self._imagen_bytes = dialog.captured_image_bytes
                pixmap = QPixmap()
                pixmap.loadFromData(self._imagen_bytes)
                self._mostrar_pixmap(pixmap)
                self.lbl_nombre_archivo.setText("Capturada por cámara")
                self.contenedor_preview.setStyleSheet("QFrame { background-color: #1a1a2e; border: 2px solid #2ecc71; border-radius: 8px; }")

    def _cargar_archivo(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, f"Seleccionar foto - {self.titulo}", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if ruta:
            try:
                with open(ruta, "rb") as f:
                    self._imagen_bytes = f.read()
                pixmap = QPixmap(ruta)
                self._mostrar_pixmap(pixmap)
                nombre = ruta.replace("\\", "/").split("/")[-1]
                self.lbl_nombre_archivo.setText(nombre)
                self.contenedor_preview.setStyleSheet("QFrame { background-color: #1a1a2e; border: 2px solid #2ecc71; border-radius: 8px; }")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar la imagen:\n{e}")

    def _mostrar_pixmap(self, pixmap: QPixmap):
        scaled = pixmap.scaled(132, 152, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.lbl_preview.setPixmap(scaled)

    def tiene_foto(self) -> bool:
        return self._imagen_bytes is not None

    def obtener_bytes(self) -> Optional[bytes]:
        return self._imagen_bytes

    def limpiar(self):
        self._imagen_bytes = None
        self.lbl_preview.clear()
        self.lbl_preview.setText("Sin foto")
        self.lbl_nombre_archivo.setText("")
        self.contenedor_preview.setStyleSheet("QFrame { background-color: #1a1a2e; border: 2px dashed #4a4a6a; border-radius: 8px; }")


class RegistrarDocenteWidget(QWidget):
    """
    Formulario de enrolamiento de docentes para el IES N.º 7 Populorum Progressio.
    """
    docente_guardado = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.docente_repo = DocenteRepository()
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        contenido = QWidget()
        contenido.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(contenido)
        main_layout.setContentsMargins(60, 40, 60, 40)
        main_layout.setSpacing(24)

        # 1. Cabecera
        card_header = QFrame()
        card_header.setStyleSheet("background-color: transparent; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.1);")
        header_layout = QVBoxLayout(card_header)
        header_layout.setContentsMargins(36, 16, 36, 16)
        
        lbl_inst = QLabel("IES N.º 7 POPULORUM PROGRESSIO")
        lbl_inst.setStyleSheet("font-size: 11px; font-weight: bold; color: #3498db; letter-spacing: 1px; border: none;")
        
        title = QLabel("Enrolamiento y Registro de Docentes")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; border: none;")
        
        header_layout.addWidget(lbl_inst)
        header_layout.addWidget(title)
        main_layout.addWidget(card_header)

        # 2. Datos Personales
        card_datos = QFrame()
        card_datos.setStyleSheet("background-color: #1a1e36; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);")
        layout_datos = QVBoxLayout(card_datos)
        layout_datos.setContentsMargins(24, 20, 24, 20)
        layout_datos.setSpacing(16)

        lbl_secc1 = QLabel("Datos Institucionales y de Identificación")
        lbl_secc1.setStyleSheet("color: #3498db; font-size: 15px; font-weight: bold; border: none;")
        layout_datos.addWidget(lbl_secc1)

        grid = QGridLayout()
        grid.setSpacing(14)

        self.txt_legajo = self._crear_input("Ej: DOC-101")
        self.txt_nombre = self._crear_input("Nombre(s)")
        self.txt_apellido = self._crear_input("Apellido(s)")
        self.txt_dni = self._crear_input("DNI (solo números)")
        self.txt_cuil = self._crear_input("CUIL (ej: 20-30123456-3)")
        self.txt_correo = self._crear_input("ejemplo@populorum.edu.ar")
        self.txt_telefono = self._crear_input("Teléfono / Celular")
        self.txt_domicilio = self._crear_input("Domicilio")

        grid.addWidget(self._crear_label("Legajo (*):"), 0, 0)
        grid.addWidget(self.txt_legajo, 0, 1)

        grid.addWidget(self._crear_label("DNI (*):"), 0, 2)
        grid.addWidget(self.txt_dni, 0, 3)

        grid.addWidget(self._crear_label("Apellido(s) (*):"), 1, 0)
        grid.addWidget(self.txt_apellido, 1, 1)

        grid.addWidget(self._crear_label("Nombre(s) (*):"), 1, 2)
        grid.addWidget(self.txt_nombre, 1, 3)

        grid.addWidget(self._crear_label("CUIL (*):"), 2, 0)
        grid.addWidget(self.txt_cuil, 2, 1)

        grid.addWidget(self._crear_label("Correo Institucional:"), 2, 2)
        grid.addWidget(self.txt_correo, 2, 3)

        grid.addWidget(self._crear_label("Teléfono de Contacto:"), 3, 0)
        grid.addWidget(self.txt_telefono, 3, 1)

        grid.addWidget(self._crear_label("Domicilio:"), 3, 2)
        grid.addWidget(self.txt_domicilio, 3, 3)

        layout_datos.addLayout(grid)
        main_layout.addWidget(card_datos)

        # 3. Muestras Biométricas
        card_fotos = QFrame()
        card_fotos.setStyleSheet("background-color: #1a1e36; border-radius: 10px; border: 1px solid rgba(255, 255, 255, 0.08);")
        layout_fotos = QVBoxLayout(card_fotos)
        layout_fotos.setContentsMargins(24, 20, 24, 20)
        layout_fotos.setSpacing(16)

        lbl_secc2 = QLabel("Enrolamiento Biométrico Facial (Obligatorio 3 Ángulos)")
        lbl_secc2.setStyleSheet("color: #2ecc71; font-size: 15px; font-weight: bold; border: none;")
        layout_fotos.addWidget(lbl_secc2)

        fotos_row = QHBoxLayout()
        fotos_row.setSpacing(24)

        self.foto_frontal = AnguloDocenteWidget("Ángulo Frontal", "frontal")
        self.foto_izq = AnguloDocenteWidget("Ángulo Izquierdo", "izquierdo")
        self.foto_der = AnguloDocenteWidget("Ángulo Derecho", "derecho")

        fotos_row.addWidget(self.foto_frontal)
        fotos_row.addWidget(self.foto_izq)
        fotos_row.addWidget(self.foto_der)

        layout_fotos.addLayout(fotos_row)
        main_layout.addWidget(card_fotos)

        # 4. Botón Guardar
        btn_guardar_layout = QHBoxLayout()
        btn_guardar_layout.addStretch()

        self.btn_guardar = QPushButton("  Guardar Docente y Registrar Biometría")
        self.btn_guardar.setIcon(QIcon("src/ui/assets/check.svg"))
        self.btn_guardar.setIconSize(QSize(18, 18))
        self.btn_guardar.setFixedHeight(48)
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 10px 32px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_guardar.clicked.connect(self._guardar_docente)

        btn_guardar_layout.addWidget(self.btn_guardar)
        main_layout.addLayout(btn_guardar_layout)

        scroll.setWidget(contenido)
        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)
        layout_externo.addWidget(scroll)

    def _guardar_docente(self):
        legajo = self.txt_legajo.text().strip()
        nombre = self.txt_nombre.text().strip()
        apellido = self.txt_apellido.text().strip()
        dni = self.txt_dni.text().strip()
        cuil = self.txt_cuil.text().strip()

        if not all([legajo, nombre, apellido, dni, cuil]):
            QMessageBox.warning(self, "Campos Incompletos", "Por favor complete todos los campos obligatorios (*).")
            return

        if not (self.foto_frontal.tiene_foto() and self.foto_izq.tiene_foto() and self.foto_der.tiene_foto()):
            QMessageBox.warning(
                self, "Biometría Incompleta",
                "Para garantizar la precisión de DeepFace, es obligatorio registrar los 3 ángulos biométricos (Frontal, Izquierdo y Derecho)."
            )
            return

        try:
            docente_id = self.docente_repo.crear_docente(
                legajo=legajo,
                nombre=nombre,
                apellido=apellido,
                dni=dni,
                cuil=cuil,
                correo_electronico=self.txt_correo.text().strip() or None,
                telefono=self.txt_telefono.text().strip() or None,
                domicilio=self.txt_domicilio.text().strip() or None,
            )

            # Guardar las 3 fotos en foto_docente
            self.docente_repo.guardar_foto(docente_id, "frontal", self.foto_frontal.obtener_bytes())
            self.docente_repo.guardar_foto(docente_id, "izquierdo", self.foto_izq.obtener_bytes())
            self.docente_repo.guardar_foto(docente_id, "derecho", self.foto_der.obtener_bytes())

            QMessageBox.information(
                self, "Registro Exitoso",
                f"El docente {apellido}, {nombre} (Legajo: {legajo}) fue enrolado exitosamente con sus 3 muestras biométricas."
            )

            self._limpiar_formulario()
            self.docente_guardado.emit(docente_id)

        except Exception as e:
            QMessageBox.critical(self, "Error de Persistencia", f"No se pudo registrar el docente en PostgreSQL:\n{e}")

    def _limpiar_formulario(self):
        self.txt_legajo.clear()
        self.txt_nombre.clear()
        self.txt_apellido.clear()
        self.txt_dni.clear()
        self.txt_cuil.clear()
        self.txt_correo.clear()
        self.txt_telefono.clear()
        self.txt_domicilio.clear()
        self.foto_frontal.limpiar()
        self.foto_izq.limpiar()
        self.foto_der.limpiar()

    @staticmethod
    def _crear_label(texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setStyleSheet("color: #bdc3c7; font-size: 13px; font-weight: bold; border: none;")
        return lbl

    @staticmethod
    def _crear_input(placeholder: str = "") -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setStyleSheet("""
            QLineEdit {
                background-color: #242946;
                color: #ffffff;
                font-size: 13px;
                padding: 8px 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
            }
        """)
        return inp
