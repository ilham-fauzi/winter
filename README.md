# Winter - Snowflake Terminal Client

❄️ **Winter** is a powerful q

## ✨ Features

- 🔐 **Dual Authentication Support** - Password authentication or RSA keypair authentication (.p8 private keys)
- 🔍 **File Browser** - Interactive file browser for selecting private key files during setup
- 🏷️ **Table Prefix System** - Automatic prefix application to all table references (JOINs, subqueries, CTEs, DML, DDL)
- 🔒 **Security Controls** - Default SELECT-only with configurable permissions and audit logging
- ⏰ **Connection Timeout** - Automatic connection timeout after 5 minutes of inactivity
- 🔌 **Mandatory Connection** - Must run `winter connect` before executing queries for better security
- 📊 **Interactive Table Display** - Smooth vertical and horizontal scrolling with Rich tables
- 🎮 **Advanced Scrolling** - Arrow keys and WASD navigation without Enter key
- 📈 **Data Analysis** - Intelligent column formatting and data type detection
- 📁 **Export Capabilities** - Export to CSV, JSON, and Excel (XLSX) formats
- 📝 **Query History** - Automatic logging and searchable query history
- ⭐ **Favorites System** - Save and manage favorite queries with tags
- 🔍 **Search Functionality** - Search through history and favorites
- 🌍 **Multi-Environment Support** - Support for different environments
- ⚡ **High Performance** - Optimized for speed and efficiency

## 🚀 Quick Start

```bash
# Install Winter
pip install winter

# Run interactive setup wizard
winter setup

# Connect to Snowflake (mandatory before queries)
winter connect

# Execute your first query (default: 10 rows, 5 columns)
winter execute-query "SELECT * FROM users"

# Use interactive table viewer
winter execute-query "SELECT * FROM users" --interactive

# Custom limits
winter execute-query "SELECT * FROM users" --limit 50 --max-columns 8

# View query history
winter history

# Manage favorite queries
winter manage-favorites
```

## 📦 Installation

### From Source
```bash
git clone https://github.com/your-org/winter.git
cd winter
pip install -e .
```

### Development Installation
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## ⚙️ Configuration

Winter uses `~/.winter/config.yaml` for configuration and supports two authentication methods:

### 🔐 Authentication Methods

#### 1. Password Authentication
```yaml
account: your_account.snowflakecomputing.com
user: your_username
auth_method: password
password: your_password  # Optional: leave empty to prompt each time
warehouse: COMPUTE_WH
database: YOUR_DB
schema: PUBLIC
role: YOUR_ROLE
connection_timeout: 5  # Minutes (or use hours: 0.5 = 30 minutes)
```

#### 2. RSA Keypair Authentication
```yaml
account: your_account.snowflakecomputing.com
user: your_username
auth_method: keypair
private_key_path: ~/.snowflake/rsa_key.p8
warehouse: COMPUTE_WH
database: YOUR_DB
schema: PUBLIC
role: YOUR_ROLE
connection_timeout: 5  # Minutes (or use hours: 0.5 = 30 minutes)
```

### 🔒 Security Configuration

**SELECT-Only Enforcement:**
- 🔒 **SELECT-only queries** - Only SELECT statements allowed by default
- 🛡️ **Data protection** - Prevents accidental data modification
- 🔐 **Secure by default** - No DML/DDL operations allowed
- 📝 **Audit logging** - All queries are logged for security

### 🔍 File Browser for Private Key Setup

**Interactive File Selection:**
- 🔍 **File browser** - Navigate directories to find .p8 files
- 📁 **Smart navigation** - Start from Downloads directory
- 📄 **File filtering** - Only shows .p8 files and directories
- 📊 **File information** - Shows file size and details
- ✅ **Auto-copy** - Automatically copies selected file to `~/.winter/rsa_key.p8`
- 🔍 **Manual search** - Search for .p8 files in specific directories

**Search Options:**
- 📥 **Downloads directory** - Search in Downloads folder
- 🖥️ **Desktop directory** - Search in Desktop folder  
- 📄 **Documents directory** - Search in Documents folder
- 🏠 **Home directory** - Search in entire home directory
- 📁 **Custom directory** - Search in user-specified directory
- 🔄 **Recursive search** - Finds .p8 files in subdirectories

**Setup Flow:**
```bash
winter setup

# Choose RSA Keypair Authentication
# Choose "Browse for .p8 file (Recommended)"
# Navigate directories OR type 'search' for manual search
# Select your .p8 file
# File automatically copied to ~/.winter/rsa_key.p8
```

