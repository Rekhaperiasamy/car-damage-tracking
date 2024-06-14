from pydantic import BaseModel
from datetime import date


class CarDataResponse(BaseModel):
    license_plate: str
    model: str
    color: str
    vin_number: str
    brand: str


class CarDataRequest(BaseModel):
    license_plate: str
    model: str
    color: str
    vin_number: str
    brand: str


class DamageDataResponse(BaseModel):
    damage_type: str
    damaged_part: str
    date: date
    car: CarDataResponse


class DamageCreateDataResponse(BaseModel):
    damage_type: str
    damaged_part: str
    date: date


class DamageDataRequest(BaseModel):
    license_plate: str
    damage_type: str
    damaged_part: str
    date: date


class CarAndDamageResponse(BaseModel):
    car: CarDataResponse
    damages: list[DamageCreateDataResponse]
