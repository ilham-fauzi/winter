"""
Connection state management for Winter.
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any


class ConnectionState:
    """Manage connection state persistence."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.state_file = Path.home() / '.winter' / 'connection_state.json'
        self.config = config or {}
        self.timeout_minutes = self.config.get('connection_timeout', 300)  # Default 5 minutes
    
    def save_connection_state(self, client_info: Dict[str, Any], password: Optional[str] = None):
        """Save connection state to file."""
        state = {
            'connected': True,
            'connected_at': time.time(),
            'client_info': client_info,
            'last_activity': time.time(),
            'cached_password': password  # Cache password for session
        }
        
        # Ensure directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f)
        
        # Set secure permissions
        os.chmod(self.state_file, 0o600)
    
    def load_connection_state(self) -> Optional[Dict[str, Any]]:
        """Load connection state from file."""
        if not self.state_file.exists():
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            
            # Check if connection is still valid (not timed out)
            if not state.get('connected', False):
                return None
            
            # Check timeout using configured timeout
            last_activity = state.get('last_activity', 0)
            timeout_seconds = self.timeout_minutes * 60
            if time.time() - last_activity > timeout_seconds:
                self.clear_connection_state()
                return None
            
            return state
        except Exception:
            return None
    
    def update_activity(self):
        """Update last activity timestamp."""
        state = self.load_connection_state()
        if state:
            state['last_activity'] = time.time()
            self.save_connection_state(state['client_info'])
    
    def clear_connection_state(self):
        """Clear connection state."""
        if self.state_file.exists():
            self.state_file.unlink()
    
    def is_connected(self) -> bool:
        """Check if there's a valid connection state."""
        return self.load_connection_state() is not None
    
    def get_cached_password(self) -> Optional[str]:
        """Get cached password from connection state."""
        state = self.load_connection_state()
        if state:
            return state.get('cached_password')
        return None
    
    def clear_password_cache(self):
        """Clear cached password from connection state."""
        state = self.load_connection_state()
        if state:
            state['cached_password'] = None
            self.save_connection_state(state['client_info'], None)
