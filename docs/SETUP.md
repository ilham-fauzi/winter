# Winter Setup Guide

## Quick Start

```bash
# Install Winter
pip install winter

# Run setup wizard
winter setup

# Check configuration
winter config

# Validate configuration
winter validate
```

## Setup Wizard

The setup wizard will guide you through configuring Winter for your Snowflake environment.

### What You'll Need

1. **Snowflake Account Information**
   - Account identifier (e.g., `abc12345.snowflakecomputing.com`)
   - Username
   - Default warehouse name
   - Default database name
   - Default schema (usually `PUBLIC`)
   - Default role

2. **RSA Keypair**
   - Private key file (`.p8` format)
   - Public key (will be generated from private key)

3. **Security Preferences**
   - SELECT-only mode (recommended for production)
   - All queries allowed (for development/testing)

### Setup Process

1. **Run Setup Wizard**
   ```bash
   winter setup
   ```

2. **Fill Configuration Form**
   - Enter your Snowflake account details
   - Choose security level
   - Select your private key file

3. **Generate Public Key**
   ```bash
   winter extract-public-key ~/.snowflake/rsa_key.p8
   ```

4. **Add Public Key to Snowflake**
   ```sql
   ALTER USER your_username SET RSA_PUBLIC_KEY='<paste_public_key_here>';
   ```

5. **Test Connection**
   ```bash
   winter test-connection
   ```

## Configuration Management

### View Configuration
```bash
winter config
```

### Validate Configuration
```bash
winter validate
```

### Reset Configuration
```bash
winter reset
```

## Configuration File

Winter stores configuration in `~/.snowflake/config.yaml`:

```yaml
account: abc12345.snowflakecomputing.com
user: your_username
private_key_path: ~/.snowflake/rsa_key.p8
warehouse: COMPUTE_WH
database: YOUR_DB
schema: PUBLIC
role: YOUR_ROLE
table_prefix: "prod_"
security:
  allowed_all_query_types: false
  audit_logging: true
```

## Security Settings

### SELECT-only Mode (Default)
- Only allows SELECT queries
- Recommended for production environments
- Prevents accidental data modification

### All Queries Allowed
- Allows all SQL operations (SELECT, INSERT, UPDATE, DELETE, etc.)
- Recommended for development/testing environments
- Use with caution in production

## Troubleshooting

### Common Issues

1. **"Config file not found"**
   - Run `winter setup` to create configuration

2. **"Private key file not found"**
   - Ensure your `.p8` file exists and is accessible
   - Check file permissions (should be 600)

3. **"OpenSSL not found"**
   - Install OpenSSL on your system
   - Or generate public key manually

4. **"Invalid configuration"**
   - Run `winter validate` to check configuration
   - Ensure all required fields are present

### File Permissions

Winter automatically sets secure permissions:
- Configuration file: `600` (read/write for owner only)
- Private key file: `600` (read/write for owner only)

## Next Steps

After setup, you can:

1. **Test your connection**
   ```bash
   winter test-connection
   ```

2. **Run your first query**
   ```bash
   winter query "SELECT * FROM information_schema.tables LIMIT 5"
   ```

3. **Explore more features**
   ```bash
   winter --help
   ```
