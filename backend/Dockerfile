# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY ./backend/requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY ./backend/app /app/app
COPY ./scripts /app/scripts

# Make the wait-for-db.sh script executable
RUN chmod +x /app/scripts/wait-for-db.sh

# Expose the port the app runs on
EXPOSE ${PORT}

# Define the command to run your app
# The wait-for-db.sh script will handle db_init.py and seed.py
CMD ["/app/scripts/wait-for-db.sh", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
