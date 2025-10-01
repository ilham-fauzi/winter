# Winter - Developer Guide

## 🏗️ Architecture Overview

Winter is built with a modular architecture that separates concerns and provides clean interfaces between components.

### Core Components

```
winter/
├── main.py                 # CLI entry point and command definitions
├── cli/                    # CLI-specific components
├── snowflake/              # Snowflake connection and authentication
├── query/                  # Query processing and prefix system
├── security/               # Security controls and validation
├── ui/                     # Interactive table viewer and display
├── formatters/             # Data formatting and column analysis
├── export/                 # Export functionality (CSV, JSON, Excel)
├── history/                # Query history and favorites management
├── setup/                  # Interactive setup wizard
└── utils/                  # Utility functions and helpers
```

## 🔧 Development Setup

### Prerequisites
- Python 3.8+
- Git
- Snowflake account with RSA keypair

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/your-org/winter.git
cd winter

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### Running Tests
```bash
# Run all tests
python3 test_winter.py

# Run specific test modules
python3 -m pytest tests/test_query.py -v
python3 -m pytest tests/test_snowflake.py -v
python3 -m pytest tests/test_security.py -v

# Run with coverage
python3 -m pytest --cov=winter tests/
```

## 📁 Component Details

### 1. Main CLI (`main.py`)
Entry point for all CLI commands. Uses Click framework for command-line interface.

**Key Functions:**
- `main()`: Click group definition
- `execute_query()`: Main query execution with history logging
- `export_query()`: Single format export
- `export_all()`: Multi-format export
- History and favorites commands

**Dependencies:**
- `click`: CLI framework
- `rich`: Terminal output formatting

### 2. Snowflake Connection (`snowflake/`)
Handles Snowflake connectivity using RSA keypair authentication.

**Key Classes:**
- `SnowflakeClient`: Main connection class

**Key Methods:**
- `connect()`: Establish connection with retry logic
- `disconnect()`: Close connection
- `execute_query_with_columns()`: Execute query and return results
- `_load_private_key()`: Load and validate RSA private key
- `_normalize_account()`: Normalize Snowflake account format

**Features:**
- RSA keypair authentication
- Connection retry with exponential backoff
- Account format normalization
- Connection testing and validation

### 3. Query Processing (`query/`)
Handles SQL parsing, prefix application, and query validation.

**Key Classes:**
- `SQLParser`: Parses SQL to identify table references
- `PrefixProcessor`: Applies prefixes to table references
- `QueryProcessor`: Main processor combining parsing and prefixing

**Key Methods:**
- `parse_query()`: Parse SQL and identify table references
- `process_query()`: Apply prefixes and validate query
- `_parse_table_reference()`: Parse individual table references
- `_apply_prefix()`: Apply prefix to table references

**Features:**
- Comprehensive SQL parsing
- Prefix application to all table references
- Alias preservation
- Schema-qualified table handling
- Query type detection

### 4. Security System (`security/`)
Implements security controls and validation.

**Key Classes:**
- `SecurityManager`: Main security management class
- `SecurityPolicy`: Security policy configuration
- `PermissionManager`: Permission validation

**Key Methods:**
- `validate_query()`: Validate query against security policy
- `_check_schema_access()`: Check schema access permissions
- `log_audit_event()`: Log security events
- `get_security_status()`: Get current security status

**Features:**
- SELECT-only by default
- Schema access control
- Audit logging
- Session management
- Dangerous function blocking

### 5. Interactive UI (`ui/`)
Provides interactive table viewing with scrolling capabilities.

**Key Classes:**
- `InteractiveTableViewer`: Main interactive table viewer
- `TableViewer`: Base table viewer class

**Key Methods:**
- `display_interactive_table()`: Display interactive table with scrolling
- `_create_scrolled_table()`: Create table with current scroll position
- `_show_column_info()`: Display column information
- `_show_help()`: Display help information

**Features:**
- Horizontal and vertical scrolling
- Arrow key and WASD navigation
- Column information display
- Consistent column widths
- Data type color coding

### 6. Data Formatting (`formatters/`)
Handles data formatting and column analysis.

**Key Classes:**
- `DataFormatter`: Formats data values for display
- `ColumnAnalyzer`: Analyzes column data types and statistics

**Key Methods:**
- `format_value()`: Format individual data values
- `analyze_column()`: Analyze column data types
- `suggest_column_width()`: Suggest optimal column width

**Features:**
- Automatic data type detection
- Color coding by data type
- Column width optimization
- Null value handling
- Sample value analysis

### 7. Export System (`export/`)
Handles data export to various formats.

**Key Classes:**
- `DataExporter`: Handles individual format exports
- `ExportManager`: Manages export operations

**Key Methods:**
- `export_csv()`: Export to CSV format
- `export_json()`: Export to JSON format
- `export_excel()`: Export to Excel format
- `export_multiple_formats()`: Export to multiple formats

**Features:**
- CSV, JSON, Excel export
- Automatic filename generation
- Metadata inclusion
- Progress indicators
- Error handling

