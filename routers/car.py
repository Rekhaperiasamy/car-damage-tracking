from fastapi import APIRouter, Query, HTTPException
from typing import List
from sqlalchemy.exc import SQLAlchemyError
import logging

from database.database import Database
from database.models import CarData
from routers.models import CarDataResponse, CarDataRequest

router = APIRouter()

db_session = Database().get_session()

tags_metadata = [
    {"name": "Admin operations", "description": "Admin operations Endpoint"},
    {"name": "Car & Damage Data", "description": "Car & Damage Data Results"}
]


@router.get("/cars", response_model=list[CarDataResponse], tags=["Car & Damage Data"])
def read_car_data():
    try:
        car_data = db_session.query(CarData).all()
        return [CarDataResponse(**car.__dict__) for car in car_data]

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/admin/cars/{license_plate}", response_model=dict, tags=["Admin operations"])
def delete_car_data(license_plate: str):
    try:
        car_to_delete = db_session.query(CarData).filter(
            CarData.license_plate == license_plate).first()

        if not car_to_delete:
            raise HTTPException(status_code=404, detail="Car not found")

        db_session.delete(car_to_delete)
        db_session.commit()

        return {"detail": "Car and related damages deleted successfully"}

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/admin/cars", response_model=CarDataResponse, tags=["Admin operations"])
def create_car_data(car_data_request: CarDataRequest):
    try:
        new_car = CarData(**car_data_request.dict())
        db_session.add(new_car)
        db_session.commit()
        db_session.refresh(new_car)
        return CarDataResponse(**new_car.__dict__)

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
