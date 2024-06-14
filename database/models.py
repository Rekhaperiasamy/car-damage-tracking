from sqlalchemy import Column, String, Date, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CarData(Base):
    __tablename__ = "cars"

    license_plate = Column(String, primary_key=True, index=True)
    model = Column(String)
    color = Column(String)
    vin_number = Column(String, unique=True, index=True)
    brand = Column(String, index=True)

    # damages = relationship("DamageData", back_populates="car")
    damages = relationship(
        "DamageData", back_populates="car", cascade="all, delete-orphan")


class DamageData(Base):
    __tablename__ = "damages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    license_plate = Column(String, ForeignKey("cars.license_plate"))
    damage_type = Column(String, index=True)
    damaged_part = Column(String, index=True)
    date = Column(Date)

    car = relationship("CarData", back_populates="damages")
