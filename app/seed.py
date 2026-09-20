from app.database import SessionLocal, engine
from app import models, security

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(models.User).count() == 0:
    print("Seeding SECURE Mumbai data...")
    # Hashing the passwords using Argon2 before saving them
    admin_pw = security.get_password_hash("admin123")
    user_pw = security.get_password_hash("user123")
    
    admin = models.User(email="admin@parking.com", hashed_password=admin_pw, full_name="System Admin", is_admin=True)
    driver = models.User(email="driver@parking.com", hashed_password=user_pw, full_name="Nimit Mishra", is_admin=False)
    
    db.add_all([admin, driver])
    db.commit()

    spots = [
        models.ParkingSpot(title="Covered Parking BKC", address="G Block, BKC", area="BKC", latitude=19.0657, longitude=72.8686, price_per_hour=80.0, owner_id=admin.id),
        models.ParkingSpot(title="Mall Basement Spot", address="Lower Parel", area="Lower Parel", latitude=18.9953, longitude=72.8242, price_per_hour=100.0, owner_id=admin.id)
    ]
    db.add_all(spots)
    db.commit()
    print("Secure Data seeded successfully!")
else:
    print("Data already exists.")
db.close()
