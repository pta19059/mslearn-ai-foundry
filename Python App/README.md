# Azure AI Foundry Weather Agent Python App

A Python application that interacts with the Weather Agent using Azure AI Foundry SDK. This application leverages **Azure AI Projects** and **DefaultAzureCredential** for secure, production-ready integration with Azure AI services.

## Features

- ✅ **Azure AI Foundry Integration**: Native integration with Azure AI Projects
- ✅ **Secure Authentication**: DefaultAzureCredential for production-ready auth
- ✅ **Retry Logic**: Exponential backoff for transient failures
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Input Validation**: Using Pydantic models for request/response validation
- ✅ **CLI Interface**: Command-line interface for easy interaction
- ✅ **Configuration**: Environment-based configuration management
- ✅ **Logging**: Structured logging with configurable levels
- ✅ **Resource Management**: Proper cleanup with context managers

## Project Structure

```
Python App/
├── main.py                          # CLI application entry point
├── ai_foundry_weather_client.py     # Azure AI Foundry client library
├── example.py                       # Usage example
├── test_setup.py                    # Setup verification script
├── requirements_foundry.txt         # Python dependencies
├── .env.example                     # Environment configuration template
├── PROJECT_SUMMARY.md               # Project overview and features
├── VIRTUAL_ENV_GUIDE.md             # Virtual environment setup guide
└── README.md                        # This file
```

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd "c:\Work\AI Foundry\Python App"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv azure_ai_env
   azure_ai_env\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements_foundry.txt
   ```

4. **Configure Azure AI Foundry credentials:**
   
   Copy `.env.example` to `.env` and update with your Azure AI Project details:
   ```bash
   # Azure AI Foundry Configuration
   AZURE_AI_PROJECT_CONNECTION_STRING=your_project_connection_string_here
   ASSISTANT_ID=asst_14scpW964zK5TSFzjpdek9jG
   
   # Optional: Request configuration
   REQUEST_TIMEOUT=120
   LOG_LEVEL=INFO
   ```

5. **Authenticate with Azure (one of the following):**
   ```bash
   # Option 1: Azure CLI
   az login
   
   # Option 2: Set environment variables for Service Principal
   # AZURE_CLIENT_ID=your_client_id
   # AZURE_CLIENT_SECRET=your_client_secret  
   # AZURE_TENANT_ID=your_tenant_id
   ```

6. **Test the installation:**
   ```bash
   python test_setup.py
   ```

## Usage

### CLI Application

The main application provides a command-line interface for interacting with the weather agent:

#### Get weather for a single city:

```bash
python main.py weather Milan
python main.py weather "New York" --verbose
python main.py weather London --timeout 120
```

#### Get help:
```bash
python main.py --help
python main.py weather --help
```

### Programmatic Usage

You can also use the `AIFoundryWeatherAgentClient` directly in your Python code:

```python
from ai_foundry_weather_client import create_ai_foundry_weather_client, AIFoundryWeatherAgentError

# Create client with Azure AI Foundry
connection_string = "your_project_connection_string"
assistant_id = "asst_14scpW964zK5TSFzjpdek9jG"

with create_ai_foundry_weather_client(connection_string, assistant_id) as client:
    try:
        # Get weather information
        weather = client.get_weather("Milan")
        
        print(f"Temperature in {weather.city}: {weather.temperature}")
        print(f"Condition: {weather.condition}")
        print(f"Humidity: {weather.humidity}")
        
    except AIFoundryWeatherAgentError as e:
        print(f"Error: {e}")
```

### Simple Example

Run the included example script to see basic functionality:

```bash
python example.py
```

## API Reference

### AIFoundryWeatherAgentClient

The main client class for interacting with the weather agent via Azure AI Foundry.

#### Constructor
```python
AIFoundryWeatherAgentClient(config: AIFoundryConfig)
```

#### Methods

**`get_weather(city: str) -> WeatherResult`**
- Get weather information for a specified city
- Returns a `WeatherResult` object with temperature, condition, and humidity
- Raises `AIFoundryWeatherAgentError` on API errors

### AIFoundryConfig

Configuration class for the Azure AI Foundry client.

```python
@dataclass
class AIFoundryConfig:
    connection_string: str          # Azure AI Project connection string
    assistant_id: str               # Assistant ID 
    timeout: int = 120              # Request timeout in seconds
    max_retries: int = 3            # Maximum retry attempts
    backoff_factor: float = 0.5     # Exponential backoff factor
```

### Models

**`WeatherResult`**
```python
class WeatherResult(BaseModel):
    city: str           # Resolved city name
    temperature: str    # Temperature with unit
    condition: str      # Weather condition description
    humidity: str       # Humidity percentage
```

**`AIFoundryWeatherAgentError`**
```python
class AIFoundryWeatherAgentError(Exception):
    """Custom exception for Azure AI Foundry weather agent errors."""
    pass
