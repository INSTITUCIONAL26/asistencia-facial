"""
Diálogo Modal Obligatorio de Confirmación de Marcación.
Sistema de Asistencia - IES N.º 7 Populorum Progressio
"""
from typing import Dict, Any
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon


class ConfirmacionMarcacionDialog(QDialog):
    """
    Diálogo modal exigido por el reglamento de cursada (Sección 4 y 5.3):
    - Muestra al docente reconocido, cátedra u obligación y la operación propuesta.
    - Botón OK (Confirma la operación y autoriza la persistencia en BD).
    - Botón Cancelar (Descarta la operación sin modificar la base de datos).
    """

    def __init__(self, datos_evaluacion: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.datos = datos_evaluacion
        self.setWindowTitle("Confirmación de Asistencia - IES N.º 7 Populorum Progressio")
        self.setFixedSize(540, 440)
        self.setModal(True)
        # Quitar botón de ayuda de la barra de título de Windows
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #111424;
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        # 1. Cabecera institucional
        header_layout = QVBoxLayout()
        lbl_instituto = QLabel("IES N.º 7 POPULORUM PROGRESSIO")
        lbl_instituto.setStyleSheet("color: #3498db; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        lbl_titulo = QLabel("Confirmación de Asistencia Docente")
        lbl_titulo.setStyleSheet("color: #ffffff; font-size: 20px; font-weight: bold;")
        
        header_layout.addWidget(lbl_instituto)
        header_layout.addWidget(lbl_titulo)
        layout.addLayout(header_layout)

        # 2. Tarjeta de Datos de la Marcación
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1e36;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(14)

        # Badge de Operación (ENTRADA / SALIDA)
        tipo_op = self.datos.get("tipo_operacion", "OPERACIÓN")
        clasificacion = self.datos.get("clasificacion", "")
        minutos = self.datos.get("minutos_diferencia", 0)

        badge_row = QHBoxLayout()
        lbl_badge_op = QLabel(f" {tipo_op} ")
        
        if tipo_op == "ENTRADA":
            if clasificacion == "tardanza":
                badge_bg = "#e67e22"
                desc_estado = f"Tardanza ({minutos} min de demora)"
                color_desc = "#f39c12"
            else:
                badge_bg = "#27ae60"
                desc_estado = "En Horario Reglamentario"
                color_desc = "#2ecc71"
        else: # SALIDA
            if clasificacion == "anticipada":
                badge_bg = "#d35400"
                desc_estado = f"Salida Anticipada ({minutos} min antes)"
                color_desc = "#e67e22"
            else:
                badge_bg = "#2980b9"
                desc_estado = "Salida Normal"
                color_desc = "#3498db"

        lbl_badge_op.setStyleSheet(f"""
            background-color: {badge_bg};
            color: white;
            font-size: 13px;
            font-weight: bold;
            padding: 4px 12px;
            border-radius: 5px;
        """)
        lbl_badge_op.setFixedHeight(28)

        lbl_clasificacion = QLabel(desc_estado)
        lbl_clasificacion.setStyleSheet(f"color: {color_desc}; font-size: 13px; font-weight: bold;")

        badge_row.addWidget(lbl_badge_op)
        badge_row.addWidget(lbl_clasificacion)
        badge_row.addStretch()
        card_layout.addLayout(badge_row)

        # Grid de Detalles
        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(14)

        campos = [
            ("Docente:", self.datos.get("docente_nombre", "-")),
            ("Legajo:", self.datos.get("docente_legajo", "-")),
            ("Actividad / Cátedra:", self.datos.get("actividad_nombre", "-")),
            ("Carrera:", self.datos.get("carrera_nombre", "Institucional")),
            ("Horario Programado:", self.datos.get("horario_esperado", "-")),
        ]

        if self.datos.get("rol_mesa"):
            campos.append(("Rol en Mesa:", str(self.datos.get("rol_mesa")).upper()))

        for fila, (etiqueta, valor) in enumerate(campos):
            lbl_etq = QLabel(etiqueta)
            lbl_etq.setStyleSheet("color: #95a5a6; font-size: 13px; font-weight: bold;")
            
            lbl_val = QLabel(valor)
            lbl_val.setStyleSheet("color: #ecf0f1; font-size: 13px;")
            lbl_val.setWordWrap(True)

            grid.addWidget(lbl_etq, fila, 0)
            grid.addWidget(lbl_val, fila, 1)

        card_layout.addLayout(grid)
        layout.addWidget(card)

        # 3. Pregunta de Confirmación
        lbl_pregunta = QLabel("¿Desea registrar esta marcación en el sistema?")
        lbl_pregunta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_pregunta.setStyleSheet("color: #bdc3c7; font-size: 13px; font-style: italic;")
        layout.addWidget(lbl_pregunta)

        # 4. Botones de Acción (OK y Cancelar)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setFixedHeight(44)
        self.btn_cancelar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            QPushButton:hover {
                background-color: #415b76;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_confirmar = QPushButton("OK (Confirmar Registro)")
        self.btn_confirmar.setFixedHeight(44)
        self.btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirmar.setDefault(True)
        self.btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        self.btn_confirmar.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancelar, 1)
        btn_layout.addWidget(self.btn_confirmar, 2)
        layout.addLayout(btn_layout)
