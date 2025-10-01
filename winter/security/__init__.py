"""
Security controls and permission validation for Winter.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for Winter."""
    RESTRICTED = "restricted"  # SELECT only
    STANDARD = "standard"     # SELECT + some safe operations
    PERMISSIVE = "permissive" # All operations allowed


class AuditEventType(Enum):
    """Types of audit events."""
    QUERY_EXECUTED = "query_executed"
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_CLOSED = "connection_closed"
    CONFIGURATION_CHANGED = "configuration_changed"
    SECURITY_VIOLATION = "security_violation"
    LOGIN_ATTEMPT = "login_attempt"
    PERMISSION_DENIED = "permission_denied"


@dataclass
class AuditEvent:
    """Represents an audit event."""
    timestamp: datetime
    event_type: AuditEventType
    user: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    allowed_query_types: List[str]
    max_query_length: int = 10000
    max_results_limit: int = 1000
    session_timeout_minutes: int = 60
    require_connection_validation: bool = True
    audit_logging_enabled: bool = True
    block_dangerous_functions: bool = True
    allowed_schemas: Optional[List[str]] = None
    blocked_schemas: Optional[List[str]] = None


class SecurityManager:
    """Manages security policies and audit logging."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.audit_log_path = Path.home() / '.snowflake' / 'audit.log'
        self.security_log_path = Path.home() / '.snowflake' / 'security.log'
        self.session_start_time = None
        self.session_id = None
        
        # Initialize security policy
        self.policy = self._load_security_policy()
        
        # Ensure log directories exist
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_security_policy(self) -> SecurityPolicy:
        """Load security policy from configuration."""
        security_config = self.config.get('security', {})
        
        # Determine allowed query types
        if security_config.get('allowed_all_query_types', False):
            allowed_query_types = [
                'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 
                'ALTER', 'TRUNCATE', 'MERGE', 'CALL', 'SHOW', 'DESCRIBE', 'EXPLAIN'
            ]
        else:
            allowed_query_types = ['SELECT']
        
        return SecurityPolicy(
            allowed_query_types=allowed_query_types,
            max_query_length=security_config.get('max_query_length', 10000),
            max_results_limit=security_config.get('max_results_limit', 1000),
            session_timeout_minutes=security_config.get('session_timeout_minutes', 60),
            require_connection_validation=security_config.get('require_connection_validation', True),
            audit_logging_enabled=security_config.get('audit_logging', True),
            block_dangerous_functions=security_config.get('block_dangerous_functions', True),
            allowed_schemas=security_config.get('allowed_schemas'),
            blocked_schemas=security_config.get('blocked_schemas')
        )
    
    def start_session(self, user: str, ip_address: Optional[str] = None) -> str:
        """Start a new security session."""
        self.session_id = f"{user}_{int(time.time())}"
        self.session_start_time = datetime.now()
        
        self.log_audit_event(
            AuditEventType.LOGIN_ATTEMPT,
            user,
            {"action": "session_started", "session_id": self.session_id},
            ip_address
        )
        
        return self.session_id
    
    def end_session(self, user: str):
        """End the current security session."""
        if self.session_start_time:
            session_duration = datetime.now() - self.session_start_time
            
            self.log_audit_event(
                AuditEventType.CONNECTION_CLOSED,
                user,
                {
                    "action": "session_ended",
                    "session_id": self.session_id,
                    "duration_seconds": session_duration.total_seconds()
                }
            )
        
        self.session_id = None
        self.session_start_time = None
    
    def validate_query(self, query: str, user: str) -> Tuple[bool, str]:
        """Validate query against security policy."""
        # Check query length
        if len(query) > self.policy.max_query_length:
            self.log_security_violation(
                user,
                "query_too_long",
                {"query_length": len(query), "max_length": self.policy.max_query_length}
            )
            return False, f"Query too long. Maximum length: {self.policy.max_query_length}"
        
        # Check for dangerous functions
        if self.policy.block_dangerous_functions:
            dangerous_functions = [
                'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE'
            ]
            query_upper = query.upper()
            for func in dangerous_functions:
                if func in query_upper and func not in self.policy.allowed_query_types:
                    self.log_security_violation(
                        user,
                        "dangerous_function_blocked",
                        {"function": func, "query": query[:100]}
                    )
                    return False, f"Dangerous function '{func}' not allowed in current security mode"
        
        # Check schema access
        schema_check = self._check_schema_access(query, user)
        if not schema_check[0]:
            return schema_check
        
        return True, "Query validation passed"
    
    def _check_schema_access(self, query: str, user: str) -> Tuple[bool, str]:
        """Check if user has access to schemas referenced in query."""
        # This is a simplified check - in production, you'd parse the query properly
        query_upper = query.upper()
        
        # Check blocked schemas first (higher priority)
        if self.policy.blocked_schemas:
            for schema in self.policy.blocked_schemas:
                if f"{schema.upper()}." in query_upper:
                    self.log_security_violation(
                        user,
                        "blocked_schema_access",
                        {"schema": schema, "query": query[:100]}
                    )
                    return False, f"Access to schema '{schema}' is blocked"
        
        # Check allowed schemas (if specified)
        if self.policy.allowed_schemas:
            # Extract schema references from query (simplified)
            import re
            schema_pattern = r'\b(\w+)\.\w+\b'
            schemas_in_query = re.findall(schema_pattern, query_upper)
            
            for schema in schemas_in_query:
                if schema not in [s.upper() for s in self.policy.allowed_schemas]:
                    self.log_security_violation(
                        user,
                        "unauthorized_schema_access",
                        {"schema": schema, "query": query[:100]}
                    )
                    return False, f"Access to schema '{schema}' is not authorized"
        
        return True, "Schema access check passed"
    
    def log_audit_event(self, event_type: AuditEventType, user: str, details: Dict[str, Any], 
                       ip_address: Optional[str] = None):
        """Log an audit event."""
        if not self.policy.audit_logging_enabled:
            return
        
        event = AuditEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            user=user,
            details=details,
            ip_address=ip_address,
            session_id=self.session_id
        )
        
        try:
            with open(self.audit_log_path, 'a') as f:
                log_entry = {
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type.value,
                    'user': event.user,
                    'details': event.details,
                    'ip_address': event.ip_address,
                    'session_id': event.session_id
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def log_security_violation(self, user: str, violation_type: str, details: Dict[str, Any]):
        """Log a security violation."""
        self.log_audit_event(
            AuditEventType.SECURITY_VIOLATION,
            user,
            {
                "violation_type": violation_type,
                **details
            }
        )
        
        # Also log to security log
        try:
            with open(self.security_log_path, 'a') as f:
                violation_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'user': user,
                    'violation_type': violation_type,
                    'details': details,
                    'session_id': self.session_id
                }
                f.write(json.dumps(violation_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write security log: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        return {
            'policy': asdict(self.policy),
            'session_active': self.session_id is not None,
            'session_id': self.session_id,
            'session_start_time': self.session_start_time.isoformat() if self.session_start_time else None,
            'audit_logging_enabled': self.policy.audit_logging_enabled,
            'security_level': self._get_security_level()
        }
    
    def _get_security_level(self) -> str:
        """Determine current security level."""
        if len(self.policy.allowed_query_types) == 1 and 'SELECT' in self.policy.allowed_query_types:
            return SecurityLevel.RESTRICTED.value
        elif len(self.policy.allowed_query_types) <= 5:
            return SecurityLevel.STANDARD.value
        else:
            return SecurityLevel.PERMISSIVE.value
    
    def get_audit_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get audit summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        events = []
        violations = []
        
        try:
            # Read audit log
            if self.audit_log_path.exists():
                with open(self.audit_log_path, 'r') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            event_time = datetime.fromisoformat(event['timestamp'])
                            if event_time >= cutoff_time:
                                events.append(event)
                                if event['event_type'] == 'security_violation':
                                    violations.append(event)
                        except (json.JSONDecodeError, KeyError, ValueError):
                            continue
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
        
        return {
            'period_hours': hours,
            'total_events': len(events),
            'security_violations': len(violations),
            'events_by_type': self._count_events_by_type(events),
            'recent_violations': violations[-10:] if violations else []
        }
    
    def _count_events_by_type(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count events by type."""
        counts = {}
        for event in events:
            event_type = event.get('event_type', 'unknown')
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts


