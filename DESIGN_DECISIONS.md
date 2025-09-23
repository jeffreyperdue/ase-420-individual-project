# StressSpec Design Decisions & Reference Framework

This document captures the key architectural patterns, design principles, and implementation guidelines derived from the reference documentation in `ref_docs/`. Use this as a guide when making decisions about code structure, patterns, and implementation approaches.

## 🏗️ Core Architectural Principles

### Software Design Philosophy
> **"Software design is about interfaces and modules"**

- **Modules**: Self-contained units of functionality (like rooms in a house)
- **Interfaces**: Contracts that define how modules communicate (like doors and windows)
- Each module should have a single, clear responsibility
- Use interfaces to define contracts between modules

### Architectural Patterns for StressSpec

#### 1. Layered Architecture (Recommended for CLI Tool)
```
┌─────────────────────┐
│   Presentation      │ ← CLI Interface (main.py)
├─────────────────────┤
│   Business Logic    │ ← Risk Detection, Parsing
├─────────────────────┤
│   Data Access       │ ← File Loading, Configuration
├─────────────────────┤
│   Data Storage      │ ← Files, Rules, Reports
└─────────────────────┘
```

#### 2. Factory Method Pattern
Use for creating different risk detection modules:

```python
class RiskDetectorFactory:
    def create_detector(self, detector_type: str) -> RiskDetector:
        # Creates AmbiguityDetector, SecurityDetector, etc.
```

#### 3. Strategy Pattern
Use for different risk detection algorithms:

```python
class RiskDetectionStrategy:
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        pass

class AmbiguityStrategy(RiskDetectionStrategy):
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        # Ambiguity-specific detection logic
```

#### 4. Template Method Pattern
Use for consistent risk detection workflow:

```python
class BaseRiskDetector:
    def analyze_requirement(self, requirement: Requirement):
        # Template method defining the workflow
        risks = self.detect_risks(requirement)
        return self.calculate_severity(risks)
```

## 🎯 SOLID Principles Implementation

### Current Implementation Status ✅
The existing code already demonstrates excellent SOLID adherence:

- **✅ Single Responsibility**: `FileLoader`, `RequirementParser`, `Requirement` each have one job
- **✅ Open/Closed**: Ready for extension with new risk detection modules
- **✅ Liskov Substitution**: Interfaces are well-designed
- **✅ Interface Segregation**: Clean, focused interfaces
- **✅ Dependency Inversion**: Good separation of concerns

### Future Implementation Guidelines

When adding new modules, ensure they follow these principles:

```python
# ✅ Good: Single Responsibility
class AmbiguityDetector:
    def detect_ambiguity_risks(self, requirement: Requirement) -> List[Risk]:
        # Only handles ambiguity detection

# ❌ Bad: Multiple Responsibilities
class RiskDetector:
    def detect_all_risks(self, requirement: Requirement):
        # Handles ambiguity, security, performance, etc.
```

## 🧪 Testing Standards

### Testing Philosophy
> **"Testing is the most efficient way to make high-quality software"**

### Testing Pyramid
1. **Unit Tests** (Bottom - Most tests)
   - Test individual functions/methods
   - Fast and isolated
   - Current status: ✅ 27 passing tests

2. **Integration Tests** (Middle)
   - Test how modules work together
   - Current status: ✅ 3 integration tests

3. **Acceptance Tests** (Top - Fewest tests)
   - Test complete user scenarios
   - Current status: ⏳ To be implemented

### Testing Rules
1. **Test Early, Test Often** - Write tests as you develop, not after
2. **Make It Automatic** - Set up continuous testing
3. **Bug = Update Tests** - Fix the bug AND prevent it from recurring
4. **Regression Tests** - Re-run after every code change

### Test Structure Example
```python
class TestAmbiguityDetector:
    def test_detect_vague_terms(self):
        """Test detection of vague terms like 'should', 'might'."""
        detector = AmbiguityDetector()
        requirement = Requirement("R001", 1, "The system should be fast")
        risks = detector.detect_risks(requirement)
        assert len(risks) > 0
        assert any(risk.category == "ambiguity" for risk in risks)
```

## 🔧 Design Patterns for Risk Detection

### Recommended Pattern Structure

```python
# 1. Interface Definition
from abc import ABC, abstractmethod

class RiskDetector(ABC):
    @abstractmethod
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        """Detect risks in a single requirement."""
        pass
    
    @abstractmethod
    def get_detector_name(self) -> str:
        """Return the name of this detector."""
        pass

# 2. Concrete Implementation
class AmbiguityDetector(RiskDetector):
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        risks = []
        vague_terms = ["should", "might", "could", "possibly", "maybe"]
        
        for term in vague_terms:
            if term.lower() in requirement.text.lower():
                risk = Risk(
                    id=f"AMB-{requirement.id}",
                    category="ambiguity",
                    severity="medium",
                    description=f"Vague term '{term}' found",
                    requirement_id=requirement.id,
                    line_number=requirement.line_number
                )
                risks.append(risk)
        
        return risks
    
    def get_detector_name(self) -> str:
        return "Ambiguity Detector"

# 3. Factory for Creation
class RiskDetectorFactory:
    _detectors = {
        "ambiguity": AmbiguityDetector,
        "security": SecurityDetector,
        "performance": PerformanceDetector,
        "availability": AvailabilityDetector
    }
    
    def create_detector(self, detector_type: str) -> RiskDetector:
        if detector_type not in self._detectors:
            raise ValueError(f"Unknown detector type: {detector_type}")
        return self._detectors[detector_type]()
```

