from fastapi import FastAPI, HTTPException
import psycopg2

app = FastAPI()

connection = psycopg2.connect(
    host = 'localhost',
    port = '5432',
    database = 'postgres',
    user = 'postgres',
    password = 'Pawan@2004'
)

cursor = connection.cursor()

# Get All Students
@app.get('/students')
def get_all_students():
    cursor.execute('SELECT * FROM students')
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append({
            'id': row[0],
            'name': row[1],
            'course': row[2]
        })
    return result

# Get Single Student by ID
@app.get('/students/{id}')
def get_single_student(id: int):
    try:
        cursor.execute('SELECT * FROM students WHERE id=%s', (id,))
        row = cursor.fetchone()
        return {
            'id': row[0],
            'name': row[1],
            'course': row[2]
        }
    except:
        raise HTTPException(status_code=404, detail='Invalid Student ID')
        
    