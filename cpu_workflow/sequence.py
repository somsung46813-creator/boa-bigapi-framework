"""CPU Workflow Module - Sequence Layer

Sequential operation processing and orchestration.
"""

from typing import Any, Dict, List, Optional, Callable
from core.base import BaseComponent
from core.exceptions import ProcessingError
from datetime import datetime


class Sequence(BaseComponent):
    """Sequence component for operation orchestration."""

    def __init__(self, sequence_id: str = 'sequence_01', config: Optional[Dict[str, Any]] = None):
        """Initialize Sequence component.
        
        Args:
            sequence_id: Unique identifier for the sequence
            config: Optional configuration dictionary
        """
        super().__init__(sequence_id, 'Sequence', config)
        self.operations = []
        self.execution_history = []
        self.current_step = 0

    def add_operation(self, operation_id: str, func: Callable, params: Optional[Dict[str, Any]] = None) -> None:
        """Add an operation to the sequence.
        
        Args:
            operation_id: Operation identifier
            func: Operation function
            params: Operation parameters
        """
        self.operations.append({
            'id': operation_id,
            'func': func,
            'params': params or {},
            'added_at': datetime.now()
        })

    def execute_sequence(self, initial_data: Any = None) -> Any:
        """Execute the sequence of operations.
        
        Args:
            initial_data: Initial data to process
            
        Returns:
            Final result
        """
        current_data = initial_data
        self.current_step = 0
        
        for operation in self.operations:
            try:
                self.current_step += 1
                result = operation['func'](current_data, **operation['params'])
                
                self.execution_history.append({
                    'operation_id': operation['id'],
                    'step': self.current_step,
                    'timestamp': datetime.now(),
                    'status': 'success'
                })
                
                current_data = result
            except Exception as e:
                self.execution_history.append({
                    'operation_id': operation['id'],
                    'step': self.current_step,
                    'timestamp': datetime.now(),
                    'status': 'failed',
                    'error': str(e)
                })
                raise ProcessingError(f"Operation {operation['id']} failed: {e}")
        
        return current_data

    def skip_operation(self, step: int) -> None:
        """Skip an operation.
        
        Args:
            step: Step number to skip
        """
        if 0 <= step < len(self.operations):
            self.operations[step]['skipped'] = True

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history.
        
        Returns:
            List of execution records
        """
        return self.execution_history.copy()

    def reset_sequence(self) -> None:
        """Reset sequence state."""
        self.current_step = 0
        self.execution_history = []

    def process(self, data: Any) -> Any:
        """Process data through sequence.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        if not self.is_active:
            return data
        return self.execute_sequence(data)
