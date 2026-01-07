"""Entity API routes - Generic CRUD operations using EntityManager"""
from flask import Blueprint, request, jsonify
from core.entity_manager import entity_manager

entity_api_bp = Blueprint('entity_api', __name__, url_prefix='/api/entity')

@entity_api_bp.route('/<entity_type>', methods=['GET'])
def get_entities(entity_type):
    """Get all entities of a type"""
    try:
        # Get query parameters
        filters = {}
        for key, value in request.args.items():
            if key not in ['order_by', 'limit', 'page', 'per_page']:
                filters[key] = value
        
        order_by = request.args.get('order_by')
        limit = request.args.get('limit', type=int)
        
        # Find entities
        entities = entity_manager.find(entity_type, filters=filters, order_by=order_by, limit=limit)
        
        return jsonify([entity.to_dict() for entity in entities]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/<entity_type>/<int:entity_id>', methods=['GET'])
def get_entity(entity_type, entity_id):
    """Get a specific entity"""
    try:
        entity = entity_manager.get(entity_type, entity_id)
        if not entity:
            return jsonify({'error': 'Entity not found'}), 404
        
        return jsonify(entity.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/<entity_type>', methods=['POST'])
def create_entity(entity_type):
    """Create a new entity"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        entity = entity_manager.create(entity_type, data)
        return jsonify(entity.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/<entity_type>/<int:entity_id>', methods=['PUT'])
def update_entity(entity_type, entity_id):
    """Update an entity"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        entity = entity_manager.update(entity_type, entity_id, data)
        if not entity:
            return jsonify({'error': 'Entity not found'}), 404
        
        return jsonify(entity.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/<entity_type>/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_type, entity_id):
    """Delete an entity"""
    try:
        success = entity_manager.delete(entity_type, entity_id)
        if not success:
            return jsonify({'error': 'Entity not found'}), 404
        
        return jsonify({'message': 'Entity deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/<entity_type>/<int:entity_id>/relationships/<relationship_name>', methods=['GET'])
def get_related_entities(entity_type, entity_id, relationship_name):
    """Get related entities"""
    try:
        related = entity_manager.get_related(entity_type, entity_id, relationship_name)
        return jsonify([entity.to_dict() for entity in related]), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/<entity_type>/<int:entity_id>/relationships/<relationship_name>', methods=['POST'])
def relate_entities(entity_type, entity_id, relationship_name):
    """Create a relationship between entities"""
    try:
        data = request.get_json()
        if not data or 'related_entity_type' not in data or 'related_entity_id' not in data:
            return jsonify({'error': 'Invalid data'}), 400
        
        success = entity_manager.relate(
            entity_type, entity_id,
            data['related_entity_type'], data['related_entity_id'],
            relationship_name
        )
        
        if not success:
            return jsonify({'error': 'Failed to create relationship'}), 400
        
        return jsonify({'message': 'Relationship created successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/<entity_type>/<int:entity_id>/relationships/<relationship_name>/<int:related_entity_id>', methods=['DELETE'])
def unrelate_entities(entity_type, entity_id, relationship_name, related_entity_id):
    """Remove a relationship between entities"""
    try:
        # Extract related entity type from request
        related_entity_type = request.args.get('related_entity_type')
        if not related_entity_type:
            return jsonify({'error': 'related_entity_type parameter required'}), 400
        
        success = entity_manager.unrelate(
            entity_type, entity_id,
            related_entity_type, related_entity_id,
            relationship_name
        )
        
        if not success:
            return jsonify({'error': 'Failed to remove relationship'}), 400
        
        return jsonify({'message': 'Relationship removed successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/metadata/<entity_type>', methods=['GET'])
def get_entity_metadata(entity_type):
    """Get entity metadata (definitions)"""
    try:
        metadata = entity_manager.get_entity_defs(entity_type)
        if not metadata:
            return jsonify({'error': 'Entity type not found'}), 404
        
        return jsonify(metadata), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@entity_api_bp.route('/metadata', methods=['GET'])
def get_all_metadata():
    """Get metadata for all entity types"""
    try:
        entity_types = entity_manager.get_all_entity_types()
        metadata = {}
        for entity_type in entity_types:
            metadata[entity_type] = entity_manager.get_entity_defs(entity_type)
        
        return jsonify(metadata), 200
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
