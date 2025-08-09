"""OpenAI API client wrapper for Info Agent.

This module provides a wrapper around the OpenAI API client with:
- Configuration management
- Error handling
- Retry logic
- Rate limiting
- Response validation
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai.types import CreateEmbeddingResponse


logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """Standardized response from AI operations."""
    content: str
    model: str
    tokens_used: int
    success: bool
    error: Optional[str] = None


@dataclass
class EmbeddingResponse:
    """Response from embedding generation."""
    embedding: List[float]
    model: str
    tokens_used: int
    success: bool
    dimensions: int
    error: Optional[str] = None


class OpenAIClientError(Exception):
    """Custom exception for OpenAI client errors."""
    pass


class OpenAIClient:
    """Wrapper for OpenAI API with error handling and retry logic."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: str = "gpt-3.5-turbo",
        default_embedding_model: str = "text-embedding-3-small",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var
            default_model: Default model for chat completions
            default_embedding_model: Default model for embeddings
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.default_model = default_model
        self.default_embedding_model = default_embedding_model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        if not self.api_key:
            raise OpenAIClientError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        if not self.api_key.startswith('sk-'):
            raise OpenAIClientError(
                "Invalid OpenAI API key format. Key should start with 'sk-'"
            )
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            raise OpenAIClientError(f"Failed to initialize OpenAI client: {e}")
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with retry logic and exponential backoff."""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except openai.RateLimitError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit, retrying in {delay}s (attempt {attempt + 1})")
                    time.sleep(delay)
                else:
                    raise OpenAIClientError(f"Rate limit exceeded after {self.max_retries} attempts")
            
            except openai.APIConnectionError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Connection error, retrying in {delay}s (attempt {attempt + 1})")
                    time.sleep(delay)
                else:
                    raise OpenAIClientError(f"Connection failed after {self.max_retries} attempts: {e}")
            
            except (openai.AuthenticationError, openai.PermissionDeniedError) as e:
                # Don't retry authentication errors
                raise OpenAIClientError(f"Authentication error: {e}")
            
            except openai.APIError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"API error, retrying in {delay}s (attempt {attempt + 1}): {e}")
                    time.sleep(delay)
                else:
                    raise OpenAIClientError(f"API error after {self.max_retries} attempts: {e}")
        
        # This should not be reached, but just in case
        if last_exception:
            raise OpenAIClientError(f"Operation failed: {last_exception}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> AIResponse:
        """Generate chat completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to self.default_model)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-2)
            **kwargs: Additional parameters for the API call
            
        Returns:
            AIResponse with completion result
        """
        model = model or self.default_model
        
        try:
            def _make_request():
                return self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
            
            response: ChatCompletion = self._retry_with_backoff(_make_request)
            
            if not response.choices:
                return AIResponse(
                    content="",
                    model=response.model,
                    tokens_used=response.usage.total_tokens if response.usage else 0,
                    success=False,
                    error="No response choices received"
                )
            
            content = response.choices[0].message.content or ""
            
            return AIResponse(
                content=content,
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                success=True
            )
            
        except OpenAIClientError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {e}")
            return AIResponse(
                content="",
                model=model,
                tokens_used=0,
                success=False,
                error=str(e)
            )
    
    def generate_embedding(
        self,
        text: Union[str, List[str]],
        model: Optional[str] = None
    ) -> EmbeddingResponse:
        """Generate text embedding.
        
        Args:
            text: Text or list of texts to embed
            model: Embedding model to use (defaults to self.default_embedding_model)
            
        Returns:
            EmbeddingResponse with embedding result
        """
        model = model or self.default_embedding_model
        
        try:
            def _make_request():
                return self.client.embeddings.create(
                    model=model,
                    input=text
                )
            
            response: CreateEmbeddingResponse = self._retry_with_backoff(_make_request)
            
            if not response.data:
                return EmbeddingResponse(
                    embedding=[],
                    model=response.model,
                    tokens_used=response.usage.total_tokens if response.usage else 0,
                    success=False,
                    dimensions=0,
                    error="No embedding data received"
                )
            
            embedding = response.data[0].embedding
            
            return EmbeddingResponse(
                embedding=embedding,
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                success=True,
                dimensions=len(embedding)
            )
            
        except OpenAIClientError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in embedding generation: {e}")
            return EmbeddingResponse(
                embedding=[],
                model=model,
                tokens_used=0,
                success=False,
                dimensions=0,
                error=str(e)
            )
    
    def test_connection(self) -> bool:
        """Test API connection with a simple request.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.chat_completion(
                messages=[{"role": "user", "content": "Hello! Please respond with 'API test successful'."}],
                max_tokens=10,
                temperature=0
            )
            return response.success and "API test successful" in response.content
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models.
        
        Returns:
            List of model names
        """
        try:
            def _make_request():
                return self.client.models.list()
            
            response = self._retry_with_backoff(_make_request)
            return [model.id for model in response.data]
            
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def validate_models(self, required_models: Optional[List[str]] = None) -> Dict[str, bool]:
        """Validate that required models are available.
        
        Args:
            required_models: List of required model names. If None, uses defaults.
            
        Returns:
            Dict mapping model names to availability status
        """
        if required_models is None:
            required_models = [self.default_model, self.default_embedding_model]
        
        try:
            available_models = set(self.get_available_models())
            return {model: model in available_models for model in required_models}
        except Exception as e:
            logger.error(f"Failed to validate models: {e}")
            return {model: False for model in required_models}


# Convenience function for creating a client with default settings
def create_client(api_key: Optional[str] = None) -> OpenAIClient:
    """Create OpenAI client with default settings.
    
    Args:
        api_key: Optional API key override
        
    Returns:
        Configured OpenAIClient instance
    """
    return OpenAIClient(api_key=api_key)