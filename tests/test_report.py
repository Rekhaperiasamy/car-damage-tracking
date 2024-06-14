import pytest
from unittest.mock import patch, MagicMock
from database.models import CarData, DamageData
from routers.models import CarDataResponse, DamageCreateDataResponse, CarAndDamageResponse
import tempfile


def mock_car_data():
    car_data = CarData(
        license_plate="ABC123",
        model="Test Model",
        color="Red",
        vin_number="1HGBH41JXMN109186",
        brand="Test Brand"
    )
    return car_data


def mock_damage_data():
    return [
        DamageData(
            damage_type="Scratch",
            damaged_part="Front Bumper",
            date="2023-01-01"
        ),
        DamageData(
            damage_type="Dent",
            damaged_part="Left Door",
            date="2023-01-02"
        )
    ]


def mock_car_response():
    return CarDataResponse(
        license_plate="ABC123",
        model="Test Model",
        color="Red",
        vin_number="1HGBH41JXMN109186",
        brand="Test Brand"
    )


def mock_damage_response():
    return [
        DamageCreateDataResponse(
            damage_type="Scratch",
            damaged_part="Front Bumper",
            date="2023-01-01"
        ),
        DamageCreateDataResponse(
            damage_type="Dent",
            damaged_part="Left Door",
            date="2023-01-02"
        )
    ]


@pytest.fixture
def mock_db_session():
    with patch('routers.report.db_session') as mock:
        yield mock


@pytest.fixture
def mock_requests_post():
    with patch('routers.report.requests.post') as mock:
        yield mock


@pytest.fixture
def mock_extract_plate():
    with patch('routers.report.extract_plate') as mock:
        yield mock


def test_generate_report_success(test_client, mock_db_session, mock_requests_post, mock_extract_plate):
    # Mock the database session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_car_data()
    mock_db_session.query.return_value.filter.return_value.all.return_value = mock_damage_data()

    # Mock the external API call
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"plate_text": "ABC123"}]
    mock_requests_post.return_value = mock_response

    # Mock the extract_plate function
    mock_extract_plate.return_value = "ABC123"

    # Create a temporary file to simulate file upload
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"fake image data")
        tmp_file.seek(0)
        tmp_file_name = tmp_file.name

    # Mock file upload
    with open(tmp_file_name, "rb") as f:
        response = test_client.post(
            "/generate-report", files={"file": f})

    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == 'attachment; filename="report.pdf"'
    assert response.headers["content-type"] == 'application/pdf'


def test_generate_report_car_not_found(test_client, mock_db_session, mock_requests_post, mock_extract_plate):
    # Mock the database session with no car data
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Mock the external API call
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"plate_text": "ABC123"}]
    mock_requests_post.return_value = mock_response

    # Mock the extract_plate function
    mock_extract_plate.return_value = "ABC123"

    # Create a temporary file to simulate file upload
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"fake image data")
        tmp_file.seek(0)
        tmp_file_name = tmp_file.name

    # Mock file upload
    with open(tmp_file_name, "rb") as f:
        response = test_client.post(
            "/generate-report", files={"file": f})

    assert response.status_code == 404
    assert response.json() == {"detail": "Car not found"}


def test_generate_report_external_api_failure(test_client, mock_requests_post):
    # Mock the external API call with failure
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_requests_post.return_value = mock_response

    # Create a temporary file to simulate file upload
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(b"fake image data")
        tmp_file.seek(0)
        tmp_file_name = tmp_file.name

    # Mock file upload
    with open(tmp_file_name, "rb") as f:
        response = test_client.post(
            "/generate-report", files={"file": f})

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Failed to upload image to external API"}
