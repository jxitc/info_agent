"""AI-powered information processing utilities.

This module provides high-level functions to process text into Memory objects
using AI extraction and embeddings.
"""

import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .client import OpenAIClient, OpenAIClientError
from .prompts import extract_all_information_prompt
from ..core.models import Memory


logger = logging.getLogger(__name__)


class ProcessingError(Exception):
    """Raised when text processing fails."""
    pass


class MemoryProcessor:
    """Processes text into Memory objects using AI extraction."""
    
    def __init__(self, ai_client: Optional[OpenAIClient] = None):
        """Initialize memory processor.
        
        Args:
            ai_client: Optional OpenAI client. If None, creates a new one.
        """
        self.ai_client = ai_client or OpenAIClient()
        
    def process_text_to_memory(
        self, 
        text: str, 
        memory_id: Optional[int] = None,
        force_title: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Memory:
        """Process text into a Memory object using AI extraction.
        
        Args:
            text: The text content to process
            memory_id: Optional ID for the memory (used for testing/specific cases)
            force_title: Optional title to override AI-generated title
            additional_context: Optional context to include in extraction
            
        Returns:
            Memory object with AI-extracted metadata
            
        Raises:
            ProcessingError: If processing fails
        """
        logger.info(f"Processing {len(text)} characters of text into memory")
        
        try:
            # Generate extraction prompt
            prompt = extract_all_information_prompt(text)
            
            # Add context if provided
            if additional_context:
                context_str = json.dumps(additional_context, indent=2)
                prompt += f"\n\nAdditional context to consider:\n{context_str}"
            
            # Call AI for extraction
            logger.debug("Calling AI for information extraction")
            response = self.ai_client.chat_completion([{"role": "user", "content": prompt}])
            
            if not response.success:
                raise ProcessingError(f"AI extraction failed: {response.error}")
            
            # Parse JSON response
            try:
                extracted_data = json.loads(response.content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.debug(f"Raw response: {response.content}")
                raise ProcessingError(f"Invalid JSON response from AI: {e}")
            
            # Create Memory object
            title = force_title or extracted_data.get('title', 'Untitled Memory')
            
            memory = Memory(
                id=memory_id,
                content=text,
                title=title,
                dynamic_fields={}
            )
            
            # Add extracted metadata as dynamic fields
            if 'description' in extracted_data:
                memory.dynamic_fields['description'] = extracted_data['description']
            
            if 'summary' in extracted_data:
                memory.dynamic_fields['summary'] = extracted_data['summary']
            
            if 'categories' in extracted_data and extracted_data['categories']:
                memory.dynamic_fields['categories'] = extracted_data['categories']
                # Use first category as primary category for compatibility
                memory.dynamic_fields['category'] = extracted_data['categories'][0]
            
            if 'key_facts' in extracted_data and extracted_data['key_facts']:
                memory.dynamic_fields['key_facts'] = extracted_data['key_facts']
            
            if 'dates_times' in extracted_data and extracted_data['dates_times']:
                memory.dynamic_fields['dates_times'] = extracted_data['dates_times']
            
            if 'entities' in extracted_data and extracted_data['entities']:
                # Flatten entities for easier searching
                entities = extracted_data['entities']
                if entities.get('people'):
                    memory.dynamic_fields['people'] = entities['people']
                if entities.get('places'):
                    memory.dynamic_fields['places'] = entities['places']
                if entities.get('organizations'):
                    memory.dynamic_fields['organizations'] = entities['organizations']
            
            if 'action_items' in extracted_data and extracted_data['action_items']:
                memory.dynamic_fields['action_items'] = extracted_data['action_items']
            
            # Add any additional dynamic fields from extraction
            if 'dynamic_fields' in extracted_data and extracted_data['dynamic_fields']:
                for key, value in extracted_data['dynamic_fields'].items():
                    memory.dynamic_fields[key] = value
            
            # Add processing metadata
            memory.dynamic_fields['ai_processed'] = True
            memory.dynamic_fields['ai_model'] = response.model
            memory.dynamic_fields['ai_tokens_used'] = response.tokens_used
            memory.dynamic_fields['processing_timestamp'] = datetime.now().isoformat()
            memory.dynamic_fields['processor_version'] = '1.0'
            
            logger.info(f"Successfully processed text into memory with title: {title}")
            logger.debug(f"Extracted {len(memory.dynamic_fields)} dynamic fields")
            
            return memory
            
        except OpenAIClientError as e:
            logger.error(f"OpenAI client error during processing: {e}")
            raise ProcessingError(f"AI service error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during processing: {e}")
            raise ProcessingError(f"Processing failed: {e}")
    
    def generate_embedding(self, text: str, model: Optional[str] = None) -> Optional[list]:
        """Generate embedding for text.
        
        Args:
            text: Text to generate embedding for
            model: Optional model override
            
        Returns:
            Embedding vector as list of floats, or None if failed
        """
        try:
            response = self.ai_client.generate_embedding(text, model=model)
            if response.success:
                return response.embedding
            else:
                logger.error(f"Embedding generation failed: {response.error}")
                return None
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test if AI client connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        return self.ai_client.test_connection()


# Convenience functions for direct usage
_default_processor = None


def get_default_processor() -> MemoryProcessor:
    """Get or create default memory processor instance.
    
    Returns:
        Default MemoryProcessor instance
    """
    global _default_processor
    if _default_processor is None:
        try:
            _default_processor = MemoryProcessor()
        except OpenAIClientError as e:
            logger.error(f"Failed to create default processor: {e}")
            raise ProcessingError(f"Cannot initialize AI processor: {e}")
    return _default_processor


def process_text_to_memory(
    text: str,
    memory_id: Optional[int] = None,
    force_title: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> Memory:
    """Process text into Memory object using default processor.
    
    This is a convenience function that uses the default MemoryProcessor instance.
    
    Args:
        text: The text content to process
        memory_id: Optional ID for the memory
        force_title: Optional title to override AI-generated title
        additional_context: Optional context for extraction
        
    Returns:
        Memory object with AI-extracted metadata
        
    Raises:
        ProcessingError: If processing fails
    """
    processor = get_default_processor()
    return processor.process_text_to_memory(
        text=text,
        memory_id=memory_id,
        force_title=force_title,
        additional_context=additional_context
    )


def generate_text_embedding(text: str, model: Optional[str] = None) -> Optional[list]:
    """Generate embedding for text using default processor.
    
    Args:
        text: Text to generate embedding for
        model: Optional model override
        
    Returns:
        Embedding vector as list of floats, or None if failed
    """
    processor = get_default_processor()
    return processor.generate_embedding(text, model=model)


def test_ai_connection() -> bool:
    """Test AI connection using default processor.
    
    Returns:
        True if connection is working, False otherwise
    """
    try:
        processor = get_default_processor()
        return processor.test_connection()
    except ProcessingError:
        return False