"""CPU Workflow Module - Frame Layer

Frame-based processing with temporal management.
"""

from typing import Any, Dict, Optional, List
from core.base import BaseComponent
from datetime import datetime, timedelta


class Frame(BaseComponent):
    """Frame component for temporal data processing."""

    def __init__(self, frame_id: str = 'frame_01', frame_rate: int = 30, config: Optional[Dict[str, Any]] = None):
        """Initialize Frame component.
        
        Args:
            frame_id: Unique identifier for the frame manager
            frame_rate: Frames per second
            config: Optional configuration dictionary
        """
        super().__init__(frame_id, 'Frame', config)
        self.frame_rate = frame_rate
        self.frame_duration = 1.0 / frame_rate
        self.frames = {}
        self.current_frame_number = 0
        self.start_time = datetime.now()

    def create_frame(self, frame_data: Any) -> Dict[str, Any]:
        """Create a new frame.
        
        Args:
            frame_data: Data for the frame
            
        Returns:
            Frame information
        """
        frame = {
            'frame_number': self.current_frame_number,
            'timestamp': datetime.now(),
            'data': frame_data,
            'duration': self.frame_duration
        }
        
        self.frames[self.current_frame_number] = frame
        self.current_frame_number += 1
        
        return frame

    def get_frame(self, frame_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific frame.
        
        Args:
            frame_number: Frame number
            
        Returns:
            Frame data or None
        """
        return self.frames.get(frame_number)

    def get_frame_range(self, start: int, end: int) -> List[Dict[str, Any]]:
        """Get a range of frames.
        
        Args:
            start: Start frame number
            end: End frame number
            
        Returns:
            List of frames
        """
        return [self.frames[i] for i in range(start, end+1) if i in self.frames]

    def get_frames_by_time(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get frames within a time range.
        
        Args:
            start_time: Start time
            end_time: End time
            
        Returns:
            List of frames
        """
        return [f for f in self.frames.values() if start_time <= f['timestamp'] <= end_time]

    def process_frames(self, processor: callable) -> List[Any]:
        """Process all frames with a processor function.
        
        Args:
            processor: Processing function
            
        Returns:
            List of processed frame results
        """
        results = []
        for frame_num in sorted(self.frames.keys()):
            frame = self.frames[frame_num]
            result = processor(frame)
            results.append(result)
        return results

    def clear_frames(self) -> None:
        """Clear all frames."""
        self.frames.clear()
        self.current_frame_number = 0

    def get_statistics(self) -> Dict[str, Any]:
        """Get frame statistics.
        
        Returns:
            Statistics dictionary
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'total_frames': len(self.frames),
            'current_frame': self.current_frame_number,
            'frame_rate': self.frame_rate,
            'uptime_seconds': uptime,
            'average_fps': self.current_frame_number / uptime if uptime > 0 else 0
        }

    def process(self, data: Any) -> Any:
        """Process data through frame layer.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        if not self.is_active:
            return data
        return self.create_frame(data)