### 8. History Management (`history/`)
Manages query history and favorites.

**Key Classes:**
- `QueryHistoryManager`: Manages history and favorites
- `HistoryUI`: UI components for history management
- `QueryHistory`: Data class for history entries
- `QueryFavorite`: Data class for favorite queries

**Key Methods:**
- `add_query_history()`: Add query to history
- `get_query_history()`: Retrieve query history
- `search_query_history()`: Search history by content
- `add_favorite()`: Add query to favorites
- `get_favorites()`: Retrieve favorites

**Features:**
- SQLite database storage
- Automatic query logging
- Search functionality
- Favorites management
- Usage tracking

## 🧪 Testing

### Test Structure
```
tests/
├── test_cli.py              # CLI command tests
├── test_snowflake.py         # Snowflake connection tests
├── test_query.py             # Query processing tests
├── test_security.py          # Security system tests
├── test_setup.py             # Setup wizard tests
└── test_winter.py            # Comprehensive integration tests
```

### Test Categories

#### Unit Tests
- Individual component testing
- Mock external dependencies
- Test edge cases and error conditions

#### Integration Tests
- End-to-end functionality testing
- Real Snowflake connection testing (with test credentials)
- CLI command testing

#### Test Data
- Mock Snowflake responses
- Sample SQL queries
- Test configuration files

### Running Tests
```bash
# Run all tests
python3 test_winter.py

# Run specific test file
python3 -m pytest tests/test_query.py -v

# Run with coverage
python3 -m pytest --cov=winter tests/

# Run integration tests (requires Snowflake connection)
python3 -m pytest tests/test_snowflake.py -v
```

## 🔨 Adding New Features

### 1. Adding New CLI Commands
```python
# In main.py
@main.command()
@click.argument('param')
@click.option('--option', help='Option description')
def new_command(param, option):
    """Command description."""
    # Implementation
```

### 2. Adding New Export Formats
```python
# In export/__init__.py
def export_new_format(self, results, columns, filepath):
    """Export to new format."""
    # Implementation
```

### 3. Adding New Security Controls
```python
# In security/__init__.py
def _check_new_security(self, query, user):
    """Check new security rule."""
    # Implementation
```

### 4. Adding New Data Types
```python
# In formatters/__init__.py
def _detect_data_type(self, values):
    """Detect data type including new types."""
    # Add new type detection logic
```

## 🐛 Debugging

### Debug Mode
```bash
# Enable debug logging
export WINTER_DEBUG=1
python3 run_winter.py execute-query "SELECT 1"
```

### Common Debug Points
1. **Connection Issues**: Check `_load_private_key()` and `connect()`
2. **Query Parsing**: Check `SQLParser` and `PrefixProcessor`
3. **UI Issues**: Check `InteractiveTableViewer` scrolling logic
4. **Export Issues**: Check `ExportManager` file handling
5. **History Issues**: Check SQLite database operations

### Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

## 📦 Packaging

### Building Package
```bash
# Build source distribution
python3 setup.py sdist

# Build wheel
python3 setup.py bdist_wheel

# Install from source
pip install dist/winter-0.1.0.tar.gz
```

### Dependencies
```python
# requirements.txt
snowflake-connector-python>=3.0.0
cryptography>=3.4.8
pyyaml>=6.0
rich>=13.0.0
click>=8.0.0
inquirer>=3.0.0
pandas>=1.5.0
openpyxl>=3.0.0
```

## 🚀 Performance Optimization

### Query Execution
- Connection pooling
- Query result caching
- Lazy loading of large datasets

### UI Performance
- Virtual scrolling for large tables
- Efficient column width calculation
- Optimized Rich table rendering

### Memory Management
- Streaming large result sets
- Garbage collection optimization
- Memory usage monitoring

## 🔒 Security Considerations

### Authentication
- Secure private key handling
- Key file permission validation
- Connection encryption

### Query Validation
- SQL injection prevention
- Query type validation
- Schema access control

### Data Protection
- Audit logging
- Sensitive data masking
- Export permission controls

## 📚 API Reference

### Core Classes

#### SnowflakeClient
```python
class SnowflakeClient:
    def __init__(self, config: Dict[str, Any])
    def connect(self) -> SnowflakeConnection
    def disconnect(self)
    def execute_query_with_columns(self, query: str) -> Tuple[List[str], List[tuple]]
```

#### QueryProcessor
```python
class QueryProcessor:
    def __init__(self, config: Dict[str, Any])
    def process_query(self, query: str) -> QueryInfo
    def parse_query(self, query: str) -> QueryInfo
```

#### InteractiveTableViewer
```python
class InteractiveTableViewer:
    def __init__(self)
    def display_interactive_table(self, results: List[tuple], columns: List[str])
    def _create_scrolled_table(self, results: List[tuple], columns: List[str]) -> Table
```

## 🤝 Contributing

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings
- Add unit tests

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Update documentation
6. Submit pull request

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered

---

For more information, see the [main README](README.md) or [user guide](USER_GUIDE.md).
