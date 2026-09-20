from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_host = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False) # BANK LEVEL CONTROL: Only true for system operators

    spots = relationship("ParkingSpot", back_populates="owner")
    bookings = relationship("Booking", back_populates="guest")

class ParkingSpot(Base):
    __tablename__ = "parking_spots"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    address = Column(String, nullable=False)
    area = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="spots")
    bookings = relationship("Booking", back_populates="spot")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"))
    guest_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(String, default="confirmed")

    spot = relationship("ParkingSpot", back_populates="bookings")
    guest = relationship("User", back_populates="bookings")
