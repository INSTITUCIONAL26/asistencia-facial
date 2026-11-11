# Sistema de Asistencia por Reconocimiento Facial
## Trabajo Final de Cursada - Contexto A: IES N.º 7 Populorum Progressio

Este proyecto es la transformación y adaptación del Sistema de Asistencia Facial al contexto real del **Instituto de Educación Superior N.º 7 Populorum Progressio** (San Salvador de Jujuy).

---

## 🎯 Objetivo de la Adaptación
Automatizar el control de asistencia y permanencia del personal docente mediante biometría facial, integrando el conocimiento de sus obligaciones horarias, carreras y cátedras, eliminando la necesidad de verificación manual externa por parte del personal de secretaría.

---

## 📋 Reglas de Negocio Implementadas

1. **Reconocimiento Facial con Modal de Confirmación Obligatorio:**
   * Al reconocer el rostro de un docente, la cámara permanece activa transmitiendo video fluido a 30 FPS, pero el sistema suspende temporalmente nuevos intentos de inferencia.
   * Se despliega un diálogo modal obligatorio (`ConfirmacionMarcacionDialog`) que muestra la identidad del docente, la cátedra/actividad y la operación propuesta (**ENTRADA** o **SALIDA**).
   * **[ OK ]**: Efectiviza el registro en PostgreSQL.
   * **[ Cancelar ]**: Descarta la marcación sin modificar la base de datos (0 modificaciones).
   * Al cerrarse el modal, el reconocimiento se reanuda aplicando un enfriamiento preventivo (*cooldown*).

2. **Estructura Horaria de Cátedras:**
   * Cada clase dura **1 hora y 20 minutos reloj (80 minutos)**.
   * Un docente puede dictar cátedras en una o múltiples carreras.
   * Soporte nativo para clases consecutivas en un mismo día sin solapamiento.

3. **Clasificación de Marcaciones:**
   * **Tardanza:** Si el ingreso se registra pasados los **5 minutos** del inicio previsto, el sistema lo audita automáticamente calculando los minutos exactos de demora.
   * **Salida Anticipada:** Si el docente se retira antes del horario pactado, se registra como salida anticipada con los minutos de antelación.
   * **Sin Salida:** Si existe entrada sin marcación de salida, el registro queda identificado como pendiente de revisión.

4. **Eventos Especiales:**
   * **Mesas de Examen:** Permite asignar fecha puntual y rol docente (*Presidente, Vocal o Auxiliar*).
   * **Jornadas Institucionales:** Cobertura institucional general sin obligatoriedad de cátedra específica.

5. **Régimen de Inasistencias y Licencias:**
   * **Días Particulares:** Control estricto de hasta **6 días anuales** por docente, con cálculo dinámico del saldo disponible en tiempo real y sin necesidad de certificado.
   * **Licencias Médicas:** Ciclo de vida con estado inicial `PENDIENTE` que es promovido a `CONFIRMADA` una vez que el personal administrativo recibe y registra el certificado médico correspondiente.

6. **Auditoría y Reportes de Secretaría:**
   * Filtros combinados por Docente, Carrera, Cátedra, Rango de Fechas y Anomalías.
   * Cruce automático de horarios previstos vs horas reales marcadas.
   * Exportación de planillas oficiales en **Excel (.xlsx)** y documentos formales en **PDF (.pdf)** con membrete y firmas institucionales.

---

## 🏗️ Arquitectura de la Base de Datos (PostgreSQL 15)

El sistema se apoya en 8 tablas normalizadas:
* `usuario`: Operadores administrativos del sistema en mesa de entrada.
* `docente`: Profesores del instituto con DNI, CUIL y Legajo.
* `foto_docente`: Muestras biométricas vectoriales en 3 ángulos (*frontal, izquierdo, derecho*).
* `carrera`: Carreras terciarias del instituto.
* `catedra`: Materias asignadas a carreras.
* `obligacion_horaria`: Planificación de clases de 80m, jornadas y mesas de examen.
* `asistencia`: Registros biométricos confirmados de entrada y salida con clasificación automática.
* `licencia_docente`: Control de cupos particulares y seguimiento de certificados médicos.

---

## 🚀 Instrucciones de Instalación y Ejecución

### 1. Requisitos Previos
* Python 3.10+
* Docker Desktop instalado y en ejecución.

### 2. Base de Datos en Docker
Desde la raíz del proyecto, iniciar el contenedor PostgreSQL independiente (puerto `5440`):
```powershell
docker compose up -d
```
*(Para verificar que está activo: `docker ps`).*

### 3. Entorno Virtual de Python
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Iniciar la Aplicación
```powershell
python src/main.py
```

---

## 🧪 Validación y Pruebas Automatizadas
El proyecto cuenta con suites de pruebas unitarias e integrales que validan el 100% de los requisitos:
```powershell
# Pruebas de repositorios, cálculo de 80 min, tardanzas y licencias
python tests/test_paso2.py

# Pruebas de pausa/reanudación de cámara y diálogo modal obligatorio
python tests/test_paso3.py

# Pruebas de integración de interfaz de usuario y navegación
python tests/test_paso4.py

# Pruebas de exportación a Excel y PDF
python tests/test_paso5.py
```
