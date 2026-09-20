from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
import psycopg2
import os
import jwt
from pydantic import BaseModel
from datetime import datetime
from app import models, database, security

models.Base.metadata.create_all(bind=database.engine)

db_session = database.SessionLocal()
try:
    db_session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    db_session.commit()
except Exception:
    db_session.rollback()
finally:
    db_session.close()

app = FastAPI(title="Secure Parking Marketplace API")
DB_URL = os.getenv("DATABASE_URL", "postgresql://parking_user:parking_pass@db:5432/parking_db")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- SCHEMAS ---
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class BookingCreate(BaseModel):
    spot_id: int
    start_time: datetime
    end_time: datetime

# --- SECURITY DEPENDENCIES ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Bank-Level Restriction: Admin privileges required to alter this resource.")
    return current_user

# --- AUTH ENDPOINTS ---
@app.post("/register", status_code=201)
def register_user(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = security.get_password_hash(user.password)
    # The first user created is automatically an admin for our testing purposes
    is_first_user = db.query(models.User).count() == 0 
    
    new_user = models.User(email=user.email, hashed_password=hashed_pw, full_name=user.full_name, is_admin=is_first_user)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- LOCKED ENDPOINTS ---
@app.get("/spots")
def get_all_spots(db: Session = Depends(database.get_db)):
    return db.query(models.ParkingSpot).all()

# Notice the Depends(get_current_user) - You CANNOT book without a valid JWT token
@app.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.id == booking.spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
        
    overlapping = db.query(models.Booking).filter(
        models.Booking.spot_id == booking.spot_id,
        models.Booking.status == "confirmed",
        models.Booking.start_time < booking.end_time,
        models.Booking.end_time > booking.start_time
    ).first()
    
    if overlapping:
        raise HTTPException(status_code=400, detail="Spot is already booked")
        
    duration_hours = (booking.end_time - booking.start_time).total_seconds() / 3600
    total_price = round(duration_hours * spot.price_per_hour, 2)
    
    new_booking = models.Booking(
        spot_id=booking.spot_id,
        guest_id=current_user.id, # Automatically uses the verified ID from the JWT token
        start_time=booking.start_time,
        end_time=booking.end_time,
        total_price=total_price
    )
    db.add(new_booking)
    db.commit()
    
    return {"message": "Booking successful!", "total_price": total_price}

# ADMIN ONLY ENDPOINT - Normal users will be blocked here with a 403 error
@app.delete("/spots/{spot_id}")
def admin_delete_spot(spot_id: int, db: Session = Depends(database.get_db), admin_user: models.User = Depends(get_current_admin_user)):
    spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Spot not found")
    db.delete(spot)
    db.commit()
    return {"message": "Spot forcibly removed by Admin."}
