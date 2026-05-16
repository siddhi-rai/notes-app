# Notes App - Backend API

A multi-user notes service REST API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

## Features

### Core Features
- **User Registration** (`POST /register`)
- **User Login with JWT** (`POST /login`)
- **CRUD Operations on Notes** (`GET/POST/PUT/DELETE /notes`)
- **Note Sharing** (`POST /notes/{id}/share`)
- **OpenAPI Documentation** (`GET /openapi.json`)
- **About Endpoint** (`GET /about`)

### Custom Feature: Note Tagging 🏷️
Notes can be tagged with custom labels for better organization. Users can:
- Add tags when creating or updating notes
- Filter notes by tags using `GET /notes?tags=tag1,tag2`

### Stretch Goals Implemented
- **Pagination**: `GET /notes?page=1&per_page=10`
- **Full-text Search**: `GET /search?q=keyword`
- **Dockerized** application

## Tech Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic v2

## Local Setup

### 1. Clone and install dependencies
```bash
cd Assignment-intern
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create a PostgreSQL database
Open pgAdmin and create a database called `notes_db`.

### 3. Set environment variables
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and a secure SECRET_KEY
# DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/notes_db
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

### 5. Interactive API Docs
Visit `http://localhost:8000/docs` for Swagger UI.

## Docker

```bash
docker build -t notes-app .
docker run -p 8000:8000 -e SECRET_KEY=your-secret-key -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/notes_db notes-app
```

## Deployment (Render.com)

1. Push code to GitHub
2. Create a new **Web Service** on Render
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `SECRET_KEY=<your-secure-key>` and `DATABASE_URL=<your-postgresql-url>`

## API Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /register | Register a new user | No |
| POST | /login | Login & get JWT token | No |
| GET | /notes | Get all notes (with pagination/tag filter) | Yes |
| GET | /notes/{id} | Get a specific note | Yes |
| POST | /notes | Create a new note | Yes |
| PUT | /notes/{id} | Update a note | Yes |
| DELETE | /notes/{id} | Delete a note | Yes |
| POST | /notes/{id}/share | Share note with another user | Yes |
| GET | /search?q=keyword | Search notes | Yes |
| GET | /openapi.json | OpenAPI specification | No |
| GET | /about | About the developer | No |
