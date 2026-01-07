"""Trainers Module - Organizes trainer-related features"""
from core.module import Module
from models.database import Trainer

class TrainersModule(Module):
    """Module for trainer management"""
    
    def __init__(self):
        super().__init__('Trainers')
        self.dependencies = []  # No dependencies
    
    def initialize(self):
        """Initialize the Trainers module"""
        # Register entities
        from core.entity_manager import entity_manager
        entity_manager.register_entity(Trainer)
        
        # Register relationships
        from core.relationship import relationship_manager, Relationship, RelationType
        
        # Trainer -> Assignments (one-to-many)
        relationship_manager.register('trainers', Relationship(
            name='assignments',
            type=RelationType.ONE_TO_MANY,
            entity='assignments',
            foreign_key='trainer_id',
            opposite_name='trainer'
        ))
        
        # Trainer -> Sessions (one-to-many)
        relationship_manager.register('trainers', Relationship(
            name='sessions',
            type=RelationType.ONE_TO_MANY,
            entity='sessions',
            foreign_key='trainer_id',
            opposite_name='trainer'
        ))
