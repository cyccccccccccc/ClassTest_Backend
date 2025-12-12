# Contact Book Backend

A Flask-based backend service for managing contacts, supporting full CRUD operations, bookmarking, and import/export functionality via Excel files. The implementation follows a modular development approach with clear separation of concerns.

## Features

- Create, read, update, and delete contacts
- Toggle bookmark status for any contact
- Export all contacts to an Excel (.xlsx) file
- Import contacts from an Excel (.xlsx) file
- Enforced data integrity with cascade deletion of associated contact methods
- RESTful API design

## Technology Stack

- Python 3.8+
- Flask 3.0.3
- Flask-SQLAlchemy 3.1.1
- MySQL (via mysql-connector-python 9.1.0)
- pandas 2.2.2 and openpyxl 3.1.5 for Excel handling

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ClassTest_Backend.git
   cd ClassTest_Backend
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database:
   Ensure MySQL is installed and running. Create the database:
   ```sql
   CREATE DATABASE contact_book CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
   The default connection string assumes:
   - Host: localhost
   - Username: root
   - Password: root
   - Database: contact_book
   This can be modified in `app.py`.

5. Run the application:
   ```bash
   python app.py
   ```
   The server will start on http://0.0.0.0:5000.

## API Endpoints

| Method | Endpoint                        | Description                              |
|--------|----------------------------------|------------------------------------------|
| GET    | /api/contacts                   | Retrieve all contacts                    |
| POST   | /api/contacts                   | Create a new contact                     |
| PUT    | /api/contacts/<id>              | Update an existing contact               |
| DELETE | /api/contacts/<id>              | Delete a contact                         |
| PUT    | /api/contacts/<id>/bookmark     | Toggle bookmark status                   |
| GET    | /api/export                     | Download contacts as Excel file          |
| POST   | /api/import                     | Upload Excel file to import contacts     |

### Request/Response Examples

**Create a contact (POST /api/contacts):**
```json
{
  "name": "John Doe",
  "is_bookmarked": false,
  "methods": [
    {"type": "phone", "value": "1234567890"},
    {"type": "email", "value": "john@example.com"}
  ]
}
```

**Excel Import Format:**
The Excel file must contain columns `name` and `is_bookmarked`. Contact methods are represented as columns named `<type>_<index>`, e.g., `phone_1`, `email_1`, `address_1`, etc. Empty cells are ignored.

Example:
```
name        is_bookmarked   phone_1       email_1
Alice Smith 1               5551234567    alice@example.com
```

## Project Structure

```
.
├── app.py                # Application entry point
├── requirements.txt      # Python dependencies
└── backend/
    ├── models.py         # SQLAlchemy models
    ├── routes.py         # API route definitions
    └── utils.py          # Excel import/export utilities
```

## Development Process

The Git history is structured to reflect incremental feature development:

1. Project initialization and dependency setup
2. Definition of database models with cascade delete behavior
3. Implementation of core CRUD and bookmark APIs
4. Addition of Excel export functionality
5. Implementation of Excel import with secure temporary file handling
6. Final refinements for data integrity and error handling

This approach ensures each commit represents a coherent, testable unit of work.

## Notes

- The application uses `tempfile.NamedTemporaryFile` for secure handling of uploaded/downloaded Excel files.
- All database operations include error handling and transaction rollback on failure.
- Debug mode is enabled by default; disable it in production environments.
- The MySQL connection uses `pymysql` dialect; ensure compatibility with your database version.
