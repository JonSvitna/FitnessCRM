"""Module system for organizing features"""
from typing import Dict, List, Optional, Callable
from abc import ABC, abstractmethod

class Module(ABC):
    """
    Base module class.
    Modules organize features and can define entities, routes, etc.
    """
    
    def __init__(self, name: str):
        """
        Initialize module.
        
        Args:
            name: Module name
        """
        self.name = name
        self.dependencies = []
        self.entities = []
        self.routes = []
    
    @abstractmethod
    def initialize(self):
        """Initialize module - must be implemented by subclasses"""
        pass
    
    def register_entity(self, entity_class):
        """Register an entity with this module"""
        self.entities.append(entity_class)
    
    def register_route(self, route_blueprint):
        """Register a route blueprint with this module"""
        self.routes.append(route_blueprint)
    
    def get_dependencies(self) -> List[str]:
        """Get module dependencies"""
        return self.dependencies
    
    def get_entities(self) -> List:
        """Get module entities"""
        return self.entities
    
    def get_routes(self) -> List:
        """Get module routes"""
        return self.routes


class ModuleRegistry:
    """
    Registry for managing modules.
    Similar to EspoCRM's module system.
    """
    
    def __init__(self):
        """Initialize module registry"""
        self._modules = {}
        self._load_order = []
    
    def register(self, module: Module):
        """
        Register a module.
        
        Args:
            module: Module instance
        """
        self._modules[module.name] = module
        self._calculate_load_order()
    
    def get(self, name: str) -> Optional[Module]:
        """
        Get a module by name.
        
        Args:
            name: Module name
            
        Returns:
            Module instance or None
        """
        return self._modules.get(name)
    
    def get_all(self) -> Dict[str, Module]:
        """Get all modules"""
        return self._modules
    
    def get_load_order(self) -> List[str]:
        """Get module load order based on dependencies"""
        return self._load_order
    
    def _calculate_load_order(self):
        """Calculate module load order using topological sort"""
        # Simple topological sort
        visited = set()
        temp_mark = set()
        order = []
        
        def visit(module_name):
            if module_name in visited:
                return
            if module_name in temp_mark:
                raise ValueError(f"Circular dependency detected: {module_name}")
            
            temp_mark.add(module_name)
            
            module = self._modules.get(module_name)
            if module:
                for dep in module.get_dependencies():
                    if dep in self._modules:
                        visit(dep)
            
            temp_mark.remove(module_name)
            visited.add(module_name)
            order.append(module_name)
        
        for module_name in self._modules.keys():
            if module_name not in visited:
                visit(module_name)
        
        self._load_order = order
    
    def initialize_all(self):
        """Initialize all modules in correct order"""
        for module_name in self._load_order:
            module = self._modules.get(module_name)
            if module:
                module.initialize()


# Global module registry instance
module_registry = ModuleRegistry()
