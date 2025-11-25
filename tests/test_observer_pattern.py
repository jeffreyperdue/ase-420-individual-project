"""
Tests for Observer pattern implementation.

This module tests the Observer pattern used for progress reporting.
"""

import pytest
from src.patterns.observer import (
    AnalysisProgressObserver,
    ConsoleProgressObserver,
    SilentProgressObserver,
    AnalysisProgressSubject
)


class TestAnalysisProgressObserver:
    """Test cases for progress observers."""
    
    def test_console_observer_output(self, capsys):
        """Test that ConsoleProgressObserver prints progress."""
        observer = ConsoleProgressObserver()
        observer.on_progress("Loading", 50, "Loading file...")
        
        captured = capsys.readouterr()
        assert "[50%] Loading: Loading file..." in captured.out
    
    def test_silent_observer_no_output(self, capsys):
        """Test that SilentProgressObserver produces no output."""
        observer = SilentProgressObserver()
        observer.on_progress("Loading", 50, "Loading file...")
        
        captured = capsys.readouterr()
        assert captured.out == ""


class TestAnalysisProgressSubject:
    """Test cases for progress subject."""
    
    def test_add_observer(self):
        """Test adding an observer."""
        subject = AnalysisProgressSubject()
        observer = ConsoleProgressObserver()
        
        subject.add_observer(observer)
        assert len(subject.observers) == 1
        assert observer in subject.observers
    
    def test_add_duplicate_observer(self):
        """Test that duplicate observers are not added."""
        subject = AnalysisProgressSubject()
        observer = ConsoleProgressObserver()
        
        subject.add_observer(observer)
        subject.add_observer(observer)
        
        assert len(subject.observers) == 1
    
    def test_remove_observer(self):
        """Test removing an observer."""
        subject = AnalysisProgressSubject()
        observer = ConsoleProgressObserver()
        
        subject.add_observer(observer)
        subject.remove_observer(observer)
        
        assert len(subject.observers) == 0
    
    def test_notify_progress(self, capsys):
        """Test notifying observers of progress."""
        subject = AnalysisProgressSubject()
        observer = ConsoleProgressObserver()
        
        subject.add_observer(observer)
        subject.notify_progress("Loading", 50, "Loading file...")
        
        captured = capsys.readouterr()
        assert "[50%] Loading: Loading file..." in captured.out
    
    def test_notify_multiple_observers(self, capsys):
        """Test notifying multiple observers."""
        subject = AnalysisProgressSubject()
        observer1 = ConsoleProgressObserver()
        observer2 = ConsoleProgressObserver()
        
        subject.add_observer(observer1)
        subject.add_observer(observer2)
        subject.notify_progress("Loading", 50, "Loading file...")
        
        captured = capsys.readouterr()
        # Should see the message twice (once per observer)
        assert captured.out.count("[50%] Loading: Loading file...") == 2
    
    def test_notify_handles_observer_errors(self, capsys):
        """Test that observer errors don't break notification."""
        subject = AnalysisProgressSubject()
        
        class FailingObserver(AnalysisProgressObserver):
            def on_progress(self, stage: str, progress: int, message: str) -> None:
                raise ValueError("Observer error")
        
        observer1 = FailingObserver()
        observer2 = ConsoleProgressObserver()
        
        subject.add_observer(observer1)
        subject.add_observer(observer2)
        
        # Should not raise, and second observer should still be notified
        subject.notify_progress("Loading", 50, "Loading file...")
        
        captured = capsys.readouterr()
        assert "[50%] Loading: Loading file..." in captured.out

