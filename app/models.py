from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    spots = relationship("Spot", back_populates="owner")
    bookings = relationship("Booking", back_populates="guest")

class Spot(Base):
    __tablename__ = "spots"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price_per_hour = Column(Float, nullable=False)
    
    # Store latitude and longitude directly for easy access
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # PostGIS geometry column for spatial queries (SRID 4326 is standard GPS coordinates)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=True)
    
    is_available = Column(Boolean, default=True)
    
    owner = relationship("User", back_populates="spots")
    bookings = relationship("Booking", back_populates="spot")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("spots.id"))
    guest_id = Column(Integer, ForeignKey("users.id"))
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    total_price = Column(Float, nullable=False)
    status = Column(String, default="pending") # pending, confirmed, cancelled, completed
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    spot = relationship("Spot", back_populates="bookings")
    guest = relationship("User", back_populates="bookings")
