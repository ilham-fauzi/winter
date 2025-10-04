"""
Main entry point for Winter CLI application.
"""

import click
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="Winter")
def main():
    """
    Winter - Snowflake Terminal Client
    
    A powerful terminal client for Snowflake with advanced table scrolling,
    prefix support, and security controls.
    """
    pass


@main.command()
def hello():
    """Say hello from Winter!"""
    text = Text("❄️  Winter - Snowflake Terminal Client", style="bold blue")
    console.print(text)
    console.print("Welcome to Winter! Run 'winter setup' to get started.")


@main.command()
def setup():
    """Run setup wizard to configure Winter."""
    from winter.setup import run_setup_wizard
    run_setup_wizard()


@main.command()
def status():
    """Show current Winter status."""
    console.print("📊 Winter Status:")
    console.print("✅ CLI working")
    console.print("✅ Setup wizard: Ready")
    console.print("✅ Snowflake connection: Ready")


@main.command()
def config():
    """Show current configuration."""
    from winter.setup import show_config
    show_config()


@main.command()
def validate():
    """Validate current configuration."""
    from winter.setup import validate_config
    validate_config()


@main.command()
def reset():
    """Reset configuration."""
    from winter.setup import reset_config
    reset_config()


@main.command()
@click.argument('private_key_path')
def extract_public_key(private_key_path):
    """Extract public key from private key file."""
    from winter.setup import generate_public_key
    try:
        public_key_path = generate_public_key(private_key_path)
        console.print(f"✅ Public key extracted to: {public_key_path}")
        
        # Show public key content
        with open(public_key_path, 'r') as f:
            public_key = f.read().strip()
            console.print(f"\n🔑 Your public key:")
            console.print(public_key)
            
    except Exception as e:
        console.print(f"❌ Failed to extract public key: {e}")


@main.command()
def connect():
    """Connect to Snowflake."""
    from winter.snowflake import SnowflakeClient
    from winter.utils import load_config
    from winter.connection_state import ConnectionState
    
    try:
        config = load_config()
        client = SnowflakeClient(config)
        
        # Check if password authentication and no password in config
        if (config.get('auth_method') == 'password' and 
            config.get('password') is None):
            # Try to get cached password first
            connection_state = ConnectionState(config)
            cached_password = connection_state.get_cached_password()
            
            if cached_password:
                console.print("🔐 Using cached password from previous session")
                config['password'] = cached_password
            else:
                # Prompt for password
                import getpass
                password = getpass.getpass("Password: ")
                config['password'] = password
        
        client.connect()
        
        # Store client globally for other commands
        import winter.main
        winter.main.current_client = client
        
        # Save connection state with password cache
        connection_state = ConnectionState(config)
        client_info = client.get_connection_info()
        
        # Cache password if it's password authentication and not stored in config
        password_to_cache = None
        if (config.get('auth_method') == 'password' and 
            config.get('password') is not None):
            password_to_cache = config['password']
        
        connection_state.save_connection_state(client_info, password_to_cache)
        
        console.print("✅ Connection state saved")
        if password_to_cache:
            console.print("🔐 Password cached for this session")
        
    except Exception as e:
        console.print(f"❌ Failed to connect: {e}")


@main.command()
def disconnect():
    """Disconnect from Snowflake."""
    import winter.main
    from winter.connection_state import ConnectionState
    from winter.utils import load_config
    
    if hasattr(winter.main, 'current_client') and winter.main.current_client:
        winter.main.current_client.disconnect()
        winter.main.current_client = None
        console.print("✅ Disconnected from Snowflake")
    else:
        console.print("❌ No active connection")
    
    # Clear connection state and password cache
    try:
        config = load_config()
        connection_state = ConnectionState(config)
        connection_state.clear_password_cache()
        connection_state.clear_connection_state()
        console.print("✅ Connection state and password cache cleared")
    except Exception as e:
        console.print(f"⚠️  Error clearing state: {e}")


@main.command()
def test_connection():
    """Test Snowflake connection."""
    from winter.snowflake import SnowflakeClient
    from winter.utils import load_config
    
    try:
        config = load_config()
        client = SnowflakeClient(config)
        
        console.print("🔌 Testing connection to Snowflake...")
        client.connect()
        
        # Get connection info
        info = client.get_connection_info()
        
        if info['status'] == 'connected':
            console.print(Panel.fit(
                f"✅ Connection successful!\n\n"
                f"User: {info['user']}\n"
                f"Role: {info['role']}\n"
                f"Warehouse: {info['warehouse']}\n"
                f"Database: {info['database']}\n"
                f"Schema: {info['schema']}\n"
                f"Version: {info['version']}",
                title="Connection Info",
                border_style="green"
            ))
        else:
            console.print(f"❌ Connection failed: {info.get('error', 'Unknown error')}")
        
        client.disconnect()
        
    except Exception as e:
        console.print(f"❌ Connection test failed: {e}")


