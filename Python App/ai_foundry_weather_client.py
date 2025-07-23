"""
Azure AI Foundry Weather Agent Client

This module provides a client interface to interact with the weather agent
using Azure AI Foundry SDK with best practices including:
- Azure Identity for secure authentication (DefaultAzureCredential)
- Azure AI Foundry project endpoint
- Proper error handling and retry logic
- Structured logging and monitoring
- Resource cleanup and connection management

Best Practices Implemented:
- Use DefaultAzureCredential for authentication (supports Managed Identity, Service Principal, etc.)
- Never hardcode credentials
- Implement retry logic with exponential backoff
- Comprehensive error handling and logging
- Proper resource cleanup
- Input validation using Pydantic models
"""

import json
import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError
from pydantic import BaseModel, Field, field_validator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WeatherRequest(BaseModel):
    """Pydantic model for weather request validation."""
    
    city: str = Field(..., min_length=1, description="City name to get weather for")
    
    @field_validator('city')
    def validate_city(cls, v):
        """Validate city name format."""
        if not v.strip():
            raise ValueError("City name cannot be empty")
        return v.strip()


class WeatherResult(BaseModel):
    """Pydantic model for weather response."""
    
    city: str
    temperature: str
    condition: str
    humidity: str


@dataclass
class AIFoundryConfig:
    """Configuration for the Azure AI Foundry Weather Agent Client."""
    
    endpoint: str
    assistant_id: str = "asst_14scpW964zK5TSFzjpdek9jG"
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0


