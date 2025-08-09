#!/usr/bin/env python3
"""
Test script for prompt templates.

This script tests the prompt template functionality including:
- Template formatting
- Variable validation
- Prompt manager operations
- Convenience functions
"""

import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from info_agent.ai.prompts import (
    PromptManager, PromptTemplate, PromptType,
    extract_all_information_prompt
)


def test_prompt_template():
    """Test basic PromptTemplate functionality."""
    print("Testing PromptTemplate...")
    
    # Test simple template
    template = PromptTemplate(
        template="Hello {name}, how are you?",
        required_vars=["name"]
    )
    
    formatted = template.format(name="World")
    if formatted == "Hello World, how are you?":
        print("✅ Basic template formatting works")
    else:
        print(f"❌ Template formatting failed: {formatted}")
        return False
    
    # Test missing required variable
    try:
        template.format()  # Missing name
        print("❌ Should have failed with missing variable")
        return False
    except ValueError as e:
        if "Missing required variables: ['name']" in str(e):
            print("✅ Correctly validates required variables")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    
    # Test template without required vars
    simple_template = PromptTemplate("Static template")
    result = simple_template.format()
    if result == "Static template":
        print("✅ Templates without variables work")
    else:
        print(f"❌ Static template failed: {result}")
        return False
    
    return True


def test_prompt_manager():
    """Test PromptManager functionality."""
    print("\nTesting PromptManager...")
    
    manager = PromptManager()
    
    # Test getting available prompts
    available = manager.list_available_prompts()
    expected_prompts = [PromptType.EXTRACT_ALL]
    
    if all(prompt_type in available for prompt_type in expected_prompts):
        print("✅ Expected prompt type is available")
    else:
        print(f"❌ Missing prompt types. Available: {available}")
        return False
    
    # Test getting a prompt
    test_text = "This is a test document about AI and machine learning."
    prompt = manager.get_prompt(PromptType.EXTRACT_ALL, text=test_text)
    
    if "This is a test document about AI and machine learning." in prompt:
        print("✅ Prompt generation works")
    else:
        print("❌ Prompt generation failed")
        return False
    
    # Test adding custom template
    custom_template = PromptTemplate("Custom: {text}", required_vars=["text"])
    manager.add_template(PromptType.EXTRACT_ALL, custom_template)  # Override existing
    
    result = manager.get_prompt(PromptType.EXTRACT_ALL, text="test")
    if result == "Custom: test":
        print("✅ Adding custom templates works")
    else:
        print(f"❌ Custom template failed: {result}")
        return False
    
    return True


def test_convenience_functions():
    """Test convenience function."""
    print("\nTesting convenience function...")
    
    test_text = "Meeting with John about the quarterly report. Due date is Friday."
    
    # Test extract_all_information_prompt
    try:
        prompt = extract_all_information_prompt(test_text)
        if "Meeting with John about the quarterly report" in prompt and "JSON format" in prompt:
            print("✅ extract_all_information_prompt works")
        else:
            print("❌ extract_all_information_prompt failed")
            return False
    except Exception as e:
        print(f"❌ extract_all_information_prompt error: {e}")
        return False
    
    return True


def test_prompt_content():
    """Test that unified prompt contains expected content and structure."""
    print("\nTesting prompt content...")
    
    test_text = "I need to schedule a meeting with Sarah for next Tuesday to discuss the project budget."
    
    # Test unified extraction prompt structure
    extract_prompt = extract_all_information_prompt(test_text)
    expected_keys = ["title", "description", "summary", "categories", "key_facts", "dates_times", "entities", "action_items", "dynamic_fields"]
    
    all_keys_present = all(key in extract_prompt for key in expected_keys)
    if all_keys_present and "JSON format" in extract_prompt:
        print("✅ Unified extraction prompt has correct structure")
    else:
        print("❌ Unified extraction prompt missing elements")
        return False
    
    # Test that prompt includes guidelines for different field types
    guidelines = ["80 characters", "200 characters", "100 words"]
    
    if all(guideline in extract_prompt for guideline in guidelines):
        print("✅ Unified prompt has correct length guidelines")
    else:
        print("❌ Unified prompt missing guidelines")
        return False
    
    return True


def test_error_handling():
    """Test error handling in prompt templates."""
    print("\nTesting error handling...")
    
    manager = PromptManager()
    
    # Test invalid prompt type
    try:
        from enum import Enum
        class FakePromptType(Enum):
            FAKE = "fake"
        
        manager.get_prompt(FakePromptType.FAKE, text="test")
        print("❌ Should have failed with invalid prompt type")
        return False
    except ValueError as e:
        if "not found" in str(e):
            print("✅ Correctly handles invalid prompt type")
        else:
            print(f"❌ Wrong error for invalid type: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test missing required variables through manager
    try:
        # This should fail because we're not providing the 'text' variable
        manager.get_prompt(PromptType.EXTRACT_ALL)
        print("❌ Should have failed with missing text variable")
        return False
    except ValueError as e:
        if "Missing required variables" in str(e):
            print("✅ Correctly handles missing variables through manager")
        else:
            print(f"❌ Wrong error for missing vars: {e}")
            return False
    
    return True


def main():
    """Run all prompt template tests."""
    print("=" * 60)
    print("INFO AGENT - Unified Prompt Template Test")
    print("=" * 60)
    
    tests = [
        ("Prompt Template", test_prompt_template),
        ("Prompt Manager", test_prompt_manager),
        ("Convenience Function", test_convenience_functions),
        ("Prompt Content", test_prompt_content),
        ("Error Handling", test_error_handling),
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
        print("\n🎉 All prompt template tests passed!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())