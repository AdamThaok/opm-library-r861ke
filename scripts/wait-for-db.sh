#!/bin/sh
# wait-for-db.sh

set -e

host="$DB_HOST"
port="$DB_PORT"

# Remove the 'postgresql+asyncpg://' prefix if present, and split into user, password, host, port, dbname
DB_URL_NO_DRIVER=$(echo "$DATABASE_URL" | sed 's/postgresql+asyncpg:\/\///' | sed 's/postgres:\/\///')
DB_USER=$(echo "$DB_URL_NO_DRIVER" | cut -d ':' -f 1)
DB_PASSWORD=$(echo "$DB_URL_NO_DRIVER" | cut -d ':' -f 2 | cut -d '@' -f 1)
DB_HOST=$(echo "$DB_URL_NO_DRIVER" | cut -d '@' -f 2 | cut -d ':' -f 1)
DB_PORT=$(echo "$DB_URL_NO_DRIVER" | cut -d ':' -f 3 | cut -d '/' -f 1)
DB_NAME=$(echo "$DB_URL_NO_DRIVER" | cut -d '/' -f 2)


>&2 echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."

until PGPASSWORD=$DB_PASSWORD pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"

# Run database initialization and seeding scripts
python /app/scripts/db_init.py
python /app/scripts/seed.py

# Execute the original command passed to the script
exec "$@"