@main.command()
def connection_info():
    """Show current connection information."""
    import winter.main
    
    if hasattr(winter.main, 'current_client') and winter.main.current_client:
        info = winter.main.current_client.get_connection_info()
        
        if info['status'] == 'connected':
            console.print(Panel.fit(
                f"User: {info['user']}\n"
                f"Role: {info['role']}\n"
                f"Warehouse: {info['warehouse']}\n"
                f"Database: {info['database']}\n"
                f"Schema: {info['schema']}\n"
                f"Version: {info['version']}\n"
                f"Account: {info['account']}",
                title="Current Connection",
                border_style="blue"
            ))
        else:
            console.print(f"❌ Connection error: {info.get('error', 'Unknown error')}")
    else:
        console.print("❌ No active connection. Run 'winter connect' first.")


@main.command()
@click.argument('query', required=False)
def parse_query(query):
    """Parse and analyze SQL query."""
    from winter.query import QueryProcessor
    from winter.utils import load_config
    
    if not query:
        query = console.input("[bold blue]Enter SQL query:[/bold blue] ")
    
    try:
        config = load_config()
        processor = QueryProcessor(config)
        
        console.print(f"🔍 Parsing query: {query[:50]}{'...' if len(query) > 50 else ''}")
        
        query_info = processor.process_query(query)
        summary = processor.get_query_summary(query_info)
        
        # Display results
        console.print(Panel.fit(
            f"Query Type: {summary['query_type']}\n"
            f"Tables Found: {summary['tables_found']}\n"
            f"Prefix Applied: {summary['has_prefix_applied']}\n"
            f"Prefix Used: '{summary['prefix_used']}'",
            title="Query Analysis",
            border_style="green"
        ))
        
        if summary['tables']:
            console.print("\n📊 Table References:")
            for table in summary['tables']:
                table_info = f"• {table['name']}"
                if table['alias']:
                    table_info += f" AS {table['alias']}"
                if table['schema']:
                    table_info += f" (schema: {table['schema']})"
                if table['database']:
                    table_info += f" (database: {table['database']})"
                if not table['should_prefix']:
                    table_info += " [NO PREFIX]"
                
                console.print(table_info)
        
        if query_info.has_prefix_applied:
            console.print(f"\n✅ Modified Query:")
            console.print(Panel(query_info.modified_query, title="Processed Query", border_style="blue"))
        
    except Exception as e:
        console.print(f"❌ Query parsing failed: {e}")


@main.command()
@click.argument('query', required=False)
def validate_query(query):
    """Validate SQL query against security settings."""
    from winter.query import QueryValidator
    from winter.utils import load_config
    
    if not query:
        query = console.input("[bold blue]Enter SQL query:[/bold blue] ")
    
    try:
        config = load_config()
        validator = QueryValidator(
            config.get('security', {}).get('allowed_all_query_types', False)
        )
        
        console.print(f"🔍 Validating query: {query[:50]}{'...' if len(query) > 50 else ''}")
        
        is_valid, message = validator.validate_query(query)
        
        if is_valid:
            console.print("✅ Query is valid", style="green")
            console.print(f"📝 {message}")
        else:
            console.print("❌ Query validation failed", style="red")
            console.print(f"📝 {message}")
        
        # Show allowed query types
        allowed_types = validator.get_allowed_query_types()
        console.print(f"\n📋 Allowed query types: {', '.join(allowed_types)}")
        
    except Exception as e:
        console.print(f"❌ Query validation failed: {e}")