```

## Configuration

The application can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_AI_PROJECT_CONNECTION_STRING` | Required | Azure AI Project connection string |
| `ASSISTANT_ID` | `asst_14scpW964zK5TSFzjpdek9jG` | Weather Assistant ID |
| `REQUEST_TIMEOUT` | `120` | Request timeout in seconds |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Azure Authentication

The application uses `DefaultAzureCredential` which supports multiple authentication methods:

1. **Environment Variables** (Service Principal)
2. **Managed Identity** (when running on Azure)
3. **Azure CLI** (`az login`)
4. **Visual Studio Code** (when signed in)
5. **Azure PowerShell** (when signed in)

For development, the easiest method is Azure CLI:
```bash
az login
```

## Error Handling

The application implements comprehensive error handling:

- **Azure Authentication Errors**: Credential chain failures with helpful guidance
- **Network Errors**: Connection timeouts, DNS resolution failures
- **Azure AI Service Errors**: Service unavailable, rate limiting
- **API Errors**: Assistant communication errors with detailed context
- **Validation Errors**: Input validation and response format validation
- **Retry Logic**: Automatic retries for transient failures with exponential backoff

## Logging

Structured logging is implemented throughout the application:

- **INFO**: High-level operations and results
- **DEBUG**: Detailed request/response information
- **ERROR**: Error conditions with context
- **WARNING**: Non-fatal issues

Enable verbose logging with the `--verbose` flag or set `LOG_LEVEL=DEBUG` in your environment.

## Security Features

- **DefaultAzureCredential**: Production-ready authentication chain
- **No Hardcoded Credentials**: Uses environment-based configuration
- **Secure Communication**: HTTPS with proper certificate validation
- **Input Validation**: Pydantic models prevent injection attacks
- **Resource Cleanup**: Proper session management and resource cleanup
- **Rate Limiting**: Respects Azure AI service limits with retry backoff

## Azure AI Foundry Integration

This application is designed to work with Azure AI Foundry and the Weather Agent:

- **Agent ID**: `asst_14scpW964zK5TSFzjpdek9jG`
- **Platform**: Azure AI Foundry with AI Projects SDK
- **Authentication**: DefaultAzureCredential for secure access
- **Features**: Native integration with Azure AI services

## Examples

### CLI Examples

```bash
# Basic weather query
python main.py weather Milan

# Verbose output with custom timeout
python main.py weather Tokyo --verbose --timeout 180

# Multiple cities
python main.py weather "San Francisco"
python main.py weather London --verbose
```

### Python Examples

```python
# Basic usage with Azure AI Foundry
from ai_foundry_weather_client import create_ai_foundry_weather_client

connection_string = "your_azure_ai_project_connection_string"
assistant_id = "asst_14scpW964zK5TSFzjpdek9jG"

with create_ai_foundry_weather_client(connection_string, assistant_id) as client:
    weather = client.get_weather("Milan")
    print(f"{weather.city}: {weather.temperature}")

# With custom configuration
from ai_foundry_weather_client import AIFoundryWeatherAgentClient, AIFoundryConfig

config = AIFoundryConfig(
    connection_string="your_connection_string",
    assistant_id="asst_14scpW964zK5TSFzjpdek9jG",
    timeout=180,
    max_retries=5
)

with AIFoundryWeatherAgentClient(config) as client:
    weather = client.get_weather("Rome")
    print(f"Weather in {weather.city}: {weather.condition}")
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure you're logged in with `az login`
   - Verify your Azure AI Project connection string
   - Check that your account has access to the Azure AI Project

2. **Connection Timeout**
   - Increase timeout with `--timeout` option
   - Check network connectivity to Azure
   - Verify the Azure AI Project is accessible

3. **Assistant Errors**
   - Verify the Assistant ID is correct
   - Check that the assistant is deployed and available
   - Use `--verbose` for detailed error information

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements_foundry.txt`
   - Verify Python version compatibility (3.8+)
   - Check that Azure AI Projects SDK is properly installed

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
python main.py weather Milan --verbose
```

Or set environment variable:
```bash
set LOG_LEVEL=DEBUG
python main.py weather Milan
```

### Setup Verification

Use the included test script to verify your setup:

```bash
python test_setup.py
```

## Dependencies

Key dependencies (see `requirements_foundry.txt` for complete list):

- **azure-ai-projects**: Azure AI Foundry SDK
- **azure-identity**: Azure authentication
- **azure-core**: Azure core functionality  
- **click**: CLI framework
- **pydantic**: Data validation
- **python-dotenv**: Environment configuration

## Contributing

To extend or modify this application:

1. **Add new features**: Extend the `AIFoundryWeatherAgentClient` class
2. **Add new CLI commands**: Add commands to the `cli` group in `main.py`
3. **Add validation**: Update the Pydantic models for input/output validation
4. **Add tests**: Create unit tests for the client functionality

## License

This project is created as an example for integrating with Azure AI Foundry and follows Azure development best practices.

---

For more information about Azure AI Foundry, visit the [Azure AI Foundry documentation](https://docs.microsoft.com/azure/ai-foundry/).
