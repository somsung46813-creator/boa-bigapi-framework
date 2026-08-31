"""CPU Workflow Module - Controller Layer

Request routing and control flow management for the BOA framework.
"""

from typing import Any, Dict, Optional, Callable
from core.base import BaseComponent
from core.exceptions import ControllerError
import uuid
from datetime import datetime


class Controller(BaseComponent):
    """Controller component for request routing and management."""

    def __init__(self, controller_id: str = 'controller_01', config: Optional[Dict[str, Any]] = None):
        """Initialize Controller component.
        
        Args:
            controller_id: Unique identifier for the controller
            config: Optional configuration dictionary
        """
        super().__init__(controller_id, 'Controller', config)
        self.routes = {}
        self.middleware = []
        self.request_log = []
        self.handlers = {}

    def register_route(self, path: str, handler: Callable, methods: list = None) -> None:
        """Register a route handler.
        
        Args:
            path: Route path
            handler: Handler function
            methods: HTTP methods (GET, POST, etc.)
        """
        if methods is None:
            methods = ['GET', 'POST']
        
        self.routes[path] = {
            'handler': handler,
            'methods': methods,
            'created_at': datetime.now()
        }
        self._logger.info(f"Route registered: {path} [{', '.join(methods)}]")

    def add_middleware(self, middleware: Callable) -> None:
        """Add middleware function.
        
        Args:
            middleware: Middleware function to add
        """
        self.middleware.append(middleware)

    def route_request(self, path: str, method: str, data: Any = None) -> Any:
        """Route request to appropriate handler.
        
        Args:
            path: Request path
            method: HTTP method
            data: Request data
            
        Returns:
            Handler response
        """
        request_id = str(uuid.uuid4())
        
        if path not in self.routes:
            raise ControllerError(f"Route not found: {path}")
        
        route = self.routes[path]
        if method not in route['methods']:
            raise ControllerError(f"Method {method} not allowed for {path}")
        
        # Apply middleware
        current_data = data
        for mw in self.middleware:
            current_data = mw(current_data, path, method)
        
        # Call handler
        response = route['handler'](current_data)
        
        # Log request
        self.request_log.append({
            'request_id': request_id,
            'path': path,
            'method': method,
            'timestamp': datetime.now(),
            'status': 'success'
        })
        
        return response

    def process(self, data: Any) -> Any:
        """Process data through controller.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        if not self.is_active:
            return data
        return data

    def get_routes(self) -> Dict[str, Any]:
        """Get all registered routes.
        
        Returns:
            Dictionary of routes
        """
        return self.routes.copy()

    def get_request_log(self, limit: int = 100) -> list:
        """Get request log.
        
        Args:
            limit: Maximum number of log entries
            
        Returns:
            List of request log entries
        """
        return self.request_log[-limit:]