### ⏰ Connection Timeout Configuration

**Configurable Timeout:**
- **Minutes**: `connection_timeout: 5` (5 minutes)
- **Hours**: `connection_timeout: 0.5` (30 minutes)
- **Default**: 5 minutes if not specified

**Password Caching:**
- 🔐 **Session-based caching** - Password cached until disconnect/timeout
- 🔒 **Secure storage** - Password only stored in memory during session
- ⚡ **Auto-reconnect** - Uses cached password for seamless reconnection
- 🧹 **Auto-clear** - Password cleared on disconnect or timeout

### 🔒 Security Configuration
```yaml
table_prefix: "prod_"  # Applied to all table references
security:
  allowed_all_query_types: false  # Default: SELECT-only
  audit_logging: true
  blocked_schemas: ["SENSITIVE"]
  allowed_schemas: ["PUBLIC", "ANALYTICS"]
```

## 📖 Usage

### Connection Management

```bash
# Connect to Snowflake (mandatory before queries)
winter connect

# Test connection
winter test-connection

# Show connection info
winter connection-info

# Disconnect
winter disconnect
```

**⚠️ Important Notes:**
- You must run `winter connect` before executing any queries
- Connection automatically times out after 5 minutes of inactivity
- If connection expires, run `winter connect` again to reconnect

### Query Execution

```bash
# Basic query execution (default: 10 rows, 5 columns)
# Note: Must run 'winter connect' first
winter execute-query "SELECT * FROM users"

# Interactive table viewer with scrolling
winter execute-query "SELECT * FROM users" --interactive

# Limit rows and columns
winter execute-query "SELECT * FROM users" --limit 50 --max-columns 8

# Query with custom prefix
winter execute-query "SELECT * FROM users" --prefix "dev_"
```

### Table Prefix System

The prefix system automatically applies prefixes to all table references:

```sql
-- Input query
SELECT u.name, o.total 
FROM users u 
JOIN orders o ON u.id = o.user_id

-- With prefix "prod_" becomes:
SELECT u.name, o.total 
FROM prod_users u 
JOIN prod_orders o ON u.id = o.user_id
```

**Prefix Rules:**
- ✅ Applied to: `FROM`, `JOIN`, `UPDATE`, `INSERT INTO`, `DELETE FROM`, `TRUNCATE TABLE`
- ✅ Applied to: Subqueries, CTEs, DML, DDL statements
- ❌ Not applied to: Schema-qualified tables (`schema.table`)
- ❌ Not applied to: Database-qualified tables (`db.schema.table`)
- ❌ Not applied to: Aliased tables (preserves original alias format)

### Interactive Table Viewer

```bash
# Enable interactive mode
winter execute-query "SELECT * FROM large_table" --interactive

# Navigation controls:
# ←/→ : Scroll horizontally OR smart pagination
# ↑/↓ : Scroll vertically (up/down)
# WASD : Alternative navigation (W=up, A=left, S=down, D=right)
# i    : Show column information and data types
# q    : Quit interactive mode
# h    : Show help

# Smart Pagination:
# → at last columns = Next page of data
# ← at first columns = Previous page of data
```

### Export Functionality

```bash
# Export to single format
winter export-query "SELECT * FROM users" --format csv
winter export-query "SELECT * FROM users" --format json
winter export-query "SELECT * FROM users" --format xlsx

# Export with custom filename
winter export-query "SELECT * FROM users" --format csv --output "my_data"

# Export to multiple formats
winter export-all "SELECT * FROM users"

# Export with row limit
winter export-query "SELECT * FROM users" --limit 1000
```

### Query History & Favorites

```bash
# View query history
winter history
winter history --limit 50

# Search query history
winter search-history "users"
winter search-history "JOIN"

# View favorite queries
winter favorites

# Add favorite query
winter add-favorite "user_summary" "SELECT id, name, email FROM users" --description "User summary query" --tags "users,summary"

# Search favorites
winter search-favorites "users"

# Delete favorite
winter delete-favorite 1

# Interactive favorite manager
winter manage-favorites
```

### Security Management

```bash
# Check security status
winter security-status

# View audit log
winter audit-log

# Test security controls
winter security-test

# Configure security settings
winter security-config
```

### Connection Management

```bash
# Test connection
winter test-connection

# Show connection info
winter connection-info

# Connect to Snowflake
winter connect

# Disconnect
winter disconnect
```

### Query Analysis

