"""
Observer pattern implementation for progress reporting in StressSpec.

This module implements the Observer pattern to allow components to observe
and react to analysis progress updates without tight coupling.

BEGINNER NOTES:
- This follows the Observer pattern from design patterns course materials
- It allows multiple observers to be notified of progress updates
- It decouples progress reporting from analysis logic
- It makes it easy to add new progress observers (console, file, web socket, etc.)
"""

from abc import ABC, abstractmethod
from typing import List


class AnalysisProgressObserver(ABC):
    """
    Observer interface for analysis progress updates.
    
    BEGINNER NOTES:
    - This is the "observer contract" that all progress observers must follow
    - It's like a subscription - observers subscribe to progress updates
    - When progress changes, all observers are notified
    - This follows the Observer pattern from design patterns course
    
    This interface defines:
    - on_progress(): Method called when progress updates occur
    """
    
    @abstractmethod
    def on_progress(self, stage: str, progress: int, message: str) -> None:
        """
        Called when analysis progress updates.
        
        Args:
            stage: Current stage name (e.g., "Loading", "Detecting")
            progress: Progress percentage (0-100)
            message: Human-readable progress message
        """
        pass


class ConsoleProgressObserver(AnalysisProgressObserver):
    """
    Console-based progress observer that prints to stdout.
    
    BEGINNER NOTES:
    - This observer prints progress to the console
    - It's useful for CLI applications
    - It's like a "progress reporter" that shows updates on screen
    """
    
    def on_progress(self, stage: str, progress: int, message: str) -> None:
        """Print progress to console."""
        print(f"[{progress}%] {stage}: {message}")


class SilentProgressObserver(AnalysisProgressObserver):
    """
    Silent progress observer that does nothing.
    
    BEGINNER NOTES:
    - This observer doesn't output anything
    - It's useful when you don't want progress updates
    - It's like a "null observer" - it observes but does nothing
    """
    
    def on_progress(self, stage: str, progress: int, message: str) -> None:
        """Do nothing - silent observer."""
        pass


class AnalysisProgressSubject:
    """
    Subject that notifies observers of progress updates.
    
    BEGINNER NOTES:
    - This is the "subject" in the Observer pattern
    - It maintains a list of observers
    - When progress changes, it notifies all observers
    - It's like a "broadcaster" that sends updates to all subscribers
    
    This class provides:
    - Observer registration (add/remove observers)
    - Progress notification (notify all observers)
    """
    
    def __init__(self):
        """Initialize with empty observer list."""
        self.observers: List[AnalysisProgressObserver] = []
    
    def add_observer(self, observer: AnalysisProgressObserver) -> None:
        """
        Register an observer to receive progress updates.
        
        Args:
            observer: Observer instance to register
        """
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: AnalysisProgressObserver) -> None:
        """
        Unregister an observer.
        
        Args:
            observer: Observer instance to remove
        """
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_progress(self, stage: str, progress: int, message: str) -> None:
        """
        Notify all observers of progress update.
        
        Args:
            stage: Current stage name
            progress: Progress percentage (0-100)
            message: Progress message
        """
        for observer in self.observers:
            try:
                observer.on_progress(stage, progress, message)
            except Exception as e:
                # Don't let observer errors break the analysis
                # Log error but continue
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Observer {type(observer).__name__} failed: {e}")

