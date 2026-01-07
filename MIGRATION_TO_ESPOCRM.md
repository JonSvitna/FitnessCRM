# Migration Guide: EspoCRM-Inspired Architecture

## Overview

This guide explains how to migrate from the old FitnessCRM architecture to the new EspoCRM-inspired structure. The new architecture provides better organization, clearer relationships, and more maintainable code.

## What Changed

### Architecture Improvements

1. **Entity System**
   - All models now inherit from `BaseEntity`
   - Common fields added: `deleted_at` for soft deletes
   - Lifecycle hooks: `before_save()`, `after_save()`, `before_delete()`, `after_delete()`
   - Metadata-driven configuration

2. **EntityManager**
   - Centralized CRUD operations
   - Consistent API for all entities
   - Relationship management built-in

3. **Module System**
   - Features organized into modules
   - Dependency management
   - Clear separation of concerns

4. **Relationship System**
   - Declarative relationship definitions
   - Relationship types: ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY, ONE_TO_ONE
   - Automatic relationship resolution

### Backward Compatibility

**Important**: The new architecture is **fully backward compatible**. All existing API endpoints continue to work as before.

## Database Changes

### New Columns

The following columns were added to support the new architecture:

- `deleted_at` (DATETIME) - For soft delete functionality

### Migration SQL

```sql
-- Add deleted_at column to trainers
ALTER TABLE trainers ADD COLUMN deleted_at TIMESTAMP;

-- Add deleted_at column to clients
ALTER TABLE clients ADD COLUMN deleted_at TIMESTAMP;

-- Add deleted_at column to assignments
ALTER TABLE assignments ADD COLUMN deleted_at TIMESTAMP;

-- Add deleted_at column to sessions
ALTER TABLE sessions ADD COLUMN deleted_at TIMESTAMP;
```

You can run this migration with:

```bash
cd backend
python -c "
from app_factory import create_app
from models.database import db
app = create_app()
with app.app_context():
    db.engine.execute('ALTER TABLE trainers ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP')
    db.engine.execute('ALTER TABLE clients ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP')
    db.engine.execute('ALTER TABLE assignments ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP')
    db.engine.execute('ALTER TABLE sessions ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP')
    print('Migration completed successfully')
"
```

## API Changes

### New API Endpoints

Generic entity API endpoints are now available:

```bash
# List entities
GET /api/entity/<entity_type>
GET /api/entity/trainers
GET /api/entity/clients

# Get specific entity
GET /api/entity/<entity_type>/<id>
GET /api/entity/trainers/1

# Create entity
POST /api/entity/<entity_type>
POST /api/entity/clients
Body: {"name": "John", "email": "john@example.com"}

# Update entity
PUT /api/entity/<entity_type>/<id>
PUT /api/entity/clients/1
Body: {"phone": "555-1234"}

# Delete entity
DELETE /api/entity/<entity_type>/<id>
DELETE /api/entity/clients/1

# Get related entities
GET /api/entity/<entity_type>/<id>/relationships/<relationship_name>
GET /api/entity/trainers/1/relationships/assignments

# Create relationship
POST /api/entity/<entity_type>/<id>/relationships/<relationship_name>
Body: {"related_entity_type": "clients", "related_entity_id": 2}

# Remove relationship
DELETE /api/entity/<entity_type>/<id>/relationships/<relationship_name>/<related_id>?related_entity_type=clients

# Get entity metadata
GET /api/entity/metadata/<entity_type>
GET /api/entity/metadata/trainers

# Get all metadata
GET /api/entity/metadata
```

### Existing Endpoints

All existing endpoints continue to work:

```bash
GET /api/trainers
GET /api/trainers/:id
POST /api/trainers
PUT /api/trainers/:id
DELETE /api/trainers/:id

GET /api/clients
GET /api/clients/:id
POST /api/clients
PUT /api/clients/:id
DELETE /api/clients/:id
```

## Code Migration

