from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# DATABASE_URL = "postgresql://postgres:pwd123@localhost/car_damage_tracking"
DATABASE_URL = "postgresql://postgres:pwd123@db:5432/car_damage_tracking"


class Database:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.session()

    def get_engine(self):
        return self.engine
