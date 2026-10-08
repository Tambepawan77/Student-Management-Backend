from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # Use ["*"] to allow all origins (not recommended with credentials)
    allow_credentials=False,    # Allow cookies or authorization headers
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],       # Allow all request headers
)

# connection = psycopg2.connect(
#     host = os.getenv('DB_HOST'),
#     port = os.getenv('DB_PORT'),
#     database = os.getenv('DB_DATABASE'),
#     user = os.getenv('DB_USER'),
#     password = os.getenv('DB_PASS')
# )

connection = psycopg2.connect('postgresql://neondb_owner:npg_oDjqHzS7X5by@ep-lively-dream-b39oep82-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')

cursor = connection.cursor()

class Student(BaseModel):
    id: int = None
    name: str = None
    course: str = None

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

# Update Student Record
@app.put('/students/{id}')
def update_student_record(id: int, student: Student):
    cursor.execute('Update Students SET id=%s, name=%s, course=%s WHERE id=%s',(student.id, student.name, student.course,id))
    if(cursor.rowcount == 0):
        raise HTTPException(status_code=404, detail='Invalid Id')
    connection.commit()
    raise HTTPException(status_code=200, detail='Student Record Updated Successfully')

# Partial update
@app.patch('/students/{id}')
def partial_update(id: int, student: Student):
    if(student.id != None):
        cursor.execute('UPDATE students SET id=%s WHERE id=%s', (student.id, id))
    if(student.name != None):
        cursor.execute('UPDATE students SET name=%s WHERE id=%s', (student.name, id))
    if(student.course != None):
        cursor.execute('UPDATE students SET course=%s WHERE id=%s', (student.course, id))
    if(cursor.rowcount == 0):
        raise HTTPException(status_code=404, detail='Invalid ID')
    connection.commit()
    raise HTTPException(status_code=200, detail='Partial Update Successful')

# Delete Record 
@app.delete('/students/{id}')
def delete_student_record(id: int):
    cursor.execute('DELETE FROM students WHERE id=%s', (id,))
    if (cursor.rowcount == 0):
        raise HTTPException(status_code=404, detail='Invalid ID')
    connection.commit()
    raise HTTPException(status_code=200,detail='Student record deleted Successfully')
    