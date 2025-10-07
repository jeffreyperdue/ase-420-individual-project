"""
Requirement Structure Detector for StressSpec.

This module handles the detection and parsing of structured requirements,
particularly user stories and other multi-line requirement formats.

BEGINNER NOTES:
- This module understands the structure of requirements (like user stories)
- It can identify when multiple lines belong to the same requirement
- It filters out structural elements like separators and headers
- It follows the Single Responsibility Principle by focusing only on structure detection
"""

import re
from typing import List, Dict, Tuple, Optional
from enum import Enum

class RequirementType(Enum):
    """Types of requirements that can be detected."""
    USER_STORY = "user_story"
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    HEADER = "header"
    SEPARATOR = "separator"
    UNKNOWN = "unknown"

class RequirementStructureDetector:
    """
    Detects and parses structured requirements from raw text lines.
    
    BEGINNER NOTES:
    - This class understands different requirement formats
    - It can combine related lines into complete requirements
    - It filters out non-requirement content like headers and separators
    - It uses pattern matching to identify requirement structures
    """
    
    def __init__(self):
        """Initialize the structure detector with common patterns."""
        # User story patterns (As a... I want... so that...)
        self.user_story_patterns = [
            r'^As\s+a\s+.*?,\s*$',  # "As a user,"
            r'^I\s+want\s+.*?,\s*$',  # "I want to..."
            r'^so\s+that\s+.*?\.?\s*$',  # "so that I can..."
        ]
        
        # Functional requirement patterns
        self.functional_patterns = [
            r'^The\s+system\s+shall\s+.*?\.?\s*$',
            r'^The\s+application\s+must\s+.*?\.?\s*$',
            r'^The\s+system\s+will\s+.*?\.?\s*$',
        ]
        
        # Non-functional requirement patterns
        self.non_functional_patterns = [
            r'^Performance\s*[-:]\s*.*?\.?\s*$',
            r'^Usability\s*[-:]\s*.*?\.?\s*$',
            r'^Reliability\s*[-:]\s*.*?\.?\s*$',
            r'^Scalability\s*[-:]\s*.*?\.?\s*$',
            r'^Security\s*[-:]\s*.*?\.?\s*$',
            r'^Availability\s*[-:]\s*.*?\.?\s*$',
            r'^Maintainability\s*[-:]\s*.*?\.?\s*$',
        ]
        
        # Header patterns (markdown headers, numbered sections)
        self.header_patterns = [
            r'^#+\s+.*?$',  # Markdown headers
            r'^##+\s+.*?$',  # Sub-headers
            r'^\d+\.\s+.*?$',  # Numbered sections
            r'^###\s+.*?$',  # Sub-sections
        ]
        
        # Separator patterns
        self.separator_patterns = [
            r'^---+$',  # Markdown horizontal rules
            r'^===+$',  # Alternative separators
            r'^___+$',  # Underscore separators
            r'^\*\*\*+$',  # Asterisk separators
        ]
    
    def detect_requirement_type(self, line: str) -> RequirementType:
        """
        Detect the type of a single line.
        
        Args:
            line: The text line to analyze
            
        Returns:
            RequirementType enum value
        """
        line = line.strip()
        
        # Check for separators first
        for pattern in self.separator_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return RequirementType.SEPARATOR
        
        # Check for headers
        for pattern in self.header_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return RequirementType.HEADER
        
        # Check for user story patterns
        for pattern in self.user_story_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return RequirementType.USER_STORY
        
        # Check for functional requirements
        for pattern in self.functional_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return RequirementType.FUNCTIONAL
        
        # Check for non-functional requirements
        for pattern in self.non_functional_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return RequirementType.NON_FUNCTIONAL
        
        return RequirementType.UNKNOWN
    
    def parse_structured_requirements(self, lines: List[str]) -> List[Dict]:
        """
        Parse structured requirements from a list of lines.
        
        Args:
            lines: List of text lines to parse
            
        Returns:
            List of dictionaries containing structured requirements
        """
        requirements = []
        current_requirement = None
        current_type = None
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Detect the type of this line
            line_type = self.detect_requirement_type(line)
            
            # Handle separators - end current requirement if any
            if line_type == RequirementType.SEPARATOR:
                if current_requirement:
                    requirements.append(current_requirement)
                    current_requirement = None
                    current_type = None
                continue
            
            # Handle headers - end current requirement and start new section
            if line_type == RequirementType.HEADER:
                if current_requirement:
                    requirements.append(current_requirement)
                    current_requirement = None
                    current_type = None
                continue
            
            # Handle user story lines
            if line_type == RequirementType.USER_STORY:
                # If we have a current requirement, finish it
                if current_requirement and current_type != RequirementType.USER_STORY:
                    requirements.append(current_requirement)
                    current_requirement = None
                
                # Start new user story
                if current_requirement is None:
                    current_requirement = {
                        'type': 'user_story',
                        'lines': [],
                        'line_numbers': [],
                        'text': ''
                    }
                    current_type = RequirementType.USER_STORY
                
                current_requirement['lines'].append(line)
                current_requirement['line_numbers'].append(line_num)
                current_requirement['text'] += line + ' '
                continue
            
            # Handle functional/non-functional requirements
            if line_type in [RequirementType.FUNCTIONAL, RequirementType.NON_FUNCTIONAL]:
                # If we have a current requirement, finish it
                if current_requirement:
                    requirements.append(current_requirement)
                
                # Start new requirement
                current_requirement = {
                    'type': line_type.value,
                    'lines': [line],
                    'line_numbers': [line_num],
                    'text': line
                }
                current_type = line_type
                continue
            
            # Handle continuation lines (unknown type that might be part of current requirement)
            if current_requirement and line_type == RequirementType.UNKNOWN:
                # Only add if it looks like it could be a continuation
                if self._looks_like_continuation(line, current_type):
                    current_requirement['lines'].append(line)
                    current_requirement['line_numbers'].append(line_num)
                    current_requirement['text'] += line + ' '
                    continue
            
            # If we get here, it's an unknown line that doesn't fit current requirement
            # Finish current requirement if any
            if current_requirement:
                requirements.append(current_requirement)
                current_requirement = None
                current_type = None
        
        # Don't forget the last requirement
        if current_requirement:
            requirements.append(current_requirement)
        
        return requirements
    
    def _looks_like_continuation(self, line: str, requirement_type: RequirementType) -> bool:
        """
        Determine if a line looks like it could be a continuation of the current requirement.
        
        Args:
            line: The line to check
            requirement_type: The type of the current requirement
            
        Returns:
            True if the line looks like a continuation
        """
        line = line.strip()
        
        # For user stories, look for continuation patterns
        if requirement_type == RequirementType.USER_STORY:
            # Lines that start with lowercase or are clearly continuations
            if (line[0].islower() or 
                line.startswith('I want') or 
                line.startswith('so that') or
                line.startswith('I need')):
                return True
        
        # For other requirements, look for lines that don't start with new requirement indicators
        if (not any(line.startswith(pattern.split()[0]) for pattern in self.functional_patterns) and
            not any(line.startswith(pattern.split()[0]) for pattern in self.non_functional_patterns) and
            not line.startswith('As a') and
            len(line) > 10):  # Reasonable length for a continuation
            return True
        
        return False
    
    def filter_valid_requirements(self, structured_requirements: List[Dict]) -> List[Dict]:
        """
        Filter out requirements that aren't actually valid requirements.
        
        Args:
            structured_requirements: List of structured requirements
            
        Returns:
            List of valid requirements only
        """
        valid_requirements = []
        
        for req in structured_requirements:
            # Skip if it's too short or doesn't look like a real requirement
            if len(req['text'].strip()) < 10:
                continue
            
            # Skip if it's just a single word or very short phrase
            if len(req['text'].split()) < 3:
                continue
            
            # Skip if it's clearly not a requirement (like just punctuation)
            if req['text'].strip() in ['---', '...', '***', '___']:
                continue
            
            # For user stories, make sure we have at least 2 parts
            if req['type'] == 'user_story' and len(req['lines']) < 2:
                continue
            
            valid_requirements.append(req)
        
        return valid_requirements

