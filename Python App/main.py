#!/usr/bin/env python3
"""
Azure AI Foundry Weather Agent CLI Application

A command-line interface for interacting with the Weather Agent using
Azure AI Foundry SDK with best practices including:
- DefaultAzureCredential for secure authentication
- Azure AI Foundry project endpoint
- Proper error handling and retry logic
- Comprehensive logging

Usage:
    python main.py [OPTIONS] CITY

Examples:
    python main.py weather Milan
    python main.py weather "New York" --verbose
    python main.py weather London --timeout 120
"""

import os
import sys
import logging

import click
from dotenv import load_dotenv

from ai_foundry_weather_client import (
    AIFoundryWeatherAgentClient,
    AIFoundryConfig,
    AIFoundryWeatherAgentError,
    create_ai_foundry_weather_client
)


# Load environment variables
load_dotenv()


def setup_logging(verbose: bool) -> None:
    """
    Configure logging based on verbosity level.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True  # Override existing configuration
    )


def get_project_endpoint() -> str:
    """
    Get the Azure AI Foundry project endpoint from environment variables.
    
    Returns:
        Project endpoint URL
        
    Raises:
        SystemExit: If endpoint is not configured
    """
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    if not endpoint or endpoint == "https://your-ai-project.cognitiveservices.azure.com/":
        click.echo("❌ Azure AI Foundry project endpoint not configured!", err=True)
        click.echo("Please set AZURE_AI_PROJECT_ENDPOINT in your .env file", err=True)
        click.echo("\nExample:", err=True)
        click.echo("AZURE_AI_PROJECT_ENDPOINT=https://your-ai-project.cognitiveservices.azure.com/", err=True)
        sys.exit(1)
    
    return endpoint


def get_assistant_id() -> str:
    """
    Get the assistant ID from environment variables.
    
    Returns:
        Assistant ID string
    """
    return os.getenv("ASSISTANT_ID", "asst_14scpW964zK5TSFzjpdek9jG")


def format_weather_output(weather_data, city_input: str) -> str:
    """
    Format weather data for display.
    
    Args:
        weather_data: Weather result from the AI agent
        city_input: Original city input from user
        
    Returns:
        Formatted weather information string
    """
    return f"""
🌤️  Weather Information for {weather_data.city}
{'=' * (25 + len(weather_data.city))}

🌡️  Temperature: {weather_data.temperature}
☁️  Condition:   {weather_data.condition}
💧 Humidity:    {weather_data.humidity}

