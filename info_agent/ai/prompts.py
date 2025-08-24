"""Prompt templates for AI-powered information extraction.

This module contains structured prompt templates for various AI operations including:
- Information extraction from unstructured text
- Title and description generation
- Dynamic field creation
- Content categorization
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class PromptType(Enum):
    """Types of prompts available."""
    EXTRACT_ALL = "extract_all"  # Unified extraction for all information
    SEARCH_ANALYSIS = "search_analysis"  # Search query analysis and enhancement


class PromptTemplate:
    """Base class for prompt templates."""
    
    def __init__(self, template: str, required_vars: List[str] = None):
        """Initialize prompt template.
        
        Args:
            template: Template string with {variable} placeholders
            required_vars: List of required variable names
        """
        self.template = template
        self.required_vars = required_vars or []
    
    def format(self, **kwargs) -> str:
        """Format template with provided variables.
        
        Args:
            **kwargs: Variables to substitute in template
            
        Returns:
            Formatted prompt string
            
        Raises:
            ValueError: If required variables are missing
        """
        # Check required variables
        missing_vars = [var for var in self.required_vars if var not in kwargs]
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        return self.template.format(**kwargs)


# Unified information extraction prompt template
EXTRACT_INFO_TEMPLATE = PromptTemplate(
    template="""You are an AI assistant that extracts structured information from unstructured text and generates appropriate metadata.

Given the following text, analyze it comprehensively and extract all relevant information:

TEXT:
{text}

Perform a complete analysis and return your results in the following JSON format:
{{
    "title": "A concise, descriptive title (max 80 characters)",
    "description": "A brief summary of the key points (max 200 characters)",
    "summary": "A longer summary preserving essential information (max 100 words)",
    "categories": ["category1", "category2"],
    "key_facts": ["fact1", "fact2", ...],
    "dates_times": ["date1", "date2", ...],
    "entities": {{
        "people": ["person1", "person2", ...],
        "places": ["place1", "place2", ...],
        "organizations": ["org1", "org2", ...]
    }},
    "action_items": ["task1", "task2", ...],
    "dynamic_fields": {{
        "priority": "high|medium|low",
        "status": "active|completed|pending",
        "due_date": "YYYY-MM-DD or null",
        "source": "meeting|email|note|etc",
        "tags": ["tag1", "tag2", ...],
        "additional_field_name": "field_value"
    }}
}}

Guidelines:
- if the original text is chinese, keep extracted fields also in Chinese
- Title: Be specific and descriptive, capture the main topic, avoid generic words
- Description: Summarize 2-3 main points in complete sentences
- Summary: Preserve the most important information while being concise
- Categories: Choose from common categories like "work", "personal", "learning", "meetings", "tasks", "ideas", "projects" or suggest new ones
- Dynamic fields: Include relevant metadata that would help with searching and organization
- Only include fields that have relevant content from the text
- For dynamic fields, focus on practical metadata like priority, status, due dates, source type, and relevant tags""",
    required_vars=["text"]
)


# Search query analysis prompt template
SEARCH_ANALYSIS_TEMPLATE = PromptTemplate(
    template="""Analyze this search query and extract structured search criteria for filtering search results.

Search Query: "{query}"

Return a JSON object with the following structure:
{{
    "field_filters": {{"field_name": "value"}},
    "categories": ["category1", "category2"],
    "people": ["person1", "person2"],
    "places": ["place1", "place2"],
    "date_hints": ["specific dates or time periods mentioned"],
    "priority_level": "high/medium/low based on query urgency",
    "search_intent": "brief description of what user is looking for"
}}

Guidelines:
- field_filters should map to common dynamic field names (category, people, places, etc.)
- Extract any mentioned people, places, categories from the query
- Identify time/date references if mentioned
- Focus on extracting filter criteria, not rewriting the search query
- Keep response concise and structured""",
    required_vars=["query"]
)


class PromptManager:
    """Manager for handling prompt templates and generation."""
    
    def __init__(self):
        """Initialize prompt manager with unified template."""
        self.templates = {
            PromptType.EXTRACT_ALL: EXTRACT_INFO_TEMPLATE,
            PromptType.SEARCH_ANALYSIS: SEARCH_ANALYSIS_TEMPLATE,
        }
    
    def get_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """Get formatted prompt for given type.
        
        Args:
            prompt_type: Type of prompt to generate
            **kwargs: Variables for template substitution
            
        Returns:
            Formatted prompt string
            
        Raises:
            ValueError: If prompt type not found or required variables missing
        """
        if prompt_type not in self.templates:
            raise ValueError(f"Prompt type {prompt_type} not found")
        
        template = self.templates[prompt_type]
        
        return template.format(**kwargs)
    
    def add_template(self, prompt_type: PromptType, template: PromptTemplate):
        """Add or update a prompt template.
        
        Args:
            prompt_type: Type identifier for the prompt
            template: PromptTemplate instance
        """
        self.templates[prompt_type] = template
    
    def list_available_prompts(self) -> List[PromptType]:
        """Get list of available prompt types.
        
        Returns:
            List of available PromptType values
        """
        return list(self.templates.keys())


# Convenience function
def extract_all_information_prompt(text: str) -> str:
    """Generate unified prompt for complete information extraction.
    
    Extracts title, description, summary, categories, entities, facts, 
    and dynamic fields in a single AI call for maximum efficiency.
    
    Args:
        text: Text to analyze
        
    Returns:
        Formatted unified extraction prompt
    """
    manager = PromptManager()
    return manager.get_prompt(PromptType.EXTRACT_ALL, text=text)


def search_analysis_prompt(query: str) -> str:
    """Generate prompt for search query analysis and enhancement.
    
    Analyzes search queries to extract structured criteria like categories,
    people, places, and enhanced search terms for better search results.
    
    Args:
        query: Search query to analyze
        
    Returns:
        Formatted search analysis prompt
    """
    manager = PromptManager()
    return manager.get_prompt(PromptType.SEARCH_ANALYSIS, query=query)