class AIFoundryWeatherAgentError(Exception):
    """Custom exception for AI Foundry Weather Agent errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.response_data = response_data


class AIFoundryWeatherAgentClient:
    """
    Client for interacting with the Weather Agent using Azure AI Foundry SDK.
    
    This client implements Azure best practices:
    - Uses DefaultAzureCredential for secure authentication
    - Supports Managed Identity, Service Principal, and Interactive authentication
    - Implements retry logic with exponential backoff for transient failures
    - Comprehensive error handling and logging
    - Proper resource cleanup
    - Performance optimizations
    """
    
    def __init__(self, config: AIFoundryConfig):
        """
        Initialize the AI Foundry Weather Agent Client.
        
        Args:
            config: Configuration object containing AI Foundry project details
        """
        self.config = config
        self.credential = DefaultAzureCredential()
        self.client = self._create_client()
        
        logger.info(f"AI Foundry Weather Agent Client initialized for assistant {config.assistant_id}")
        logger.info(f"Using authentication: DefaultAzureCredential")
    
    def _create_client(self) -> AIProjectClient:
        """
        Create and configure an Azure AI Foundry Project client.
        
        Returns:
            Configured Azure AI Project client
        """
        try:
            return AIProjectClient(
                endpoint=self.config.endpoint,
                credential=self.credential
            )
        except Exception as e:
            error_msg = f"Failed to create AI Foundry client: {e}"
            logger.error(error_msg)
            raise AIFoundryWeatherAgentError(error_msg)
    
    def diagnose_agent(self) -> Dict[str, Any]:
        """
        Diagnose the agent configuration and connectivity.
        
        Returns:
            Dictionary with diagnostic information
        """
        diagnostics = {
            "agent_id": self.config.assistant_id,
            "endpoint": self.config.endpoint,
            "agent_exists": False,
            "agent_details": None,
            "error": None
        }
        
        try:
            agents_client = self.client.agents
            
            # Try to get agent details
            try:
                agent = agents_client.get_agent(self.config.assistant_id)
                diagnostics["agent_exists"] = True
                diagnostics["agent_details"] = {
                    "id": getattr(agent, 'id', 'Unknown'),
                    "name": getattr(agent, 'name', 'Unknown'),
                    "description": getattr(agent, 'description', 'Unknown'),
                    "model": getattr(agent, 'model', 'Unknown'),
                    "tools": getattr(agent, 'tools', [])
                }
                logger.info(f"Agent diagnostic: Agent {self.config.assistant_id} exists and is accessible")
            except Exception as e:
                diagnostics["error"] = f"Cannot access agent: {e}"
                logger.error(f"Agent diagnostic failed: {e}")
        
        except Exception as e:
            diagnostics["error"] = f"Cannot access agents client: {e}"
            logger.error(f"Agents client diagnostic failed: {e}")
        
        return diagnostics
    
    def get_weather(self, city: str) -> WeatherResult:
        """
        Get weather information for a specified city using Azure AI Foundry.
        
        Args:
            city: Name of the city to get weather for
            
        Returns:
            WeatherResult object containing weather information
            
        Raises:
            AIFoundryWeatherAgentError: If the agent request fails or returns an error
        """
        start_time = time.time()
        thread = None
        
        try:
            # Validate input
            weather_request = WeatherRequest(city=city)
            
            logger.info(f"Requesting weather for city: {city} using assistant {self.config.assistant_id}")
            
            # Get the agents client from the project client (following official examples)
            agents_client = self.client.agents
            
            # Create a thread for the conversation
            thread = self._create_thread_with_retry(agents_client)
            logger.debug(f"Created thread: {thread.id}")
            
            # Add the user message to the thread
            message_content = f"Get weather information for {weather_request.city}"
            message = self._add_message_with_retry(agents_client, thread.id, message_content)
            logger.debug(f"Added message to thread: {message.id}")
            
            # Run the assistant
            run = self._run_assistant_with_retry(agents_client, thread.id)
            logger.debug(f"Started run: {run.id}")
            
            # Wait for the run to complete with timeout
            run = self._wait_for_completion(agents_client, thread.id, run.id)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Assistant request completed in {elapsed_time:.2f}s, status: {run.status}")
            
            # Check if the run completed successfully
            if run.status != 'completed':
                error_msg = f"Assistant run failed with status: {run.status}"
                if hasattr(run, 'last_error') and run.last_error:
                    error_msg += f" - {run.last_error}"
                    # Log detailed error information
                    logger.error(f"Detailed error info: {run.last_error}")
                    if hasattr(run.last_error, '__dict__'):
                        logger.error(f"Error details: {run.last_error.__dict__}")
                
                # Log the full run object for debugging
                logger.error(f"Full run object: {run}")
                if hasattr(run, '__dict__'):
                    logger.error(f"Run details: {run.__dict__}")
                
                logger.error(error_msg)
                raise AIFoundryWeatherAgentError(error_msg, error_code=run.status)
            
            # Get the assistant's response
            messages = self._get_messages_with_retry(agents_client, thread.id)
            
            # Find the assistant's latest message
            assistant_message = self._find_latest_assistant_message(messages)
            
            if not assistant_message:
                error_msg = "No response from assistant"
                logger.error(error_msg)
                raise AIFoundryWeatherAgentError(error_msg)
            
            # Extract the content from the assistant's message
            response_content = self._extract_message_content(assistant_message)
            logger.debug(f"Assistant response: {response_content}")
            
            # Parse the weather information from the response
            weather_result = self._parse_weather_response(response_content, city)
            
            logger.info(f"Successfully retrieved weather for {weather_result.city}")
            return weather_result
            
        except Exception as e:
            if isinstance(e, AIFoundryWeatherAgentError):
                raise
            
            error_msg = f"Request failed: {e}"
            logger.error(error_msg, exc_info=True)
            raise AIFoundryWeatherAgentError(error_msg)
        
        finally:
            # Cleanup: Delete the thread to free resources
            if thread:
                try:
                    self.client.agents.threads.delete(thread.id)
                    logger.debug(f"Cleaned up thread: {thread.id}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup thread {thread.id}: {e}")
    
    def _create_thread_with_retry(self, agents_client: Any) -> Any:
        """Create a thread with retry logic."""
        for attempt in range(self.config.max_retries):
            try:
                return agents_client.threads.create()
            except AzureError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                logger.warning(f"Thread creation attempt {attempt + 1} failed: {e}")
                time.sleep(self.config.retry_delay * (2 ** attempt))
        
        raise AIFoundryWeatherAgentError("Failed to create thread after retries")
    
    def _add_message_with_retry(self, agents_client: Any, thread_id: str, content: str) -> Any:
        """Add a message to thread with retry logic."""
        for attempt in range(self.config.max_retries):
            try:
                return agents_client.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=content
                )
            except AzureError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                logger.warning(f"Message creation attempt {attempt + 1} failed: {e}")
                time.sleep(self.config.retry_delay * (2 ** attempt))
        
        raise AIFoundryWeatherAgentError("Failed to add message after retries")
    
    def _run_assistant_with_retry(self, agents_client: Any, thread_id: str) -> Any:
        """Run the assistant with retry logic."""
        for attempt in range(self.config.max_retries):
            try:
                return agents_client.runs.create(
                    thread_id=thread_id,
                    agent_id=self.config.assistant_id
                )
            except AzureError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                logger.warning(f"Run creation attempt {attempt + 1} failed: {e}")
                time.sleep(self.config.retry_delay * (2 ** attempt))
        
        raise AIFoundryWeatherAgentError("Failed to run assistant after retries")
    
    def _get_messages_with_retry(self, agents_client: Any, thread_id: str) -> List[Any]:
        """Get messages with retry logic."""
        for attempt in range(self.config.max_retries):
            try:
                return agents_client.messages.list(thread_id=thread_id)
            except AzureError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                logger.warning(f"Message retrieval attempt {attempt + 1} failed: {e}")
                time.sleep(self.config.retry_delay * (2 ** attempt))
        
        raise AIFoundryWeatherAgentError("Failed to retrieve messages after retries")
    
    def _wait_for_completion(self, agents_client: Any, thread_id: str, run_id: str) -> Any:
        """Wait for the run to complete with timeout."""
        start_time = time.time()
        
        while True:
            try:
                run = agents_client.runs.get(thread_id=thread_id, run_id=run_id)
                
                if run.status in ['completed', 'failed', 'cancelled', 'expired']:
                    return run
                
                # Check timeout
                if time.time() - start_time > self.config.timeout:
                    error_msg = f"Assistant run timed out after {self.config.timeout} seconds"
                    logger.error(error_msg)
                    raise AIFoundryWeatherAgentError(error_msg, error_code="timeout")
                
                # Wait before polling again
                time.sleep(1)
                logger.debug(f"Run status: {run.status}")
                
            except AzureError as e:
                error_msg = f"Failed to get run status: {e}"
                logger.error(error_msg)
                raise AIFoundryWeatherAgentError(error_msg)
    
    def _find_latest_assistant_message(self, messages: List[Any]) -> Optional[Any]:
        """Find the latest assistant message from the list."""
        for message in messages:
            if message.role == "assistant":
                return message
        return None
    
    def _extract_message_content(self, message: Any) -> str:
        """Extract text content from a message."""
        content = ""
        for content_block in message.content:
            if hasattr(content_block, 'text') and content_block.text:
                content += content_block.text.value
        return content
    
    def _parse_weather_response(self, response_content: str, requested_city: str) -> WeatherResult:
        """
        Parse the weather information from the assistant's response.
        
        Args:
            response_content: The assistant's response content
            requested_city: The originally requested city
            
        Returns:
            WeatherResult object
            
        Raises:
            AIFoundryWeatherAgentError: If parsing fails
        """
        try:
            # Try to extract JSON from the response if it contains structured data
            if "{" in response_content and "}" in response_content:
                start = response_content.find("{")
                end = response_content.rfind("}") + 1
                json_str = response_content[start:end]
                
                try:
                    weather_data = json.loads(json_str)
                    if all(key in weather_data for key in ["city", "temperature", "condition", "humidity"]):
                        return WeatherResult(**weather_data)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: try to parse the response text manually
            # This is a simple parser - in a real implementation you might want more sophisticated NLP
            lines = response_content.strip().split('\n')
            
            # Initialize default values
            city = requested_city
            temperature = "Unknown"
            condition = "Unknown"
            humidity = "Unknown"
            
            # Try to extract information from the text
            for line in lines:
                line = line.strip().lower()
                if 'temperature' in line or 'temp' in line:
                    # Extract temperature
                    import re
                    temp_match = re.search(r'(\d+(?:\.\d+)?)\s*°?[cf]?', line)
                    if temp_match:
                        temperature = f"{temp_match.group(1)}°C"
                
                elif 'condition' in line or 'weather' in line:
                    # Extract condition
                    if 'sunny' in line:
                        condition = "Sunny"
                    elif 'cloudy' in line:
                        condition = "Cloudy"
                    elif 'rainy' in line or 'rain' in line:
                        condition = "Rainy"
                    elif 'clear' in line:
                        condition = "Clear"
                
                elif 'humidity' in line:
                    # Extract humidity
                    import re
                    humidity_match = re.search(r'(\d+(?:\.\d+)?)\s*%?', line)
                    if humidity_match:
                        humidity = f"{humidity_match.group(1)}%"
            
            return WeatherResult(
                city=city,
                temperature=temperature,
                condition=condition,
                humidity=humidity
            )
            
        except Exception as e:
            error_msg = f"Failed to parse weather response: {e}"
            logger.error(f"{error_msg}. Response: {response_content}")
            raise AIFoundryWeatherAgentError(error_msg, response_data=response_content)
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with proper resource cleanup."""
        # The AI Foundry client handles its own cleanup
        logger.debug("AI Foundry agent client closed successfully")


# Factory function for easy client creation
def create_ai_foundry_weather_client(endpoint: str, assistant_id: str = "asst_14scpW964zK5TSFzjpdek9jG", **kwargs) -> AIFoundryWeatherAgentClient:
    """
    Factory function to create an AIFoundryWeatherAgentClient with default configuration.
    
    Args:
        endpoint: Azure AI Foundry project endpoint
        assistant_id: Assistant ID to use (defaults to weather agent)
        **kwargs: Additional configuration parameters
        
    Returns:
        Configured AIFoundryWeatherAgentClient instance
    """
    config = AIFoundryConfig(
        endpoint=endpoint,
        assistant_id=assistant_id,
        **kwargs
    )
    return AIFoundryWeatherAgentClient(config)
