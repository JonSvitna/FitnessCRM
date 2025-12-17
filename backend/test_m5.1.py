"""
Test script for M5.1: In-App Messaging
Run this to verify the messaging system is set up correctly
"""

import sys

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from flask_socketio import SocketIO
        print("✓ Flask-SocketIO imported successfully")
    except ImportError as e:
        print(f"✗ Flask-SocketIO import failed: {e}")
        return False
    
    try:
        from models.database import MessageThread, Message, MessageAttachment
        print("✓ Message models imported successfully")
    except ImportError as e:
        print(f"✗ Message models import failed: {e}")
        return False
    
    try:
        from api.message_routes import message_bp
        print("✓ Message routes imported successfully")
    except ImportError as e:
        print(f"✗ Message routes import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test that the Flask app can be created"""
    print("\nTesting app creation...")
    
    try:
        from app import create_app, socketio
        app = create_app()
        print("✓ Flask app created successfully")
        print(f"✓ SocketIO initialized: {socketio is not None}")
        return True, app, socketio
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def test_database_models():
    """Test that database models are properly defined"""
    print("\nTesting database models...")
    
    try:
        from models.database import db, MessageThread, Message, MessageAttachment
        
        # Check that models have required attributes
        assert hasattr(MessageThread, 'trainer_id')
        assert hasattr(MessageThread, 'client_id')
        assert hasattr(MessageThread, 'to_dict')
        print("✓ MessageThread model structure correct")
        
        assert hasattr(Message, 'thread_id')
        assert hasattr(Message, 'sender_type')
        assert hasattr(Message, 'content')
        assert hasattr(Message, 'to_dict')
        print("✓ Message model structure correct")
        
        assert hasattr(MessageAttachment, 'message_id')
        assert hasattr(MessageAttachment, 'file_id')
        assert hasattr(MessageAttachment, 'to_dict')
        print("✓ MessageAttachment model structure correct")
        
        return True
    except Exception as e:
        print(f"✗ Database model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("M5.1: In-App Messaging - Test Suite")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install dependencies.")
        sys.exit(1)
    
    # Test database models
    if not test_database_models():
        print("\n❌ Database model tests failed.")
        sys.exit(1)
    
    # Test app creation
    success, app, socketio = test_app_creation()
    if not success:
        print("\n❌ App creation tests failed.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ All tests passed! M5.1 is ready to test.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the backend server: python app.py")
    print("2. Start the frontend dev server (if using Vite)")
    print("3. Navigate to /messages.html in your browser")
    print("4. Test creating a new thread and sending messages")

