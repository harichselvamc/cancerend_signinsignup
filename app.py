from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import sqlite3
from typing import List

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        phone TEXT NOT NULL)''')
    conn.commit()

class SignInRequest(BaseModel):
    email: str
    phone: str

class Patient(BaseModel):
    email: str
    phone: str

@app.post("/signin")
def signin(request: SignInRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE email = ? AND phone = ?", (request.email, request.phone))
    patient = cursor.fetchone()
    conn.close()
    return {"authenticated": bool(patient)}

@app.post("/admin/patient")
def create_patient(patient: Patient):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO patients (email, phone) VALUES (?, ?)", (patient.email, patient.phone))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()
    return {"message": "Patient created successfully"}

@app.get("/admin/patients", response_model=List[Patient])
def read_patients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT email, phone FROM patients")
    patients = cursor.fetchall()
    conn.close()
    return [Patient(email=row["email"], phone=row["phone"]) for row in patients]

@app.put("/admin/patient/{email}")
def update_patient(email: str, patient: Patient):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE patients SET phone = ? WHERE email = ?", (patient.phone, email))
    conn.commit()
    conn.close()
    return {"message": "Patient updated successfully"}

@app.delete("/admin/patient/{email}")
def delete_patient(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    return {"message": "Patient deleted successfully"}
