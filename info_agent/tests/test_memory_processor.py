#!/usr/bin/env python3
"""
Test script for memory processor functionality.

This script tests the AI-powered memory processing pipeline that converts
text into Memory objects with extracted metadata.
"""

import os
import sys
import json
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from info_agent.ai import MemoryProcessor, ProcessingError, process_text_to_memory
from info_agent.core.models import Memory


def test_memory_processor_initialization():
    """Test memory processor initialization."""
    print("Testing memory processor initialization...")
    
    # Test with default client
    try:
        with patch('info_agent.ai.processor.OpenAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            processor = MemoryProcessor()
            
            if processor.ai_client is not None:
                print("✅ Memory processor initializes with default client")
            else:
                print("❌ Memory processor failed to initialize client")
                return False
    except Exception as e:
        print(f"❌ Memory processor initialization failed: {e}")
        return False
    
    # Test with custom client
    try:
        with patch('info_agent.ai.processor.OpenAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            custom_client = Mock()
            processor = MemoryProcessor(ai_client=custom_client)
            
            if processor.ai_client == custom_client:
                print("✅ Memory processor accepts custom client")
            else:
                print("❌ Memory processor didn't use custom client")
                return False
    except Exception as e:
        print(f"❌ Custom client test failed: {e}")
        return False
    
    return True


def test_text_to_memory_processing():
    """Test processing text into Memory objects."""
    print("\nTesting text to memory processing...")
    
    test_text = "Team meeting with John and Sarah on Friday at 2pm to discuss the Q4 budget and project milestones. Need to prepare financial reports."
    
    # Mock AI response data
    mock_extracted_data = {
        "title": "Team Meeting - Q4 Budget and Milestones",
        "description": "Team meeting to discuss Q4 budget and project milestones",
        "summary": "Meeting with John and Sarah about Q4 budget and project milestones, need to prepare reports",
        "categories": ["work", "meetings", "finance"],
        "key_facts": ["Q4 budget discussion", "project milestones review", "financial reports needed"],
        "dates_times": ["Friday at 2pm"],
        "entities": {
            "people": ["John", "Sarah"],
            "places": [],
            "organizations": []
        },
        "action_items": ["prepare financial reports"],
        "dynamic_fields": {
            "priority": "high",
            "status": "planned",
            "meeting_type": "team_meeting"
        }
    }
    
    try:
        with patch('info_agent.ai.processor.OpenAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock successful AI response
            mock_response = Mock()
            mock_response.success = True
            mock_response.content = json.dumps(mock_extracted_data)
            mock_response.model = "gpt-3.5-turbo"
            mock_response.tokens_used = 150
            
            mock_client.chat_completion.return_value = mock_response
            
            processor = MemoryProcessor()
            memory = processor.process_text_to_memory(test_text, memory_id=123)
            
            # Verify memory object
            if not isinstance(memory, Memory):
                print(f"❌ Expected Memory object, got {type(memory)}")
                return False
            
            # Check basic properties
            if (memory.content == test_text and 
                memory.title == "Team Meeting - Q4 Budget and Milestones" and
                memory.id == 123):
                print("✅ Memory object has correct basic properties")
            else:
                print("❌ Memory object missing basic properties")
                return False
            
            # Check dynamic fields
            if (memory.dynamic_fields.get('description') == mock_extracted_data['description'] and
                memory.dynamic_fields.get('categories') == ['work', 'meetings', 'finance'] and
                memory.dynamic_fields.get('people') == ['John', 'Sarah'] and
                memory.dynamic_fields.get('priority') == 'high'):
                print("✅ Memory object has extracted dynamic fields")
            else:
                print("❌ Memory object missing expected dynamic fields")
                print(f"   Actual fields: {list(memory.dynamic_fields.keys())}")
                return False
            
            # Check processing metadata
            if (memory.dynamic_fields.get('ai_processed') is True and
                memory.dynamic_fields.get('ai_model') == 'gpt-3.5-turbo' and
                memory.dynamic_fields.get('ai_tokens_used') == 150):
                print("✅ Memory object has processing metadata")
            else:
                print("❌ Memory object missing processing metadata")
                return False
    
    except Exception as e:
        print(f"❌ Text to memory processing test failed: {e}")
        return False
    
    return True


def test_processing_error_handling():
    """Test error handling in memory processing."""
    print("\nTesting processing error handling...")
    
    test_text = "Simple test text"
    
    try:
        with patch('info_agent.ai.processor.OpenAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            processor = MemoryProcessor()
            
            # Test AI failure
            mock_response = Mock()
            mock_response.success = False
            mock_response.error = "API rate limit exceeded"
            
            mock_client.chat_completion.return_value = mock_response
            
            try:
                memory = processor.process_text_to_memory(test_text)
                print("❌ Expected ProcessingError for AI failure")
                return False
            except ProcessingError as e:
                if "AI extraction failed" in str(e):
                    print("✅ Correctly handles AI extraction failure")
                else:
                    print(f"❌ Wrong error message: {e}")
                    return False
            
            # Test JSON parsing error
            mock_response.success = True
            mock_response.content = "Invalid JSON response"
            mock_response.model = "gpt-3.5-turbo"
            mock_response.tokens_used = 10
            
            try:
                memory = processor.process_text_to_memory(test_text)
                print("❌ Expected ProcessingError for invalid JSON")
                return False
            except ProcessingError as e:
                if "Invalid JSON response" in str(e):
                    print("✅ Correctly handles JSON parsing error")
                else:
                    print(f"❌ Wrong error message: {e}")
                    return False
    
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    return True


def test_convenience_functions():
    """Test convenience functions."""
    print("\nTesting convenience functions...")
    
    test_text = "Test text for convenience functions"
    
    try:
        with patch('info_agent.ai.processor.OpenAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock successful response
            mock_extracted_data = {
                "title": "Test Memory",
                "description": "A test memory",
                "categories": ["test"],
                "dynamic_fields": {"test": True}
            }
            
            mock_response = Mock()
            mock_response.success = True
            mock_response.content = json.dumps(mock_extracted_data)
            mock_response.model = "gpt-3.5-turbo"
            mock_response.tokens_used = 50
            
            mock_client.chat_completion.return_value = mock_response
            
            # Test process_text_to_memory function
            memory = process_text_to_memory(test_text, memory_id=999)
            
            if (isinstance(memory, Memory) and 
                memory.content == test_text and
                memory.title == "Test Memory" and
                memory.id == 999):
                print("✅ Convenience function process_text_to_memory works")
            else:
                print("❌ Convenience function failed")
                return False
            
            # Test embedding generation
            mock_embed_response = Mock()
            mock_embed_response.success = True
            mock_embed_response.embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
            
            mock_client.generate_embedding.return_value = mock_embed_response
            
            from info_agent.ai import generate_text_embedding
            embedding = generate_text_embedding(test_text)
            
            if embedding == [0.1, 0.2, 0.3, 0.4, 0.5]:
                print("✅ Convenience function generate_text_embedding works")
            else:
                print(f"❌ Wrong embedding result: {embedding}")
                return False
            
            # Test connection test
            mock_client.test_connection.return_value = True
            
            from info_agent.ai import test_ai_connection
            if test_ai_connection():
                print("✅ Convenience function test_ai_connection works")
            else:
                print("❌ Connection test failed")
                return False
    
    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        return False
    
    return True


def test_forced_title_and_context():
    """Test forced title and additional context features."""
    print("\nTesting forced title and additional context...")
    
    test_text = "Basic meeting notes"
    
    try:
        with patch('info_agent.ai.processor.OpenAIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            mock_extracted_data = {
                "title": "AI Generated Title",
                "description": "Test description",
                "dynamic_fields": {}
            }
            
            mock_response = Mock()
            mock_response.success = True
            mock_response.content = json.dumps(mock_extracted_data)
            mock_response.model = "gpt-3.5-turbo"
            mock_response.tokens_used = 25
            
            mock_client.chat_completion.return_value = mock_response
            
            processor = MemoryProcessor()
            
            # Test forced title
            memory = processor.process_text_to_memory(
                test_text, 
                force_title="Custom Title",
                memory_id=100
            )
            
            if memory.title == "Custom Title":
                print("✅ Forced title override works")
            else:
                print(f"❌ Expected 'Custom Title', got '{memory.title}'")
                return False
            
            # Test additional context
            additional_context = {"meeting_room": "Conference A", "attendees": 5}
            
            memory = processor.process_text_to_memory(
                test_text,
                additional_context=additional_context,
                memory_id=101
            )
            
            # Check that the prompt included the context (by checking if it was called)
            call_args = mock_client.chat_completion.call_args[0][0][0]["content"]
            if "Conference A" in call_args and "attendees" in call_args:
                print("✅ Additional context is included in prompt")
            else:
                print("❌ Additional context not found in prompt")
                return False
    
    except Exception as e:
        print(f"❌ Forced title and context test failed: {e}")
        return False
    
    return True


def main():
    """Run all memory processor tests."""
    print("=" * 60)
    print("INFO AGENT - Memory Processor Test")
    print("=" * 60)
    
    tests = [
        ("Memory Processor Initialization", test_memory_processor_initialization),
        ("Text to Memory Processing", test_text_to_memory_processing),
        ("Processing Error Handling", test_processing_error_handling),
        ("Convenience Functions", test_convenience_functions),
        ("Forced Title and Context", test_forced_title_and_context),
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
        print("\n🎉 All memory processor tests passed!")
        print("\n📋 Memory Processing Pipeline Ready:")
        print("   • MemoryProcessor class for flexible processing ✅")
        print("   • AI-powered information extraction ✅")
        print("   • Automatic dynamic field population ✅")
        print("   • Processing metadata tracking ✅")
        print("   • Error handling and validation ✅")
        print("   • Convenience functions for easy usage ✅")
        print("   • Support for custom titles and context ✅")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())