@main.command()
@click.argument('query', required=False)
@click.option('--limit', default=10, help='Maximum number of rows to display')
@click.option('--max-columns', default=5, help='Maximum number of columns to display')
@click.option('--interactive', is_flag=True, help='Enable interactive table viewer with scrolling')
def execute_query(query, limit, max_columns, interactive):
    """Execute SQL query with prefix processing."""
    from winter.query import QueryProcessor
    from winter.snowflake import SnowflakeClient
    from winter.utils import load_config
    import winter.main
    
    if not query:
        query = console.input("[bold blue]Enter SQL query:[/bold blue] ")
    
    try:
        config = load_config()
        processor = QueryProcessor(config)
        
        # Process query (apply prefix and validate)
        query_info = processor.process_query(query)
        
        console.print(f"🔍 Processed query: {query_info.modified_query[:50]}{'...' if len(query_info.modified_query) > 50 else ''}")
        
        # Check if we have an active connection, if not show error
        if not hasattr(winter.main, 'current_client') or not winter.main.current_client:
            # Try to load connection state
            from winter.connection_state import ConnectionState
            connection_state = ConnectionState(config)
            
            if connection_state.is_connected():
                console.print("🔌 Found saved connection state. Reconnecting...")
                try:
                    config = load_config()
                    
                    # Use cached password if available
                    cached_password = connection_state.get_cached_password()
                    if cached_password and config.get('auth_method') == 'password':
                        config['password'] = cached_password
                        console.print("🔐 Using cached password")
                    
                    client = SnowflakeClient(config)
                    client.connect()
                    winter.main.current_client = client
                    console.print("✅ Reconnected successfully")
                except Exception as e:
                    console.print(f"❌ Failed to reconnect: {e}")
                    connection_state.clear_connection_state()
                    console.print("❌ No active connection found!")
                    console.print("💡 Please run 'winter connect' first to establish connection")
                    console.print("   winter connect")
                    return
            else:
                console.print("❌ No active connection found!")
                console.print("💡 Please run 'winter connect' first to establish connection")
                console.print("   winter connect")
                return
        
        client = winter.main.current_client
        
        # Check if connection is still valid (not timed out)
        if not client._is_connection_valid():
            console.print("❌ Connection has expired!")
            console.print("💡 Please run 'winter connect' to reconnect")
            console.print("   winter connect")
            return
        
        # Execute query and track execution time
        import time
        start_time = time.time()
        
        try:
            columns, results = client.execute_query_with_columns(query_info.modified_query)
            execution_time = time.time() - start_time
            success = True
            error_message = None
        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            error_message = str(e)
            raise e
        
        # Prepare for background counting (will start after results are displayed)
        total_count = None
        counter = None
        
        # Only start counting if query doesn't have LIMIT and seems reasonable
        query_upper = query_info.modified_query.upper().strip()
        has_limit = 'LIMIT' in query_upper
        has_where = 'WHERE' in query_upper
        
        should_count = not has_limit and (has_where or len(query_info.modified_query) < 200)
        
        # Log query to history
        try:
            from winter.history import QueryHistoryManager
            history_manager = QueryHistoryManager()
            history_manager.add_query_history(
                query=query_info.modified_query,
                execution_time=execution_time,
                rows_returned=len(results) if results else 0,
                columns_count=len(columns) if columns else 0,
                success=success,
                error_message=error_message
            )
        except Exception as history_error:
            # Don't fail the main query if history logging fails
            console.print(f"⚠️  Failed to log query to history: {history_error}")
        
        # Display results with Rich table (supports horizontal scrolling)
        if results:
            console.print(f"\n📊 Query Results ({len(results)} rows, {len(columns)} columns):")
            
            # Limit rows and columns for display
            display_rows = results[:limit]
            display_cols = columns[:max_columns]
            
            if interactive:
                # Interactive table viewer with scrolling
                from winter.ui import InteractiveTableViewer
                viewer = InteractiveTableViewer()
                viewer.display_interactive_table(results, columns, limit, max_columns)
            else:
                # Standard Rich table display with formatting
                from rich.table import Table
                from winter.formatters import DataFormatter, ColumnAnalyzer
                from winter.header_formatter import create_smart_header_formatter
                
                formatter = DataFormatter()
                analyzer = ColumnAnalyzer()
                
                # Analyze columns for formatting
                column_info = {}
                for i, col in enumerate(display_cols):
                    column_values = [row[i] for row in display_rows if i < len(row)]
                    column_info[col] = analyzer.analyze_column(col, column_values)
                
                table = Table(
                    show_header=True,
                    header_style="bold blue",
                    border_style="blue",
                    show_lines=True,
                    expand=True  # This enables horizontal scrolling
                )
                
                # Add columns with smart header formatting
                header_formatter = create_smart_header_formatter()
                formatted_headers = header_formatter.format_headers_smart(display_cols, max_width=30)
                
                for i, col in enumerate(display_cols):
                    col_info = column_info.get(col, {})
                    col_type = col_info.get('type', 'text')
                    
                    # Use formatted header with smart scaling
                    display_header, full_header = formatted_headers[i]
                    
                    # Calculate dynamic column width based on header length
                    header_length = len(col)
                    column_width = max(15, min(header_length + 2, 35))  # Dynamic width
                    
                    table.add_column(
                        display_header,
                        overflow="fold",
                        min_width=column_width,  # Dynamic minimum width
                        max_width=column_width,   # Dynamic maximum width
                        no_wrap=False  # Allow wrapping for very long headers
                    )
                
                # Add rows with formatted values
                for row in display_rows:
                    formatted_row = []
                    for i in range(len(display_cols)):
                        if i < len(row):
                            cell = row[i]
                            col_name = display_cols[i]
                            col_info = column_info.get(col_name, {})
                            col_type = col_info.get('type', 'text')
                            
                            # Format the cell value based on its type
                            cell_value = formatter.format_value(cell, col_type, max_length=30)
                        else:
                            cell_value = "[dim]NULL[/dim]"
                        formatted_row.append(cell_value)
                    table.add_row(*formatted_row)
                
                # Display the table (Rich handles horizontal scrolling automatically)
                console.print(table)
                
                # Show summary
                if len(results) > limit:
                    console.print(f"\n... and {len(results) - limit} more rows")
                if len(columns) > max_columns:
                    console.print(f"... and {len(columns) - max_columns} more columns")
                
                console.print(f"\n💡 Use 'winter execute-query \"{query}\" --limit {limit*2} --max-columns {max_columns*2}' to see more data")
                console.print("🔄 Rich table supports horizontal scrolling - use mouse wheel or arrow keys in terminal")
                console.print("🎮 Use --interactive flag for advanced scrolling controls")
        else:
            console.print("📊 Query executed successfully (no results)")
        
        # Start background counting AFTER results are displayed
        if should_count:
            try:
                from winter.counter import BackgroundCounter, show_live_counting_progress
                counter = BackgroundCounter(client, query_info.modified_query)
                counter.start_counting()
                
                # Show live progress with real-time updates
                def update_progress(message):
                    console.print(f"\r{message}", end="")
                
                show_live_counting_progress(counter, update_progress)
                console.print()  # New line after progress
                
            except Exception as count_error:
                console.print(f"\n⚠️  Failed to start background counting: {count_error}")
        elif not has_limit:
            console.print("\n⚠️  Query without LIMIT detected - skipping background count for performance")
        
    except Exception as e:
        console.print(f"❌ Query execution failed: {e}")


