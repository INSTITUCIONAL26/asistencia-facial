import os
import sys

# Fijar directorio al script actual
base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)
sys.path.insert(0, os.path.join(base_dir, 'src'))

from config.database import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute('TRUNCATE TABLE asistencia, licencia_docente, obligacion_horaria, foto_docente, docente RESTART IDENTITY CASCADE;')
conn.commit()
cur.close()
conn.close()
print('¡Todos los registros de prueba fueron eliminados exitosamente! IDs reiniciados a 1.')
