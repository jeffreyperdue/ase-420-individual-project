"""
StressSpec service for orchestrating the complete analysis workflow.

This module provides a high-level service that coordinates the entire
requirement analysis process from file loading to report generation.

BEGINNER NOTES:
- This service is like a "conductor" that orchestrates all the components
- It coordinates file loading, parsing, analysis, scoring, and reporting
- It follows the Single Responsibility Principle - orchestrates the workflow
- It makes the main.py simpler and easier to test
"""

from pathlib import Path
from typing import Optional, List
from src.file_loader import FileLoader
from src.requirement_parser import RequirementParser
from src.factories.detector_factory import RiskDetectorFactory
from src.factories.reporter_factory import ReporterFactory
from src.analyzer import analyze_requirements
from src.scoring import calculate_risk_scores, get_top_riskiest
from src.reporting import ReportFormat, ReportData
from src.patterns.observer import AnalysisProgressSubject, AnalysisProgressObserver
from src.constants import AnalysisProgress


class StressSpecService:
    """
    Orchestrates the complete analysis workflow.
    
    BEGINNER NOTES:
    - This service coordinates all the steps needed to analyze requirements
    - It's like a "recipe" that combines all the ingredients (components)
    - It makes the main program simpler by hiding the complexity
    - It can be easily tested by injecting mock dependencies
    
    This service provides:
    - Complete workflow orchestration (load → parse → analyze → report)
    - Dependency injection for testing
    - Clean separation of concerns
    """
    
    def __init__(self, 
                 file_loader: Optional[FileLoader] = None,
                 parser: Optional[RequirementParser] = None,
                 detector_factory: Optional[RiskDetectorFactory] = None,
                 reporter_factory: Optional[ReporterFactory] = None,
                 progress_observers: Optional[List[AnalysisProgressObserver]] = None):
        """
        Initialize the service with dependencies.
        
        Args:
            file_loader: Optional FileLoader instance (for dependency injection/testing)
            parser: Optional RequirementParser instance (for dependency injection/testing)
            detector_factory: Optional RiskDetectorFactory instance (for dependency injection/testing)
            reporter_factory: Optional ReporterFactory instance (for dependency injection/testing)
            progress_observers: Optional list of progress observers (for Observer pattern)
        """
        self.file_loader = file_loader or FileLoader()
        self.parser = parser or RequirementParser()
        self.detector_factory = detector_factory or RiskDetectorFactory()
        self.reporter_factory = reporter_factory or ReporterFactory()
        
        # Set up progress notification (Observer pattern)
        self.progress_subject = AnalysisProgressSubject()
        if progress_observers:
            for observer in progress_observers:
                self.progress_subject.add_observer(observer)
    
    def add_progress_observer(self, observer: AnalysisProgressObserver) -> None:
        """
        Add a progress observer (Observer pattern).
        
        Args:
            observer: Observer instance to add
        """
        self.progress_subject.add_observer(observer)
    
    def analyze_file(self, 
                    file_path: str,
                    report_format: ReportFormat,
                    output_path: Optional[str] = None) -> Path:
        """
        Complete analysis workflow: load file, parse requirements, detect risks, generate report.
        
        Args:
            file_path: Path to the requirements file
            report_format: Format for the output report
            output_path: Optional output file path (defaults to report.{format})
            
        Returns:
            Path to the generated report file
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If the file is invalid or empty
        """
        # Step 1: Load the file
        self.progress_subject.notify_progress("Loading", AnalysisProgress.LOADING, "Loading file...")
        raw_lines = self.file_loader.load_file(file_path)
        
        # Step 2: Parse requirements
        self.progress_subject.notify_progress("Parsing", AnalysisProgress.PARSING, "Parsing requirements...")
        requirements = self.parser.parse_requirements(raw_lines)
        
        # Step 3: Run risk detectors
        self.progress_subject.notify_progress("Detecting", AnalysisProgress.DETECTING, "Running risk detectors...")
        detectors = (self.detector_factory.create_enabled_detectors() or 
                    self.detector_factory.create_all_detectors())
        risks_by_requirement = analyze_requirements(requirements, detectors)
        
        # Step 4: Calculate risk scores and identify top 5 riskiest
        self.progress_subject.notify_progress("Scoring", AnalysisProgress.SCORING, "Calculating risk scores...")
        risk_scores = calculate_risk_scores(requirements, risks_by_requirement)
        top_5_riskiest = get_top_riskiest(requirements, risk_scores, top_n=5)
        
        # Step 5: Generate report
        self.progress_subject.notify_progress("Generating", AnalysisProgress.GENERATING, "Generating report...")
        data = ReportData(
            requirements=requirements,
            risks_by_requirement=risks_by_requirement,
            source_file=file_path,
            top_5_riskiest=top_5_riskiest,
        )
        
        reporter = self.reporter_factory.create_reporter(report_format)
        output_path = reporter.write(data, output_path)
        
        self.progress_subject.notify_progress("Complete", AnalysisProgress.COMPLETE, "Analysis completed successfully")
        return output_path