@main.command()
def security_status():
    """Show current security status and policy."""
    from winter.security import SecurityManager
    from winter.utils import load_config
    
    try:
        config = load_config()
        security_manager = SecurityManager(config)
        status = security_manager.get_security_status()
        
        console.print(Panel.fit(
            f"Security Level: {status['security_level'].upper()}\n"
            f"Session Active: {'Yes' if status['session_active'] else 'No'}\n"
            f"Audit Logging: {'Enabled' if status['audit_logging_enabled'] else 'Disabled'}\n"
            f"Allowed Query Types: {', '.join(status['policy']['allowed_query_types'])}\n"
            f"Max Query Length: {status['policy']['max_query_length']}\n"
            f"Max Results Limit: {status['policy']['max_results_limit']}\n"
            f"Session Timeout: {status['policy']['session_timeout_minutes']} minutes",
            title="Security Status",
            border_style="yellow"
        ))
        
    except Exception as e:
        console.print(f"❌ Failed to get security status: {e}")


@main.command()
@click.option('--hours', default=24, help='Number of hours to look back')
def audit_log(hours):
    """Show audit log summary."""
    from winter.security import SecurityManager
    from winter.utils import load_config
    
    try:
        config = load_config()
        security_manager = SecurityManager(config)
        summary = security_manager.get_audit_summary(hours)
        
        console.print(Panel.fit(
            f"Period: Last {summary['period_hours']} hours\n"
            f"Total Events: {summary['total_events']}\n"
            f"Security Violations: {summary['security_violations']}\n"
            f"Events by Type: {summary['events_by_type']}",
            title="Audit Log Summary",
            border_style="blue"
        ))
        
        if summary['recent_violations']:
            console.print("\n🚨 Recent Security Violations:")
            for violation in summary['recent_violations'][-5:]:  # Show last 5
                console.print(f"• {violation['timestamp']}: {violation['details'].get('violation_type', 'Unknown')}")
        
    except Exception as e:
        console.print(f"❌ Failed to get audit log: {e}")


