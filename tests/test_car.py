import pytest
from unittest.mock import MagicMock
from unittest.mock import patch

from database.models import CarData


@pytest.fixture
def mock_car_data_db_session():
    with patch("routers.car.db_session") as mock:
        yield mock


MOCK_DATA = [
    CarData(license_plate='ABC123', model="Civic", color="Red",
            vin_number="1HGFA16568L000001", brand="Honda"),
    CarData(license_plate='XYZ456', model="Camry", color="Blue",
            vin_number="4T1BE46K97U514571", brand="Toyota")
]


def test_random(test_client, mock_car_data_db_session):
    assert True


def test_read_car_data(test_client, mock_car_data_db_session):
    # Mock the query and all() method
    mock_query = MagicMock()
    mock_query.all.return_value = MOCK_DATA
    mock_car_data_db_session.query.return_value = mock_query

    response = test_client.get("/cars")

    assert response.status_code == 200
    assert response.json() == [
        {'license_plate': 'ABC123', 'model': "Civic", 'color': "Red",
            'vin_number': "1HGFA16568L000001", 'brand': "Honda"},
        {'license_plate': 'XYZ456', 'model': "Camry", 'color': "Blue",
            'vin_number': "4T1BE46K97U514571", 'brand': "Toyota"}
    ]


def test_delete_existing_car(test_client, mock_car_data_db_session):
    # Mocking the db_session and CarData
    mock_car_data = MagicMock()
    mock_car_data.license_plate = "ABC123"
    mock_car_data_db_session.query().filter().first.return_value = mock_car_data

    response = test_client.delete("/admin/cars/ABC123")

    assert response.status_code == 200
    assert response.json() == {
        "detail": "Car and related damages deleted successfully"}
    mock_car_data_db_session.delete.assert_called_once_with(mock_car_data)
    mock_car_data_db_session.commit.assert_called_once()


def test_create_car_data_success(test_client, mock_car_data_db_session):
    car_data_request = {
        "license_plate": "HHP85866",
        "model": "Z6",
        "color": "White",
        "vin_number": "1HGCR2F3XHA12345666",
        "brand": "BMW"
    }
    mock_new_car = CarData(**car_data_request)

    mock_car_data_db_session.add.return_value = None
    mock_car_data_db_session.commit.return_value = None
    mock_car_data_db_session.query(
        CarData).return_value = mock_new_car

    response = test_client.post("/admin/cars", json=car_data_request)

    assert response.status_code == 200
    assert response.json() == {
        "license_plate": "HHP85866",
        "model": "Z6",
        "color": "White",
        "vin_number": "1HGCR2F3XHA12345666",
        "brand": "BMW"
    }
