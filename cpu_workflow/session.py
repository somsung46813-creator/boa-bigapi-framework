"""CPU Workflow Module - Session Layer

Session management and state persistence for the BOA framework.
"""

from typing import Any, Dict, Optional
from core.base import BaseComponent
from core.exceptions import SessionError
import json
import os
from datetime import datetime, timedelta
import pickle


class Session(BaseComponent):
    """Session component for state management."""

    def __init__(self, session_id: str = 'session_01', storage_path: str = '/tmp/boa_sessions', 
                 config: Optional[Dict[str, Any]] = None):
        """Initialize Session component.
        
        Args:
            session_id: Unique identifier for the session
            storage_path: Path for session storage
            config: Optional configuration dictionary
        """
        super().__init__(session_id, 'Session', config)
        self.storage_path = storage_path
        self.sessions = {}
        self.session_timeout = 3600  # 1 hour default
        self._ensure_storage_path()

    def _ensure_storage_path(self) -> None:
        """Ensure storage path exists."""
        os.makedirs(self.storage_path, exist_ok=True)

    def create_session(self, session_data: Optional[Dict[str, Any]] = None) -> str:
        """Create a new session.
        
        Args:
            session_data: Initial session data
            
        Returns:
            Session ID
        """
        session_id = f"sess_{datetime.now().timestamp()}"
        self.sessions[session_id] = {
            'data': session_data or {},
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'active': True
        }
        self._logger.info(f"Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data
        """
        if session_id not in self.sessions:
            raise SessionError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Check if expired
        if self._is_expired(session):
            self.destroy_session(session_id)
            raise SessionError(f"Session {session_id} expired")
        
        session['last_accessed'] = datetime.now()
        return session['data']

    def set_session_data(self, session_id: str, key: str, value: Any) -> None:
        """Set session data.
        
        Args:
            session_id: Session identifier
            key: Data key
            value: Data value
        """
        if session_id not in self.sessions:
            raise SessionError(f"Session {session_id} not found")
        
        self.sessions[session_id]['data'][key] = value
        self.sessions[session_id]['last_accessed'] = datetime.now()

    def destroy_session(self, session_id: str) -> None:
        """Destroy a session.
        
        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._logger.info(f"Session destroyed: {session_id}")

    def save_session(self, session_id: str) -> None:
        """Save session to disk.
        
        Args:
            session_id: Session identifier
        """
        if session_id not in self.sessions:
            raise SessionError(f"Session {session_id} not found")
        
        session_file = os.path.join(self.storage_path, f"{session_id}.pkl")
        with open(session_file, 'wb') as f:
            pickle.dump(self.sessions[session_id], f)

    def load_session(self, session_id: str) -> None:
        """Load session from disk.
        
        Args:
            session_id: Session identifier
        """
        session_file = os.path.join(self.storage_path, f"{session_id}.pkl")
        if not os.path.exists(session_file):
            raise SessionError(f"Session file {session_id} not found")
        
        with open(session_file, 'rb') as f:
            self.sessions[session_id] = pickle.load(f)

    def _is_expired(self, session: Dict[str, Any]) -> bool:
        """Check if session is expired.
        
        Args:
            session: Session object
            
        Returns:
            True if expired
        """
        age = (datetime.now() - session['last_accessed']).total_seconds()
        return age > self.session_timeout

    def process(self, data: Any) -> Any:
        """Process data through session layer.
        
        Args:
            data: Input data
            
        Returns:
            Processed data
        """
        if not self.is_active:
            return data
        return data