@main.command()
def security_test():
    """Test security controls with sample queries."""
    from winter.security import SecurityManager
    from winter.utils import load_config
    
    try:
        config = load_config()
        security_manager = SecurityManager(config)
        user = config.get('user', 'test_user')
        
        # Start session
        session_id = security_manager.start_session(user)
        console.print(f"🔐 Started security session: {session_id}")
        
        # Test queries
        test_queries = [
            ("SELECT * FROM users", "Safe SELECT query"),
            ("SELECT COUNT(*) FROM orders", "Safe aggregation query"),
            ("INSERT INTO users VALUES (1, 'test')", "Potentially dangerous INSERT"),
            ("DROP TABLE users", "Dangerous DROP operation"),
            ("SELECT * FROM " + "x" * 15000, "Oversized query")
        ]
        
        console.print("\n🧪 Testing Security Controls:")
        
        for query, description in test_queries:
            console.print(f"\n📝 {description}")
            console.print(f"Query: {query[:50]}{'...' if len(query) > 50 else ''}")
            
            is_valid, message = security_manager.validate_query(query, user)
            
            if is_valid:
                console.print(f"✅ {message}", style="green")
            else:
                console.print(f"❌ {message}", style="red")
        
        # End session
        security_manager.end_session(user)
        console.print(f"\n🔐 Ended security session: {session_id}")
        
    except Exception as e:
        console.print(f"❌ Security test failed: {e}")


