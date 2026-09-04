from datetime import date

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QScrollArea, QDateEdit, QSpinBox,
    QFileDialog, QMessageBox, QSizePolicy, QStackedWidget
)
from PySide6.QtCore import Qt, QDate, QRegularExpression, QSize
from PySide6.QtGui import QPixmap, QRegularExpressionValidator, QIcon

from repositories.alumno_repository import AlumnoRepository


# ════════════════════════════════════════════════════════════════════
#  Widget reutilizable para cada ángulo de foto
# ════════════════════════════════════════════════════════════════════

class AnguloFotoWidget(QWidget):
    """
    Componente para captura/carga de foto de un ángulo del alumno.
    Se instancia tres veces: Frontal, Izquierdo y Derecho.
    """

    def __init__(self, titulo: str, angulo_key: str):
        """
        titulo    : texto visible ('Ángulo Frontal', etc.)
        angulo_key: string para la BD ('frontal', 'izquierdo', 'derecho')
        """
        super().__init__()
        self.titulo     = titulo
        self.angulo_key = angulo_key
        self._imagen_bytes = None
        self._build_ui()

    # ── UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Título del ángulo
        lbl_titulo = QLabel(self.titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #2c3e50;"
        )
        layout.addWidget(lbl_titulo)

        # Fila de botones
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.btn_cargar = QPushButton(" Cargar Foto")
        self.btn_cargar.setIcon(QIcon("src/ui/assets/upload.svg"))
        self.btn_cargar.setIconSize(QSize(14, 14))
        self.btn_cargar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cargar.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #2471a3; }
        """)
        self.btn_cargar.clicked.connect(self._cargar_foto)

        self.btn_tomar = QPushButton(" Tomar Foto")
        self.btn_tomar.setIcon(QIcon("src/ui/assets/camera.svg"))
        self.btn_tomar.setIconSize(QSize(14, 14))
        self.btn_tomar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_tomar.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 14px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #626567; }
        """)
        # Sin lógica por ahora — próximo incremento

        btn_row.addWidget(self.btn_cargar)
        btn_row.addWidget(self.btn_tomar)
        layout.addLayout(btn_row)

        # Panel de imagen
        self.panel = QFrame()
        self.panel.setMinimumHeight(200)
        self.panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        self._set_panel_style(vacio=True)

        panel_inner = QVBoxLayout(self.panel)
        panel_inner.setContentsMargins(6, 6, 6, 6)
        panel_inner.setSpacing(4)

        # ── Stack: página 0 = sin imagen / página 1 = con imagen ────
        self.stack = QStackedWidget()

        # Página 0 — sin imagen
        page_vacia = QWidget()
        pv_layout = QVBoxLayout(page_vacia)
        lbl_vacio = QLabel("Sin imagen\ntodavía")
        lbl_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_vacio.setStyleSheet(
            "color: #95a5a6; font-size: 12px; border: none; background: transparent;"
        )
        pv_layout.addWidget(lbl_vacio)

        # Página 1 — con imagen
        page_imagen = QWidget()
        pi_layout = QVBoxLayout(page_imagen)
        pi_layout.setContentsMargins(4, 4, 4, 4)
        pi_layout.setSpacing(4)

        # Botón borrar arriba a la derecha
        trash_row = QHBoxLayout()
        trash_row.addStretch()
        self.btn_borrar = QPushButton()
        self.btn_borrar.setIcon(QIcon("src/ui/assets/trash-2.svg"))
        self.btn_borrar.setIconSize(QSize(16, 16))
        self.btn_borrar.setFixedSize(30, 30)
        self.btn_borrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_borrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.btn_borrar.clicked.connect(self._borrar_foto)
        trash_row.addWidget(self.btn_borrar)
        pi_layout.addLayout(trash_row)

        # Label con la imagen
        self.lbl_imagen = QLabel()
        self.lbl_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_imagen.setStyleSheet("border: none; background: transparent;")
        pi_layout.addWidget(self.lbl_imagen)

        self.stack.addWidget(page_vacia)   # índice 0
        self.stack.addWidget(page_imagen)  # índice 1

        panel_inner.addWidget(self.stack)
        layout.addWidget(self.panel)

    # ── Slots ────────────────────────────────────────────────────────

    def _cargar_foto(self):
        """Abre el diálogo de archivo y carga la imagen seleccionada."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleccionar imagen — {self.titulo}",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if not path:
            return

        # Leer bytes para la BD
        with open(path, "rb") as f:
            self._imagen_bytes = f.read()

        # Mostrar preview escalado
        pixmap = QPixmap(path).scaled(
            190, 160,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.lbl_imagen.setPixmap(pixmap)
        self.stack.setCurrentIndex(1)
        self._set_panel_style(vacio=False)

    def _borrar_foto(self):
        """Elimina la imagen cargada y vuelve al estado vacío."""
        self._imagen_bytes = None
        self.lbl_imagen.clear()
        self.stack.setCurrentIndex(0)
        self._set_panel_style(vacio=True)

    # ── Helpers ──────────────────────────────────────────────────────

    def _set_panel_style(self, vacio: bool):
        if vacio:
            self.panel.setStyleSheet("""
                QFrame {
                    background-color: #ecf0f1;
                    border: 2px dashed #bdc3c7;
                    border-radius: 6px;
                }
            """)
        else:
            self.panel.setStyleSheet("""
                QFrame {
                    background-color: #eafaf1;
                    border: 2px solid #27ae60;
                    border-radius: 6px;
                }
            """)

    # ── API pública ──────────────────────────────────────────────────

    def tiene_imagen(self) -> bool:
        return self._imagen_bytes is not None

    def get_imagen_bytes(self) -> bytes | None:
        return self._imagen_bytes

    def reset(self):
        self._borrar_foto()


# ════════════════════════════════════════════════════════════════════
#  Widget principal: Registrar Alumno
# ════════════════════════════════════════════════════════════════════

class RegistrarAlumnoWidget(QWidget):
    """
    Vista de Registrar Alumno.

    Zona 1 : Formulario de datos personales (10 campos).
    Zona 2 : 3 ángulos fotográficos (Frontal, Izquierdo, Derecho).
    Botón  : Registrar — valida todo y persiste en la BD.
    """

    def __init__(self):
        super().__init__()
        self.repo = AlumnoRepository()
        self._build_ui()

    # ── Construcción de la UI ────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("background-color: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # ── ScrollArea ───────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        content = QWidget()
        content.setStyleSheet("background-color: transparent;")

        cl = QVBoxLayout(content)
        cl.setContentsMargins(60, 40, 60, 40)
        cl.setSpacing(24)

        # Título
        title = QLabel("Registrar Alumno")
        title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #2c3e50;"
        )
        cl.addWidget(title)

        # ── ZONA 1: Datos personales ─────────────────────────────────
        cl.addWidget(self._build_datos_card())

        # ── ZONA 2: Fotos ────────────────────────────────────────────
        cl.addWidget(self._build_fotos_card())

        # ── Botón Registrar ──────────────────────────────────────────
        btn_registrar = QPushButton("  Registrar Alumno")
        btn_registrar.setIcon(QIcon("src/ui/assets/check.svg"))
        btn_registrar.setIconSize(QSize(20, 20))
        btn_registrar.setFixedHeight(48)
        btn_registrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_registrar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 15px;
                font-weight: bold;
                border-radius: 7px;
                border: none;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        btn_registrar.clicked.connect(self._registrar)
        cl.addWidget(btn_registrar)
        cl.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

    # ── Card datos personales ────────────────────────────────────────

    def _build_datos_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        sub = QLabel("Datos Personales")
        sub.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #2c3e50; margin-bottom: 4px;"
        )
        layout.addWidget(sub)

        grid = QGridLayout()
        grid.setHorizontalSpacing(20)
        grid.setVerticalSpacing(14)

        # Fila 0 — Nombre / Apellido
        self.nombre_input   = self._make_input("Nombre")
        self.apellido_input = self._make_input("Apellido")
        self._add_grid_row(grid, 0, "Nombre *", self.nombre_input,
                                    "Apellido *", self.apellido_input)

        # Fila 1 — DNI / Carrera
        self.dni_input     = self._make_input("Solo dígitos")
        self.dni_input.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^\d{1,20}$"))
        )
        self.carrera_input = self._make_input("Nombre de la carrera")
        self._add_grid_row(grid, 1, "DNI *", self.dni_input,
                                    "Carrera *", self.carrera_input)

        # Fila 2 — Celular / Correo
        self.celular_input = self._make_input("Solo dígitos")
        self.celular_input.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^\d{1,20}$"))
        )
        self.correo_input = self._make_input("ejemplo@mail.com")
        self._add_grid_row(grid, 2, "Celular *", self.celular_input,
                                    "Correo Electrónico *", self.correo_input)

        # Fila 3 — Fecha nac. / Año ingreso
        self.fecha_nac_edit = QDateEdit()
        self.fecha_nac_edit.setCalendarPopup(True)
        self.fecha_nac_edit.setDisplayFormat("dd/MM/yyyy")
        self.fecha_nac_edit.setDate(QDate(2000, 1, 1))
        self.fecha_nac_edit.setFixedHeight(36)
        self.fecha_nac_edit.setMinimumWidth(130)
        self.fecha_nac_edit.setStyleSheet(self._date_edit_style())

        self.anio_spin = QSpinBox()
        self.anio_spin.setRange(1900, 2100)
        self.anio_spin.setValue(date.today().year)
        self.anio_spin.setFixedHeight(36)
        self.anio_spin.setMinimumWidth(100)
        self.anio_spin.setStyleSheet(self._spinbox_style())

        self._add_grid_row(grid, 3, "Fecha de Nacimiento *", self.fecha_nac_edit,
                                    "Año de Ingreso *", self.anio_spin)

        # Fila 4 — Domicilio / Libreta
        self.domicilio_input = self._make_input("Calle y número")
        self.libreta_input   = self._make_input("Número de libreta")
        self._add_grid_row(grid, 4, "Domicilio *", self.domicilio_input,
                                    "Nro. de Libreta *", self.libreta_input)

        layout.addLayout(grid)
        return card

    # ── Card fotos ───────────────────────────────────────────────────

    def _build_fotos_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #dfe6e9;
            }
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        sub = QLabel("Imágenes Biométricas  (las tres son obligatorias)")
        sub.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #2c3e50; margin-bottom: 4px;"
        )
        layout.addWidget(sub)

        angulos_row = QHBoxLayout()
        angulos_row.setSpacing(20)

        self.angulo_frontal   = AnguloFotoWidget("Ángulo Frontal",    "frontal")
        self.angulo_izquierdo = AnguloFotoWidget("Ángulo Izquierdo",  "izquierdo")
        self.angulo_derecho   = AnguloFotoWidget("Ángulo Derecho",    "derecho")

        angulos_row.addWidget(self.angulo_frontal)
        angulos_row.addWidget(self.angulo_izquierdo)
        angulos_row.addWidget(self.angulo_derecho)

        layout.addLayout(angulos_row)
        return card

    # ── Slot Registrar ───────────────────────────────────────────────

    def _registrar(self):
        """Valida todos los campos y persiste en la BD si todo es correcto."""

        # 1. Validar campos de texto obligatorios
        campos = {
            "Nombre":             self.nombre_input.text().strip(),
            "Apellido":           self.apellido_input.text().strip(),
            "DNI":                self.dni_input.text().strip(),
            "Carrera":            self.carrera_input.text().strip(),
            "Celular":            self.celular_input.text().strip(),
            "Correo Electrónico": self.correo_input.text().strip(),
            "Domicilio":          self.domicilio_input.text().strip(),
            "Nro. de Libreta":    self.libreta_input.text().strip(),
        }
        vacios = [k for k, v in campos.items() if not v]
        if vacios:
            QMessageBox.warning(
                self, "Campos incompletos",
                "Los siguientes campos son obligatorios:\n• " + "\n• ".join(vacios)
            )
            return

        # 2. Validar las 3 imágenes
        angulos = [self.angulo_frontal, self.angulo_izquierdo, self.angulo_derecho]
        faltantes = [a.titulo for a in angulos if not a.tiene_imagen()]
        if faltantes:
            QMessageBox.warning(
                self, "Imágenes faltantes",
                "Las siguientes imágenes son obligatorias:\n• " + "\n• ".join(faltantes)
            )
            return

        # 3. Persistir en la BD
        try:
            alumno_id = self.repo.crear_alumno(
                nombre               = campos["Nombre"],
                apellido             = campos["Apellido"],
                dni                  = campos["DNI"],
                carrera              = campos["Carrera"],
                celular              = campos["Celular"],
                correo_electronico   = campos["Correo Electrónico"],
                fecha_de_nacimiento  = self.fecha_nac_edit.date().toPython(),
                anio_de_ingreso      = self.anio_spin.value(),
                domicilio            = campos["Domicilio"],
                libreta              = campos["Nro. de Libreta"],
            )

            for aw in angulos:
                self.repo.guardar_foto(alumno_id, aw.angulo_key, aw.get_imagen_bytes())

            QMessageBox.information(self, "Éxito", "Alumno registrado correctamente.")
            self._limpiar()

        except Exception as e:
            QMessageBox.critical(
                self, "Error al registrar",
                f"No se pudo guardar el alumno en la base de datos:\n{str(e)}"
            )

    # ── Reset del formulario ─────────────────────────────────────────

    def _limpiar(self):
        for inp in [self.nombre_input, self.apellido_input, self.dni_input,
                    self.carrera_input, self.celular_input, self.correo_input,
                    self.domicilio_input, self.libreta_input]:
            inp.clear()
        self.fecha_nac_edit.setDate(QDate(2000, 1, 1))
        self.anio_spin.setValue(date.today().year)
        for aw in [self.angulo_frontal, self.angulo_izquierdo, self.angulo_derecho]:
            aw.reset()

    # ── Helpers de construcción ──────────────────────────────────────

    @staticmethod
    def _input_style() -> str:
        return (
            "padding: 7px 10px;"
            "font-size: 13px;"
            "color: #2c3e50;"
            "border: 1px solid #dfe6e9;"
            "border-radius: 5px;"
            "background-color: #fdfdfd;"
        )

    @staticmethod
    def _date_edit_style() -> str:
        return """
            QDateEdit {
                padding: 4px 8px;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                background-color: #fdfdfd;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
                border-left: 1px solid #dfe6e9;
                background-color: #f0f2f5;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QDateEdit::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #636e72;
            }
            /* Fix transparent arrows and styles in the pop-up calendar */
            QCalendarWidget QWidget {
                alternate-background-color: #f5f6fa;
            }
            QCalendarWidget QToolButton {
                color: #2c3e50;
                background-color: transparent;
                font-size: 14px;
                icon-size: 16px 16px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #dfe6e9;
                border-radius: 4px;
            }
            QCalendarWidget QMenu {
                width: 150px;
                left: 20px;
                color: #2c3e50;
                font-size: 14px;
                background-color: white;
            }
            QCalendarWidget QSpinBox {
                width: 50px;
                font-size: 14px;
                color: #2c3e50;
                background-color: white;
                selection-background-color: #2980b9;
                selection-color: white;
            }
            QCalendarWidget QSpinBox::up-button { subcontrol-origin: border; subcontrol-position: top right; width: 16px; }
            QCalendarWidget QSpinBox::down-button { subcontrol-origin: border; subcontrol-position: bottom right; width: 16px; }
            QCalendarWidget QAbstractItemView:enabled {
                font-size: 13px;
                color: #2c3e50;
                background-color: white;
                selection-background-color: #2980b9;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled { color: #bdc3c7; }
        """

    @staticmethod
    def _spinbox_style() -> str:
        return """
            QSpinBox {
                padding: 4px 8px;
                font-size: 13px;
                color: #2c3e50;
                border: 1px solid #dfe6e9;
                border-radius: 5px;
                background-color: #fdfdfd;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #dfe6e9;
                background-color: #f0f2f5;
                border-top-right-radius: 5px;
            }
            QSpinBox::up-button:hover { background-color: #dfe6e9; }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #dfe6e9;
                background-color: #f0f2f5;
                border-bottom-right-radius: 5px;
            }
            QSpinBox::down-button:hover { background-color: #dfe6e9; }
            QSpinBox::up-arrow {
                image: none; width: 0; height: 0;
                border-left: 4px solid transparent; border-right: 4px solid transparent;
                border-bottom: 5px solid #636e72;
            }
            QSpinBox::down-arrow {
                image: none; width: 0; height: 0;
                border-left: 4px solid transparent; border-right: 4px solid transparent;
                border-top: 5px solid #636e72;
            }
        """

    def _make_input(self, placeholder: str = "") -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(36)
        inp.setStyleSheet(self._input_style())
        return inp

    @staticmethod
    def _add_grid_row(grid, row, lbl1, widget1, lbl2, widget2):
        """Agrega una fila de 2 columnas (label + input) al grid."""
        label_style = "font-size: 13px; color: #636e72;"

        l1 = QLabel(lbl1)
        l1.setStyleSheet(label_style)
        l2 = QLabel(lbl2)
        l2.setStyleSheet(label_style)

        grid.addWidget(l1,      row, 0)
        grid.addWidget(widget1, row, 1)
        grid.addWidget(l2,      row, 2)
        grid.addWidget(widget2, row, 3)
