# Winter - User Guide

## 📚 Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Configuration](#configuration)
3. [Basic Usage](#basic-usage)
4. [Interactive Table Viewer](#interactive-table-viewer)
5. [Query History & Favorites](#query-history--favorites)
6. [Export Functionality](#export-functionality)
7. [Security Features](#security-features)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Snowflake account with RSA keypair authentication
- Modern terminal (iTerm2, Terminal.app, Windows Terminal)

### Installation
```bash
# Install from source
git clone https://github.com/your-org/winter.git
cd winter
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Initial Setup
```bash
# Run the interactive setup wizard
winter setup
```

The setup wizard will guide you through:
1. Snowflake account configuration
2. Private key file setup
3. Default warehouse, database, schema, and role
4. Table prefix configuration
5. Security settings

## ⚙️ Configuration

### Configuration File Location
`~/.snowflake/config.yaml`

### Configuration Options
```yaml
# Snowflake connection details
account: your_account.snowflakecomputing.com
user: your_username
private_key_path: ~/.snowflake/rsa_key.p8

# Default warehouse, database, schema, role
warehouse: COMPUTE_WH
database: YOUR_DATABASE
schema: PUBLIC
role: YOUR_ROLE

# Table prefix (applied to all table references)
table_prefix: "prod_"

# Security settings
security:
  allowed_all_query_types: false  # Default: SELECT-only
  audit_logging: true
  blocked_schemas: ["SENSITIVE", "PRIVATE"]
  allowed_schemas: ["PUBLIC", "ANALYTICS"]
```

### Private Key Setup
1. Generate RSA keypair in Snowflake
2. Download the private key (.p8 file)
3. Place it in `~/.snowflake/` directory
4. Set proper permissions: `chmod 600 ~/.snowflake/rsa_key.p8`

## 📖 Basic Usage

### Command Structure
```bash
winter <command> [options] [arguments]
```

### Available Commands
```bash
# Query execution (default: 10 rows, 5 columns)
winter execute-query "SELECT * FROM users"
winter execute-query "SELECT * FROM users" --interactive
winter execute-query "SELECT * FROM users" --limit 50 --max-columns 8

# Query analysis
winter parse-query "SELECT * FROM users u JOIN orders o ON u.id = o.user_id"
winter validate-query "SELECT * FROM users"
winter query-summary "SELECT * FROM users"

# Connection management
winter connect
winter disconnect
winter test-connection
winter connection-info

# Security
winter security-status
winter audit-log
winter security-test
winter security-config

# History & Favorites
winter history
winter search-history "users"
winter favorites
winter add-favorite "user_summary" "SELECT id, name FROM users"
winter manage-favorites

# Export
winter export-query "SELECT * FROM users" --format csv
winter export-all "SELECT * FROM users"
```

## 🎮 Interactive Table Viewer

### Starting Interactive Mode
```bash
winter execute-query "SELECT * FROM large_table" --interactive
```

### Navigation Controls
- **Arrow Keys**: Navigate without pressing Enter
  - `←` / `→`: Scroll horizontally OR smart pagination
  - `↑` / `↓`: Scroll vertically (up/down)
- **WASD Keys**: Alternative navigation
  - `W`: Up
  - `A`: Left  
  - `S`: Down
  - `D`: Right
- **Special Keys**:
  - `i`: Show column information and data types
  - `h`: Show help
  - `q`: Quit interactive mode

### Smart Pagination
When you reach the boundaries of the current view:
- **`→` at last columns**: Automatically shows next page of data
- **`←` at first columns**: Automatically shows previous page of data

This allows seamless navigation through large datasets without needing separate pagination controls.

### Features
- **Consistent Column Widths**: Prevents header "heaping"
- **Intelligent Formatting**: Automatic data type detection
- **Color Coding**: Different colors for different data types
- **Column Analysis**: Press `i` to see detailed column statistics
- **Smooth Scrolling**: Navigate large datasets easily

### Data Type Colors
- 📅 **DateTime**: Cyan
- 📆 **Date**: Green
- 🔢 **Integer**: Magenta
- 💰 **Decimal**: Yellow
- ✅ **Boolean**: Blue
- 📝 **Text**: White

## 📝 Query History & Favorites

### Query History
All executed queries are automatically logged with:
- Execution timestamp
- Query text
- Execution time
- Rows returned
- Columns count
- Success/failure status
- Error messages (if any)

```bash
# View recent history
winter history

# View more entries
winter history --limit 50

# Search history
winter search-history "users"
winter search-history "JOIN"
```

### Favorites System
Save frequently used queries with names, descriptions, and tags:

```bash
# Add favorite
winter add-favorite "user_summary" "SELECT id, name, email FROM users" --description "User summary query" --tags "users,summary"

# View favorites
winter favorites

# Search favorites
winter search-favorites "users"

# Interactive management
winter manage-favorites
```

### Interactive Favorite Manager
```bash
winter manage-favorites
```

Options:
1. View favorites
2. Add favorite
3. Search favorites
4. Delete favorite
5. Back to main menu

## 📁 Export Functionality

### Supported Formats
- **CSV**: Comma-separated values
- **JSON**: Structured JSON with metadata
- **Excel (XLSX)**: Full Excel format

### Export Commands
```bash
# Single format export
winter export-query "SELECT * FROM users" --format csv
winter export-query "SELECT * FROM users" --format json
winter export-query "SELECT * FROM users" --format xlsx

# Custom filename
winter export-query "SELECT * FROM users" --format csv --output "my_data"

# Multiple formats
winter export-all "SELECT * FROM users"

# With row limit
winter export-query "SELECT * FROM users" --limit 1000
```

### Export Location
Files are saved to: `~/Downloads/winter_exports/`

## 🔒 Security Features

### Default Security
- **SELECT-only**: Only SELECT queries allowed by default
- **Audit Logging**: All queries are logged
- **Schema Control**: Block or allow specific schemas

### Security Commands
```bash
# Check security status
winter security-status

# View audit log
winter audit-log

# Test security controls
winter security-test

# Configure security
winter security-config
```

### Enabling All Query Types
To allow INSERT, UPDATE, DELETE, etc.:
1. Edit `~/.snowflake/config.yaml`
2. Set `allowed_all_query_types: true`
3. Restart Winter

## 🔧 Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Test connection
winter test-connection

# Check connection info
winter connection-info

# Verify configuration
cat ~/.snowflake/config.yaml
```

#### Private Key Issues
```bash
# Check key file permissions
ls -la ~/.snowflake/rsa_key.p8

# Fix permissions
chmod 600 ~/.snowflake/rsa_key.p8

# Verify key format
head -1 ~/.snowflake/rsa_key.p8
# Should show: -----BEGIN PRIVATE KEY----- or -----BEGIN RSA PRIVATE KEY-----
```

#### Table Display Issues
- **Headers "heaping"**: Fixed in latest version with consistent column widths
- **Column stacking**: Fixed with proper horizontal scrolling
- **Input not working**: Use arrow keys or WASD, no Enter needed

#### Export Issues
- **Permission denied**: Check write permissions to `~/Downloads/winter_exports/`
- **File not found**: Ensure the export directory exists
- **Large files**: Use `--limit` option to limit rows

### Debug Mode
```bash
# Run with verbose output
python3 run_winter.py execute-query "SELECT 1" --verbose
```

## 🚀 Advanced Usage

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

### Complex Query Examples
```sql
-- CTE with multiple joins
WITH user_stats AS (
  SELECT u.id, COUNT(o.id) as order_count, SUM(o.total) as total_spent
  FROM users u
  LEFT JOIN orders o ON u.id = o.user_id
  GROUP BY u.id
)
SELECT us.*, u.name, u.email
FROM user_stats us
JOIN users u ON us.id = u.id
WHERE us.order_count > 5
ORDER BY us.total_spent DESC;

-- Subquery with window functions
SELECT 
  user_id,
  order_date,
  total,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY order_date DESC) as rn
FROM (
  SELECT o.user_id, o.order_date, o.total
  FROM orders o
  WHERE o.order_date >= '2023-01-01'
) recent_orders
WHERE rn <= 5;
```

### Performance Tips
1. **Use LIMIT**: Always use LIMIT for large result sets
2. **Limit Columns**: Use `--max-columns` for wide tables
3. **Interactive Mode**: Use `--interactive` for large datasets
4. **Export**: Use export for very large result sets

### Best Practices
1. **Security**: Keep `allowed_all_query_types: false` for production
2. **Prefixes**: Use meaningful prefixes for different environments
3. **History**: Regularly review query history for optimization
4. **Favorites**: Save commonly used queries as favorites
5. **Export**: Use appropriate export formats for your needs

---

For more information, visit the [GitHub repository](https://github.com/your-org/winter) or open an issue for support.
