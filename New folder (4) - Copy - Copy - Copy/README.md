# Mini Employee Management API

A Flask-based REST API for managing employee records with PostgreSQL database integration.

## Features

- **CRUD Operations**: Create, Read, Update, Delete employees
- **Input Validation**: Comprehensive validation for all fields
- **Environment Configuration**: Secure database connection using environment variables
- **Error Handling**: Proper HTTP status codes and error messages
- **Database Integration**: PostgreSQL with psycopg2
- **CORS Support**: Cross-origin resource sharing enabled

## API Endpoints

### 1. List All Employees
```
GET /employees
```
**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john.doe@company.com",
      "department": "Engineering",
      "salary": 75000.00,
      "hire_date": "2023-01-15",
      "created_at": "2023-01-15T10:30:00",
      "updated_at": "2023-01-15T10:30:00"
    }
  ],
  "count": 1
}
```

### 2. Create New Employee
```
POST /employees
```
**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane.smith@company.com",
  "department": "Marketing",
  "salary": 65000.00
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane.smith@company.com",
    "department": "Marketing",
    "salary": 65000.00,
    "hire_date": "2023-01-15",
    "created_at": "2023-01-15T10:35:00",
    "updated_at": "2023-01-15T10:35:00"
  },
  "message": "Employee created successfully"
}
```

### 3. Update Employee
```
PUT /employees/<id>
```
**Request Body (partial update allowed):**
```json
{
  "salary": 80000.00,
  "department": "Senior Engineering"
}
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Senior Engineering",
    "salary": 80000.00,
    "hire_date": "2023-01-15",
    "created_at": "2023-01-15T10:30:00",
    "updated_at": "2023-01-15T11:00:00"
  },
  "message": "Employee updated successfully"
}
```

### 4. Delete Employee
```
DELETE /employees/<id>
```
**Response:**
```json
{
  "success": true,
  "message": "Employee deleted successfully"
}
```

### 5. Get Single Employee
```
GET /employees/<id>
```
**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "salary": 75000.00,
    "hire_date": "2023-01-15",
    "created_at": "2023-01-15T10:30:00",
    "updated_at": "2023-01-15T10:30:00"
  }
}
```

### 6. Health Check
```
GET /health
```
**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "database": "connected",
  "timestamp": "2023-01-15T10:30:00"
}
```

## Setup Instructions

### Prerequisites
- Python 3.7+
- PostgreSQL 12+
- pip (Python package installer)

### 1. Clone and Setup Environment
```bash
# Navigate to project directory
cd employee-management-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Create PostgreSQL database
createdb employee_db

# Or using psql:
psql -U postgres
CREATE DATABASE employee_db;
\q
```

### 3. Environment Configuration
Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=employee_db
DB_USER=postgres
DB_PASSWORD=your_password
FLASK_ENV=development
FLASK_DEBUG=True
```

### 4. Run the Application
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Input Validation

### Employee Creation (POST /employees)
- **name**: Required, minimum 2 characters
- **email**: Required, must be valid email format, unique
- **department**: Required, minimum 2 characters
- **salary**: Required, must be greater than 0

### Employee Update (PUT /employees/<id>)
- All fields are optional for updates
- Same validation rules apply for provided fields
- At least one field must be provided

## Error Handling

The API returns consistent JSON error responses:

```json
{
  "success": false,
  "error": "Error message",
  "details": ["Additional validation errors"]
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `404` - Not Found
- `405` - Method Not Allowed
- `409` - Conflict (duplicate email)
- `500` - Internal Server Error
- `503` - Service Unavailable (database issues)

## Testing the API

### Using curl

1. **Create an employee:**
```bash
curl -X POST http://localhost:5000/employees \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@company.com",
    "department": "Engineering",
    "salary": 75000
  }'
```

2. **Get all employees:**
```bash
curl http://localhost:5000/employees
```

3. **Update an employee:**
```bash
curl -X PUT http://localhost:5000/employees/1 \
  -H "Content-Type: application/json" \
  -d '{"salary": 80000}'
```

4. **Delete an employee:**
```bash
curl -X DELETE http://localhost:5000/employees/1
```

### Using Python requests
```python
import requests

# Create employee
response = requests.post('http://localhost:5000/employees', json={
    'name': 'Jane Smith',
    'email': 'jane.smith@company.com',
    'department': 'Marketing',
    'salary': 65000
})
print(response.json())

# Get all employees
response = requests.get('http://localhost:5000/employees')
print(response.json())
```

## Database Schema

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary DECIMAL(10,2) NOT NULL CHECK (salary > 0),
    hire_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security Features

- Environment variable configuration for database credentials
- Input validation and sanitization
- SQL injection prevention through parameterized queries
- Proper error handling without exposing sensitive information

## Project Structure

```
employee-management-api/
├── app.py              # Main Flask application
├── config.py           # Configuration management
├── database.py         # Database connection and operations
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env               # Environment variables (create this)
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check database credentials in `.env` file
   - Ensure database exists

2. **Import Errors**
   - Activate virtual environment
   - Install dependencies: `pip install -r requirements.txt`

3. **Port Already in Use**
   - Change port in `app.py` or stop other services using port 5000

### Logs
The application logs important events to the console. Check logs for debugging information.
