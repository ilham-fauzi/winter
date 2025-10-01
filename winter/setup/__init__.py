"""
Setup wizard for Winter configuration.
"""

import os
import yaml
import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm

console = Console()


def run_setup_wizard():
    """Interactive setup wizard for Winter."""
    console.print(Panel.fit(
        Text("❄️  Welcome to Winter - Snowflake Terminal Client!", style="bold blue"),
        title="Setup Wizard",
        border_style="blue"
    ))
    console.print("Let's set up your Snowflake connection...\n")
    
    # Check if config already exists
    config_dir = Path.home() / '.snowflake'
    config_file = config_dir / 'config.yaml'
    
    if config_file.exists():
        overwrite = Confirm.ask("Configuration already exists. Overwrite?", default=False)
        if not overwrite:
            console.print("❌ Setup cancelled")
            return
    
    # Collect configuration
    console.print("📝 Please provide the following information:")
    
    account = Prompt.ask("Snowflake account", default="abc12345.snowflakecomputing.com")
    user = Prompt.ask("Username")
    warehouse = Prompt.ask("Default warehouse name")
    database = Prompt.ask("Default database name")
    schema = Prompt.ask("Default schema", default="PUBLIC")
    role = Prompt.ask("Default role")
    table_prefix = Prompt.ask("Table prefix (optional)", default="")
    key_filename = Prompt.ask("Private key filename (without .p8 extension)", default="rsa_key")
    
    # Security level
    console.print("\n🔒 Security Level:")
    console.print("1. SELECT-only (Recommended for production)")
    console.print("2. All queries allowed (Development/Testing)")
    security_choice = Prompt.ask("Choose security level", choices=["1", "2"], default="1")
    security_level = security_choice == "2"
    
    # Create config directory
    config_dir.mkdir(exist_ok=True)
    
    # Handle key filename
    if not key_filename.endswith('.p8'):
        key_filename += '.p8'
    
    key_path = config_dir / key_filename
    
    # Ask for private key file
    console.print(f"\n🔑 Private Key File:")
    console.print(f"Please provide the path to your existing .p8 private key file.")
    console.print(f"It will be copied to: {key_path}")
    
    while True:
        key_file_path = Prompt.ask("Path to your .p8 private key file")
        
        if not key_file_path:
            console.print("❌ No key file provided")
            return
        
        source_key = Path(key_file_path)
        
        if not source_key.exists():
            console.print(f"❌ File not found: {source_key}")
            continue
        
        if not source_key.suffix == '.p8':
            console.print(f"❌ File must have .p8 extension: {source_key}")
            continue
        
        # Copy file to config directory
        try:
            shutil.copy2(source_key, key_path)
            console.print(f"✅ Copied key file to: {key_path}")
            break
        except Exception as e:
            console.print(f"❌ Failed to copy key file: {e}")
            return
    
    # Create config file
    config = {
        'account': account,
        'user': user,
        'private_key_path': str(key_path),
        'warehouse': warehouse,
        'database': database,
        'schema': schema,
        'role': role,
        'table_prefix': table_prefix,
        'security': {
            'allowed_all_query_types': security_level,
            'audit_logging': True
        }
    }
    
    # Save config file
    try:
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Set secure permissions
        os.chmod(config_file, 0o600)
        os.chmod(key_path, 0o600)
        
        console.print(f"\n✅ Configuration saved to: {config_file}")
        console.print(f"✅ Private key saved to: {key_path}")
        
        # Show next steps
        show_next_steps(account, user, key_path)
        
    except Exception as e:
        console.print(f"❌ Failed to save configuration: {e}")


def show_next_steps(account: str, user: str, key_path: Path):
    """Show next steps to user."""
    console.print("\n📋 Next Steps:")
    console.print("1. Generate public key from your private key:")
    console.print(f"   openssl rsa -in {key_path} -pubout -out {key_path.with_suffix('.pub')}")
    console.print("\n2. Copy your public key:")
    console.print(f"   cat {key_path.with_suffix('.pub')}")
    console.print("\n3. Add public key to Snowflake:")
    console.print(f"   ALTER USER {user} SET RSA_PUBLIC_KEY='<paste_public_key_here>';")
    console.print("\n4. Test your connection:")
    console.print("   winter test-connection")
    console.print("\n5. Start querying:")
    console.print("   winter query \"SELECT * FROM information_schema.tables LIMIT 5\"")


def generate_public_key(private_key_path: str) -> str:
    """Generate public key from private key using OpenSSL."""
    private_path = Path(private_key_path)
    public_path = private_path.with_suffix('.pub')
    
    # Use OpenSSL to extract public key
    cmd = [
        'openssl', 'rsa', 
        '-in', str(private_path),
        '-pubout',
        '-out', str(public_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return str(public_path)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"OpenSSL failed: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("OpenSSL not found. Please install OpenSSL or generate public key manually.")


def validate_config(config_path: str = None) -> bool:
    """Validate Winter configuration."""
    if config_path is None:
        config_path = os.path.expanduser("~/.snowflake/config.yaml")
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        console.print(f"❌ Config file not found: {config_path}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['account', 'user', 'private_key_path']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            console.print(f"❌ Missing required config fields: {missing_fields}")
            return False
        
        # Validate private key file
        key_path = Path(config['private_key_path']).expanduser()
        if not key_path.exists():
            console.print(f"❌ Private key file not found: {key_path}")
            return False
        
        if not key_path.suffix == '.p8':
            console.print(f"❌ Private key file must have .p8 extension: {key_path}")
            return False
        
        console.print("✅ Configuration is valid")
        return True
        
    except Exception as e:
        console.print(f"❌ Error validating config: {e}")
        return False


def show_config():
    """Show current configuration."""
    config_path = os.path.expanduser("~/.snowflake/config.yaml")
    config_file = Path(config_path)
    
    if not config_file.exists():
        console.print("❌ No configuration found. Run 'winter setup' to create one.")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        console.print(Panel.fit(
            yaml.dump(config, default_flow_style=False),
            title="Current Configuration",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"❌ Error reading config: {e}")


def reset_config():
    """Reset configuration."""
    config_dir = Path.home() / '.snowflake'
    
    if not config_dir.exists():
        console.print("❌ No configuration found.")
        return
    
    confirm = Confirm.ask("Are you sure you want to reset all configuration?", default=False)
    
    if confirm:
        try:
            import shutil
            shutil.rmtree(config_dir)
            console.print("✅ Configuration reset successfully")
        except Exception as e:
            console.print(f"❌ Error resetting config: {e}")
    else:
        console.print("❌ Reset cancelled")