"""
Test script for EspoCRM-inspired architecture
Tests core functionality of the new architecture
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_core_structure():
    """Test the core structure components"""
    print("Testing EspoCRM-inspired Architecture")
    print("=" * 50)
    
    # Test 1: Import core modules
    print("\n1. Testing core module imports...")
    try:
        from core.entity import BaseEntity, EntityType
        from core.entity_manager import EntityManager, entity_manager
        from core.relationship import RelationType, Relationship, relationship_manager
        from core.module import Module, module_registry
        print("✓ Core modules imported successfully")
    except Exception as e:
        print(f"✗ Failed to import core modules: {e}")
        return False
    
    # Test 2: Bootstrap application
    print("\n2. Testing application bootstrap...")
    try:
        from bootstrap import bootstrap_application
        bootstrap_application()
        print("✓ Application bootstrapped successfully")
    except Exception as e:
        print(f"✗ Failed to bootstrap: {e}")
        return False
    
    # Test 3: Check entity registration
    print("\n3. Testing entity registration...")
    try:
        entity_types = entity_manager.get_all_entity_types()
        print(f"✓ Registered entities: {', '.join(entity_types)}")
        
        if 'trainers' not in entity_types:
            print("✗ Trainers entity not registered")
            return False
        if 'clients' not in entity_types:
            print("✗ Clients entity not registered")
            return False
        if 'sessions' not in entity_types:
            print("✗ Sessions entity not registered")
            return False
    except Exception as e:
        print(f"✗ Failed to check entity registration: {e}")
        return False
    
    # Test 4: Check entity metadata
    print("\n4. Testing entity metadata...")
    try:
        trainer_defs = entity_manager.get_entity_defs('trainers')
        print(f"✓ Trainer entity metadata: {trainer_defs['type']}")
        print(f"  - Relationships: {list(trainer_defs['relationships'].keys())}")
        
        client_defs = entity_manager.get_entity_defs('clients')
        print(f"✓ Client entity metadata: {client_defs['type']}")
        print(f"  - Relationships: {list(client_defs['relationships'].keys())}")
    except Exception as e:
        print(f"✗ Failed to get entity metadata: {e}")
        return False
    
    # Test 5: Check module loading
    print("\n5. Testing module system...")
    try:
        load_order = module_registry.get_load_order()
        print(f"✓ Module load order: {' -> '.join(load_order)}")
        
        # Verify dependency resolution
        if load_order.index('Clients') > load_order.index('Sessions') or \
           load_order.index('Trainers') > load_order.index('Sessions'):
            print("✗ Module dependencies not resolved correctly")
            return False
        print("✓ Module dependencies resolved correctly")
    except Exception as e:
        print(f"✗ Failed to check module system: {e}")
        return False
    
    # Test 6: Check relationships
    print("\n6. Testing relationship system...")
    try:
        trainer_assignments = relationship_manager.get('trainers', 'assignments')
        if trainer_assignments:
            print(f"✓ Trainer->Assignments relationship registered")
            print(f"  - Type: {trainer_assignments.type.value}")
            print(f"  - Target entity: {trainer_assignments.entity}")
        else:
            print("✗ Trainer->Assignments relationship not found")
            return False
        
        client_sessions = relationship_manager.get('clients', 'sessions')
        if client_sessions:
            print(f"✓ Client->Sessions relationship registered")
            print(f"  - Type: {client_sessions.type.value}")
            print(f"  - Target entity: {client_sessions.entity}")
        else:
            print("✗ Client->Sessions relationship not found")
            return False
    except Exception as e:
        print(f"✗ Failed to check relationships: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All tests passed successfully!")
    print("\nNew Architecture Summary:")
    print(f"  - {len(entity_types)} entities registered")
    print(f"  - {len(load_order)} modules loaded")
    print(f"  - Module loading order: {' -> '.join(load_order)}")
    print("\nThe EspoCRM-inspired backbone is working correctly!")
    return True


if __name__ == '__main__':
    success = test_core_structure()
    sys.exit(0 if success else 1)
