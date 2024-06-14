from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
import logging

from database.database import Database
from database.models import DamageData
from routers.models import CarDataResponse, DamageDataResponse, DamageDataRequest, DamageCreateDataResponse
from database.damagefilters import DamageFilters

router = APIRouter()

db_session = Database().get_session()

tags_metadata = [
    {"name": "Admin operations", "description": "Admin operations Endpoint"},
    {"name": "Car & Damage Data", "description": "Car & Damage Data Results"}
]


@router.get("/damage", response_model=list[DamageDataResponse], tags=["Car & Damage Data"])
def read_damage_data(
    damage_type: Optional[str] = Query(None, description="Car's Damage Type"),
    damaged_part: Optional[str] = Query(
        None, description="Car's Damaged part"),
    limit: int = Query(100, description="Limit the number of results"),
    offset: int = Query(0, description="Offset for pagination")
):
    try:
        filters = DamageFilters.get_damage_data_filter(
            DamageData,
            damage_type,
            damaged_part
        )
        damage_data = (db_session.query(DamageData)
                       .options(joinedload(DamageData.car))
                       .filter(*filters)
                       .limit(limit)
                       .offset(offset)
                       .all())

        result = []
        for damage in damage_data:
            car_data = CarDataResponse(
                license_plate=damage.car.license_plate,
                model=damage.car.model,
                color=damage.car.color,
                vin_number=damage.car.vin_number,
                brand=damage.car.brand
            )
            damage_response = DamageDataResponse(
                license_plate=damage.license_plate,
                damage_type=damage.damage_type,
                damaged_part=damage.damaged_part,
                date=damage.date,
                car=car_data
            )
            result.append(damage_response)

        return result

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/admin/damage", response_model=DamageCreateDataResponse, tags=["Admin operations"])
def create_damage_data(damage_data_request: DamageDataRequest):
    try:
        new_damage = DamageData(**damage_data_request.dict())
        db_session.add(new_damage)
        db_session.commit()
        db_session.refresh(new_damage)
        return DamageCreateDataResponse(**new_damage.__dict__)

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        db_session.rollback()
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(
                status_code=400, detail="Duplicate entry for damage ID")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/admin/damage/{damage_id}", response_model=dict, tags=["Admin operations"])
def delete_damage_data(damage_id: int = Path(..., description="The ID of the damage to delete")):
    try:
        damage_data = db_session.query(DamageData).filter(
            DamageData.id == damage_id).first()
        if not damage_data:
            raise HTTPException(
                status_code=404, detail="Damage data not found")

        db_session.delete(damage_data)
        db_session.commit()
        return {"message": "Damage data deleted successfully"}

    except SQLAlchemyError as e:
        logging.error(f"Database error: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        db_session.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
