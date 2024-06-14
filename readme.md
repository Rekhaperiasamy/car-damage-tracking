# Start the app

App runs inside a docker container. It also depends on another container where database runs.

To start both app and the database, run docker-compose up

Once containers are up and running, run the setup script to load data to the database.

Run the following commands.

> docker-compose up --build

> chmod +x setup.sh

> ./setup.sh

# Access the endpoints

After the previous steps, App will run on http://0.0.0.0:8000

Go to http://0.0.0.0:8000/docs to access the swagger doc.

There are seven endpoints

/cars

/damage

/generate-report

/admin/cars

/admin/damage

/admin/cars/{license_plate}

/admin/damage/{license_plate}

All filters and response models are documented in swagger.

# How to run tests

Unit tests are written using pytest.

Run the following commands.

> pip install -r test-requirements.txt

> pytest

# Report

The details of the car and damage are saved in the report.pdf file, which is included in the git repository.
