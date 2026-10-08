from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_oDjqHzS7X5by@ep-lively-dream-b39oep82-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

# Helper function: opens a fresh connection per request so connections never drop/close
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

class Student(BaseModel):
    id: int
    name: str
    course: str


# 1. Get All Students
@app.get('/students')
def get_all_students():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT id, name, course FROM students ORDER BY id ASC')
            return cursor.fetchall()
    finally:
        conn.close()


# 2. Get Single Student by ID
@app.get('/students/{id}')
def get_single_student(id: int):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT id, name, course FROM students WHERE id=%s', (id,))
            student = cursor.fetchone()
            if not student:
                raise HTTPException(status_code=404, detail='Student not found')
            return student
    finally:
        conn.close()


# 3. Create Student Record
@app.post('/students', status_code=status.HTTP_201_CREATED)
def create_student_record(student: Student):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO students (id, name, course) VALUES (%s, %s, %s)',
                (student.id, student.name, student.course)
            )
            return {"detail": "Student record created successfully"}
    except psycopg2.IntegrityError:
        raise HTTPException(status_code=409, detail="Student ID already exists")
    finally:
        conn.close()


# 4. Update Student Record
@app.put('/students/{id}')
def update_student_record(id: int, student: Student):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE students SET id=%s, name=%s, course=%s WHERE id=%s',
                (student.id, student.name, student.course, id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail='Invalid ID')
            return {"detail": "Student record updated successfully"}
    finally:
        conn.close()


# 5. Delete Record
@app.delete('/students/{id}')
def delete_student_record(id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM students WHERE id=%s', (id,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail='Invalid ID')
            return {"detail": "Student record deleted successfully"}
    finally:
        conn.close()