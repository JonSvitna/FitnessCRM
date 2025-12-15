# API Documentation 📚

Complete API documentation for the Fitness CRM Backend API.

**Base URL**: `https://your-api.railway.app` or `http://localhost:5000` (development)

## Table of Contents
- [Overview](#overview)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Health Check](#health-check)
  - [Trainers](#trainers)
  - [Clients](#clients)
  - [CRM Management](#crm-management)

## Overview

The Fitness CRM API is a RESTful API built with Flask that provides CRUD operations for managing trainers, clients, and their assignments.

### Authentication

**Current Version**: No authentication required
**Future Versions**: Will implement JWT-based authentication

### Content Type

All requests and responses use `application/json` content type.

### CORS

CORS is enabled for all origins in development. Configure appropriately for production.

## Response Format

### Success Response

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}
```

### List Response

```json
[
  {
    "id": 1,
    "name": "John Doe"
  },
  {
    "id": 2,
    "name": "Jane Smith"
  }
]
```

## Error Handling

### Error Response Format

```json
{
  "error": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK` - Request succeeded
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists (e.g., duplicate email)
- `500 Internal Server Error` - Server error

## Endpoints

### Health Check

#### Get API Health Status

```
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

---

## Trainers

### Get All Trainers

```
GET /api/trainers
```

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1 (555) 123-4567",
    "specialization": "Strength Training",
    "certification": "NASM-CPT",
    "experience": 5,
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
]
```

---

### Get Single Trainer

```
GET /api/trainers/:id
```

**Parameters**:
- `id` (integer, required) - Trainer ID

**Response**: `200 OK`

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1 (555) 123-4567",
  "specialization": "Strength Training",
  "certification": "NASM-CPT",
  "experience": 5,
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

**Error**: `404 Not Found`

```json
{
  "error": "Resource not found"
}
```

---

### Create Trainer

```
POST /api/trainers
```

**Request Body**:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1 (555) 123-4567",
  "specialization": "Strength Training",
  "certification": "NASM-CPT",
  "experience": 5
}
```

**Required Fields**:
- `name` (string)
- `email` (string, must be unique)

**Optional Fields**:
- `phone` (string)
- `specialization` (string)
- `certification` (string)
- `experience` (integer)

**Response**: `201 Created`

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1 (555) 123-4567",
  "specialization": "Strength Training",
  "certification": "NASM-CPT",
  "experience": 5,
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

**Error**: `400 Bad Request`

```json
{
  "error": "Name and email are required"
}
```

**Error**: `409 Conflict`

```json
{
  "error": "Trainer with this email already exists"
}
```

---

### Update Trainer

```
PUT /api/trainers/:id
```

**Parameters**:
- `id` (integer, required) - Trainer ID

**Request Body** (all fields optional):

```json
{
  "name": "John Updated",
  "email": "john.updated@example.com",
  "phone": "+1 (555) 999-8888",
  "specialization": "Cardio Training",
  "certification": "ACE-CPT",
  "experience": 7
}
```

**Response**: `200 OK`

```json
{
  "id": 1,
  "name": "John Updated",
  "email": "john.updated@example.com",
  ...
}
```

**Error**: `404 Not Found`

**Error**: `409 Conflict` (if email already exists)

---

### Delete Trainer

```
DELETE /api/trainers/:id
```

**Parameters**:
- `id` (integer, required) - Trainer ID

**Response**: `200 OK`

```json
{
  "message": "Trainer deleted successfully"
}
```

**Error**: `404 Not Found`

**Note**: Deleting a trainer will also delete all associated assignments (cascade delete).

---

## Clients

### Get All Clients

```
GET /api/clients
```

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1 (555) 987-6543",
    "age": 30,
    "goals": "Weight loss, muscle toning",
    "medical_conditions": "None",
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
]
```

---

### Get Single Client

```
GET /api/clients/:id
```

**Parameters**:
- `id` (integer, required) - Client ID

**Response**: `200 OK`

```json
{
  "id": 1,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1 (555) 987-6543",
  "age": 30,
  "goals": "Weight loss, muscle toning",
  "medical_conditions": "None",
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

**Error**: `404 Not Found`

---

### Create Client

```
POST /api/clients
```

**Request Body**:

```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1 (555) 987-6543",
  "age": 30,
  "goals": "Weight loss, muscle toning",
  "medical_conditions": "None"
}
```

**Required Fields**:
- `name` (string)
- `email` (string, must be unique)

**Optional Fields**:
- `phone` (string)
- `age` (integer)
- `goals` (text)
- `medical_conditions` (text)

**Response**: `201 Created`

```json
{
  "id": 1,
  "name": "Jane Smith",
  "email": "jane@example.com",
  ...
}
```

**Error**: `400 Bad Request`

```json
{
  "error": "Name and email are required"
}
```

**Error**: `409 Conflict`

```json
{
  "error": "Client with this email already exists"
}
```

---

### Update Client

```
PUT /api/clients/:id
```

**Parameters**:
- `id` (integer, required) - Client ID

**Request Body** (all fields optional):

```json
{
  "name": "Jane Updated",
  "email": "jane.updated@example.com",
  "phone": "+1 (555) 111-2222",
  "age": 31,
  "goals": "Marathon training",
  "medical_conditions": "Knee injury (recovered)"
}
```

**Response**: `200 OK`

**Error**: `404 Not Found`

**Error**: `409 Conflict` (if email already exists)

---

### Delete Client

```
DELETE /api/clients/:id
```

**Parameters**:
- `id` (integer, required) - Client ID

**Response**: `200 OK`

```json
{
  "message": "Client deleted successfully"
}
```

**Error**: `404 Not Found`

**Note**: Deleting a client will also delete all associated assignments (cascade delete).

---

## CRM Management

### Get Dashboard Statistics

```
GET /api/crm/dashboard
```

**Response**: `200 OK`

```json
{
  "trainers_count": 10,
  "clients_count": 45,
  "assignments_count": 38
}
```

---

### Get Detailed Statistics

```
GET /api/crm/stats
```

**Response**: `200 OK`

```json
{
  "total_trainers": 10,
  "total_clients": 45,
  "trainers_with_clients": 8,
  "clients_assigned": 38
}
```

---

### Assign Client to Trainer

```
POST /api/crm/assign
```

**Request Body**:

```json
{
  "trainer_id": 1,
  "client_id": 5,
  "notes": "Initial consultation completed. Focus on cardio."
}
```

**Required Fields**:
- `trainer_id` (integer)
- `client_id` (integer)

**Optional Fields**:
- `notes` (text)

**Response**: `201 Created`

```json
{
  "id": 1,
  "trainer_id": 1,
  "client_id": 5,
  "notes": "Initial consultation completed. Focus on cardio.",
  "created_at": "2024-01-15T10:30:00.000Z",
  "updated_at": "2024-01-15T10:30:00.000Z"
}
```

**Error**: `400 Bad Request`

```json
{
  "error": "trainer_id and client_id are required"
}
```

**Error**: `404 Not Found`

```json
{
  "error": "Trainer not found"
}
```

```json
{
  "error": "Client not found"
}
```

---

### Get All Assignments

```
GET /api/crm/assignments
```

**Response**: `200 OK`

```json
[
  {
    "id": 1,
    "trainer_id": 1,
    "client_id": 5,
    "notes": "Initial consultation completed. Focus on cardio.",
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-15T10:30:00.000Z"
  }
]
```

---

### Delete Assignment

```
DELETE /api/crm/assignments/:id
```

**Parameters**:
- `id` (integer, required) - Assignment ID

**Response**: `200 OK`

```json
{
  "message": "Assignment deleted successfully"
}
```

**Error**: `404 Not Found`

---

## Example Usage

### Using cURL

**Create a Trainer**:

```bash
curl -X POST https://your-api.railway.app/api/trainers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "specialization": "Strength Training",
    "experience": 5
  }'
```

**Get All Trainers**:

```bash
curl https://your-api.railway.app/api/trainers
```

### Using JavaScript (Axios)

```javascript
import axios from 'axios';

const API_URL = 'https://your-api.railway.app';

// Create a trainer
const createTrainer = async () => {
  try {
    const response = await axios.post(`${API_URL}/api/trainers`, {
      name: 'John Doe',
      email: 'john@example.com',
      specialization: 'Strength Training',
      experience: 5
    });
    console.log(response.data);
  } catch (error) {
    console.error(error.response.data);
  }
};

// Get all trainers
const getTrainers = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/trainers`);
    console.log(response.data);
  } catch (error) {
    console.error(error);
  }
};
```

### Using Python (Requests)

```python
import requests

