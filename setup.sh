#!/bin/bash

# Define file paths
COMPOSE_FILE="docker-compose.yml"
TABLE_STRUCTURE_FILE="sql.txt"
CARS_CSV_FILE="cars.csv"
DAMAGES_CSV_FILE="damages.csv"

# Extract PostgreSQL credentials from docker-compose.yml
DB_USER=$(grep POSTGRES_USER $COMPOSE_FILE | awk '{print $2}')
DB_PASSWORD=$(grep POSTGRES_PASSWORD $COMPOSE_FILE | awk '{print $2}')
DB_NAME=$(grep POSTGRES_DB $COMPOSE_FILE | awk '{print $2}')
DB_CONTAINER=$(docker-compose ps -q db)

# Wait for the database to be ready
echo "Waiting for PostgreSQL to be ready..."
until docker exec $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME; do
  sleep 1
done
echo "PostgreSQL is ready."

# Read and execute the table structure SQL
TABLE_STRUCTURE=$(cat $TABLE_STRUCTURE_FILE)

echo "Creating table structure..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "$TABLE_STRUCTURE"

# Load the CSV data into the tables
echo "Loading data from cars.csv..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "\copy cars FROM STDIN WITH CSV HEADER" < $CARS_CSV_FILE

echo "Loading data from damages.csv..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "\copy damages FROM STDIN WITH CSV HEADER" < $DAMAGES_CSV_FILE

# Run the additional query
echo "Updating damages_id_seq sequence..."
docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "SELECT setval('damages_id_seq', (SELECT MAX(id) FROM damages));"

echo "Data loaded successfully."
