from app.database import SessionLocal, engine
from app import models

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

if db.query(models.User).count() == 0:
    print("Seeding Mumbai fake data...")
    host1 = models.User(full_name="Rahul M.", phone="+919876543210", is_host=True)
    host2 = models.User(full_name="Priya S.", phone="+919876543211", is_host=True)
    db.add_all([host1, host2])
    db.commit()

    spots = [
        models.ParkingSpot(title="Covered Parking BKC", address="G Block, BKC", area="BKC", latitude=19.0657, longitude=72.8686, price_per_hour=80.0, owner_id=host1.id),
        models.ParkingSpot(title="Open plot near Station", address="Andheri East", area="Andheri", latitude=19.1136, longitude=72.8697, price_per_hour=50.0, owner_id=host2.id),
        models.ParkingSpot(title="Mall Basement Spot", address="Lower Parel", area="Lower Parel", latitude=18.9953, longitude=72.8242, price_per_hour=100.0, owner_id=host1.id)
    ]
    db.add_all(spots)
    db.commit()
    print("Data seeded successfully!")
else:
    print("Data already exists.")
db.close()