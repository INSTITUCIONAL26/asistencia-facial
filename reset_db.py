import sys
sys.path.insert(0, 'src')

from config.database import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute('TRUNCATE TABLE asistencia, foto_alumno, alumno, jornada RESTART IDENTITY CASCADE;')
conn.commit()
cur.close()
conn.close()
print('¡Todos los registros de prueba fueron eliminados exitosamente! IDs reiniciados a 1.')
