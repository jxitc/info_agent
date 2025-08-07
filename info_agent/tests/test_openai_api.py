#!/usr/bin/env python3
"""
OpenAI API connection test script for Info Agent.

This script tests OpenAI API functionality including:
- API key configuration
- Client initialization
- Basic API connectivity
- Model availability
"""

import openai
import os
import sys
from typing import Optional


def test_api_key_configuration() -> bool:
    """Test that OpenAI API key is properly configured."""
    print("Testing OpenAI API key configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("   Please set your API key: export OPENAI_API_KEY='your-key-here'")
        return False
    
    if not api_key.startswith('sk-'):
        print("❌ API key format appears invalid (should start with 'sk-')")
        return False
    
    # Don't print the full API key for security
    masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 11 else "***"
    print(f"✅ API key configured: {masked_key}")
    return True


def test_client_initialization() -> Optional[openai.OpenAI]:
    """Test OpenAI client initialization."""
    print("\nTesting OpenAI client initialization...")
    
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return None


def test_api_connectivity(client: openai.OpenAI) -> bool:
    """Test basic API connectivity with a simple request."""
    print("\nTesting API connectivity...")
    
    try:
        # Test with a minimal completion request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello! Please respond with 'API test successful'."}
            ],
            max_tokens=10,
            temperature=0
        )
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"✅ API connectivity successful")
            print(f"   Response: {content}")
            print(f"   Model used: {response.model}")
            print(f"   Tokens used: {response.usage.total_tokens}")
            return True
        else:
            print("❌ API responded but no content received")
            return False
            
    except openai.AuthenticationError:
        print("❌ Authentication failed - check your API key")
        return False
    except openai.RateLimitError:
        print("❌ Rate limit exceeded - please try again later")
        return False
    except openai.APIConnectionError:
        print("❌ Network connection error - check your internet connection")
        return False
    except openai.APIError as e:
        print(f"❌ OpenAI API error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during API test: {e}")
        return False


def test_model_availability(client: openai.OpenAI) -> bool:
    """Test availability of models needed for the application."""
    print("\nTesting model availability...")
    
    required_models = [
        "gpt-3.5-turbo",
        "text-embedding-3-small"
    ]
    
    try:
        # Get list of available models
        models = client.models.list()
        available_model_ids = {model.id for model in models.data}
        
        all_available = True
        for model in required_models:
            if model in available_model_ids:
                print(f"✅ Model available: {model}")
            else:
                print(f"❌ Model not available: {model}")
                all_available = False
        
        if all_available:
            print("✅ All required models are available")
        else:
            print("⚠️  Some required models may not be available")
        
        return all_available
        
    except Exception as e:
        print(f"❌ Failed to check model availability: {e}")
        return False


def test_embedding_functionality(client: openai.OpenAI) -> bool:
    """Test embedding generation functionality."""
    print("\nTesting embedding functionality...")
    
    try:
        test_text = "This is a test text for embedding generation."
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=test_text
        )
        
        if response.data and len(response.data) > 0:
            embedding = response.data[0].embedding
            print(f"✅ Embedding generated successfully")
            print(f"   Embedding dimensions: {len(embedding)}")
            print(f"   Model used: {response.model}")
            print(f"   Tokens used: {response.usage.total_tokens}")
            return True
        else:
            print("❌ No embedding data received")
            return False
            
    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False


def main():
    """Run all OpenAI API tests."""
    print("=" * 60)
    print("INFO AGENT - OpenAI API Connection Test")
    print("=" * 60)
    
    tests = [
        ("API Key Configuration", test_api_key_configuration, []),
    ]
    
    # Only proceed with client-dependent tests if API key is configured
    api_key_ok = test_api_key_configuration()
    if api_key_ok:
        client = test_client_initialization()
        if client:
            tests.extend([
                ("Client Initialization", lambda: True, []),  # Already tested
                ("API Connectivity", test_api_connectivity, [client]),
                ("Model Availability", test_model_availability, [client]),
                ("Embedding Functionality", test_embedding_functionality, [client])
            ])
        else:
            tests.append(("Client Initialization", lambda: False, []))
    
    passed = 0
    failed = 0
    
    for test_name, test_func, args in tests:
        if test_name == "Client Initialization" and args == []:
            # Skip if already handled above
            continue
            
        try:
            if test_func(*args):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All OpenAI API tests passed! API setup is ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        if not api_key_ok:
            print("\n💡 Tip: Make sure to set your OpenAI API key:")
            print("   export OPENAI_API_KEY='your-api-key-here'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
                    