### Using EntityManager in Your Code

**Old Way:**
```python
from models.database import db, Client

# Create
client = Client(name="John", email="john@example.com")
db.session.add(client)
db.session.commit()

# Read
client = Client.query.get(1)
clients = Client.query.filter_by(status='active').all()

# Update
client = Client.query.get(1)
client.phone = "555-1234"
db.session.commit()

# Delete
client = Client.query.get(1)
db.session.delete(client)
db.session.commit()
```

**New Way (Recommended):**
```python
from core.entity_manager import entity_manager

# Create
client = entity_manager.create('clients', {
    'name': 'John',
    'email': 'john@example.com'
})

# Read
client = entity_manager.get('clients', 1)
clients = entity_manager.find('clients', 
    filters={'status': 'active'},
    order_by='name'
)

# Update
entity_manager.update('clients', 1, {'phone': '555-1234'})

# Delete
entity_manager.delete('clients', 1)

# Relationships
entity_manager.relate('trainers', 1, 'clients', 2, 'assignments')
assignments = entity_manager.get_related('trainers', 1, 'assignments')
```

### Adding Lifecycle Hooks

You can now add custom logic at specific points in an entity's lifecycle:

```python
class Client(db.Model, BaseEntity):
    # ... fields ...
    
    def before_save(self):
        """Called before creating or updating"""
        # Normalize email
        if self.email:
            self.email = self.email.lower().strip()
    
    def after_save(self):
        """Called after creating or updating"""
        # Send welcome email for new clients
        if not self.id:
            send_welcome_email(self.email)
    
    def before_delete(self):
        """Called before deleting"""
        # Archive data before deletion
        archive_client_data(self.id)
    
    def after_delete(self):
        """Called after deleting"""
        # Log deletion
        log_activity(f"Client {self.name} deleted")
```

### Creating New Entities

**1. Create the Model:**

```python
from models.database import db
from core.entity import BaseEntity
from core.relationship import RelationType

class NewEntity(db.Model, BaseEntity):
    __tablename__ = 'new_entities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    @classmethod
    def get_relationship_defs(cls):
        return {
            'related_entity': {
                'type': RelationType.MANY_TO_ONE.value,
                'entity': 'OtherEntity',
                'foreign_key': 'other_id'
            }
        }
```

**2. Create a Module:**

```python
# modules/new_feature/__init__.py
from core.module import Module
from models.database import NewEntity

class NewFeatureModule(Module):
    def __init__(self):
        super().__init__('NewFeature')
        self.dependencies = []
    
    def initialize(self):
        from core.entity_manager import entity_manager
        from core.relationship import relationship_manager, Relationship, RelationType
        
        entity_manager.register_entity(NewEntity)
        
        # Register relationships...
```

**3. Register the Module:**

```python
# In bootstrap.py
from modules.new_feature import NewFeatureModule

def bootstrap_application():
    # ... existing code ...
    module_registry.register(NewFeatureModule())
    module_registry.initialize_all()
```

## Frontend Integration

### Using New API Endpoints

**Old Way:**
```javascript
// Get trainers
const response = await fetch('/api/trainers');
const trainers = await response.json();

// Create client
const response = await fetch('/api/clients', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: 'John', email: 'john@example.com'})
});
```

**New Way (works with any entity):**
```javascript
// Get trainers
const response = await fetch('/api/entity/trainers');
const result = await response.json();
const trainers = result; // array of trainers

// Create client
const response = await fetch('/api/entity/clients', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: 'John', email: 'john@example.com'})
});

// Get trainer's assignments
const response = await fetch('/api/entity/trainers/1/relationships/assignments');
const assignments = await response.json();

// Get entity metadata
const response = await fetch('/api/entity/metadata/clients');
const metadata = await response.json();
// metadata = {type: 'clients', fields: {...}, relationships: {...}}
```

### Generic CRUD Component

You can now create generic components that work with any entity:

