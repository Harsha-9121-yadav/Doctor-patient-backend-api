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

### Appointments

- `POST /api/v1/appointments`
- `GET /api/v1/appointments`
- `PUT /api/v1/appointments/{appointment_id}`
- `DELETE /api/v1/appointments/{appointment_id}`

## Authorization

Protected endpoints require a valid JWT access token.

Admin-only operations include:

- Creating doctors
- Updating doctors
- Deleting doctors
- Assigning patients to doctors
- Other administrative operations

Unauthorized users receive appropriate HTTP status codes such as:

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Content`

## Doctor Management

The Doctor API supports:

- Creating doctors
- Listing doctors
- Getting a doctor by ID
- Updating doctor information
- Deleting doctors
- Assigning patients to doctors
- Viewing patients assigned to a doctor

Doctor profiles are associated with registered users through the user ID.

## Patient Management

The Patient API supports:

- Creating patients
- Listing patients
- Getting patients by ID
- Updating patient information
- Deleting patients
- Assigning patients to doctors

## Appointment Management

The Appointment API supports:

- Creating appointments
- Listing appointments
- Updating appointments
- Deleting appointments

Appointments are associated with doctors and patients.

## Swagger Documentation

After starting the application, Swagger documentation is available at:

`http://127.0.0.1:8000/docs`

Alternative API documentation:

`http://127.0.0.1:8000/redoc`

## Running the Application

Create a virtual environment:

```bash
python -m venv venv

## Project Structure

Doctor_Patient_Backend-App/

├── auth/
│   ├── __init__.py
│   └── security.py
│
├── routers/
│   ├── __init__.py
│   ├── auth.py
│   ├── doctors.py
│   ├── patients.py
│   └── appointments.py
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py
│   ├── doctor_service.py
│   ├── patient_service.py
│   └── appointment_service.py
│
├── tests/
│   └── test_api.py
│
├── screenshots/
│   └── API and Swagger screenshots
│
├── config.py
├── database.py
├── models.py
├── schemas.py
├── main.py
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md
