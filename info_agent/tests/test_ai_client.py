#!/usr/bin/env python3
"""
Test script for the OpenAI client wrapper.

This script tests the wrapper functionality including:
- Client initialization
- Error handling
- Response parsing
- Configuration management
"""

import os
import sys
import logging
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from info_agent.ai import OpenAIClient, create_client, OpenAIClientError, AIResponse, EmbeddingResponse


def test_client_initialization():
    """Test client initialization with various configurations."""
    print("Testing client initialization...")
    
    # Test with missing API key
    try:
        with patch.dict(os.environ, {}, clear=True):
            client = OpenAIClient()
        print("❌ Should have failed with missing API key")
        return False
    except OpenAIClientError as e:
        if "API key not provided" in str(e):
            print("✅ Correctly handles missing API key")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    
    # Test with invalid API key format
    try:
        client = OpenAIClient(api_key="invalid-key-format")
        print("❌ Should have failed with invalid key format")
        return False
    except OpenAIClientError as e:
        if "Invalid OpenAI API key format" in str(e):
            print("✅ Correctly validates API key format")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    
    # Test with valid format (mock key)
    try:
        with patch('openai.OpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            client = OpenAIClient(api_key="sk-test1234567890abcdef")
            print("✅ Successfully initializes with valid key format")
    except Exception as e:
        print(f"❌ Failed initialization with valid key: {e}")
        return False
    
    return True


def test_convenience_function():
    """Test the create_client convenience function."""
    print("\nTesting convenience function...")
    
    try:
        with patch('info_agent.ai.client.OpenAI') as mock_openai:
            mock_openai.return_value = Mock()
            client = create_client(api_key="sk-test1234567890abcdef")
            
        if isinstance(client, OpenAIClient):
            print("✅ create_client returns OpenAIClient instance")
            return True
        else:
            print(f"❌ create_client returned wrong type: {type(client)}")
            return False
    except Exception as e:
        print(f"❌ create_client failed: {e}")
        return False


def test_response_objects():
    """Test response object creation and attributes."""
    print("\nTesting response objects...")
    
    # Test AIResponse
    ai_response = AIResponse(
        content="Test response",
        model="gpt-3.5-turbo",
        tokens_used=10,
        success=True
    )
    
    if (ai_response.content == "Test response" and 
        ai_response.model == "gpt-3.5-turbo" and
        ai_response.tokens_used == 10 and
        ai_response.success is True and
        ai_response.error is None):
        print("✅ AIResponse object works correctly")
    else:
        print("❌ AIResponse object has wrong attributes")
        return False
    
    # Test EmbeddingResponse
    embedding_response = EmbeddingResponse(
        embedding=[0.1, 0.2, 0.3],
        model="text-embedding-3-small",
        tokens_used=5,
        success=True,
        dimensions=3
    )
    
    if (embedding_response.embedding == [0.1, 0.2, 0.3] and
        embedding_response.model == "text-embedding-3-small" and
        embedding_response.dimensions == 3 and
        embedding_response.success is True):
        print("✅ EmbeddingResponse object works correctly")
    else:
        print("❌ EmbeddingResponse object has wrong attributes")
        return False
    
    return True


def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting error handling...")
    
    try:
        with patch('info_agent.ai.client.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            client = OpenAIClient(api_key="sk-test1234567890abcdef")
            
            # Test chat completion with no choices
            mock_response = Mock()
            mock_response.choices = []
            mock_response.model = "gpt-3.5-turbo"
            mock_response.usage = Mock()
            mock_response.usage.total_tokens = 0
            
            mock_client.chat.completions.create.return_value = mock_response
            
            response = client.chat_completion([{"role": "user", "content": "test"}])
            
            if not response.success and response.error == "No response choices received":
                print("✅ Correctly handles empty response choices")
            else:
                print(f"❌ Wrong handling of empty choices: {response}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_mock_functionality():
    """Test client functionality with mocked OpenAI responses."""
    print("\nTesting mocked client functionality...")
    
    try:
        with patch('info_agent.ai.client.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            client = OpenAIClient(api_key="sk-test1234567890abcdef")
            
            # Test successful chat completion
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message.content = "Test response content"
            mock_response.model = "gpt-3.5-turbo"
            mock_response.usage = Mock()
            mock_response.usage.total_tokens = 25
            
            mock_client.chat.completions.create.return_value = mock_response
            
            response = client.chat_completion([{"role": "user", "content": "test"}])
            
            if (response.success and 
                response.content == "Test response content" and
                response.model == "gpt-3.5-turbo" and
                response.tokens_used == 25):
                print("✅ Chat completion works correctly")
            else:
                print(f"❌ Chat completion failed: {response}")
                return False
            
            # Test successful embedding generation
            mock_embed_response = Mock()
            mock_embed_response.data = [Mock()]
            mock_embed_response.data[0].embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_embed_response.model = "text-embedding-3-small"
            mock_embed_response.usage = Mock()
            mock_embed_response.usage.total_tokens = 10
            
            mock_client.embeddings.create.return_value = mock_embed_response
            
            embed_response = client.generate_embedding("test text")
            
            if (embed_response.success and
                embed_response.embedding == [0.1, 0.2, 0.3, 0.4, 0.5] and
                embed_response.dimensions == 5 and
                embed_response.tokens_used == 10):
                print("✅ Embedding generation works correctly")
            else:
                print(f"❌ Embedding generation failed: {embed_response}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Mock functionality test failed: {e}")
        return False


def main():
    """Run all client wrapper tests."""
    print("=" * 60)
    print("INFO AGENT - AI Client Wrapper Test")
    print("=" * 60)
    
    # Configure logging to reduce noise during testing
    logging.getLogger('info_agent.ai.client').setLevel(logging.WARNING)
    
    tests = [
        ("Client Initialization", test_client_initialization),
        ("Convenience Function", test_convenience_function),
        ("Response Objects", test_response_objects),
        ("Error Handling", test_error_handling),
        ("Mock Functionality", test_mock_functionality),
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
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All AI client wrapper tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())