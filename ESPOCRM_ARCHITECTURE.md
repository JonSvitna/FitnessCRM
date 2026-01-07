# EspoCRM-Inspired Architecture Guide

## Overview

FitnessCRM now implements an EspoCRM-inspired backbone architecture that provides:
- **Structured entity management** - All entities inherit from a common BaseEntity
- **Metadata-driven relationships** - Relationships are defined declaratively
- **Modular organization** - Features are organized into independent modules
- **Centralized operations** - EntityManager handles all CRUD operations
- **Flexible API** - Generic entity API routes for consistent access

## Architecture Components

### 1. Core Layer (`backend/core/`)

#### BaseEntity (`core/entity.py`)
Base class for all entities with common fields and lifecycle hooks:
- `id`, `created_at`, `updated_at`, `deleted_at`
- Lifecycle hooks: `before_save()`, `after_save()`, `before_delete()`, `after_delete()`
- Metadata methods: `get_entity_type()`, `get_entity_defs()`, `get_relationship_defs()`

#### EntityManager (`core/entity_manager.py`)
Centralized manager for entity operations:
- `create(entity_type, data)` - Create new entity
- `get(entity_type, entity_id)` - Get entity by ID
- `find(entity_type, filters)` - Find entities with filters
- `update(entity_type, entity_id, data)` - Update entity
- `delete(entity_type, entity_id)` - Delete entity
- `relate()` / `unrelate()` - Manage relationships
- `get_related()` - Get related entities

#### Relationship System (`core/relationship.py`)
Defines relationship types and management:
- `RelationType`: ONE_TO_MANY, MANY_TO_ONE, MANY_TO_MANY, ONE_TO_ONE
- `Relationship`: Relationship definition class
- `RelationshipManager`: Manages relationship registry

#### Module System (`core/module.py`)
Organizes features into modules:
- `Module`: Base class for feature modules
- `ModuleRegistry`: Manages module loading and dependencies

### 2. Entity Layer (`backend/models/`)

All models now inherit from both `db.Model` and `BaseEntity`:

```python
class Trainer(db.Model, BaseEntity):
    __tablename__ = 'trainers'
    
    # Fields...
    
    @classmethod
    def get_relationship_defs(cls):
        return {
            'assignments': {
                'type': RelationType.ONE_TO_MANY.value,
                'entity': 'Assignment',
                'foreign_key': 'trainer_id'
            }
        }
```

### 3. Module Layer (`backend/modules/`)

Each feature area is organized as a module:
- **ClientsModule** - Client management
- **TrainersModule** - Trainer management
- **SessionsModule** - Session and assignment management

### 4. API Layer (`backend/api/`)

#### Generic Entity API (`api/entity_routes.py`)
RESTful endpoints for all entities:
- `GET /api/entity/<entity_type>` - List entities
- `GET /api/entity/<entity_type>/<id>` - Get entity
- `POST /api/entity/<entity_type>` - Create entity
- `PUT /api/entity/<entity_type>/<id>` - Update entity
- `DELETE /api/entity/<entity_type>/<id>` - Delete entity
- `GET /api/entity/<entity_type>/<id>/relationships/<name>` - Get related
- `POST /api/entity/<entity_type>/<id>/relationships/<name>` - Create relationship
- `DELETE /api/entity/<entity_type>/<id>/relationships/<name>/<related_id>` - Remove relationship

#### Metadata API
- `GET /api/entity/metadata/<entity_type>` - Get entity metadata
- `GET /api/entity/metadata` - Get all metadata

## Usage Examples

### Using EntityManager

```python
from core.entity_manager import entity_manager

# Create a client
client = entity_manager.create('clients', {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '555-1234'
})

# Find clients
clients = entity_manager.find('clients', 
    filters={'status': 'active'},
    order_by='name',
    limit=10
)

# Get a client
client = entity_manager.get('clients', 1)

# Update a client
entity_manager.update('clients', 1, {'phone': '555-5678'})

# Create relationship
entity_manager.relate('trainers', 1, 'clients', 2, 'assignments')

# Get related entities
assignments = entity_manager.get_related('trainers', 1, 'assignments')
```