API_URL = 'https://your-api.railway.app'

# Create a trainer
response = requests.post(
    f'{API_URL}/api/trainers',
    json={
        'name': 'John Doe',
        'email': 'john@example.com',
        'specialization': 'Strength Training',
        'experience': 5
    }
)
print(response.json())

# Get all trainers
response = requests.get(f'{API_URL}/api/trainers')
print(response.json())
```

## Rate Limiting

**Current**: No rate limiting implemented

**Future**: Will implement rate limiting to prevent abuse:
- 100 requests per minute per IP
- 1000 requests per hour per IP

## Pagination

**Current**: Not implemented - all results returned

**Future**: Will implement pagination for list endpoints:
- `?page=1&per_page=20`
- Response will include pagination metadata

## Filtering and Sorting

**Future Enhancements**:

- Filter trainers by specialization: `GET /api/trainers?specialization=Strength`
- Sort by date: `GET /api/clients?sort=created_at&order=desc`
- Search: `GET /api/trainers?search=john`

## Webhooks

**Future**: Will support webhooks for events:
- Trainer created
- Client created
- Assignment created
- Assignment updated

## API Versioning

**Current**: Version 1.0

**Future**: Will use URL versioning:
- `/api/v1/trainers`
- `/api/v2/trainers`

---

**Last Updated**: December 2024
**API Version**: 1.0.0
