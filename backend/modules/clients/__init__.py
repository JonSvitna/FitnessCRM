"""Clients Module - Organizes client-related features"""
from core.module import Module
from models.database import Client

class ClientsModule(Module):
    """Module for client management"""
    
    def __init__(self):
        super().__init__('Clients')
        self.dependencies = []  # No dependencies
    
    def initialize(self):
        """Initialize the Clients module"""
        # Register entities
        from core.entity_manager import entity_manager
        entity_manager.register_entity(Client)
        
        # Register relationships
        from core.relationship import relationship_manager, Relationship, RelationType
        
        # Client -> Assignments (one-to-many)
        relationship_manager.register('clients', Relationship(
            name='assignments',
            type=RelationType.ONE_TO_MANY,
            entity='assignments',
            foreign_key='client_id',
            opposite_name='client'
        ))
        
        # Client -> Sessions (one-to-many)
        relationship_manager.register('clients', Relationship(
            name='sessions',
            type=RelationType.ONE_TO_MANY,
            entity='sessions',
            foreign_key='client_id',
            opposite_name='client'
        ))
        
        # Client -> ProgressRecords (one-to-many)
        relationship_manager.register('clients', Relationship(
            name='progress_records',
            type=RelationType.ONE_TO_MANY,
            entity='progress_records',
            foreign_key='client_id',
            opposite_name='client'
        ))
