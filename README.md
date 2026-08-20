# Library Service API

A Django REST Framework API for managing books, users, and book borrowings.

## 1. Features

* User registration and authentication
* JWT authentication
* User profile management
* Book management
* Book inventory tracking
* Borrowing creation
* Borrowing list and detail views
* Borrowing filtering
* PostgreSQL database support
* Swagger API documentation
* Docker and Docker Compose support
* Automated tests

## 2. Technologies

* Python 3.11
* Django 5.2.17
* Django REST Framework
* Simple JWT
* PostgreSQL 16
* drf-spectacular
* Docker
* Docker Compose

## 3. Project Structure

```text
py-library/
├── books/
├── borrowings/
├── users/
├── config/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── README.md
```

## 4. Installation

### 4.1 Clone the repository

```bash
git clone https://github.com/danyatatarchuk/py-library.git
cd py-library
```

### 4.2 Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4.3 Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Environment Variables

For Docker Compose, create a `.env` file in the project root:

```env
SECRET_KEY=django-insecure-local-docker-key
DEBUG=True

POSTGRES_DB=library
POSTGRES_USER=library
POSTGRES_PASSWORD=library
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Do not commit the `.env` file to the repository.

## 6. Run Locally

For local development, the project can be run with Django's development server.

Apply migrations:

```bash
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## 7. Run with Docker

Build the Docker images:

```bash
docker compose build
```

Start the application:

```bash
docker compose up
```

Docker Compose starts:

1. Django application
2. PostgreSQL database
3. PostgreSQL health check
4. Automatic Django migrations

The API will be available at:

```text
http://127.0.0.1:8000/
```

To run the application in the background:

```bash
docker compose up -d
```

To stop the containers:

```bash
docker compose down
```

## 8. API Documentation

Swagger UI is available at:

```text
http://127.0.0.1:8000/api/docs/
```

OpenAPI schema is available at:

```text
http://127.0.0.1:8000/api/schema/
```

## 9. API Endpoints

### 9.1 Books

Get all books:

```http
GET /api/books/books/
```

Create a book:

```http
POST /api/books/books/
```

Get a specific book:

```http
GET /api/books/books/{id}/
```

Update a book:

```http
PUT /api/books/books/{id}/
```

Partially update a book:

```http
PATCH /api/books/books/{id}/
```

Delete a book:

```http
DELETE /api/books/books/{id}/
```

### 9.2 Users

Register a user:

```http
POST /api/users/
```

Get the current user's profile:

```http
GET /api/users/me/
```

Update the current user's profile:

```http
PUT /api/users/me/
```

Partially update the current user's profile:

```http
PATCH /api/users/me/
```

Obtain JWT tokens:

```http
POST /api/users/token/
```

Refresh the access token:

```http
POST /api/users/token/refresh/
```

### 9.3 Borrowings

Get borrowings:

```http
GET /api/borrowings/
```

Create a borrowing:

```http
POST /api/borrowings/
```

Get a specific borrowing:

```http
GET /api/borrowings/{id}/
```

## 10. Authentication

The API uses JWT authentication.

Obtain an access token using:

```http
POST /api/users/token/
```

Use the access token for authenticated requests:

```text
Authorization: Bearer <access_token>
```

Protected endpoints require authentication.

## 11. Testing

Run all tests:

```bash
python manage.py test
```

Run only borrowing tests:

```bash
python manage.py test borrowings
```

Run tests inside Docker:

```bash
docker compose exec app python manage.py test
```

## 12. Database

The project uses SQLite for local development and PostgreSQL when running with Docker Compose.

The PostgreSQL configuration is provided through environment variables:

```env
POSTGRES_DB=library
POSTGRES_USER=library
POSTGRES_PASSWORD=library
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

When the Docker application starts, Django automatically applies database migrations.

## 13. Development Workflow

The project uses feature branches for development.

Create a new feature branch:

```bash
git checkout develop
git pull origin develop
git checkout -b feature/new-feature
```

Add and commit changes:

```bash
git add .
git commit -m "Implement new feature"
```

Push the feature branch:

```bash
git push --set-upstream origin feature/new-feature
```

After the feature is completed, merge it into the `develop` branch.
