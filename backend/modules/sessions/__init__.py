"""Sessions Module - Organizes session-related features"""
from core.module import Module
from models.database import Session, Assignment

class SessionsModule(Module):
    """Module for session management"""
    
    def __init__(self):
        super().__init__('Sessions')
        self.dependencies = ['Clients', 'Trainers']  # Depends on Clients and Trainers
    
    def initialize(self):
        """Initialize the Sessions module"""
        # Register entities
        from core.entity_manager import entity_manager
        entity_manager.register_entity(Session)
        entity_manager.register_entity(Assignment)
        
        # Register relationships
        from core.relationship import relationship_manager, Relationship, RelationType
        
        # Session -> Trainer (many-to-one)
        relationship_manager.register('sessions', Relationship(
            name='trainer',
            type=RelationType.MANY_TO_ONE,
            entity='trainers',
            foreign_key='trainer_id',
            opposite_name='sessions'
        ))
        
        # Session -> Client (many-to-one)
        relationship_manager.register('sessions', Relationship(
            name='client',
            type=RelationType.MANY_TO_ONE,
            entity='clients',
            foreign_key='client_id',
            opposite_name='sessions'
        ))
        
        # Assignment -> Trainer (many-to-one)
        relationship_manager.register('assignments', Relationship(
            name='trainer',
            type=RelationType.MANY_TO_ONE,
            entity='trainers',
            foreign_key='trainer_id',
            opposite_name='assignments'
        ))
        
        # Assignment -> Client (many-to-one)
        relationship_manager.register('assignments', Relationship(
            name='client',
            type=RelationType.MANY_TO_ONE,
            entity='clients',
            foreign_key='client_id',
            opposite_name='assignments'
        ))
