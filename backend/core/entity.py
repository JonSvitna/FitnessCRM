"""Base Entity class for EspoCRM-inspired architecture"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

class BaseEntity:
    """
    Base entity class that all entities should inherit from.
    Provides common fields and methods similar to EspoCRM.
    """
    
    # Common fields that all entities should have
    id = None  # Override in subclass
    created_at = None
    updated_at = None
    deleted_at = None  # For soft deletes
    
    @classmethod
    def get_entity_type(cls):
        """Return the entity type name"""
        return cls.__tablename__ if hasattr(cls, '__tablename__') else cls.__name__.lower()
    
    @classmethod
    def get_entity_defs(cls):
        """
        Return entity definitions (metadata).
        This allows for runtime configuration of entities.
        """
        return {
            'type': cls.get_entity_type(),
            'fields': cls.get_field_defs(),
            'relationships': cls.get_relationship_defs(),
        }
    
    @classmethod
    def get_field_defs(cls):
        """Return field definitions for this entity"""
        # Default implementation - can be overridden
        return {}
    
    @classmethod
    def get_relationship_defs(cls):
        """Return relationship definitions for this entity"""
        # Default implementation - can be overridden
        return {}
    
    def to_dict(self, include_relationships=False):
        """
        Convert entity to dictionary.
        Override in subclasses for custom serialization.
        """
        result = {}
        
        # Get all columns
        if hasattr(self, '__table__'):
            for column in self.__table__.columns:
                value = getattr(self, column.name, None)
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
        
        # Optionally include relationships
        if include_relationships:
            result['_relationships'] = self.get_relationships_data()
        
        return result
    
    def get_relationships_data(self):
        """Get data for all relationships"""
        # Default implementation - can be overridden
        return {}
    
    def before_save(self):
        """Hook called before saving"""
        pass
    
    def after_save(self):
        """Hook called after saving"""
        pass
    
    def before_delete(self):
        """Hook called before deleting"""
        pass
    
    def after_delete(self):
        """Hook called after deleting"""
        pass


class EntityType:
    """Entity type definitions similar to EspoCRM"""
    BASE = 'Base'
    PERSON = 'Person'
    COMPANY = 'Company'
    EVENT = 'Event'
