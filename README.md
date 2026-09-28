# Doctor Patient Backend API

A FastAPI backend application for managing doctors and patients.

## Tech Stack

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- JWT Authentication
- Uvicorn
- Pytest
- Docker

## Features

- User registration and login
- JWT authentication
- Role-based authorization
- Doctor management
- Patient management
- Doctor-patient relationship
- Patient assignment to doctors
- Doctor PUT and PATCH operations
- Patient PUT and PATCH operations
- Soft delete for doctors
- Data validation
- Unique doctor email validation
- Phone number validation
- Filtering
- Pagination
- SQLite database
- Modular project structure
- CORS configuration
- Environment variables
- Logging
- Docker support
- Pytest unit tests
- API versioning

## API Version

All main APIs use:

`/api/v1/`

## Main Endpoints

### Authentication

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`

### Doctors

- `POST /api/v1/doctors`
- `GET /api/v1/doctors`
- `GET /api/v1/doctors/{doctor_id}`
- `PUT /api/v1/doctors/{doctor_id}`
- `PATCH /api/v1/doctors/{doctor_id}`
- `DELETE /api/v1/doctors/{doctor_id}`
- `POST /api/v1/doctors/{doctor_id}/patients/{patient_id}`
- `GET /api/v1/doctors/{doctor_id}/patients`

### Patients

- `POST /api/v1/patients`
- `GET /api/v1/patients`
- `GET /api/v1/patients/{patient_id}`
- `PUT /api/v1/patients/{patient_id}`
- `PATCH /api/v1/patients/{patient_id}`
- `DELETE /api/v1/patients/{patient_id}`

## Project Structure

```text
Doctor_Patient_Backend-App/
│
├── auth/
│   ├── __init__.py
│   └── security.py
│
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── doctors.py
│   └── patients.py
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── doctor_service.py
│   └── patient_service.py
│
├── tests/
│   └── test_api.py
│
├── config.py
├── database.py
├── models.py
├── schemas.py
├── main.py
├── Dockerfile
├── requirements.txt
├── .env
└── .gitignore
