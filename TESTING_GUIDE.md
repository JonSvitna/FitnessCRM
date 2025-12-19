# FitnessCRM Testing Guide 🧪

Comprehensive guide for testing the FitnessCRM application, covering unit tests, integration tests, and end-to-end tests.

## Table of Contents

1. [Overview](#overview)
2. [Backend Testing](#backend-testing)
3. [Frontend Testing](#frontend-testing)
4. [Integration Testing](#integration-testing)
5. [Performance Testing](#performance-testing)
6. [Security Testing](#security-testing)
7. [Continuous Integration](#continuous-integration)

---

## Overview

### Testing Philosophy

- **Test Coverage**: Aim for 80%+ backend coverage, 70%+ frontend coverage
- **Test Types**: Unit, integration, and E2E tests
- **Test Automation**: All tests should run in CI/CD
- **Test Speed**: Tests should complete in < 5 minutes

### Testing Stack

**Backend**:
- pytest - Testing framework
- pytest-cov - Coverage reporting
- pytest-flask - Flask testing utilities

**Frontend**:
- Vitest (recommended) or Jest - Testing framework
- Testing Library - Component testing
- Playwright or Cypress - E2E testing

---

## Backend Testing

### Setup

1. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure test database**:
   ```bash
   export TEST_DATABASE_URL=postgresql://localhost/fitnesscrm_test
   createdb fitnesscrm_test
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

### Test Structure

```
backend/
├── conftest.py           # Shared fixtures
├── pytest.ini           # Pytest configuration
├── test_api.py          # API endpoint tests
├── test_models.py       # Database model tests
├── test_utils.py        # Utility function tests
└── test_integration.py  # Integration tests
```

### Writing Unit Tests

**Example: Testing API Endpoints**

```python
# test_api.py
import pytest
from models.database import Trainer

def test_get_trainers(client):
    """Test GET /api/trainers endpoint."""
    response = client.get('/api/trainers')
    assert response.status_code == 200
    data = response.get_json()
    assert 'trainers' in data or isinstance(data, list)

def test_create_trainer(client, sample_trainer):
    """Test POST /api/trainers endpoint."""
    response = client.post(
        '/api/trainers',
        json=sample_trainer
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == sample_trainer['name']
    assert data['email'] == sample_trainer['email']

def test_get_trainer_by_id(client, db_session, sample_trainer):
    """Test GET /api/trainers/<id> endpoint."""
    # Create trainer
    trainer = Trainer(**sample_trainer)
    db_session.add(trainer)
    db_session.commit()
    
    # Get trainer
    response = client.get(f'/api/trainers/{trainer.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == trainer.id
    assert data['name'] == trainer.name

def test_update_trainer(client, db_session, sample_trainer):
    """Test PUT /api/trainers/<id> endpoint."""
    # Create trainer
    trainer = Trainer(**sample_trainer)
    db_session.add(trainer)
    db_session.commit()
    
    # Update trainer
    updated_data = {'name': 'Updated Name'}
    response = client.put(
        f'/api/trainers/{trainer.id}',
        json=updated_data
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Updated Name'

def test_delete_trainer(client, db_session, sample_trainer):
    """Test DELETE /api/trainers/<id> endpoint."""
    # Create trainer
    trainer = Trainer(**sample_trainer)
    db_session.add(trainer)
    db_session.commit()
    trainer_id = trainer.id
    
    # Delete trainer
    response = client.delete(f'/api/trainers/{trainer_id}')
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f'/api/trainers/{trainer_id}')
    assert response.status_code == 404
```

**Example: Testing Database Models**

```python
# test_models.py
import pytest
from models.database import Trainer, Client, Assignment

def test_create_trainer(db_session, sample_trainer):
    """Test creating a trainer model."""
    trainer = Trainer(**sample_trainer)
    db_session.add(trainer)
    db_session.commit()
    
    assert trainer.id is not None
    assert trainer.name == sample_trainer['name']
    assert trainer.email == sample_trainer['email']
    assert trainer.created_at is not None

def test_trainer_relationships(db_session, sample_trainer, sample_client):
    """Test trainer-client relationships."""
    # Create trainer and client
    trainer = Trainer(**sample_trainer)
    client = Client(**sample_client)
    db_session.add_all([trainer, client])
    db_session.commit()
    
    # Create assignment
    assignment = Assignment(
        trainer_id=trainer.id,
        client_id=client.id,
        notes='Test assignment'
    )
    db_session.add(assignment)
    db_session.commit()
    
    # Verify relationships
    assert len(trainer.assignments) == 1
    assert len(client.assignments) == 1
    assert assignment.trainer == trainer
    assert assignment.client == client
```

### Running Tests

**Run all tests**:
```bash
pytest
```

**Run with coverage**:
```bash
pytest --cov=. --cov-report=html
```

**Run specific test file**:
```bash
pytest test_api.py
```

**Run specific test**:
```bash
pytest test_api.py::test_get_trainers
```

**Run tests by marker**:
```bash
pytest -m unit       # Run unit tests
pytest -m integration # Run integration tests
pytest -m api        # Run API tests
```

**Verbose output**:
```bash
pytest -v
```

**Stop on first failure**:
```bash
pytest -x
```

### Test Markers

Mark your tests for better organization:

```python
@pytest.mark.unit
def test_function():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.api
def test_api_endpoint():
    pass
```

### Coverage Reports

After running tests with coverage:

1. **View HTML report**:
   ```bash
   open htmlcov/index.html  # macOS
   xdg-open htmlcov/index.html  # Linux
   ```

2. **View terminal report**:
   ```bash
   pytest --cov=. --cov-report=term-missing
   ```

### Mocking External Services

**Example: Mocking Email Service**

```python
from unittest.mock import patch

@patch('flask_mail.Mail.send')
def test_send_email(mock_send, client):
    """Test email sending without actually sending."""
    response = client.post('/api/send-email', json={
        'to': 'test@example.com',
        'subject': 'Test',
        'body': 'Test message'
    })
    
    assert response.status_code == 200
    assert mock_send.called
```

---

## Frontend Testing

### Setup (Vitest)

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install -D vitest @testing-library/react @testing-library/jest-dom
   ```

2. **Configure Vitest** (`vite.config.js`):
   ```javascript
   import { defineConfig } from 'vite'
   
   export default defineConfig({
     test: {
       globals: true,
       environment: 'jsdom',
       setupFiles: './tests/setup.js'
     }
   })
   ```

3. **Add test scripts** to `package.json`:
   ```json
   {
     "scripts": {
       "test": "vitest",
       "test:ui": "vitest --ui",
       "test:coverage": "vitest --coverage"
     }
   }
   ```

### Writing Component Tests

**Example: Testing a Button Component**

```javascript
// Button.test.js
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import Button from './Button'

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText('Click me'))
    expect(handleClick).toHaveBeenCalledOnce()
  })
  
  it('applies correct CSS classes', () => {
    render(<Button variant="primary">Click me</Button>)
    const button = screen.getByText('Click me')
    expect(button).toHaveClass('btn-primary')
  })
})
```

**Example: Testing API Integration**

```javascript
// api.test.js
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { getTrainers, createTrainer } from './api'

describe('API', () => {
  beforeEach(() => {
    global.fetch = vi.fn()
  })
  
  afterEach(() => {
    vi.restoreAllMocks()
  })
  
  it('fetches trainers', async () => {
    const mockTrainers = [
      { id: 1, name: 'John Trainer' }
    ]
    
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockTrainers
    })
    
    const trainers = await getTrainers()
    expect(trainers).toEqual(mockTrainers)
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/trainers')
    )
  })
  
  it('creates trainer', async () => {
    const newTrainer = { name: 'John', email: 'john@example.com' }
    const createdTrainer = { id: 1, ...newTrainer }
    
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => createdTrainer
    })
    
    const result = await createTrainer(newTrainer)
    expect(result).toEqual(createdTrainer)
  })
})
```

### End-to-End Testing (Playwright)

1. **Install Playwright**:
   ```bash
   npm install -D @playwright/test
   npx playwright install
   ```

2. **Create E2E test**:
   ```javascript
   // e2e/trainers.spec.js
   import { test, expect } from '@playwright/test'
   
   test.describe('Trainer Management', () => {
     test('should display trainers list', async ({ page }) => {
       await page.goto('http://localhost:3000')
       await page.click('text=Trainers')
       
       await expect(page.locator('h1')).toContainText('Trainers')
       await expect(page.locator('.trainer-card')).toHaveCount(3)
     })
     
     test('should create new trainer', async ({ page }) => {
       await page.goto('http://localhost:3000')
       await page.click('text=Trainers')
       await page.click('text=Add Trainer')
       
       await page.fill('input[name="name"]', 'John Trainer')
       await page.fill('input[name="email"]', 'john@example.com')
       await page.fill('input[name="phone"]', '555-0100')
       
       await page.click('button[type="submit"]')
       
       await expect(page.locator('text=John Trainer')).toBeVisible()
     })
   })
   ```

3. **Run E2E tests**:
   ```bash
   npx playwright test
   npx playwright test --ui  # Run with UI
   ```

---

## Integration Testing

### Testing Full User Workflows

**Example: Complete Assignment Workflow**

```python
# test_workflows.py
import pytest

@pytest.mark.integration
def test_complete_assignment_workflow(client, db_session):
    """Test creating trainer, client, and assignment."""
    
    # 1. Create trainer
    trainer_data = {
        'name': 'John Trainer',
        'email': 'john@example.com',
        'specialization': 'Strength'
    }
    response = client.post('/api/trainers', json=trainer_data)
    assert response.status_code == 201
    trainer = response.get_json()
    
    # 2. Create client
    client_data = {
        'name': 'Jane Client',
        'email': 'jane@example.com',
        'goals': 'Weight loss'
    }
    response = client.post('/api/clients', json=client_data)
    assert response.status_code == 201
    client_obj = response.get_json()
    
    # 3. Create assignment
    assignment_data = {
        'trainer_id': trainer['id'],
        'client_id': client_obj['id'],
        'notes': 'Initial consultation'
    }
    response = client.post('/api/crm/assign', json=assignment_data)
    assert response.status_code == 201
    assignment = response.get_json()
    
    # 4. Verify assignment
    response = client.get('/api/crm/assignments')
    assert response.status_code == 200
    assignments = response.get_json()
    assert len(assignments) >= 1
    assert any(a['id'] == assignment['id'] for a in assignments)
```

---

## Performance Testing

### Load Testing with Locust

1. **Install Locust**:
   ```bash
   pip install locust
   ```

2. **Create load test** (`locustfile.py`):
   ```python
   from locust import HttpUser, task, between
   
   class FitnessCRMUser(HttpUser):
       wait_time = between(1, 3)
       
       @task(3)
       def get_trainers(self):
           self.client.get("/api/trainers")
       
       @task(2)
       def get_clients(self):
           self.client.get("/api/clients")
       
       @task(1)
       def get_dashboard(self):
           self.client.get("/api/crm/dashboard")
   ```

3. **Run load test**:
   ```bash
   locust -f locustfile.py --host=http://localhost:5000
   ```

4. **Open UI**: Visit `http://localhost:8089`

### Performance Benchmarks

Target performance metrics:

- API response time: < 200ms (average)
- Database queries: < 100ms
- Page load time: < 2 seconds
- Time to interactive: < 3 seconds
- Concurrent users: 100+

---

## Security Testing

### SQL Injection Testing

```python
def test_sql_injection_protection(client):
    """Test that SQL injection is prevented."""
    malicious_input = "'; DROP TABLE trainers; --"
    
    response = client.get(f'/api/trainers?search={malicious_input}')
    
    # Should not cause error or data loss
    assert response.status_code in [200, 400]
    
    # Verify tables still exist
    response = client.get('/api/trainers')
    assert response.status_code == 200
```

### XSS Testing

```python
def test_xss_protection(client):
    """Test that XSS is prevented."""
    xss_input = "<script>alert('XSS')</script>"
    
    response = client.post('/api/trainers', json={
        'name': xss_input,
        'email': 'test@example.com'
    })
    
    assert response.status_code in [201, 400]
    
    # If created, verify output is escaped
    if response.status_code == 201:
        data = response.get_json()
        assert '<script>' not in str(data)
```

### Authentication Testing

```python
def test_unauthorized_access(client):
    """Test that protected endpoints require auth."""
    response = client.get('/api/admin/users')
    assert response.status_code in [401, 403]

def test_invalid_token(client):
    """Test that invalid tokens are rejected."""
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.get('/api/protected', headers=headers)
    assert response.status_code in [401, 403]
```

---

## Continuous Integration

### GitHub Actions Workflow

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: fitnesscrm_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/fitnesscrm_test
        SECRET_KEY: test_secret_key
      run: |
        cd backend
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm test -- --coverage
```

---

## Best Practices

### Test Organization

1. **Follow AAA pattern**: Arrange, Act, Assert
2. **One assertion per test**: Keep tests focused
3. **Descriptive test names**: `test_should_return_404_when_trainer_not_found`
4. **Use fixtures**: Share setup code
5. **Clean up**: Reset state after each test

### Test Data

1. **Use factories**: Generate test data programmatically
2. **Avoid hardcoded values**: Use variables
3. **Test edge cases**: Empty strings, null values, large numbers
4. **Test boundaries**: Min/max values

### Test Maintenance

1. **Keep tests fast**: Mock external services
2. **Avoid test interdependence**: Each test should be independent
3. **Update tests with code**: Tests are documentation
4. **Delete obsolete tests**: Don't keep broken tests

---

## Quick Reference

### Common Commands

```bash
# Backend
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest -k "test_trainer"        # Run matching tests
pytest --cov                    # With coverage
pytest -x                       # Stop on first failure
pytest --pdb                    # Debug on failure

# Frontend
npm test                        # Run all tests
npm test -- --watch            # Watch mode
npm test -- --coverage         # With coverage
npm run test:e2e               # E2E tests

# System
python scripts/health_check.py  # Health check
```

---

**Last Updated**: December 2024