### Using Generic API

```bash
# List all clients
GET /api/entity/clients

# Get specific client
GET /api/entity/clients/1

# Create client
POST /api/entity/clients
{
    "name": "John Doe",
    "email": "john@example.com"
}

# Update client
PUT /api/entity/clients/1
{
    "phone": "555-5678"
}

# Get trainer's assignments
GET /api/entity/trainers/1/relationships/assignments

# Get entity metadata
GET /api/entity/metadata/clients
```

## Benefits

### 1. Structured Relationships
- Clear definition of entity relationships
- Consistent relationship management
- Automatic relationship resolution

### 2. Modular Organization
- Features organized into independent modules
- Clear dependency management
- Easy to add new features

### 3. Consistent API
- Generic CRUD operations for all entities
- Relationship management through API
- Metadata-driven functionality

### 4. Extensibility
- Easy to add new entities
- Lifecycle hooks for custom logic
- Module system for feature isolation

### 5. Maintainability
- Centralized entity operations
- Clear separation of concerns
- Self-documenting through metadata

## Migration from Old System

The new architecture maintains **backward compatibility** with existing API routes. Both systems work side-by-side:

- Existing routes (`/api/trainers`, `/api/clients`) continue to work
- New generic routes (`/api/entity/trainers`, `/api/entity/clients`) provide enhanced functionality
- Models are enhanced with BaseEntity without breaking changes

## Bootstrap Process

The application bootstrap process:

1. Register all modules
2. Initialize modules in dependency order
3. Register entities with EntityManager
4. Register relationships with RelationshipManager
5. Application ready

```python
from bootstrap import bootstrap_application

# Call during application startup
bootstrap_application()
```

## Adding New Features

### 1. Create Entity Model

```python
class NewEntity(db.Model, BaseEntity):
    __tablename__ = 'new_entities'
    
    id = db.Column(db.Integer, primary_key=True)
    # ... fields ...
    
    @classmethod
    def get_relationship_defs(cls):
        return {
            'related_entity': {
                'type': RelationType.MANY_TO_ONE.value,
                'entity': 'other_entity',
                'foreign_key': 'other_id'
            }
        }
```

### 2. Create Module

```python
from core.module import Module

class NewFeatureModule(Module):
    def __init__(self):
        super().__init__('NewFeature')
        self.dependencies = ['Clients']  # if depends on clients
    
    def initialize(self):
        from core.entity_manager import entity_manager
        entity_manager.register_entity(NewEntity)
```

### 3. Register Module

```python
# In bootstrap.py
from modules.new_feature import NewFeatureModule
module_registry.register(NewFeatureModule())
```

## Best Practices

1. **Always define relationships** in `get_relationship_defs()`
2. **Use lifecycle hooks** for business logic (before_save, after_save, etc.)
3. **Register entities** with EntityManager in module initialization
4. **Define module dependencies** correctly
5. **Use EntityManager** for programmatic entity operations
6. **Use generic API** for consistent frontend integration

## Troubleshooting

### Module not loading
Check that:
- Module is registered in bootstrap.py
- Dependencies are correctly specified
- Module's initialize() method is implemented

### Relationship not working
Check that:
- Relationship is defined in both entities
- Foreign key fields exist in database
- Entity types match registered names

### Entity not found
Check that:
- Entity is registered with EntityManager
- Entity type name matches (usually lowercase of class name)
- Module containing entity is initialized

## Future Enhancements

The architecture supports these future enhancements:
- Custom field types
- Validation rules in metadata
- Computed fields
- Event system for entity changes
- Advanced query builder
- Multi-tenancy support
- API versioning
- GraphQL integration