## 🚫 Code Smells to Avoid

### Common Anti-Patterns
1. **Long Methods** (Room too crowded)
   ```python
   # ❌ Bad
   def process_requirement():
       # 200 lines of code!
   
   # ✅ Good
   def process_requirement():
       risks = detect_risks()
       severity = calculate_severity(risks)
       return generate_report(risks, severity)
   ```

2. **Large Classes** (Room doing too many things)
   ```python
   # ❌ Bad
   class RequirementProcessor:
       def parse_requirements(self): pass
       def detect_risks(self): pass
       def generate_reports(self): pass
       def send_emails(self): pass
   
   # ✅ Good
   class RequirementParser: pass
   class RiskDetector: pass
   class ReportGenerator: pass
   class NotificationService: pass
   ```

3. **Duplicate Code** (Same room built multiple times)
   ```python
   # ❌ Bad
   # Same validation logic in multiple places
   
   # ✅ Good
   class RequirementValidator:
       def validate_requirement(self, req: Requirement) -> bool:
           # Single source of validation logic
   ```

4. **Feature Envy** (Room accessing neighbor's stuff)
   ```python
   # ❌ Bad
   class ReportGenerator:
       def generate_report(self, requirement):
           # Accessing too much of requirement's internal data
           return requirement.text.upper() + requirement.id.lower()
   
   # ✅ Good
   class ReportGenerator:
       def generate_report(self, requirement):
           return f"{requirement.id}: {requirement.text}"
   ```

## 📋 Implementation Guidelines

### File Structure
```
src/
├── detectors/           # Risk detection modules
│   ├── __init__.py
│   ├── base.py         # BaseRiskDetector abstract class
│   ├── ambiguity.py    # AmbiguityDetector
│   ├── security.py     # SecurityDetector
│   └── performance.py  # PerformanceDetector
├── models/
│   ├── __init__.py
│   ├── requirement.py  # Existing
│   ├── risk.py         # New Risk model
│   └── report.py       # New Report model
├── factories/
│   ├── __init__.py
│   └── detector_factory.py
└── utils/
    ├── __init__.py
    └── config_loader.py
```

### Error Handling
Follow the existing pattern of comprehensive error handling:

```python
try:
    detector = factory.create_detector(detector_type)
    risks = detector.detect_risks(requirement)
except ValueError as e:
    logger.error(f"Invalid detector type: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error in risk detection: {e}")
    raise
```

### Configuration Management
Use JSON configuration files for rules (following the project requirements):

```json
{
  "detectors": {
    "ambiguity": {
      "enabled": true,
      "vague_terms": ["should", "might", "could", "possibly"],
      "severity": "medium"
    },
    "security": {
      "enabled": true,
      "security_terms": ["password", "authentication", "encryption"],
      "severity": "high"
    }
  }
}
```

## 📖 Documentation Standards

### Code Documentation
Follow the existing educational documentation style:

```python
class AmbiguityDetector(RiskDetector):
    """
    Detects ambiguous language in requirements.
    
    BEGINNER NOTES:
    - This detector looks for vague terms that make requirements unclear
    - It's like a grammar checker that flags imprecise language
    - Each vague term found creates a risk flag with medium severity
    
    Examples of ambiguous terms:
    - "should" instead of "shall" or "must"
    - "might" instead of "will" or "can"
    - "possibly" instead of specific conditions
    """
    
    def detect_risks(self, requirement: Requirement) -> List[Risk]:
        """
        Analyze a requirement for ambiguous language.
        
        Args:
            requirement: The requirement to analyze
            
        Returns:
            List of Risk objects representing ambiguity issues found
        """
        # Implementation here
```

### README Updates
When adding new features, update the README with:
- New command-line options
- New detector types
- Example usage
- Updated project structure

## 🔄 Refactoring Guidelines

### When to Refactor
- When adding new risk detection modules
- When code duplication is detected
- When methods become too long (>50 lines)
- When classes have too many responsibilities

### Refactoring Process
1. **Write tests first** for existing functionality
2. **Refactor incrementally** - small, safe changes
3. **Run tests after each change** to ensure nothing breaks
4. **Update documentation** to reflect changes

## 🎯 Future Architecture Decisions

### Phase 2 Considerations
- **Plugin Architecture**: Allow external risk detectors
- **Rule Engine**: More sophisticated rule evaluation
- **Machine Learning**: AI-powered risk detection
- **Web Interface**: Browser-based GUI
- **API Endpoints**: REST API for integration

### Technology Choices
- **Configuration**: JSON files (as specified in requirements)
- **Testing**: pytest (already established)
- **Logging**: Python logging module
- **Type Hints**: Full type annotations (already implemented)
- **Documentation**: Markdown + docstrings (current standard)

## 📚 Reference Materials

This framework is derived from:
- `ref_docs/common_repo_docs/SWE/` - Software Engineering principles
- `ref_docs/420_docs/code/SOLID/` - SOLID principles examples
- `ref_docs/420_docs/code/design_patterns/` - Design pattern implementations
- `ref_docs/420_docs/code/refactoring/` - Refactoring techniques

## 🚀 Quick Start for New Features

When implementing new risk detection modules:

1. **Create the detector class** following the `RiskDetector` interface
2. **Add comprehensive tests** with edge cases
3. **Update the factory** to include the new detector
4. **Add configuration** in `rules.json`
5. **Update documentation** and examples
6. **Run the full test suite** to ensure nothing breaks

Remember: **"The goal is not just to make it work, but to make it maintainable, testable, and extensible."**
