"""AI integration and processing modules."""

from .client import OpenAIClient, create_client, AIResponse, EmbeddingResponse, OpenAIClientError
from .prompts import (
    PromptManager, 
    PromptTemplate, 
    PromptType,
    extract_all_information_prompt
)
from .processor import (
    MemoryProcessor,
    ProcessingError,
    process_text_to_memory,
    generate_text_embedding,
    test_ai_connection
)

__all__ = [
    # Client functionality
    'OpenAIClient',
    'create_client', 
    'AIResponse',
    'EmbeddingResponse',
    'OpenAIClientError',
    
    # Prompt functionality
    'PromptManager',
    'PromptTemplate',
    'PromptType',
    'extract_all_information_prompt',
    
    # Processing functionality
    'MemoryProcessor',
    'ProcessingError',
    'process_text_to_memory',
    'generate_text_embedding',
    'test_ai_connection'
]