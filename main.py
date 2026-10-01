from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel

app = FastAPI()

connection = psycopg2.connect(
    host = 'localhost',
    port = '5432',
    database = 'postgres',
    user = 'postgres',
    password = 'Pawan@2004'
)

cursor = connection.cursor()

class Student(BaseModel):
    id: int
    name: str
    course: str

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
        
# Create Student Record
@app.post('/students')
def create_student_record(student: Student):
    try:
        cursor.execute('INSERT INTO students VALUES (%s, %s, %s)', (student.id, student.name, student.course))
        connection.commit()
        raise HTTPException(status_code=201, detail='Student Record Created Successfully')
    except psycopg2.IntegrityError:
        connection.rollback()
        raise HTTPException(status_code=404, detail='Student ID already exists')
    