from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
import psycopg2
import os
from app import models, database

models.Base.metadata.create_all(bind=database.engine)

db_session = database.SessionLocal()
try:
    db_session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    db_session.commit()
except Exception:
    db_session.rollback()
finally:
    db_session.close()

app = FastAPI(title="Parking Marketplace API")
DB_URL = os.getenv("DATABASE_URL", "postgresql://parking_user:parking_pass@db:5432/parking_db")

@app.get("/")
def root():
    return {"status": "online", "message": "Parking API is live!"}

@app.get("/health")
def health_check():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.close()
        return {"database": "Connected"}
    except Exception as e:
        return {"database": "Error", "details": str(e)}

@app.get("/spots")
def get_all_spots(db: Session = Depends(database.get_db)):
    spots = db.query(models.ParkingSpot).all()
    return {"total_spots": len(spots), "data": spots}

@app.get("/spots/search")
def search_spots(
    lat: float = Query(..., description="Driver's current latitude"),
    lng: float = Query(..., description="Driver's current longitude"),
    radius_km: float = Query(5.0, description="Search radius in kilometers"),
    db: Session = Depends(database.get_db)
):
    query = text("""
        SELECT id, title, address, area, price_per_hour, latitude, longitude,
               ST_DistanceSphere(
                   ST_MakePoint(longitude, latitude),
                   ST_MakePoint(:lng, :lat)
               ) / 1000 AS distance_km
        FROM parking_spots
        WHERE ST_DistanceSphere(
                   ST_MakePoint(longitude, latitude),
                   ST_MakePoint(:lng, :lat)
               ) <= :radius_meters
        ORDER BY distance_km
    """)
    
    result = db.execute(query, {"lat": lat, "lng": lng, "radius_meters": radius_km * 1000})
    
    spots = []
    for row in result:
        spots.append({
            "id": row[0],
            "title": row[1],
            "address": row[2],
            "area": row[3],
            "price_per_hour": row[4],
            "latitude": row[5],
            "longitude": row[6],
            "distance_km": round(row[7], 2)
        })
        
    return {"total_spots": len(spots), "search_radius_km": radius_km, "data": spots}