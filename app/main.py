from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import psycopg2
import os
from pydantic import BaseModel
from datetime import datetime
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

# --- SCHEMAS ---
class BookingCreate(BaseModel):
    spot_id: int
    guest_id: int
    start_time: datetime
    end_time: datetime

# --- ENDPOINTS ---
@app.get("/")
def root():
    return {"status": "online", "message": "Parking API is live!"}

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
            "id": row[0], "title": row[1], "address": row[2], "area": row[3],
            "price_per_hour": row[4], "latitude": row[5], "longitude": row[6],
            "distance_km": round(row[7], 2)
        })
        
    return {"total_spots": len(spots), "data": spots}

@app.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(database.get_db)):
    # 1. Verify the spot exists
    spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.id == booking.spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
        
    # 2. Check for overlapping bookings (Double-booking protection)
    overlapping = db.query(models.Booking).filter(
        models.Booking.spot_id == booking.spot_id,
        models.Booking.status == "confirmed",
        models.Booking.start_time < booking.end_time,
        models.Booking.end_time > booking.start_time
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=400, detail="Spot is already booked for this time slot")
        
    # 3. Calculate total price dynamically
    duration_hours = (booking.end_time - booking.start_time).total_seconds() / 3600
    if duration_hours <= 0:
        raise HTTPException(status_code=400, detail="End time must be after start time")
        
    total_price = round(duration_hours * spot.price_per_hour, 2)
    
    # 4. Save the reservation
    new_booking = models.Booking(
        spot_id=booking.spot_id,
        guest_id=booking.guest_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
        total_price=total_price
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return {
        "message": "Booking successful!", 
        "booking_id": new_booking.id, 
        "duration_hours": round(duration_hours, 2),
        "total_price": total_price
    }
