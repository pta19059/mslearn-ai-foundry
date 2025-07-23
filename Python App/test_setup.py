#!/usr/bin/env python3
"""
Test script to verify the Weather Agent Python App installation and basic functionality.

This script performs basic tests to ensure the application is properly configured
and can interact with the Weather Agent API.
"""

import sys
import os
import importlib.util
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        ('azure-ai-projects', 'azure.ai.projects'),
        ('azure-identity', 'azure.identity'),
        ('click', 'click'),
        ('pydantic', 'pydantic'),
        ('python-dotenv', 'dotenv')
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name} is installed")
        except ImportError:
            print(f"❌ {package_name} is missing")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n📦 To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True


def check_files():
    """Check if required files exist."""
    print("\n🔍 Checking project files...")
    
    required_files = [
        'main.py',
        'ai_foundry_weather_client.py',
        'example.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} is missing")
            missing_files.append(file)
    
    return len(missing_files) == 0


def test_import():
    """Test importing the AI Foundry weather client module."""
    print("\n🔍 Testing module imports...")
    
    try:
        from ai_foundry_weather_client import (
            AIFoundryWeatherAgentClient,
            AIFoundryConfig,
            AIFoundryWeatherAgentError,
            create_ai_foundry_weather_client
        )
        print("✅ AIFoundryWeatherAgentClient module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import AIFoundryWeatherAgentClient: {e}")
        return False


def test_cli():
    """Test CLI help functionality."""
    print("\n🔍 Testing CLI functionality...")
    
    try:
        import main
        print("✅ Main CLI module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import main CLI: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\n🔍 Testing configuration...")
    
    try:
        from ai_foundry_weather_client import AIFoundryConfig
        
        # Test default configuration
        config = AIFoundryConfig(project_connection_string="test://example")
        print(f"✅ Default config created: timeout={config.timeout}s, retries={config.max_retries}")
        
        # Test custom configuration
        custom_config = AIFoundryConfig(
            project_connection_string="test://example",
            timeout=120,
            max_retries=5
        )
        print(f"✅ Custom config created: timeout={custom_config.timeout}s, retries={custom_config.max_retries}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def print_next_steps():
    """Print next steps for the user."""
    print("\n🚀 Next Steps:")
    print("1. Configure your Azure AI Foundry project connection string in .env:")
    print("   AZURE_AI_PROJECT_CONNECTION_STRING=your_actual_connection_string")
    print("")
    print("2. Set up Azure authentication (choose one):")
    print("   - Azure CLI: az login")
    print("   - Service Principal: Set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID")
    print("   - Managed Identity: Available automatically on Azure resources")
    print("")
    print("3. Test the application with a sample city:")
    print("   python main.py weather Milan")
    print("")
    print("4. Run the example script:")
    print("   python example.py")
    print("")
    print("5. Test the configuration:")
    print("   python main.py config")
    print("")
    print("6. Test batch processing:")
    print("   python main.py batch Milan Rome Paris")
    print("")
    print("7. Run connection test:")
    print("   python main.py test")


def main():
    """Run all tests."""
    print("🧪 Weather Agent Python App - Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Files", check_files),
        ("Module Import", test_import),
        ("CLI Module", test_cli),
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 All tests passed! The application is ready to use.")
        print_next_steps()
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix the issues above.")
        
        if failed > 0:
            print("\n💡 Common fixes:")
            print("- Install missing dependencies: pip install -r requirements.txt")
            print("- Ensure you're in the correct directory")
            print("- Check Python version (3.7+ required)")


if __name__ == "__main__":
    main()
