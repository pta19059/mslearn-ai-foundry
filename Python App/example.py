#!/usr/bin/env python3
"""
Azure AI Foundry Weather Agent Example

This script demonstrates how to use the Azure AI Foundry Weather Agent Client
with best practices including DefaultAzureCredential authentication.

Features demonstrated:
- Secure authentication with DefaultAzureCredential
- Proper error handling and logging
- Resource cleanup with context managers
- Configuration via environment variables
"""

import os
import logging
from ai_foundry_weather_client import create_ai_foundry_weather_client, AIFoundryWeatherAgentError


def main():
    """Main example function for Azure AI Foundry weather agent."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Azure AI Foundry configuration
    connection_string = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING")
    assistant_id = os.getenv("ASSISTANT_ID", "asst_14scpW964zK5TSFzjpdek9jG")
    
    if not connection_string or connection_string == "your_project_connection_string_here":
        print("❌ Missing Azure AI Foundry configuration!")
        print("Please set the following environment variable:")
        print("- AZURE_AI_PROJECT_CONNECTION_STRING")
        print("\nExample:")
        print("set AZURE_AI_PROJECT_CONNECTION_STRING=your_actual_connection_string")
        print("\nTo get your connection string:")
        print("1. Go to Azure AI Foundry portal")
        print("2. Navigate to your project")
        print("3. Go to Project settings > General")
        print("4. Copy the connection string")
        return
    
    # Sample cities to test
    cities = ["Milan", "Rome", "London"]
    
    try:
        # Create AI Foundry weather client
        with create_ai_foundry_weather_client(
            project_connection_string=connection_string,
            assistant_id=assistant_id,
            timeout=60,
            max_retries=3
        ) as client:
            print("🤖 Azure AI Foundry Weather Agent Example")
            print("=" * 42)
            print(f"Using Assistant: {assistant_id}")
            print(f"Authentication: DefaultAzureCredential")
            
            for city in cities:
                try:
                    print(f"\n🔄 Getting weather for {city}...")
                    
                    # Get weather information from Azure AI Foundry agent
                    weather = client.get_weather(city)
                    
                    # Display results
                    print(f"✅ {weather.city}:")
                    print(f"   🌡️  Temperature: {weather.temperature}")
                    print(f"   ☁️  Condition: {weather.condition}")
                    print(f"   💧 Humidity: {weather.humidity}")
                    
                except AIFoundryWeatherAgentError as e:
                    print(f"❌ Error getting weather for {city}: {e}")
                    if e.error_code:
                        print(f"   Error code: {e.error_code}")
                    
                except Exception as e:
                    print(f"❌ Unexpected error for {city}: {e}")
                    
            print(f"\n✨ Azure AI Foundry example completed!")
            
    except Exception as e:
        logger.error(f"Failed to create AI Foundry weather client: {e}")
        print(f"❌ Failed to initialize AI Foundry client: {e}")
        print("\nTroubleshooting:")
        print("1. Verify your AZURE_AI_PROJECT_CONNECTION_STRING is correct")
        print("2. Ensure you have proper Azure authentication configured")
        print("3. Check that the assistant ID exists in your project")
        print("4. Verify network connectivity to Azure")


if __name__ == "__main__":
    main()
