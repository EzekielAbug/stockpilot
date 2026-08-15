# Use official Python lightweight image

FROM python:3.13-slim

# Set working directory inside the container

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only requirements first (to cache the pip install step)

COPY requirements.txt .

# Install dependencies

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code

COPY . .

# Expose the port FastAPI runs on

EXPOSE 8000

# Command to run the application

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]