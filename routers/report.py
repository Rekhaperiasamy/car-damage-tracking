from fastapi import APIRouter, File, UploadFile, HTTPException, Response
from sqlalchemy.exc import SQLAlchemyError
from database.database import Database
from database.models import DamageData, CarData
from routers.models import CarDataResponse, DamageCreateDataResponse, CarAndDamageResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import base64
import requests
import base64
import re
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
EXTERNAL_API_URL = "https://gatiosoft.ro/platebber.aspx"

router = APIRouter()

db_session = Database().get_session()

tags_metadata = [
    {"name": "Car & Damage Data", "description": "Car & Damage Data Results"}
]


@router.post("/generate-report", response_model=CarAndDamageResponse, tags=["Car & Damage Data"])
async def generate_report(file: UploadFile = File(...)):
    license_plate = await call_external_api(file)

    try:
        car_data = db_session.query(CarData).filter(
            CarData.license_plate == license_plate).first()
        if not car_data:
            raise HTTPException(status_code=404, detail="Car not found")

        damage_data = db_session.query(DamageData).filter(
            DamageData.license_plate == license_plate).all()

        car_response = CarDataResponse(
            license_plate=car_data.license_plate,
            model=car_data.model,
            color=car_data.color,
            vin_number=car_data.vin_number,
            brand=car_data.brand
        )

        damage_responses = [
            DamageCreateDataResponse(
                damage_type=damage.damage_type,
                damaged_part=damage.damaged_part,
                date=damage.date
            ) for damage in damage_data
        ]

        response = CarAndDamageResponse(
            car=car_response, damages=damage_responses)

        pdf_bytes = create_pdf(response)

        return PDFResponse(content=pdf_bytes, filename="report.pdf", media_type='application/pdf')

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


async def call_external_api(file: UploadFile):

    contents = await file.read()
    file_base64 = base64.b64encode(contents).decode('utf-8')
    auth = f'{USERNAME}:{PASSWORD}'.encode('utf-8')
    auth_base64 = base64.b64encode(auth).decode('utf-8')

    response = requests.post(
        EXTERNAL_API_URL,
        json={
            "base64ImageString": file_base64,
            "languageCode": "auto",
            "plate_output": "yes"
        },
        headers={
            "Authorization": f"Basic {auth_base64}",
            'Accept': 'application/json'
        }
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code,
                            detail="Failed to upload image to external API")

    response = response.json()
    license_plate_data = extract_plate(response[0]['plate_text'])
    return license_plate_data


def extract_plate(plate_text):
    matches = re.findall(r'[A-Za-z0-9]+', plate_text)

    for match in matches:
        length = len(match)
        for size in range(1, length + 1):
            for start in range(length - size + 1):
                substring = match[start:start + size]
                if match == substring * (length // size):
                    return substring

    return max(matches, key=len) if matches else None


def create_pdf(data: CarAndDamageResponse):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.drawString(100, height - 40, f"Car Details:")
    c.drawString(100, height - 60, f"License Plate: {data.car.license_plate}")
    c.drawString(100, height - 80, f"Model: {data.car.model}")
    c.drawString(100, height - 100, f"Color: {data.car.color}")
    c.drawString(100, height - 120, f"VIN Number: {data.car.vin_number}")
    c.drawString(100, height - 140, f"Brand: {data.car.brand}")

    c.drawString(100, height - 180, f"Damages:")
    y_position = height - 200
    for damage in data.damages:
        c.drawString(100, y_position, f"Damage Type: {damage.damage_type}")
        c.drawString(100, y_position - 20,
                     f"Damaged Part: {damage.damaged_part}")
        c.drawString(100, y_position - 40, f"Date: {damage.date}")
        y_position -= 60

    c.save()
    buffer.seek(0)
    return buffer.getvalue()


class PDFResponse(Response):
    def __init__(self, content: bytes, filename: str, media_type: str):
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        super().__init__(content=content, media_type=media_type, headers=headers)