class PermissionManager:
    """Manages user permissions and access control."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.user_permissions = self._load_user_permissions()
    
    def _load_user_permissions(self) -> Dict[str, Dict[str, Any]]:
        """Load user permissions from configuration."""
        # In a real implementation, this would load from a database or config file
        # For now, we'll use the main config
        user = self.config.get('user', 'default_user')
        
        return {
            user: {
                'allowed_query_types': self.config.get('security', {}).get('allowed_all_query_types', False),
                'max_query_length': self.config.get('security', {}).get('max_query_length', 10000),
                'max_results_limit': self.config.get('security', {}).get('max_results_limit', 1000),
                'allowed_schemas': self.config.get('security', {}).get('allowed_schemas'),
                'blocked_schemas': self.config.get('security', {}).get('blocked_schemas')
            }
        }
    
    def check_permission(self, user: str, permission: str) -> bool:
        """Check if user has a specific permission."""
        user_perms = self.user_permissions.get(user, {})
        
        if permission == 'execute_query':
            return True  # All users can execute queries (with restrictions)
        elif permission == 'all_query_types':
            return user_perms.get('allowed_query_types', False)
        elif permission == 'audit_logs':
            return True  # All users can view their own audit logs
        elif permission == 'security_settings':
            return False  # Only admins can change security settings
        
        return False
    
    def get_user_permissions(self, user: str) -> Dict[str, Any]:
        """Get all permissions for a user."""
        return self.user_permissions.get(user, {})