"""Base classes for BOA Framework components."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseComponent(ABC):
    """Base class for all BOA framework components."""

    def __init__(self, component_id: str, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize a BOA component.
        
        Args:
            component_id: Unique identifier for the component
            name: Human-readable name for the component
            config: Optional configuration dictionary
        """
        self.component_id = component_id
        self.name = name
        self.config = config or {}
        self.created_at = datetime.now()
        self.is_active = False
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def initialize(self) -> None:
        """Initialize the component."""
        self.is_active = True
        self._logger.info(f"Component {self.name} ({self.component_id}) initialized")

    def shutdown(self) -> None:
        """Shutdown the component."""
        self.is_active = False
        self._logger.info(f"Component {self.name} ({self.component_id}) shutdown")

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process data through the component.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed data
        """
        pass

    def get_status(self) -> Dict[str, Any]:
        """Get component status.
        
        Returns:
            Dictionary with component status information
        """
        return {
            'component_id': self.component_id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'uptime_seconds': (datetime.now() - self.created_at).total_seconds()
        }


class BaseWorkflow(ABC):
    """Base class for BOA workflow pipelines."""

    def __init__(self, workflow_id: str, name: str):
        """Initialize a workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Human-readable name for the workflow
        """
        self.workflow_id = workflow_id
        self.name = name
        self.components = {}
        self.sequence = []
        self.created_at = datetime.now()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def register_component(self, component: BaseComponent) -> None:
        """Register a component in the workflow.
        
        Args:
            component: Component to register
        """
        self.components[component.component_id] = component
        self._logger.info(f"Component {component.name} registered in workflow {self.name}")

    def set_sequence(self, component_ids: list) -> None:
        """Set the execution sequence for components.
        
        Args:
            component_ids: List of component IDs in execution order
        """
        self.sequence = component_ids
        self._logger.info(f"Workflow {self.name} sequence set: {' -> '.join(component_ids)}")

    def execute(self, data: Any) -> Any:
        """Execute the workflow with the given data.
        
        Args:
            data: Input data for the workflow
            
        Returns:
            Final processed data
        """
        current_data = data
        for component_id in self.sequence:
            component = self.components.get(component_id)
            if component and component.is_active:
                current_data = component.process(current_data)
                self._logger.debug(f"Component {component_id} processed data")
        return current_data

    def get_status(self) -> Dict[str, Any]:
        """Get workflow status.
        
        Returns:
            Dictionary with workflow status information
        """
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'components_count': len(self.components),
            'sequence': self.sequence,
            'created_at': self.created_at.isoformat(),
            'component_statuses': {cid: self.components[cid].get_status() for cid in self.components}
        }


class BaseProcessor(ABC):
    """Base class for data processors."""

    def __init__(self, processor_id: str, name: str):
        """Initialize a processor.
        
        Args:
            processor_id: Unique identifier for the processor
            name: Human-readable name for the processor
        """
        self.processor_id = processor_id
        self.name = name
        self.input_count = 0
        self.output_count = 0
        self.error_count = 0
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Process data.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        pass

    def increment_input(self) -> None:
        """Increment input counter."""
        self.input_count += 1

    def increment_output(self) -> None:
        """Increment output counter."""
        self.output_count += 1

    def increment_error(self) -> None:
        """Increment error counter."""
        self.error_count += 1

    def get_stats(self) -> Dict[str, int]:
        """Get processor statistics.
        
        Returns:
            Dictionary with processor statistics
        """
        return {
            'processor_id': self.processor_id,
            'name': self.name,
            'input_count': self.input_count,
            'output_count': self.output_count,
            'error_count': self.error_count,
            'success_rate': (self.output_count / self.input_count * 100) if self.input_count > 0 else 0
        }
