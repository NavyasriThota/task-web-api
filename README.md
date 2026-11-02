# Student Management System

This project builds a professional student management application with a FastAPI backend, PostgreSQL database, and a responsive HTML/JavaScript frontend.

## Project purpose

The system stores student records in a real database and exposes REST APIs that support creating, reading, updating, and deleting student data. The frontend lets users enter detail, browse records, search by name, and manage student information without using local browser storage.

## Important files and their purpose

- `app/main.py`: Starts the FastAPI app, configures CORS, serves the frontend, and includes the student routes.
- `app/database.py`: Connects the application to PostgreSQL using environment variables and creates the database session factory.
- `app/models.py`: Defines the `Student` table and columns used in PostgreSQL.
- `app/schemas.py`: Uses Pydantic models to validate API request and response data.
- `app/crud.py`: Contains database logic and business rules, such as duplicate-email checks and name searches.
- `app/routers/students.py`: Exposes all student CRUD endpoints used by the frontend and API consumers.
- `frontend/index.html`: The single-page dashboard for adding, searching, updating, and deleting student records.
- `frontend/style.css`: Styles the dashboard so it looks professional and responsive.
- `frontend/script.js`: Calls the backend REST API from the browser using JavaScript `fetch`.
- `tests/test_students.py`: Contains pytest tests that validate the CRUD logic and validation rules.
- `alembic`: Stores database migration configuration for PostgreSQL schema changes.

## Database design

The project uses a `students` table with the following structure:

- `student_id`: Auto-increment integer primary key
- `first_name`: Required text
- `last_name`: Required text
- `email`: Required and unique
- `phone_number`: Required text
- `gender`: Optional text
- `date_of_birth`: Optional date
- `course`: Required text
- `batch`: Required text
- `address`: Optional long text
- `created_at`: Automatic time when row is inserted
- `updated_at`: Automatic time when row is modified

## Required environment variables

Create a local `.env` file using the sample values below:

```env
DATABASE_URL=postgresql+psycopg://username:password@host:5432/database_name?sslmode=require
```

For Neon, copy the connection string from your Neon dashboard and add it to `.env`.

## Local setup

1. Open a terminal in the project folder.
2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the environment:

On Windows:

```bash
.venv\Scripts\activate
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Add your Neon PostgreSQL connection string to `.env`.
6. Create the database tables:

```bash
python -c "from app.database import Base, engine; from app.models import Student; Base.metadata.create_all(bind=engine)"
```

7. Start the API:

```bash
uvicorn app.main:app --reload
```

8. Open the browser at:

```text
http://127.0.0.1:8000/
```

9. API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API endpoints

### POST /api/students
Creates a new student record if the email does not already exist.

### GET /api/students
Returns all students with pagination support.

### GET /api/students/search?name=nav
Searches by first name, last name, full name, or email. The search is case-insensitive and requires at least three characters.

### GET /api/students/{student_id}
Returns one student by ID.

### PUT /api/students/{student_id}
Updates an existing student and refreshes `updated_at`.

### DELETE /api/students/{student_id}
Deletes a student and returns a success message.

## Example database operations

- `get_student_by_email`: checks whether an email already exists.
- `create_student`: inserts a new student record into the database.
- `get_students`: fetches records in a paginated format.
- `search_students`: uses `ILIKE`-style filtering for partial searches.
- `update_student`: modifies an existing student and updates the timestamp.
- `delete_student`: removes a row from the table.

## Testing

To run the automated tests:

```bash
pytest
```

The tests cover create, duplicate-email, list, search, read-by-id, update, and delete operations, as well as invalid input validation.

## Security notes

- Database credentials are stored in `.env` and never hardcoded in source files.
- SQLAlchemy uses parameterized queries.
- The app validates user input with Pydantic.
- CORS is limited to trusted local origins.

## Beginner-friendly interpretation

- FastAPI handles HTTP requests.
- SQLAlchemy maps Python classes to database tables.
- Pydantic validates incoming data before it reaches the database.
- CRUD functions share the database session and protect the application from invalid or duplicate records.
- The HTML frontend sends requests to the backend instead of storing data in browser storage.

This project is designed to teach the flow of a real web application: frontend request -> API validation -> database operation -> structured response.
