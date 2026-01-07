"""Application Bootstrap - Initialize EspoCRM-inspired architecture"""
from core.module import module_registry
from modules.clients import ClientsModule
from modules.trainers import TrainersModule
from modules.sessions import SessionsModule

def bootstrap_application():
    """
    Bootstrap the application with EspoCRM-inspired architecture.
    This should be called when the application starts.
    """
    # Register all modules
    module_registry.register(ClientsModule())
    module_registry.register(TrainersModule())
    module_registry.register(SessionsModule())
    
    # Initialize all modules in correct dependency order
    module_registry.initialize_all()
    
    print("Application bootstrapped successfully!")
    print(f"Loaded modules: {', '.join(module_registry.get_load_order())}")

if __name__ == '__main__':
    bootstrap_application()
