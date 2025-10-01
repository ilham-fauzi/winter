# Winter Connection Guide

## 🔌 **Snowflake Connection & Authentication**

Winter supports secure connection to Snowflake using RSA keypair authentication.

### **Quick Start**

```bash
# 1. Setup configuration
winter setup

# 2. Test connection
winter test-connection

# 3. Connect to Snowflake
winter connect

# 4. Check connection info
winter connection-info

# 5. Disconnect when done
winter disconnect
```

## 🔑 **Authentication Setup**

### **1. Generate Keypair**

```bash
# Generate private key
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -out ~/.snowflake/rsa_key.p8 -nocrypt

# Extract public key
winter extract-public-key ~/.snowflake/rsa_key.p8
```

### **2. Add Public Key to Snowflake**

```sql
-- Copy the public key output and run in Snowflake
ALTER USER your_username SET RSA_PUBLIC_KEY='MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...';
```

### **3. Configure Winter**

```bash
# Run setup wizard
winter setup

# Or manually edit config
winter config
```

## 🔌 **Connection Commands**

### **Basic Connection**

```bash
# Test connection (connects and disconnects automatically)
winter test-connection

# Connect and keep connection alive
winter connect

# Show current connection info
winter connection-info

# Disconnect
winter disconnect
```

### **Connection Information**

The `winter connection-info` command shows:
- User
- Role
- Warehouse
- Database
- Schema
- Snowflake version
- Account

## ⚙️ **Connection Features**

### **1. Retry Mechanism**
- Automatic retry with exponential backoff
- Configurable retry count (default: 3)
- Clear error messages

### **2. Connection Pooling**
- Support for multiple connections
- Connection manager for different environments
- Automatic connection health checks

### **3. Error Handling**
- Comprehensive error messages
- Connection validation
- Graceful failure handling

### **4. Security**
- RSA keypair authentication only
- No password storage
- Secure file permissions (600)

## 🔧 **Configuration**

### **Connection Parameters**

```yaml
# ~/.snowflake/config.yaml
account: abc12345.snowflakecomputing.com
user: your_username
private_key_path: ~/.snowflake/rsa_key.p8
warehouse: COMPUTE_WH
database: YOUR_DB
schema: PUBLIC
role: YOUR_ROLE
```

### **Connection Options**

```python
# Connection parameters
timeout: 30                    # Connection timeout
login_timeout: 30              # Login timeout
retry_count: 3                 # Retry attempts
retry_delay: 2                  # Initial retry delay
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Connection Failed**
```bash
❌ Connection attempt 1 failed: 250001: Could not connect to Snowflake backend
```

**Solutions:**
- Check account URL format
- Verify network connectivity
- Check Snowflake service status

#### **2. Authentication Failed**
```bash
❌ Authentication failed: Invalid credentials
```

**Solutions:**
- Verify public key is set in Snowflake
- Check private key file exists and is readable
- Ensure correct username

#### **3. Private Key Error**
```bash
❌ Failed to load private key: [Errno 2] No such file or directory
```

**Solutions:**
- Check private key file path
- Verify file permissions (600)
- Ensure file has .p8 extension

### **Debug Commands**

```bash
# Validate configuration
winter validate

# Show current config
winter config

# Test connection with verbose output
winter test-connection
```

## 📊 **Connection Status**

### **Check Connection Health**

```bash
# Show connection info
winter connection-info

# Test if connection is alive
winter connect
# (Connection will show if it's working)
```

### **Connection States**

- **Disconnected**: No active connection
- **Connected**: Active connection to Snowflake
- **Error**: Connection failed or lost

## 🔄 **Connection Management**

### **Multiple Environments**

```bash
# Connect to different environments
winter connect --env production
winter connect --env development
winter connect --env staging
```

### **Connection Pooling**

```python
# Automatic connection management
from winter.snowflake import ConnectionManager

manager = ConnectionManager()
manager.add_connection('prod', prod_config)
manager.add_connection('dev', dev_config)
```

## 🎯 **Best Practices**

### **1. Security**
- Use RSA keypair authentication only
- Keep private keys secure (600 permissions)
- Rotate keys regularly
- Use different keys for different environments

### **2. Connection Management**
- Test connections before use
- Disconnect when done
- Monitor connection health
- Use connection pooling for multiple queries

### **3. Error Handling**
- Always handle connection errors
- Implement retry logic
- Log connection attempts
- Provide user-friendly error messages

## 📈 **Performance**

### **Connection Optimization**
- Connection pooling reduces overhead
- Retry mechanism handles temporary failures
- Timeout settings prevent hanging connections
- Health checks ensure connection validity

### **Monitoring**
- Track connection success rate
- Monitor connection duration
- Log connection errors
- Alert on connection failures

---

**With these connection features, Winter provides reliable and secure access to Snowflake!**