```bash
# Parse and analyze query
winter parse-query "SELECT * FROM users u JOIN orders o ON u.id = o.user_id"

# Validate query
winter validate-query "SELECT * FROM users"

# Show query summary
winter query-summary "SELECT * FROM users"
```

## 🎮 Interactive Controls

### Table Navigation
- **Arrow Keys**: Navigate without Enter key
- **WASD**: Alternative navigation
- **Mouse Wheel**: Scroll in terminal
- **Column Info**: Press `i` to see data types and statistics
- **Help**: Press `h` for help

### Data Display
- **Consistent Column Widths**: Prevents header "heaping"
- **Intelligent Formatting**: Automatic data type detection
- **Color Coding**: Different colors for different data types
- **Truncation**: Long values are truncated with ellipsis

## 📊 Data Types Supported

- 📅 **DateTime**: Cyan color, formatted display
- 📆 **Date**: Green color, formatted display  
- 🔢 **Integer**: Magenta color, right-aligned
- 💰 **Decimal**: Yellow color, formatted numbers
- ✅ **Boolean**: Blue color, true/false display
- 📝 **Text**: White color, standard display

## 🔧 Advanced Features

### Column Analysis
- Automatic data type detection
- Null value counting
- Unique value analysis
- Sample value display
- Optimal column width suggestions

### Export Formats
- **CSV**: Standard comma-separated values
- **JSON**: Structured JSON with metadata
- **Excel (XLSX)**: Full Excel format with formatting

### Security Features
- Query type validation (SELECT-only by default)
- Schema access control
- Audit logging
- Session management
- Dangerous function blocking

## 📁 File Structure

```
winter/
├── __init__.py
├── main.py                 # CLI entry point
├── cli/                    # CLI components
├── snowflake/              # Snowflake connection
├── query/                  # Query processing and prefix system
├── security/               # Security controls
├── ui/                     # Interactive table viewer
├── formatters/             # Data formatting and analysis
├── export/                 # Export functionality
├── history/                # Query history and favorites
├── setup/                  # Setup wizard
└── utils/                  # Utility functions
```

## 🛠️ Development

### Running Locally
```bash
# From project root
python3 run_winter.py execute-query "SELECT 1"

# Or install in development mode
pip install -e .
winter execute-query "SELECT 1"
```

### Testing
```bash
# Run all tests
python3 test_winter.py

# Run specific test modules
python3 -m pytest tests/test_query.py
python3 -m pytest tests/test_snowflake.py
```

### Requirements

- **Python**: 3.8+
- **Dependencies**:
  - `snowflake-connector-python>=3.0.0`
  - `cryptography>=3.4.8`
  - `pyyaml>=6.0`
  - `rich>=13.0.0`
  - `click>=8.0.0`
  - `inquirer>=3.0.0`
  - `pandas>=1.5.0`
  - `openpyxl>=3.0.0`

## 🔐 Security

- **RSA Keypair Authentication**: Secure .p8 key authentication
- **SELECT-only by Default**: Prevents accidental data modification
- **Schema Access Control**: Block or allow specific schemas
- **Audit Logging**: Track all query executions
- **Session Management**: Secure session handling

## 📝 Examples

### Complex Query with Prefixes
```sql
-- Input
WITH user_stats AS (
  SELECT u.id, COUNT(o.id) as order_count
  FROM users u
  LEFT JOIN orders o ON u.id = o.user_id
  GROUP BY u.id
)
SELECT us.*, u.name
FROM user_stats us
JOIN users u ON us.id = u.id
WHERE us.order_count > 5

-- With prefix "prod_" becomes:
WITH user_stats AS (
  SELECT u.id, COUNT(o.id) as order_count
  FROM prod_users u
  LEFT JOIN prod_orders o ON u.id = o.user_id
  GROUP BY u.id
)
SELECT us.*, u.name
FROM user_stats us
JOIN prod_users u ON us.id = u.id
WHERE us.order_count > 5
```

### Interactive Table Usage
```bash
# Start interactive session
winter execute-query "SELECT * FROM large_table" --interactive

# Navigate with arrow keys
# Press 'i' to see column information
# Press 'h' for help
# Press 'q' to quit
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/winter/issues)
- **Documentation**: [Wiki](https://github.com/your-org/winter/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/winter/discussions)

## 🎯 Roadmap

- [ ] Query result caching
- [ ] Advanced query templates
- [ ] Multi-database support
- [ ] Query performance analysis
- [ ] Custom themes and styling
- [ ] Plugin system for extensions

---

**Winter** - Making Snowflake terminal access powerful and intuitive! ❄️