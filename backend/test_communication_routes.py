"""
Diagnostic script to test communication route imports
Run this to identify why routes might be failing to import
"""

import sys
import traceback

def test_import(module_name, blueprint_name):
    """Test importing a blueprint"""
    print(f"\n{'='*60}")
    print(f"Testing {module_name}...")
    print('='*60)
    
    try:
        module = __import__(f'api.{module_name}', fromlist=[blueprint_name])
        blueprint = getattr(module, blueprint_name)
        
        if blueprint:
            print(f"✅ SUCCESS: {blueprint_name} imported successfully")
            print(f"   Blueprint name: {blueprint.name}")
            print(f"   URL prefix: {blueprint.url_prefix}")
            return True
        else:
            print(f"❌ FAILED: {blueprint_name} is None")
            return False
            
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        traceback.print_exc()
        return False
    except AttributeError as e:
        print(f"❌ ATTRIBUTE ERROR: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        traceback.print_exc()
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print(f"\n{'='*60}")
    print("Testing Dependencies...")
    print('='*60)
    
    dependencies = {
        'flask': 'Flask',
        'flask_socketio': 'Flask-SocketIO',
        'twilio': 'Twilio',
        'flask_mail': 'Flask-Mail',
        'sqlalchemy': 'SQLAlchemy'
    }
    
    results = {}
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name} is installed")
            results[module] = True
        except ImportError:
            print(f"❌ {name} is NOT installed")
            results[module] = False
    
    return results

def test_utils():
    """Test if utility modules can be imported"""
    print(f"\n{'='*60}")
    print("Testing Utility Modules...")
    print('='*60)
    
    utils_modules = ['utils.sms', 'utils.email', 'utils.automation', 'utils.logger']
    
    results = {}
    for module_name in utils_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} imported successfully")
            results[module_name] = True
        except Exception as e:
            print(f"❌ {module_name} import failed: {e}")
            traceback.print_exc()
            results[module_name] = False
    
    return results

def test_models():
    """Test if required models can be imported"""
    print(f"\n{'='*60}")
    print("Testing Database Models...")
    print('='*60)
    
    models_to_test = [
        'MessageThread', 'Message', 'MessageAttachment',
        'SMSLog', 'SMSTemplate', 'SMSSchedule',
        'EmailCampaign', 'EmailTemplate', 'CampaignRecipient',
        'AutomationRule', 'AutomationLog'
    ]
    
    try:
        from models.database import db
        print("✅ Database module imported")
        
        results = {}
        for model_name in models_to_test:
            try:
                model = getattr(__import__('models.database', fromlist=[model_name]), model_name)
                print(f"✅ {model_name} model found")
                results[model_name] = True
            except AttributeError:
                print(f"❌ {model_name} model NOT found")
                results[model_name] = False
        
        return results
    except Exception as e:
        print(f"❌ Database module import failed: {e}")
        traceback.print_exc()
        return {}

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Fitness CRM - Communication Routes Diagnostic")
    print("="*60)
    
    # Test dependencies
    deps = test_dependencies()
    
    # Test utils
    utils = test_utils()
    
    # Test models
    models = test_models()
    
    # Test route imports
    routes = {
        'sms_routes': 'sms_bp',
        'campaign_routes': 'campaign_bp',
        'automation_routes': 'automation_bp',
        'message_routes': 'message_bp'
    }
    
    route_results = {}
    for module, blueprint in routes.items():
        route_results[module] = test_import(module, blueprint)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    
    print("\nDependencies:")
    for dep, status in deps.items():
        print(f"  {dep}: {'✅' if status else '❌'}")
    
    print("\nUtility Modules:")
    for util, status in utils.items():
        print(f"  {util}: {'✅' if status else '❌'}")
    
    print("\nRoute Blueprints:")
    for route, status in route_results.items():
        print(f"  {route}: {'✅' if status else '❌'}")
    
    # Recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDATIONS")
    print('='*60)
    
    if not all(deps.values()):
        print("\n⚠️  Missing Dependencies:")
        for dep, status in deps.items():
            if not status:
                print(f"   - Install: pip install {dep}")
    
    if not all(utils.values()):
        print("\n⚠️  Utility Module Issues:")
        print("   - Check utils/ directory for syntax errors")
        print("   - Verify all imports in utils modules")
    
    if not all(route_results.values()):
        print("\n⚠️  Route Import Issues:")
        for route, status in route_results.items():
            if not status:
                print(f"   - Check api/{route}.py for errors")
                print(f"   - Verify all imports in {route}")
    
    if all(deps.values()) and all(utils.values()) and all(route_results.values()):
        print("\n✅ All checks passed! Routes should work correctly.")
    else:
        print("\n❌ Some checks failed. Fix the issues above and try again.")

