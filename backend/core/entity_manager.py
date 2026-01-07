"""EntityManager for centralized entity operations"""
from typing import Dict, List, Optional, Any, Type
from sqlalchemy import inspect
from models.database import db

class EntityManager:
    """
    Central manager for entity operations similar to EspoCRM.
    Provides CRUD operations and relationship management.
    """
    
    def __init__(self, db_instance=None):
        """Initialize EntityManager with database instance"""
        self.db = db_instance or db
        self._entity_registry = {}
        self._relationship_registry = {}
    
    def register_entity(self, entity_class):
        """Register an entity class"""
        entity_type = entity_class.get_entity_type() if hasattr(entity_class, 'get_entity_type') else entity_class.__name__.lower()
        self._entity_registry[entity_type] = entity_class
        
        # Register relationships
        if hasattr(entity_class, 'get_relationship_defs'):
            relationships = entity_class.get_relationship_defs()
            self._relationship_registry[entity_type] = relationships
    
    def get_entity_class(self, entity_type: str):
        """Get entity class by type"""
        return self._entity_registry.get(entity_type)
    
    def create(self, entity_type: str, data: Dict[str, Any]) -> Any:
        """
        Create a new entity.
        
        Args:
            entity_type: Type of entity to create
            data: Entity data
            
        Returns:
            Created entity instance
        """
        entity_class = self.get_entity_class(entity_type)
        if not entity_class:
            raise ValueError(f"Entity type '{entity_type}' not registered")
        
        # Create entity instance
        entity = entity_class()
        
        # Set attributes
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        # Call before_save hook
        if hasattr(entity, 'before_save'):
            entity.before_save()
        
        # Save to database
        self.db.session.add(entity)
        self.db.session.commit()
        
        # Call after_save hook
        if hasattr(entity, 'after_save'):
            entity.after_save()
        
        return entity
    
    def get(self, entity_type: str, entity_id: int) -> Optional[Any]:
        """
        Get an entity by ID.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            Entity instance or None
        """
        entity_class = self.get_entity_class(entity_type)
        if not entity_class:
            raise ValueError(f"Entity type '{entity_type}' not registered")
        
        return entity_class.query.get(entity_id)
    
    def find(self, entity_type: str, filters: Optional[Dict[str, Any]] = None, 
             order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Any]:
        """
        Find entities matching criteria.
        
        Args:
            entity_type: Type of entity
            filters: Filter criteria
            order_by: Order by field
            limit: Maximum number of results
            
        Returns:
            List of entity instances
        """
        entity_class = self.get_entity_class(entity_type)
        if not entity_class:
            raise ValueError(f"Entity type '{entity_type}' not registered")
        
        query = entity_class.query
        
        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(entity_class, key):
                    query = query.filter(getattr(entity_class, key) == value)
        
        # Apply ordering
        if order_by:
            if hasattr(entity_class, order_by):
                query = query.order_by(getattr(entity_class, order_by))
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def update(self, entity_type: str, entity_id: int, data: Dict[str, Any]) -> Optional[Any]:
        """
        Update an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            data: Updated data
            
        Returns:
            Updated entity instance or None
        """
        entity = self.get(entity_type, entity_id)
        if not entity:
            return None
        
        # Update attributes
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        # Call before_save hook
        if hasattr(entity, 'before_save'):
            entity.before_save()
        
        # Save to database
        self.db.session.commit()
        
        # Call after_save hook
        if hasattr(entity, 'after_save'):
            entity.after_save()
        
        return entity
    
    def delete(self, entity_type: str, entity_id: int) -> bool:
        """
        Delete an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            True if deleted, False if not found
        """
        entity = self.get(entity_type, entity_id)
        if not entity:
            return False
        
        # Call before_delete hook
        if hasattr(entity, 'before_delete'):
            entity.before_delete()
        
        # Delete from database
        self.db.session.delete(entity)
        self.db.session.commit()
        
        # Call after_delete hook
        if hasattr(entity, 'after_delete'):
            entity.after_delete()
        
        return True
    
    def relate(self, entity_type: str, entity_id: int, 
               related_entity_type: str, related_entity_id: int,
               relationship_name: str) -> bool:
        """
        Create a relationship between entities.
        
        Args:
            entity_type: Type of source entity
            entity_id: ID of source entity
            related_entity_type: Type of related entity
            related_entity_id: ID of related entity
            relationship_name: Name of relationship
            
        Returns:
            True if successful
        """
        entity = self.get(entity_type, entity_id)
        related_entity = self.get(related_entity_type, related_entity_id)
        
        if not entity or not related_entity:
            return False
        
        # Get relationship definition
        relationships = self._relationship_registry.get(entity_type, {})
        if relationship_name not in relationships:
            return False
        
        # Add relationship
        if hasattr(entity, relationship_name):
            relationship_attr = getattr(entity, relationship_name)
            
            # Handle different relationship types
            if hasattr(relationship_attr, 'append'):
                # One-to-many or many-to-many - check for duplicates
                # Use list comprehension to check if entity already exists
                existing_ids = [item.id for item in relationship_attr if hasattr(item, 'id')]
                if related_entity.id not in existing_ids:
                    relationship_attr.append(related_entity)
                else:
                    # Already related, still return success
                    return True
            else:
                # One-to-one or many-to-one
                setattr(entity, relationship_name, related_entity)
            
            self.db.session.commit()
            return True
        
        return False
    
    def unrelate(self, entity_type: str, entity_id: int,
                 related_entity_type: str, related_entity_id: int,
                 relationship_name: str) -> bool:
        """
        Remove a relationship between entities.
        
        Args:
            entity_type: Type of source entity
            entity_id: ID of source entity
            related_entity_type: Type of related entity
            related_entity_id: ID of related entity
            relationship_name: Name of relationship
            
        Returns:
            True if successful
        """
        entity = self.get(entity_type, entity_id)
        related_entity = self.get(related_entity_type, related_entity_id)
        
        if not entity or not related_entity:
            return False
        
        # Get relationship definition
        relationships = self._relationship_registry.get(entity_type, {})
        if relationship_name not in relationships:
            return False
        
        # Remove relationship
        if hasattr(entity, relationship_name):
            relationship_attr = getattr(entity, relationship_name)
            
            # Handle different relationship types
            if hasattr(relationship_attr, 'remove'):
                # One-to-many or many-to-many
                relationship_attr.remove(related_entity)
            else:
                # One-to-one or many-to-one
                setattr(entity, relationship_name, None)
            
            self.db.session.commit()
            return True
        
        return False
    
    def get_related(self, entity_type: str, entity_id: int, 
                   relationship_name: str) -> List[Any]:
        """
        Get related entities.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            relationship_name: Name of relationship
            
        Returns:
            List of related entities
        """
        entity = self.get(entity_type, entity_id)
        if not entity:
            return []
        
        if not hasattr(entity, relationship_name):
            return []
        
        relationship_attr = getattr(entity, relationship_name)
        
        # Handle different relationship types
        if isinstance(relationship_attr, list):
            return relationship_attr
        elif relationship_attr is not None:
            return [relationship_attr]
        
        return []
    
    def get_entity_defs(self, entity_type: str) -> Optional[Dict[str, Any]]:
        """
        Get entity definitions (metadata).
        
        Args:
            entity_type: Type of entity
            
        Returns:
            Entity definitions dict or None
        """
        entity_class = self.get_entity_class(entity_type)
        if not entity_class:
            return None
        
        if hasattr(entity_class, 'get_entity_defs'):
            return entity_class.get_entity_defs()
        
        return {
            'type': entity_type,
            'fields': {},
            'relationships': {}
        }
    
    def get_all_entity_types(self) -> List[str]:
        """Get list of all registered entity types"""
        return list(self._entity_registry.keys())


# Global entity manager instance
entity_manager = EntityManager()
