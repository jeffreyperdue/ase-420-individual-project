"""
Text normalization and keyword matching utilities for StressSpec.

This module provides text normalization and keyword matching functionality
that can be reused across different components.

BEGINNER NOTES:
- This is a utility class that handles text processing
- It can be used by detectors, parsers, or any component that needs text normalization
- It follows the Single Responsibility Principle - it only handles text operations
"""

from typing import List


class TextNormalizer:
    """
    Handles text normalization and keyword matching.
    
    BEGINNER NOTES:
    - This class is like a "text processing tool" that can be used anywhere
    - It doesn't depend on detector configuration - it's a pure utility
    - It can be easily tested and reused in different contexts
    
    This class provides:
    - Text normalization (lowercase, strip whitespace)
    - Keyword matching (find keywords in text)
    """
    
    def normalize_text(self, text: str, case_sensitive: bool = False) -> str:
        """
        Normalize text for comparison (lowercase, strip whitespace).
        
        Args:
            text: Text to normalize
            case_sensitive: If True, preserve case; if False, convert to lowercase
            
        Returns:
            Normalized text
        """
        if not case_sensitive:
            text = text.lower()
        return text.strip()
    
    def contains_keywords(self, text: str, keywords: List[str], 
                         case_sensitive: bool = False) -> List[str]:
        """
        Check if text contains any of the specified keywords.
        
        Args:
            text: Text to search in
            keywords: List of keywords to search for
            case_sensitive: If True, case-sensitive matching; if False, case-insensitive
            
        Returns:
            List of keywords found in the text (returns original keyword strings, not normalized)
        """
        normalized_text = self.normalize_text(text, case_sensitive)
        found_keywords = []
        
        for keyword in keywords:
            normalized_keyword = self.normalize_text(keyword, case_sensitive)
            if normalized_keyword in normalized_text:
                found_keywords.append(keyword)
        
        return found_keywords

