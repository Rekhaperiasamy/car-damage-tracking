import pytest
from unittest.mock import MagicMock, Mock
from unittest.mock import patch
from database.models import DamageData


@pytest.fixture
def mock_damage_data_db_session():
    with patch('routers.damage.db_session') as mock_db_session:
        yield mock_db_session


# Mock data
MOCK_DATA = [
    DamageData(
        license_plate="ABC123",
        damage_type="Scratch",
        damaged_part="Door",
        date="2023-01-01",
        car=MagicMock(
            license_plate="ABC123",
            model="Model S",
            color="Red",
            vin_number="1HGCM82633A123456",
            brand="Tesla"
        )
    ),
    DamageData(
        license_plate="XYZ789",
        damage_type="Dent",
        damaged_part="Bumper",
        date="2023-02-01",
        car=MagicMock(
            license_plate="XYZ789",
            model="Model 3",
            color="Blue",
            vin_number="5YJ3E1EA7KF317817",
            brand="Tesla"
        )
    )
]


def mock_get_damage_data_filter(model, damage_type, damaged_part):
    return []


@pytest.fixture
def mock_damage_filters():
    with patch('routers.damage.DamageFilters.get_damage_data_filter', side_effect=mock_get_damage_data_filter):
        yield


def test_read_damage_data(test_client, mock_damage_data_db_session, mock_damage_filters):
    mock_query = MagicMock()
    mock_query = mock_damage_data_db_session.query.return_value
    mock_query.options.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.limit.return_value = mock_query
    mock_query.offset.return_value = mock_query
    mock_query.all.return_value = MOCK_DATA
    response = test_client.get("/damage?limit=2&offset=0")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]['damage_type'] == "Scratch"
    assert response.json()[1]['damage_type'] == "Dent"


def test_read_damage_data_no_results(test_client, mock_damage_data_db_session, mock_damage_filters):
    mock_damage_data_db_session.query.return_value.all.return_value = []
    response = test_client.get("/damage?limit=2&offset=0")
    assert response.status_code == 200
    assert response.json() == []


def test_delete_existing_damage(test_client, mock_damage_data_db_session):
    damage_id = 1
    damage_data = DamageData(id=damage_id)

    mock_damage_data_db_session.query().filter().first.return_value = damage_data

    response = test_client.delete(f"/admin/damage/{damage_id}")

    assert response.status_code == 200
    assert response.json() == {"message": "Damage data deleted successfully"}
    mock_damage_data_db_session.delete.assert_called_once_with(damage_data)
    mock_damage_data_db_session.commit.assert_called_once()


def test_create_damage_data_success(test_client, mock_damage_data_db_session):
    damage_data_request = {
        "license_plate": "HHP85866",
        "damage_type": "Scratch",
        "damaged_part": "Bonnet",
        "date": "2024-06-14"
    }
    mock_new_damage = DamageData(**damage_data_request)

    mock_damage_data_db_session.add.return_value = None
    mock_damage_data_db_session.commit.return_value = None
    mock_damage_data_db_session.query(
        DamageData).return_value = mock_new_damage
    response = test_client.post("/admin/damage", json=damage_data_request)

    assert response.status_code == 200
    assert response.json() == {
        "damage_type": "Scratch",
        "damaged_part": "Bonnet",
        "date": "2024-06-14"
    }
