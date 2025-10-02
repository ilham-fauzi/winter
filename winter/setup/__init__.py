"""
Setup wizard for Winter configuration.
"""

import os
import yaml
import shutil
import subprocess
import getpass
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
    config_dir = Path.home() / '.winter'
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
    
    # Connection timeout configuration
    console.print("\n⏰ Connection Timeout Configuration:")
    console.print("1. Minutes")
    console.print("2. Hours")
    timeout_unit_choice = Prompt.ask("Choose timeout unit", choices=["1", "2"], default="1")
    
    if timeout_unit_choice == "2":
        timeout_value = Prompt.ask("Connection timeout (hours)", default="1")
        try:
            timeout_minutes = int(timeout_value) * 60
        except ValueError:
            timeout_minutes = 60
            console.print("⚠️  Invalid input, using default 1 hour (60 minutes)")
    else:
        timeout_value = Prompt.ask("Connection timeout (minutes)", default="5")
        try:
            timeout_minutes = int(timeout_value)
        except ValueError:
            timeout_minutes = 5
            console.print("⚠️  Invalid input, using default 5 minutes")
    
    # Authentication method selection
    console.print("\n🔐 Authentication Method:")
    console.print("1. Password Authentication (Username + Password)")
    console.print("2. RSA Keypair Authentication (Username + Private Key)")
    auth_choice = Prompt.ask("Choose authentication method", choices=["1", "2"], default="2")
    
    # Initialize config with common fields
    config = {
        'account': account,
        'user': user,
        'warehouse': warehouse,
        'database': database,
        'schema': schema,
        'role': role,
        'table_prefix': table_prefix,
        'connection_timeout': timeout_minutes,  # Use configured timeout
        'security': {
            'allowed_all_query_types': False,  # SELECT-only enforced for security
            'audit_logging': True
        }
    }
    
    # Handle authentication method
    if auth_choice == "1":
        # Password authentication
        console.print("\n🔑 Password Authentication:")
        password = getpass.getpass("Password: ")
        config['password'] = password
        config['auth_method'] = 'password'
        
        # Ask if they want to store password (not recommended for production)
        store_password = Confirm.ask("Store password in config file? (Not recommended for security)", default=False)
        if not store_password:
            config['password'] = None  # Will prompt for password each time
            console.print("⚠️  Password will be prompted for each connection")
        
    else:
        # RSA Keypair authentication
        console.print("\n🔑 RSA Keypair Authentication:")
        
        # Ask if user wants to browse for file or enter path manually
        console.print("1. Browse for .p8 file (Recommended)")
        console.print("2. Enter file path manually")
        browse_choice = Prompt.ask("Choose option", choices=["1", "2"], default="1")
        
        if browse_choice == "1":
            # Use file browser
            from winter.file_browser import browse_and_copy_p8_file
            
            console.print("🔍 Opening file browser...")
            key_path = browse_and_copy_p8_file(config_dir)
            
            if not key_path:
                console.print("❌ No file selected. Setup cancelled.")
                return
            
            config['private_key_path'] = key_path
            config['auth_method'] = 'keypair'
            
        else:
            # Manual path entry (existing logic)
            key_filename = Prompt.ask("Private key filename (without .p8 extension)", default="rsa_key")
            
            # Create config directory
            config_dir.mkdir(exist_ok=True)
            
            # Handle key filename
            if not key_filename.endswith('.p8'):
                key_filename += '.p8'
            
            key_path = config_dir / key_filename
            
            # Ask for private key file
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
            
            config['private_key_path'] = str(key_path)
            config['auth_method'] = 'keypair'
    
    # Security is always SELECT-only for safety
    console.print("\n🔒 Security Configuration:")
    console.print("✅ SELECT-only queries enforced for security")
    console.print("🛡️  This prevents accidental data modification")
    
    # Save config file
    try:
        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        # Set secure permissions
        os.chmod(config_file, 0o600)
        
        console.print(f"\n✅ Configuration saved to: {config_file}")
        
        if config['auth_method'] == 'keypair':
            os.chmod(key_path, 0o600)
            console.print(f"✅ Private key saved to: {key_path}")
        
        # Show next steps based on authentication method
        show_next_steps(account, user, config)
        
    except Exception as e:
        console.print(f"❌ Failed to save configuration: {e}")


def show_next_steps(account: str, user: str, config: dict):
    """Show next steps to user based on authentication method."""
    console.print("\n📋 Next Steps:")
    
    # Show security info
    console.print("🔒 Security: SELECT-only queries enforced")
    console.print("🛡️  This prevents accidental data modification")
    
    if config['auth_method'] == 'keypair':
        key_path = Path(config['private_key_path'])
        console.print("\n1. Generate public key from your private key:")
        console.print(f"   openssl rsa -in {key_path} -pubout -out {key_path.with_suffix('.pub')}")
        console.print("\n2. Copy your public key:")
        console.print(f"   cat {key_path.with_suffix('.pub')}")
        console.print("\n3. Add public key to Snowflake:")
        console.print(f"   ALTER USER {user} SET RSA_PUBLIC_KEY='<paste_public_key_here>';")
    else:
        console.print("\n1. Password authentication is ready to use")
        if config.get('password') is None:
            console.print("   (Password will be prompted for each connection)")
    
    console.print(f"\n4. Connect to Snowflake:")
    console.print("   winter connect")
    console.print("\n5. Test your connection:")
    console.print("   winter test-connection")
    console.print("\n6. Start querying:")
    console.print("   winter execute-query \"SELECT * FROM information_schema.tables LIMIT 5\"")
    console.print("\n💡 Note: You must run 'winter connect' before executing queries")


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
        config_path = os.path.expanduser("~/.winter/config.yaml")
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        console.print(f"❌ Config file not found: {config_path}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['account', 'user', 'auth_method']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            console.print(f"❌ Missing required config fields: {missing_fields}")
            return False
        
        # Validate authentication method specific fields
        auth_method = config.get('auth_method')
        
        if auth_method == 'keypair':
            if 'private_key_path' not in config:
                console.print("❌ Missing private_key_path for keypair authentication")
                return False
            
            # Validate private key file
            key_path = Path(config['private_key_path']).expanduser()
            if not key_path.exists():
                console.print(f"❌ Private key file not found: {key_path}")
                return False
            
            if not key_path.suffix == '.p8':
                console.print(f"❌ Private key file must have .p8 extension: {key_path}")
                return False
                
        elif auth_method == 'password':
            # Password authentication - no additional file validation needed
            if config.get('password') is None:
                console.print("ℹ️  Password will be prompted for each connection")
        else:
            console.print(f"❌ Invalid auth_method: {auth_method}. Must be 'password' or 'keypair'")
            return False
        
        console.print("✅ Configuration is valid")
        return True
        
    except Exception as e:
        console.print(f"❌ Error validating config: {e}")
        return False


def show_config():
    """Show current configuration."""
    config_path = os.path.expanduser("~/.winter/config.yaml")
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
    config_dir = Path.home() / '.winter'
    
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