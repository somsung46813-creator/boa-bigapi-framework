"""CPU Workflow Module - Grid Layer

Distributed grid computing framework for the BOA framework.
"""

from typing import Any, Dict, List, Optional, Callable
from core.base import BaseComponent
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed


class Grid(BaseComponent):
    """Grid component for distributed computing."""

    def __init__(self, grid_id: str = 'grid_01', num_workers: int = 4, config: Optional[Dict[str, Any]] = None):
        """Initialize Grid component.
        
        Args:
            grid_id: Unique identifier for the grid
            num_workers: Number of worker threads
            config: Optional configuration dictionary
        """
        super().__init__(grid_id, 'Grid', config)
        self.num_workers = num_workers
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.nodes = {}
        self.tasks = {}

    def add_node(self, node_id: str, processor: Callable) -> None:
        """Add a compute node to the grid.
        
        Args:
            node_id: Node identifier
            processor: Processing function for the node
        """
        self.nodes[node_id] = processor

    def submit_task(self, task_id: str, node_id: str, data: Any) -> None:
        """Submit a task to a grid node.
        
        Args:
            task_id: Unique task identifier
            node_id: Target node identifier
            data: Data to process
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")
            
        processor = self.nodes[node_id]
        future = self.executor.submit(processor, data)
        self.tasks[task_id] = future

    def get_result(self, task_id: str, timeout: float = None) -> Any:
        """Get result of a completed task.
        
        Args:
            task_id: Task identifier
            timeout: Timeout in seconds
            
        Returns:
            Task result
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
            
        return self.tasks[task_id].result(timeout=timeout)

    def distribute_data(self, data: List[Any], node_id: str) -> List[str]:
        """Distribute data across grid nodes.
        
        Args:
            data: List of data items
            node_id: Target node identifier
            
        Returns:
            List of task IDs
        """
        task_ids = []
        for i, item in enumerate(data):
            task_id = f"{node_id}_task_{i}"
            self.submit_task(task_id, node_id, item)
            task_ids.append(task_id)
        return task_ids

    def process(self, data: Any) -> Any:
        """Process data through the grid.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        if not self.is_active:
            return data
            
        # If multiple nodes, distribute the work
        if len(self.nodes) > 1 and isinstance(data, list):
            results = []
            node_ids = list(self.nodes.keys())
            for i, item in enumerate(data):
                node_id = node_ids[i % len(node_ids)]
                self.submit_task(f"grid_task_{i}", node_id, item)
                
            for i in range(len(data)):
                result = self.get_result(f"grid_task_{i}")
                results.append(result)
            return results
        else:
            # Single node processing
            if self.nodes:
                processor = list(self.nodes.values())[0]
                return processor(data)
        return data

    def shutdown(self) -> None:
        """Shutdown the grid executor."""
        self.executor.shutdown(wait=True)
        super().shutdown()