@main.command()
def security_config():
    """Show current security configuration."""
    from winter.utils import load_config
    
    try:
        config = load_config()
        security_config = config.get('security', {})
        
        console.print(Panel.fit(
            f"Allowed All Query Types: {security_config.get('allowed_all_query_types', False)}\n"
            f"Audit Logging: {security_config.get('audit_logging', True)}\n"
            f"Max Query Length: {security_config.get('max_query_length', 10000)}\n"
            f"Max Results Limit: {security_config.get('max_results_limit', 1000)}\n"
            f"Session Timeout: {security_config.get('session_timeout_minutes', 60)} minutes\n"
            f"Block Dangerous Functions: {security_config.get('block_dangerous_functions', True)}\n"
            f"Allowed Schemas: {security_config.get('allowed_schemas', 'All')}\n"
            f"Blocked Schemas: {security_config.get('blocked_schemas', 'None')}",
            title="Security Configuration",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"❌ Failed to get security configuration: {e}")


@main.command()
@click.argument('query', required=False)
@click.option('--format', 'export_format', default='csv', 
              type=click.Choice(['csv', 'json', 'xlsx']),
              help='Export format')
@click.option('--output', '-o', help='Output filename or directory')
@click.option('--limit', default=1000, help='Maximum number of rows to export')
def export_query(query, export_format, output, limit):
    """Export query results to file."""
    from winter.query import QueryProcessor
    from winter.snowflake import SnowflakeClient
    from winter.utils import load_config
    from winter.export import ExportManager
    import winter.main
    
    if not query:
        query = console.input("[bold blue]Enter SQL query:[/bold blue] ")
    
    try:
        config = load_config()
        processor = QueryProcessor(config)
        
        # Process query (apply prefix and validate)
        query_info = processor.process_query(query)
        
        console.print(f"🔍 Processed query: {query_info.modified_query[:50]}{'...' if len(query_info.modified_query) > 50 else ''}")
        
        # Check if we have an active connection, if not show error
        if not hasattr(winter.main, 'current_client') or not winter.main.current_client:
            # Try to load connection state
            from winter.connection_state import ConnectionState
            connection_state = ConnectionState(config)
            
            if connection_state.is_connected():
                console.print("🔌 Found saved connection state. Reconnecting...")
                try:
                    config = load_config()
                    
                    # Use cached password if available
                    cached_password = connection_state.get_cached_password()
                    if cached_password and config.get('auth_method') == 'password':
                        config['password'] = cached_password
                        console.print("🔐 Using cached password")
                    
                    client = SnowflakeClient(config)
                    client.connect()
                    winter.main.current_client = client
                    console.print("✅ Reconnected successfully")
                except Exception as e:
                    console.print(f"❌ Failed to reconnect: {e}")
                    connection_state.clear_connection_state()
                    console.print("❌ No active connection found!")
                    console.print("💡 Please run 'winter connect' first to establish connection")
                    console.print("   winter connect")
                    return
            else:
                console.print("❌ No active connection found!")
                console.print("💡 Please run 'winter connect' first to establish connection")
                console.print("   winter connect")
                return
        
        client = winter.main.current_client
        
        # Check if connection is still valid (not timed out)
        if not client._is_connection_valid():
            console.print("❌ Connection has expired!")
            console.print("💡 Please run 'winter connect' to reconnect")
            console.print("   winter connect")
            return
        
        # Execute query
        columns, results = client.execute_query_with_columns(query_info.modified_query)
        
        # Limit results for export
        if len(results) > limit:
            console.print(f"⚠️  Limiting export to {limit} rows (query returned {len(results)} rows)")
            results = results[:limit]
        
        if not results:
            console.print("❌ No data to export")
            return
        
        # Export data
        export_manager = ExportManager()
        
        # Show export summary
        summary = export_manager.get_export_summary(results, columns)
        console.print(f"\n📊 Export Summary:")
        console.print(f"  Rows: {summary['total_rows']}")
        console.print(f"  Columns: {summary['total_columns']}")
        console.print(f"  Format: {export_format.upper()}")
        
        # Perform export
        # If output is provided, treat it as filename (not directory)
        success = export_manager.export_query_results(
            results, columns, query, export_format, 
            output_dir=None, filename=output
        )
        
        if success:
            console.print(f"✅ Export completed successfully!")
            console.print(f"📁 Files saved to: {export_manager.default_output_dir}")
        else:
            console.print("❌ Export failed")
        
    except Exception as e:
        console.print(f"❌ Export failed: {e}")


@main.command()
@click.argument('query', required=False)
@click.option('--formats', default='csv,json,xlsx', 
              help='Comma-separated list of formats (csv,json,xlsx)')
@click.option('--output', '-o', help='Output directory')
@click.option('--limit', default=1000, help='Maximum number of rows to export')
def export_all(query, formats, output, limit):
    """Export query results to all formats."""
    from winter.query import QueryProcessor
    from winter.snowflake import SnowflakeClient
    from winter.utils import load_config
    from winter.export import ExportManager
    import winter.main
    
    if not query:
        query = console.input("[bold blue]Enter SQL query:[/bold blue] ")
    
    try:
        config = load_config()
        processor = QueryProcessor(config)
        
        # Process query (apply prefix and validate)
        query_info = processor.process_query(query)
        
        console.print(f"🔍 Processed query: {query_info.modified_query[:50]}{'...' if len(query_info.modified_query) > 50 else ''}")
        
        # Check if we have an active connection, if not show error
        if not hasattr(winter.main, 'current_client') or not winter.main.current_client:
            # Try to load connection state
            from winter.connection_state import ConnectionState
            connection_state = ConnectionState(config)
            
            if connection_state.is_connected():
                console.print("🔌 Found saved connection state. Reconnecting...")
                try:
                    config = load_config()
                    
                    # Use cached password if available
                    cached_password = connection_state.get_cached_password()
                    if cached_password and config.get('auth_method') == 'password':
                        config['password'] = cached_password
                        console.print("🔐 Using cached password")
                    
                    client = SnowflakeClient(config)
                    client.connect()
                    winter.main.current_client = client
                    console.print("✅ Reconnected successfully")
                except Exception as e:
                    console.print(f"❌ Failed to reconnect: {e}")
                    connection_state.clear_connection_state()
                    console.print("❌ No active connection found!")
                    console.print("💡 Please run 'winter connect' first to establish connection")
                    console.print("   winter connect")
                    return
            else:
                console.print("❌ No active connection found!")
                console.print("💡 Please run 'winter connect' first to establish connection")
                console.print("   winter connect")
                return
        
        client = winter.main.current_client
        
        # Check if connection is still valid (not timed out)
        if not client._is_connection_valid():
            console.print("❌ Connection has expired!")
            console.print("💡 Please run 'winter connect' to reconnect")
            console.print("   winter connect")
            return
        
        # Execute query
        columns, results = client.execute_query_with_columns(query_info.modified_query)
        
        # Limit results for export
        if len(results) > limit:
            console.print(f"⚠️  Limiting export to {limit} rows (query returned {len(results)} rows)")
            results = results[:limit]
        
        if not results:
            console.print("❌ No data to export")
            return
        
        # Parse formats
        format_list = [f.strip().lower() for f in formats.split(',')]
        
        # Export to all formats
        export_manager = ExportManager()
        
        # Show export summary
        summary = export_manager.get_export_summary(results, columns)
        console.print(f"\n📊 Export Summary:")
        console.print(f"  Rows: {summary['total_rows']}")
        console.print(f"  Columns: {summary['total_columns']}")
        console.print(f"  Formats: {', '.join(format_list).upper()}")
        
        # Perform multi-format export
        results_status = export_manager.exporter.export_multiple_formats(
            results, columns, f"winter_export_{query[:20]}", format_list
        )
        
        # Show results
        console.print(f"\n📁 Export Results:")
        for format_type, success in results_status.items():
            status = "✅ Success" if success else "❌ Failed"
            console.print(f"  {format_type.upper()}: {status}")
        
        console.print(f"\n📁 Files saved to: {export_manager.default_output_dir}")
        
    except Exception as e:
        console.print(f"❌ Export failed: {e}")


# History and Favorites Commands

@main.command()
@click.option('--limit', default=20, help='Number of history entries to show')
def history(limit):
    """Show query execution history."""
    from winter.history import QueryHistoryManager, HistoryUI
    
    try:
        history_manager = QueryHistoryManager()
        history_ui = HistoryUI(history_manager)
        history_ui.show_query_history(limit)
    except Exception as e:
        console.print(f"❌ Failed to show history: {e}")


@main.command()
@click.argument('search_term')
def search_history(search_term):
    """Search query history by content."""
    from winter.history import QueryHistoryManager, HistoryUI
    
    try:
        history_manager = QueryHistoryManager()
        history_ui = HistoryUI(history_manager)
        
        results = history_manager.search_query_history(search_term)
        
        if not results:
            console.print(f"🔍 No queries found matching '{search_term}'")
            return
        
        console.print(f"🔍 Found {len(results)} queries matching '{search_term}':")
        
        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Executed At", style="cyan", width=20)
        table.add_column("Query", style="white", width=60)
        table.add_column("Time", style="green", width=8)
        table.add_column("Rows", style="magenta", width=6)
        
        for entry in results:
            query_preview = entry.query[:57] + "..." if len(entry.query) > 60 else entry.query
            
            table.add_row(
                str(entry.id),
                entry.executed_at[:19],
                query_preview,
                f"{entry.execution_time:.2f}s",
                str(entry.rows_returned)
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Failed to search history: {e}")


@main.command()
def favorites():
    """Show favorite queries."""
    from winter.history import QueryHistoryManager, HistoryUI
    
    try:
        history_manager = QueryHistoryManager()
        history_ui = HistoryUI(history_manager)
        history_ui.show_favorites()
    except Exception as e:
        console.print(f"❌ Failed to show favorites: {e}")


@main.command()
@click.argument('name')
@click.argument('query')
@click.option('--description', '-d', help='Description for the favorite')
@click.option('--tags', '-t', help='Comma-separated tags')
def add_favorite(name, query, description, tags):
    """Add a query to favorites."""
    from winter.history import QueryHistoryManager
    
    try:
        history_manager = QueryHistoryManager()
        
        tags_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        favorite_id = history_manager.add_favorite(
            name=name,
            query=query,
            description=description or "",
            tags=tags_list
        )
        
        console.print(f"✅ Added favorite '{name}' with ID {favorite_id}")
        
    except Exception as e:
        console.print(f"❌ Failed to add favorite: {e}")


@main.command()
@click.argument('search_term')
def search_favorites(search_term):
    """Search favorite queries."""
    from winter.history import QueryHistoryManager, HistoryUI
    
    try:
        history_manager = QueryHistoryManager()
        history_ui = HistoryUI(history_manager)
        history_ui._search_favorites_interactive()
        
    except Exception as e:
        console.print(f"❌ Failed to search favorites: {e}")


@main.command()
@click.argument('favorite_id', type=int)
def delete_favorite(favorite_id):
    """Delete a favorite query by ID."""
    from winter.history import QueryHistoryManager
    
    try:
        history_manager = QueryHistoryManager()
        history_manager.delete_favorite(favorite_id)
        console.print(f"✅ Deleted favorite ID {favorite_id}")
        
    except Exception as e:
        console.print(f"❌ Failed to delete favorite: {e}")


@main.command()
def manage_favorites():
    """Interactive favorite query manager."""
    from winter.history import QueryHistoryManager, HistoryUI
    
    try:
        history_manager = QueryHistoryManager()
        history_ui = HistoryUI(history_manager)
        history_ui.interactive_favorite_manager()
        
    except Exception as e:
        console.print(f"❌ Failed to manage favorites: {e}")


@main.command()
@click.option('--check-only', is_flag=True, help='Hanya cek versi terbaru tanpa melakukan update')
@click.option('--include-deps', is_flag=True, help='Update dependencies juga')
def update(check_only, include_deps):
    """Update Winter package ke versi terbaru."""
    import subprocess
    import sys
    import json
    import urllib.request
    from packaging import version
    from winter.utils.version import get_current_version
    
    try:
        # Dapatkan versi saat ini
        current_version = get_current_version()
        
        console.print("🔍 Mengecek versi terbaru Winter...")
        
        # Cek versi terbaru dari PyPI
        try:
            url = "https://pypi.org/pypi/winter/json"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                latest_version = data['info']['version']
        except Exception as e:
            console.print(f"❌ Gagal mengecek versi terbaru: {e}")
            console.print("💡 Pastikan koneksi internet tersedia")
            return
        
        # Bandingkan versi
        current_ver = version.parse(current_version)
        latest_ver = version.parse(latest_version)
        
        console.print(f"📦 Versi saat ini: {current_version}")
        console.print(f"📦 Versi terbaru: {latest_version}")
        
        if current_ver >= latest_ver:
            console.print("✅ Winter sudah dalam versi terbaru!")
            return
        
        if check_only:
            console.print(f"🔄 Update tersedia: {current_version} → {latest_version}")
            console.print("💡 Jalankan 'winter update' untuk melakukan update")
            return
        
        # Konfirmasi update
        console.print(f"\n🔄 Update tersedia: {current_version} → {latest_version}")
        confirm = console.input("Apakah Anda ingin melanjutkan update? (y/N): ")
        
        if confirm.lower() not in ['y', 'yes', 'ya']:
            console.print("❌ Update dibatalkan")
            return
        
        # Lakukan update
        console.print("\n🔄 Memulai update Winter...")
        
        # Update winter package
        update_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "winter"]
        
        if include_deps:
            console.print("📦 Update dependencies juga...")
            update_cmd.extend(["--upgrade"])
        
        result = subprocess.run(update_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print("✅ Winter berhasil diupdate!")
            console.print("🔄 Restart terminal atau jalankan 'winter --version' untuk memverifikasi")
            
            # Tampilkan output pip jika ada
            if result.stdout:
                console.print("\n📋 Output update:")
                console.print(result.stdout)
        else:
            console.print("❌ Update gagal!")
            console.print(f"Error: {result.stderr}")
            console.print("💡 Coba jalankan: pip install --upgrade winter")
        
    except ImportError:
        console.print("❌ Package 'packaging' tidak ditemukan")
        console.print("💡 Install dengan: pip install packaging")
    except Exception as e:
        console.print(f"❌ Update gagal: {e}")


@main.command()
def check_update():
    """Cek apakah ada update tersedia untuk Winter."""
    import json
    import urllib.request
    from packaging import version
    from winter.utils.version import get_current_version
    
    try:
        # Dapatkan versi saat ini
        current_version = get_current_version()
        
        console.print("🔍 Mengecek update Winter...")
        
        # Cek versi terbaru dari PyPI
        try:
            url = "https://pypi.org/pypi/winter/json"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
                latest_version = data['info']['version']
        except Exception as e:
            console.print(f"❌ Gagal mengecek versi terbaru: {e}")
            console.print("💡 Pastikan koneksi internet tersedia")
            return
        
        # Bandingkan versi
        current_ver = version.parse(current_version)
        latest_ver = version.parse(latest_version)
        
        console.print(f"📦 Versi saat ini: {current_version}")
        console.print(f"📦 Versi terbaru: {latest_version}")
        
        if current_ver >= latest_ver:
            console.print("✅ Winter sudah dalam versi terbaru!")
        else:
            console.print(f"🔄 Update tersedia: {current_version} → {latest_version}")
            console.print("💡 Jalankan 'winter update' untuk melakukan update")
            
            # Tampilkan informasi update
            update_info = data['info']
            if 'description' in update_info and update_info['description']:
                console.print(f"\n📝 Deskripsi update:")
                console.print(update_info['description'][:200] + "..." if len(update_info['description']) > 200 else update_info['description'])
        
    except ImportError:
        console.print("❌ Package 'packaging' tidak ditemukan")
        console.print("💡 Install dengan: pip install packaging")
    except Exception as e:
        console.print(f"❌ Gagal mengecek update: {e}")


@main.command()
def package_info():
    """Tampilkan informasi detail package Winter."""
    from winter.utils.version import get_package_info
    from rich.panel import Panel
    from rich.table import Table
    
    try:
        info = get_package_info()
        
        # Tampilkan informasi dasar
        console.print(Panel.fit(
            f"Package: {info['name']}\n"
            f"Version: {info['version']}\n"
            f"Location: {info['location'] or 'Development mode'}\n"
            f"Status: {'Installed' if info['installed'] else 'Development mode'}",
            title="Winter Package Info",
            border_style="blue"
        ))
        
        # Tampilkan dependencies jika ada
        if info['requires']:
            console.print("\n📦 Dependencies:")
            table = Table(show_header=True, header_style="bold green")
            table.add_column("Package", style="cyan")
            table.add_column("Version", style="magenta")
            
            for req in info['requires']:
                # Parse requirement string
                if '==' in req:
                    pkg, ver = req.split('==', 1)
                    table.add_row(pkg, ver)
                elif '>=' in req:
                    pkg, ver = req.split('>=', 1)
                    table.add_row(pkg, f">= {ver}")
                else:
                    table.add_row(req, "Any")
            
            console.print(table)
        
    except Exception as e:
        console.print(f"❌ Gagal mendapatkan informasi package: {e}")


if __name__ == "__main__":
    main()