Requested city: {city_input}
Resolved city:  {weather_data.city}
"""


@click.group()
def cli():
    """Azure AI Foundry Weather Agent CLI Application."""
    pass


@cli.command()
@click.argument('city', type=str)
@click.option(
    '--timeout',
    type=int,
    default=None,
    help='Request timeout in seconds (default from env or 60s)'
)
@click.option(
    '--retries',
    type=int,
    default=None,
    help='Maximum number of retry attempts (default from env or 3)'
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Enable verbose logging'
)
@click.option(
    '--raw',
    is_flag=True,
    help='Output raw JSON response'
)
def weather(
    city: str,
    timeout: int,
    retries: int,
    verbose: bool,
    raw: bool
) -> None:
    """
    Get weather information for a specified CITY using Azure AI Foundry.
    
    This command connects to Azure AI Foundry and uses the weather agent
    to retrieve current weather conditions for the specified city.
    
    CITY: Name of the city to get weather information for
    """
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Get configuration
        endpoint = get_project_endpoint()
        assistant_id = get_assistant_id()
        
        # Use environment defaults if not specified
        if timeout is None:
            timeout = int(os.getenv("REQUEST_TIMEOUT", "60"))
        if retries is None:
            retries = int(os.getenv("MAX_RETRIES", "3"))
        
        logger.info(f"Using Azure AI Foundry assistant: {assistant_id}")
        logger.debug(f"Configuration: timeout={timeout}s, retries={retries}")
        
        # Create AI Foundry client configuration
        config = AIFoundryConfig(
            endpoint=endpoint,
            assistant_id=assistant_id,
            timeout=timeout,
            max_retries=retries
        )
        
        # Use context manager for proper resource cleanup
        with AIFoundryWeatherAgentClient(config) as client:
            click.echo(f"🤖 Getting weather for {city} using Azure AI Foundry...")
            
            # Get weather information
            weather_data = client.get_weather(city=city)
            
            if raw:
                # Output raw data as JSON
                import json
                raw_data = {
                    "city": weather_data.city,
                    "temperature": weather_data.temperature,
                    "condition": weather_data.condition,
                    "humidity": weather_data.humidity,
                    "source": "azure_ai_foundry",
                    "assistant_id": assistant_id
                }
                click.echo(json.dumps(raw_data, indent=2))
            else:
                # Output formatted weather information
                formatted_output = format_weather_output(weather_data, city)
                click.echo(formatted_output + f"\n🤖 Source: Azure AI Foundry Agent ({assistant_id})")
            
            logger.info("Weather information retrieved successfully from Azure AI Foundry")
            
    except AIFoundryWeatherAgentError as e:
        error_msg = f"AI Foundry Agent Error: {e}"
        if e.error_code:
            error_msg += f" (Code: {e.error_code})"
        
        logger.error(error_msg)
        click.echo(f"❌ {error_msg}", err=True)
        
        if verbose and e.response_data:
            click.echo(f"Response data: {e.response_data}", err=True)
        
        sys.exit(1)
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg, exc_info=True)
        click.echo(f"❌ {error_msg}", err=True)
        sys.exit(1)


@click.group()
@click.version_option(version="2.0.0", prog_name="Azure AI Foundry Weather CLI")
def cli():
    """
    Azure AI Foundry Weather Agent CLI Application
    
    A command-line interface for retrieving weather information using
    Azure AI Foundry and the Weather Agent described in Agent214.agent.yaml.
    
    Features:
    - Secure authentication with DefaultAzureCredential
    - Supports Managed Identity, Service Principal, and Interactive auth
    - Comprehensive error handling and retry logic
    - Performance optimizations and resource cleanup
    """
    pass


@cli.command()
def config():
    """Show current configuration and authentication status."""
    endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "NOT SET")
    assistant_id = get_assistant_id()
    timeout = int(os.getenv("REQUEST_TIMEOUT", "60"))
    max_retries = int(os.getenv("MAX_RETRIES", "3"))
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    click.echo("🔧 Azure AI Foundry Configuration:")
    click.echo(f"   Project Endpoint:   {'***configured***' if endpoint != 'NOT SET' and endpoint != 'https://your-ai-project.cognitiveservices.azure.com/' else '❌ NOT SET'}")
    click.echo(f"   Assistant ID:       {assistant_id}")
    click.echo(f"   Timeout:           {timeout}s")
    click.echo(f"   Max Retries:       {max_retries}")
    click.echo(f"   Log Level:         {log_level}")
    
    # Test authentication
    click.echo("\n🔐 Authentication Test:")
    try:
        from azure.identity import DefaultAzureCredential
        credential = DefaultAzureCredential()
        click.echo("   ✅ DefaultAzureCredential initialized")
        
        # Try to get a token (this will test if authentication works)
        try:
            token = credential.get_token("https://management.azure.com/.default")
            click.echo("   ✅ Authentication successful")
        except Exception as e:
            click.echo(f"   ⚠️  Authentication may have issues: {e}")
            
    except ImportError:
        click.echo("   ❌ Azure Identity SDK not available")
    except Exception as e:
        click.echo(f"   ❌ Authentication error: {e}")


@cli.command()
@click.argument('cities', nargs=-1, required=True)
@click.option('--timeout', type=int, default=None, help='Request timeout in seconds')
@click.option('--retries', type=int, default=None, help='Maximum retry attempts')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def batch(cities, timeout: int, retries: int, verbose: bool):
    """
    Get weather information for multiple cities.
    
    CITIES: Space-separated list of city names
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        endpoint = get_project_endpoint()
        assistant_id = get_assistant_id()
        
        # Use environment defaults if not specified
        if timeout is None:
            timeout = int(os.getenv("REQUEST_TIMEOUT", "60"))
        if retries is None:
            retries = int(os.getenv("MAX_RETRIES", "3"))
        
        config = AIFoundryConfig(
            endpoint=endpoint,
            assistant_id=assistant_id,
            timeout=timeout,
            max_retries=retries
        )
        
        results = []
        errors = []
        
        with AIFoundryWeatherAgentClient(config) as client:
            for city in cities:
                try:
                    click.echo(f"🔄 Fetching weather for {city}...")
                    weather_data = client.get_weather(city=city)
                    results.append((city, weather_data))
                    click.echo(f"✅ {city}: {weather_data.temperature}, {weather_data.condition}")
                    
                except AIFoundryWeatherAgentError as e:
                    error_msg = f"{city}: {e}"
                    errors.append(error_msg)
                    click.echo(f"❌ {error_msg}", err=True)
        
        # Summary
        click.echo(f"\n📊 Summary: {len(results)} successful, {len(errors)} failed")
        
        if errors and verbose:
            click.echo("\n❌ Errors:")
            for error in errors:
                click.echo(f"   {error}")
                
    except Exception as e:
        logger.error(f"Batch operation failed: {e}")
        click.echo(f"❌ Batch operation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def test():
    """Test the AI Foundry connection and authentication."""
    setup_logging(True)  # Enable verbose logging for test
    logger = logging.getLogger(__name__)
    
    click.echo("🧪 Testing Azure AI Foundry Connection...")
    
    try:
        # Test configuration
        endpoint = get_project_endpoint()
        assistant_id = get_assistant_id()
        
        click.echo(f"✅ Configuration loaded")
        click.echo(f"   Assistant ID: {assistant_id}")
        
        # Test authentication
        from azure.identity import DefaultAzureCredential
        credential = DefaultAzureCredential()
        click.echo("✅ DefaultAzureCredential initialized")
        
        # Test AI Foundry client creation
        config = AIFoundryConfig(
            endpoint=endpoint,
            assistant_id=assistant_id,
            timeout=30,
            max_retries=1
        )
        
        with AIFoundryWeatherAgentClient(config) as client:
            click.echo("✅ AI Foundry client created successfully")
            
            # Test with a simple city
            test_city = "Milan"
            click.echo(f"🔄 Testing weather request for {test_city}...")
            
            weather_data = client.get_weather(test_city)
            click.echo(f"✅ Test successful!")
            click.echo(f"   City: {weather_data.city}")
            click.echo(f"   Temperature: {weather_data.temperature}")
            click.echo(f"   Condition: {weather_data.condition}")
            click.echo(f"   Humidity: {weather_data.humidity}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        click.echo(f"❌ Test failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def diagnose(verbose: bool):
    """Diagnose agent configuration and connectivity."""
    setup_logging(verbose)
    
    try:
        endpoint = get_project_endpoint()
        assistant_id = get_assistant_id()
        
        config = AIFoundryConfig(
            endpoint=endpoint,
            assistant_id=assistant_id
        )
        
        click.echo("🔍 Diagnosing Azure AI Foundry Agent...")
        
        with AIFoundryWeatherAgentClient(config) as client:
            diagnostics = client.diagnose_agent()
            
            click.echo("\n📋 Diagnostic Results:")
            click.echo(f"   Agent ID:      {diagnostics['agent_id']}")
            click.echo(f"   Endpoint:      {diagnostics['endpoint']}")
            click.echo(f"   Agent Exists:  {'✅ Yes' if diagnostics['agent_exists'] else '❌ No'}")
            
            if diagnostics.get('error'):
                click.echo(f"   ❌ Error:      {diagnostics['error']}")
            
            if diagnostics.get('agent_details'):
                details = diagnostics['agent_details']
                click.echo("\n🤖 Agent Details:")
                click.echo(f"   Name:         {details.get('name', 'Unknown')}")
                click.echo(f"   Description:  {details.get('description', 'Unknown')}")
                click.echo(f"   Model:        {details.get('model', 'Unknown')}")
                click.echo(f"   Tools:        {len(details.get('tools', []))} tools configured")
                
                if verbose and details.get('tools'):
                    click.echo("\n🔧 Tools:")
                    for i, tool in enumerate(details['tools'], 1):
                        tool_type = tool.get('type', 'unknown') if isinstance(tool, dict) else str(tool)
                        click.echo(f"     {i}. {tool_type}")
        
    except Exception as e:
        click.echo(f"❌ Diagnostic failed: {e}")
        if verbose:
            import traceback
            click.echo(f"\nFull error:\n{traceback.format_exc()}")


# Add the commands to the CLI group
cli.add_command(weather)
cli.add_command(config)
cli.add_command(batch)
cli.add_command(diagnose)


if __name__ == '__main__':
    cli()
