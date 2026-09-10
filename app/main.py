from fastapi import FastAPI
import psycopg2
import os

app = FastAPI(title="Parking Marketplace API (Simulated Environment)")

DB_URL = os.getenv("DATABASE_URL", "postgresql://parking_user:parking_pass@db:5432/parking_db")

@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Parking Marketplace API is live!",
        "mode": "Simulation / Testing"
    }

@app.get("/health")
def health_check():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.close()
        return {"database": "Connected", "type": "PostgreSQL + PostGIS"}
    except Exception as e:
        return {"database": "Error", "details": str(e)}
