"""Relationship types and definitions for EspoCRM-inspired architecture"""
from enum import Enum

class RelationType(Enum):
    """Relationship types similar to EspoCRM"""
    ONE_TO_MANY = 'oneToMany'
    MANY_TO_ONE = 'manyToOne'
    MANY_TO_MANY = 'manyToMany'
    ONE_TO_ONE = 'oneToOne'
    PARENT = 'parent'
    CHILDREN = 'children'


class Relationship:
    """
    Relationship definition class.
    Defines how entities are related to each other.
    """
    
    def __init__(self, name: str, type: RelationType, entity: str, 
                 foreign_key: str = None, opposite_name: str = None):
        """
        Initialize relationship.
        
        Args:
            name: Name of the relationship
            type: Type of relationship
            entity: Related entity type
            foreign_key: Foreign key field name (for many-to-one)
            opposite_name: Name of opposite relationship
        """
        self.name = name
        self.type = type
        self.entity = entity
        self.foreign_key = foreign_key
        self.opposite_name = opposite_name
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'name': self.name,
            'type': self.type.value,
            'entity': self.entity,
            'foreign_key': self.foreign_key,
            'opposite_name': self.opposite_name
        }


class RelationshipManager:
    """
    Manages relationships between entities.
    Similar to EspoCRM's relationship management.
    """
    
    def __init__(self):
        """Initialize relationship manager"""
        self._relationships = {}
    
    def register(self, entity_type: str, relationship: Relationship):
        """
        Register a relationship.
        
        Args:
            entity_type: Source entity type
            relationship: Relationship definition
        """
        if entity_type not in self._relationships:
            self._relationships[entity_type] = {}
        
        self._relationships[entity_type][relationship.name] = relationship
    
    def get(self, entity_type: str, relationship_name: str):
        """
        Get a relationship definition.
        
        Args:
            entity_type: Entity type
            relationship_name: Relationship name
            
        Returns:
            Relationship definition or None
        """
        return self._relationships.get(entity_type, {}).get(relationship_name)
    
    def get_all(self, entity_type: str):
        """
        Get all relationships for an entity.
        
        Args:
            entity_type: Entity type
            
        Returns:
            Dict of relationships
        """
        return self._relationships.get(entity_type, {})
    
    def get_opposite(self, entity_type: str, relationship_name: str):
        """
        Get the opposite side of a relationship.
        
        Args:
            entity_type: Entity type
            relationship_name: Relationship name
            
        Returns:
            Tuple of (opposite_entity_type, opposite_relationship_name)
        """
        relationship = self.get(entity_type, relationship_name)
        if not relationship:
            return None, None
        
        return relationship.entity, relationship.opposite_name


# Global relationship manager instance
relationship_manager = RelationshipManager()
