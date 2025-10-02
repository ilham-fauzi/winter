"""
Utility functions for Winter.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load Winter configuration from YAML file."""
    if config_path is None:
        config_path = os.path.expanduser("~/.winter/config.yaml")
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please create config file with: winter setup"
        )
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate required fields
    required_fields = ['account', 'user', 'auth_method']
    missing_fields = [field for field in required_fields if field not in config]
    
    if missing_fields:
        raise ValueError(f"Missing required config fields: {missing_fields}")
    
    # Validate authentication method specific fields
    auth_method = config.get('auth_method')
    
    if auth_method == 'keypair':
        if 'private_key_path' not in config:
            raise ValueError("Missing private_key_path for keypair authentication")
        # Expand tilde in paths
        config['private_key_path'] = os.path.expanduser(config['private_key_path'])
    elif auth_method == 'password':
        # Password authentication - no additional validation needed
        pass
    else:
        raise ValueError(f"Invalid auth_method: {auth_method}. Must be 'password' or 'keypair'")
    
    return config


def save_config(config: Dict[str, Any], config_path: Optional[str] = None):
    """Save Winter configuration to YAML file."""
    if config_path is None:
        config_path = os.path.expanduser("~/.winter/config.yaml")
    
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    # Set secure permissions
    os.chmod(config_file, 0o600)


def validate_key_file(key_path: str) -> bool:
    """Validate private key file."""
    path = Path(key_path).expanduser()
    
    if not path.exists():
        raise FileNotFoundError(f"Private key file not found: {path}")
    
    if not path.suffix == '.p8':
        raise ValueError(f"Private key file must have .p8 extension: {path}")
    
    # Check file permissions
    stat = path.stat()
    if stat.st_mode & 0o777 > 0o600:
        print(f"⚠️  Warning: Private key file should have 600 permissions")
    
    return True
