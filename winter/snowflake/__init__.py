"""
Snowflake connection and query execution.
"""

import snowflake.connector
import time
import logging
import getpass
from cryptography.hazmat.primitives import serialization
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()
logger = logging.getLogger(__name__)


class SnowflakeClient:
    """Snowflake client for connection and query execution."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self.is_connected = False
        self.connection_pool = []
        self.max_pool_size = 5
        self.last_activity = None
        self.connection_timeout = config.get('connection_timeout', 5)  # 5 minutes default
    
    def connect(self, retry_count: int = 3, retry_delay: int = 2) -> snowflake.connector.SnowflakeConnection:
        """Establish connection to Snowflake with retry mechanism."""
        for attempt in range(retry_count):
            try:
                console.print(f"🔌 Connecting to Snowflake (attempt {attempt + 1}/{retry_count})...")
                
                # Normalize account format
                normalized_account = self._normalize_account(self.config['account'])
                
                # Prepare connection parameters based on authentication method
                connection_params = {
                    'account': normalized_account,
                    'user': self.config['user'],
                    'warehouse': self.config['warehouse'],
                    'database': self.config['database'],
                    'schema': self.config['schema'],
                    'role': self.config['role'],
                    # Connection options for better stability
                    'timeout': 30,
                    'login_timeout': 30,
                    'insecure_mode': True,  # Disable SSL certificate validation
                    'network_timeout': self.connection_timeout * 60,  # Convert minutes to seconds
                    'query_timeout': 0,  # Unlimited query timeout
                    # Application identification
                    'application': 'Winter-Terminal-Client'
                }
                
                # Add authentication based on method
                auth_method = self.config.get('auth_method', 'keypair')
                
                if auth_method == 'keypair':
                    # Load private key for keypair authentication
                    private_key = self._load_private_key()
                    connection_params['private_key'] = private_key
                elif auth_method == 'password':
                    # Use password authentication
                    password = self.config.get('password')
                    if password is None:
                        # Prompt for password if not stored
                        password = getpass.getpass("Password: ")
                    connection_params['password'] = password
                else:
                    raise ValueError(f"Invalid auth_method: {auth_method}")
                
                # Establish connection
                self.connection = snowflake.connector.connect(**connection_params)
                
                self.is_connected = True
                self.last_activity = time.time()
                console.print("✅ Successfully connected to Snowflake!")
                
                # Test connection with simple query
                self._test_connection()
                
                return self.connection
                
            except Exception as e:
                console.print(f"❌ Connection attempt {attempt + 1} failed: {e}")
                
                if attempt < retry_count - 1:
                    console.print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    console.print("❌ All connection attempts failed")
                    raise ConnectionError(f"Failed to connect to Snowflake after {retry_count} attempts: {e}")
    
    def _normalize_account(self, account: str) -> str:
        """Normalize account format for Snowflake connection."""
        if not account:
            return account
        
        # Remove .snowflakecomputing.com if present
        if account.endswith('.snowflakecomputing.com'):
            account = account[:-len('.snowflakecomputing.com')]
        
        # Trim whitespace
        account = account.strip()
        
        console.print(f"🔧 Normalized account: {account}")
        return account
    
    def _load_private_key(self):
        """Load private key from file (supports all RSA key formats)."""
        try:
            key_path = self.config['private_key_path']
            key_file_path = Path(key_path)
            
            # Check file extension
            supported_extensions = {'.p8', '.pem', '.key', '.rsa', '.pkcs8', '.der', '.crt', '.cer', '.p12', '.pfx'}
            if key_file_path.suffix.lower() not in supported_extensions:
                raise ValueError(f"Unsupported key file extension: {key_file_path.suffix}. Supported: {', '.join(sorted(supported_extensions))}")
            
            # Handle different file formats
            if key_file_path.suffix.lower() in {'.der', '.p12', '.pfx'}:
                # Binary formats - read as binary
                with open(key_path, 'rb') as key_file:
                    private_key_content = key_file.read()
                
                # Try to load as DER format
                try:
                    private_key = serialization.load_der_private_key(
                        private_key_content,
                        password=self.config.get('private_key_passphrase', None)
                    )
                except Exception:
                    # Try PKCS#12 format
                    try:
                        from cryptography.hazmat.primitives import serialization as pkcs12_serialization
                        private_key = pkcs12_serialization.load_pkcs12(
                            private_key_content,
                            password=self.config.get('private_key_passphrase', None)
                        ).key
                    except Exception as e:
                        raise ValueError(f"Failed to load binary key format: {e}")
            else:
                # Text formats - read as text
                with open(key_path, 'r') as key_file:
                    private_key_content = key_file.read()
                
                # Validate that it's a valid private key format
                if not any(marker in private_key_content for marker in [
                    'BEGIN PRIVATE KEY', 'BEGIN RSA PRIVATE KEY', 'BEGIN EC PRIVATE KEY',
                    'BEGIN ENCRYPTED PRIVATE KEY', '-----BEGIN'
                ]):
                    raise ValueError(f"Invalid private key format in {key_path}. Expected PEM format.")
                
                # Load the private key using cryptography
                private_key = serialization.load_pem_private_key(
                    private_key_content.encode('utf-8'),
                    password=self.config.get('private_key_passphrase', None)
                )
            
            return private_key
        except Exception as e:
            raise ValueError(f"Failed to load private key from {self.config['private_key_path']}: {e}")
    
    def _test_connection(self):
        """Test connection with a simple query."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            console.print(f"📊 Snowflake version: {version}")
            cursor.close()
        except Exception as e:
            console.print(f"⚠️  Connection test failed: {e}")
    
    def _is_connection_valid(self) -> bool:
        """Check if connection is still alive and not timed out."""
        if not self.is_connected or not self.connection:
            return False
        
        # Check if connection has timed out
        if self.last_activity is not None:
            time_since_activity = time.time() - self.last_activity
            timeout_seconds = self.connection_timeout * 60  # Convert minutes to seconds
            if time_since_activity > timeout_seconds:
                console.print(f"⏰ Connection timed out after {self.connection_timeout} minutes of inactivity")
                self.is_connected = False
                return False
        
        # Check if connection is still alive
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except:
            self.is_connected = False
            return False
    
    def execute_query(self, query: str, fetch_all: bool = True) -> List[tuple]:
        """Execute SQL query and return results."""
        # Check if connection is still alive and not timed out
        if not self._is_connection_valid():
            raise ConnectionError("Connection expired or lost. Run 'winter connect' first.")
        
        try:
            cursor = self.connection.cursor()
            console.print(f"🔍 Executing query: {query[:50]}{'...' if len(query) > 50 else ''}")
            
            start_time = time.time()
            cursor.execute(query)
            
            # Update last activity time
            self.last_activity = time.time()
            
            if fetch_all:
                results = cursor.fetchall()
                execution_time = time.time() - start_time
                console.print(f"✅ Query executed successfully in {execution_time:.2f}s")
                console.print(f"📊 Rows returned: {len(results)}")
                return results
            else:
                # Return cursor for streaming results
                return cursor
                
        except Exception as e:
            console.print(f"❌ Query execution failed: {e}")
            raise
    
    def execute_query_with_columns(self, query: str) -> Tuple[List[str], List[tuple]]:
        """Execute query and return columns and results."""
        # Check if connection is still alive and not timed out
        if not self._is_connection_valid():
            raise ConnectionError("Connection expired or lost. Run 'winter connect' first.")
        
        try:
            cursor = self.connection.cursor()
            console.print(f"🔍 Executing query: {query[:50]}{'...' if len(query) > 50 else ''}")
            
            start_time = time.time()
            cursor.execute(query)
            
            # Update last activity time
            self.last_activity = time.time()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Get results
            results = cursor.fetchall()
            execution_time = time.time() - start_time
            
            console.print(f"✅ Query executed successfully in {execution_time:.2f}s")
            console.print(f"📊 Rows returned: {len(results)}")
            
            return columns, results
            
        except Exception as e:
            console.print(f"❌ Query execution failed: {e}")
            raise
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information."""
        if not self.is_connected or not self.connection:
            return {"status": "disconnected"}
        
        try:
            cursor = self.connection.cursor()
            
            # Get connection details
            cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
            user, role, warehouse, database, schema = cursor.fetchone()
            
            cursor.execute("SELECT CURRENT_VERSION()")
            version = cursor.fetchone()[0]
            
            cursor.close()
            
            return {
                "status": "connected",
                "user": user,
                "role": role,
                "warehouse": warehouse,
                "database": database,
                "schema": schema,
                "version": version,
                "account": self.config['account']
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def disconnect(self):
        """Disconnect from Snowflake."""
        if self.connection:
            try:
                self.connection.close()
                console.print("🔌 Disconnected from Snowflake")
            except Exception as e:
                console.print(f"⚠️  Error during disconnect: {e}")
            finally:
                self.connection = None
                self.is_connected = False
    
    def is_connection_alive(self) -> bool:
        """Check if connection is still alive."""
        if not self.is_connected or not self.connection:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except:
            self.is_connected = False
            return False
    
    def reconnect(self):
        """Reconnect to Snowflake."""
        console.print("🔄 Reconnecting to Snowflake...")
        self.disconnect()
        return self.connect()


class ConnectionManager:
    """Manage multiple Snowflake connections."""
    
    def __init__(self):
        self.connections = {}
        self.current_connection = None
    
    def add_connection(self, name: str, config: Dict[str, Any]) -> SnowflakeClient:
        """Add a new connection."""
        client = SnowflakeClient(config)
        self.connections[name] = client
        return client
    
    def get_connection(self, name: str = None) -> Optional[SnowflakeClient]:
        """Get connection by name or current connection."""
        if name:
            return self.connections.get(name)
        return self.current_connection
    
    def set_current_connection(self, name: str):
        """Set current active connection."""
        if name in self.connections:
            self.current_connection = self.connections[name]
        else:
            raise ValueError(f"Connection '{name}' not found")
    
    def list_connections(self) -> List[str]:
        """List all available connections."""
        return list(self.connections.keys())
    
    def remove_connection(self, name: str):
        """Remove a connection."""
        if name in self.connections:
            self.connections[name].disconnect()
            del self.connections[name]
            if self.current_connection == self.connections.get(name):
                self.current_connection = None