```javascript
class EntityManager {
    constructor(entityType) {
        this.entityType = entityType;
        this.baseUrl = `/api/entity/${entityType}`;
    }
    
    async list(filters = {}) {
        const params = new URLSearchParams(filters);
        const response = await fetch(`${this.baseUrl}?${params}`);
        return await response.json();
    }
    
    async get(id) {
        const response = await fetch(`${this.baseUrl}/${id}`);
        return await response.json();
    }
    
    async create(data) {
        const response = await fetch(this.baseUrl, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        return await response.json();
    }
    
    async update(id, data) {
        const response = await fetch(`${this.baseUrl}/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        return await response.json();
    }
    
    async delete(id) {
        const response = await fetch(`${this.baseUrl}/${id}`, {
            method: 'DELETE'
        });
        return await response.json();
    }
    
    async getRelated(id, relationshipName) {
        const response = await fetch(
            `${this.baseUrl}/${id}/relationships/${relationshipName}`
        );
        return await response.json();
    }
}

// Usage
const clientManager = new EntityManager('clients');
const clients = await clientManager.list({status: 'active'});
const client = await clientManager.get(1);
```

## Testing

### Testing with New Architecture

```python
import pytest
from core.entity_manager import entity_manager
from app_factory import create_app

@pytest.fixture
def app():
    return create_app({'TESTING': True})

def test_entity_manager(app):
    with app.app_context():
        # Create
        client = entity_manager.create('clients', {
            'name': 'Test Client',
            'email': 'test@example.com'
        })
        assert client.id is not None
        
        # Read
        found = entity_manager.get('clients', client.id)
        assert found.email == 'test@example.com'
        
        # Update
        entity_manager.update('clients', client.id, {'phone': '555-1234'})
        updated = entity_manager.get('clients', client.id)
        assert updated.phone == '555-1234'
        
        # Delete
        success = entity_manager.delete('clients', client.id)
        assert success
```

## Deployment

### Running the New Application

**Development:**
```bash
cd backend
python app_factory.py
```

**Production:**
```bash
cd backend
gunicorn "app_factory:create_app()"
```

### Environment Variables

No new environment variables are required. The same configuration works:

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key
FLASK_ENV=production
CORS_ORIGINS=https://yourdomain.com
```

## Troubleshooting

### Module Not Loading

**Problem**: Module doesn't initialize
**Solution**: Check that:
1. Module is registered in `bootstrap.py`
2. Dependencies are correctly specified
3. Module's `initialize()` method is implemented

### Relationship Not Working

**Problem**: Cannot access related entities
**Solution**: Check that:
1. Relationship is defined in `get_relationship_defs()`
2. Foreign key fields exist in database
3. Entity types match registered names (usually lowercase)

### Entity Not Found

**Problem**: `ValueError: Entity type 'X' not registered`
**Solution**: Check that:
1. Entity is registered with EntityManager in module's `initialize()`
2. Module containing entity is registered and initialized
3. Entity type name matches (check with `entity_manager.get_all_entity_types()`)

## Best Practices

1. **Use EntityManager for new code** - More consistent and maintainable
2. **Define relationships** in `get_relationship_defs()` for all entities
3. **Use lifecycle hooks** for business logic instead of scattered code
4. **Create modules** for new feature areas
5. **Use generic API** for frontend to reduce duplication
6. **Add metadata** to entities for better documentation

## Getting Help

- Check `ESPOCRM_ARCHITECTURE.md` for detailed architecture documentation
- Run `python test_architecture.py` to verify your setup
- Review existing modules in `backend/modules/` for examples

## Summary

The new EspoCRM-inspired architecture provides:
- ✅ Better organization through modules
- ✅ Clearer entity relationships
- ✅ Centralized CRUD operations
- ✅ Consistent API endpoints
- ✅ Lifecycle hooks for business logic
- ✅ Full backward compatibility

All existing code continues to work while you gradually adopt the new patterns!
