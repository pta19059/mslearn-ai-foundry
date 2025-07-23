# Virtual Environment Guide - Azure AI Foundry Weather Agent

## 🐍 Virtual Environment Setup

This application uses a **Python virtual environment** to isolate dependencies and ensure compatibility.

### 📋 Prerequisites

- Python 3.8+ installed
- Azure access with configured credentials
- Active Azure AI Foundry project

### 🚀 Initial Setup

1. **Navigate to the project directory:**
   ```bash
   cd "c:\Work\AI Foundry\Python App"
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv azure_ai_env
   ```

3. **The virtual environment structure:**
   ```
   azure_ai_env/
   ├── Scripts/
   │   ├── activate.bat    # Activation script
   │   ├── python.exe      # Isolated Python
   │   └── pip.exe         # Package manager
   └── Lib/                # Installed libraries
   ```

### ✅ Daily Usage

#### Virtual Environment Activation

**Windows:**
```bash
azure_ai_env\Scripts\activate
```

**Verify activation:**
```bash
# The prompt should show (azure_ai_env)
python --version
where python  # Should point to the venv
```

#### Running the App

```bash
# Activate the virtual environment
azure_ai_env\Scripts\activate

# Run app commands
python main.py weather Milan
python main.py weather Rome --verbose
```

#### Deactivation

```bash
deactivate
```

### 📦 Dependency Management

#### Installed Packages

The virtual environment contains:
- `azure-ai-projects>=1.0.0` - Azure AI Foundry SDK
- `azure-identity>=1.15.0` - Azure authentication
- `azure-core>=1.29.0` - Azure core functionality
- `python-dotenv>=1.0.0` - Environment variable management
- `click>=8.1.0` - CLI framework
- `pydantic>=2.0.0` - Data validation

#### Installing Additional Packages

```bash
# Activate the virtual environment
azure_ai_env\Scripts\activate

# Install additional packages
pip install package-name

# Update requirements file
pip freeze > requirements_foundry.txt
```

#### Recreating the Environment

```bash
# Remove existing environment
rmdir /s azure_ai_env

# Create new environment
python -m venv azure_ai_env

# Activate and install dependencies
azure_ai_env\Scripts\activate
pip install -r requirements_foundry.txt
```

### 🔧 Azure AI Foundry Configuration

#### .env File
```bash
# Azure AI Foundry Configuration
AZURE_AI_PROJECT_CONNECTION_STRING=your_project_connection_string_here
ASSISTANT_ID=asst_14scpW964zK5TSFzjpdek9jG

# Optional settings
LOG_LEVEL=INFO
REQUEST_TIMEOUT=120
MAX_RETRIES=3
```

#### Authentication

The app uses **DefaultAzureCredential** which supports:

1. **Environment Variables** (AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID)
2. **Managed Identity** (when running on Azure)
3. **Azure CLI** (`az login`)
4. **Visual Studio Code** (when signed in)
5. **Azure PowerShell** (when signed in)
6. **Interactive Browser** (if configured)

### 🧪 Testing and Debug

#### Configuration Test
```bash
azure_ai_env\Scripts\activate
python test_setup.py
```

Expected output:
```
🔧 Azure AI Foundry Configuration:
   Project Connection: ***configured***
   Assistant ID:       asst_14scpW964zK5TSFzjpdek9jG
   Timeout:           120s
   Max Retries:       3
   Log Level:         INFO
🔐 Authentication Test:
   ✅ DefaultAzureCredential initialized
   ✅ Authentication successful
```

#### Functionality Test
```bash
azure_ai_env\Scripts\activate
python main.py weather Milan --verbose
```

#### Import Debug
```bash
azure_ai_env\Scripts\activate
python -c "
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from ai_foundry_weather_client import AIFoundryWeatherAgentClient
print('✅ All imports successful!')
"
```

### 🚨 Troubleshooting

#### Problem: "ModuleNotFoundError"
```bash
# Verify that the virtual environment is active
azure_ai_env\Scripts\activate

# Reinstall dependencies
pip install -r requirements_foundry.txt
```

#### Problem: "Authentication failed"
```bash
# Verify Azure CLI credentials
az login
az account show

# Test authentication
python test_setup.py
```

#### Problem: "AIProjectClient has no attribute..."
```bash
# Check SDK version
pip show azure-ai-projects

# Update if necessary
pip install --upgrade azure-ai-projects
```

#### Problem: "Connection timeout"
```bash
# Increase timeout in .env file
REQUEST_TIMEOUT=180

# Or use command line option
python main.py weather Milan --timeout 180
```

### 📝 Best Practices

1. **Always activate the virtual environment** before running the app
2. **Don't commit the azure_ai_env/ folder** to version control
3. **Keep requirements_foundry.txt updated** after changes
4. **Use environment variables** for sensitive credentials
5. **Test configuration regularly** with Azure
6. **Use DefaultAzureCredential** for production deployments

### 🔄 Complete Workflow

```bash
# 1. Activate environment
azure_ai_env\Scripts\activate

# 2. Verify configuration
python test_setup.py

# 3. Test functionality
python main.py weather Milan

# 4. Debug if necessary
python main.py weather Rome --verbose

# 5. Deactivate when done
deactivate
```

### 📊 Monitoring and Logs

#### Log Levels
- `DEBUG`: Complete technical details
- `INFO`: Main operations
- `WARNING`: Situations to monitor
- `ERROR`: Errors requiring attention

#### Enable Debug Mode
```bash
# Modify .env file
LOG_LEVEL=DEBUG

# Or use --verbose flag
python main.py weather Milan --verbose
```

#### Log Output Examples
```bash
# INFO level (default)
[INFO] Getting weather for Milan...
[INFO] Weather retrieved successfully: 22°C, Sunny

# DEBUG level (verbose)
[DEBUG] Initializing DefaultAzureCredential...
[DEBUG] Creating AIProjectClient with connection string: ***
[DEBUG] Sending request to assistant: asst_14scpW964zK5TSFzjpdek9jG
[DEBUG] Response received: {"temperature": "22°C", "condition": "Sunny"}
```

### 🔐 Security Considerations

#### Credential Storage
- **Never hardcode** connection strings or keys
- **Use .env files** for local development
- **Use Azure Key Vault** for production
- **Use Managed Identity** when running on Azure

#### Best Practices
```bash
# Good: Use environment variables
AZURE_AI_PROJECT_CONNECTION_STRING=your_connection_string

# Bad: Hardcoded in source code
# connection_string = "https://your-project.services.ai.azure.com..."
```

---

**Note**: This virtual environment ensures dependency isolation and compatibility with the Azure AI Foundry SDK, following enterprise Python development best practices.
