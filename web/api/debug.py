"""
Debug and Error Reporting Tools for StressSpec Web UI

This module provides comprehensive debugging and error reporting capabilities
for the StressSpec web application.

BEGINNER NOTES:
- This module provides tools for debugging and error reporting
- It helps developers and users report issues effectively
- It provides system information and error context
- It helps with troubleshooting and support
"""

import os
import sys
import json
import traceback
import platform
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

# Optional import for psutil (system monitoring)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None
    PSUTIL_AVAILABLE = False

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .exceptions import StressSpecException
from .logging_config import get_logger, log_error_with_context

logger = get_logger(__name__)

# Create router for debug endpoints
router = APIRouter()

class DebugInfo(BaseModel):
    """Model for debug information."""
    timestamp: str
    system_info: Dict[str, Any]
    application_info: Dict[str, Any]
    error_info: Optional[Dict[str, Any]] = None
    request_info: Optional[Dict[str, Any]] = None

class ErrorReport(BaseModel):
    """Model for error reports."""
    error_id: str
    timestamp: str
    error_type: str
    error_message: str
    stack_trace: str
    context: Dict[str, Any]
    user_info: Dict[str, Any]
    system_info: Dict[str, Any]

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    BEGINNER NOTES:
    - This collects information about the system environment
    - It helps with debugging by providing context
    - It includes hardware, software, and configuration details
    """
    
    try:
        # Basic system info
        system_info = {
            'platform': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': platform.node()
            },
            'python': {
                'version': sys.version,
                'executable': sys.executable,
                'path': sys.path[:5]  # First 5 paths only
            },
            'environment': {
                'python_path': os.environ.get('PYTHONPATH', ''),
                'virtual_env': os.environ.get('VIRTUAL_ENV', ''),
                'conda_env': os.environ.get('CONDA_DEFAULT_ENV', ''),
                'path': os.environ.get('PATH', '')[:500]  # Truncate long paths
            }
        }
        
        # Hardware info (if psutil is available)
        if PSUTIL_AVAILABLE:
            try:
                system_info['hardware'] = {
                    'cpu_count': psutil.cpu_count(),
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory': {
                        'total': psutil.virtual_memory().total,
                        'available': psutil.virtual_memory().available,
                        'percent': psutil.virtual_memory().percent
                    },
                    'disk': {
                        'total': psutil.disk_usage('.').total,
                        'used': psutil.disk_usage('.').used,
                        'free': psutil.disk_usage('.').free,
                        'percent': psutil.disk_usage('.').percent
                    }
                }
            except Exception as e:
                system_info['hardware'] = {'error': f'psutil error: {str(e)}'}
        else:
            system_info['hardware'] = {'error': 'psutil not available'}
        
        # Application-specific info
        system_info['application'] = {
            'working_directory': os.getcwd(),
            'script_directory': Path(__file__).parent.parent.parent,
            'log_directory': Path('logs').absolute(),
            'upload_directory': Path('uploads').absolute(),
            'data_directory': Path('data').absolute()
        }
        
        return system_info
        
    except Exception as e:
        logger.error(f"Failed to get system info: {str(e)}")
        return {'error': str(e)}

def get_application_info() -> Dict[str, Any]:
    """
    Get application-specific information.
    
    BEGINNER NOTES:
    - This collects information about the application state
    - It includes configuration, versions, and runtime info
    - It helps with debugging application-specific issues
    """
    
    try:
        app_info = {
            'version': '1.0.0',
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug_mode': os.getenv('DEBUG', 'False').lower() == 'true',
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'max_file_size': os.getenv('MAX_FILE_SIZE', '10485760'),
            'allowed_extensions': os.getenv('ALLOWED_EXTENSIONS', '.txt,.md').split(','),
            'analysis_timeout': os.getenv('ANALYSIS_TIMEOUT', '300'),
            'max_concurrent_analyses': os.getenv('MAX_CONCURRENT_ANALYSES', '5')
        }
        
        # Check if key files exist
        key_files = {
            'rules_json': Path('data/rules.json').exists(),
            'logs_dir': Path('logs').exists(),
            'uploads_dir': Path('uploads').exists(),
            'requirements_txt': Path('requirements.txt').exists(),
            'main_py': Path('main.py').exists(),
            'web_main_py': Path('web/main.py').exists()
        }
        app_info['files'] = key_files
        
        # Get recent log files
        try:
            logs_dir = Path('logs')
            if logs_dir.exists():
                log_files = []
                for log_file in logs_dir.glob('*.log'):
                    log_files.append({
                        'name': log_file.name,
                        'size': log_file.stat().st_size,
                        'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                    })
                app_info['log_files'] = sorted(log_files, key=lambda x: x['modified'], reverse=True)[:5]
            else:
                app_info['log_files'] = []
        except Exception as e:
            app_info['log_files'] = {'error': str(e)}
        
        return app_info
        
    except Exception as e:
        logger.error(f"Failed to get application info: {str(e)}")
        return {'error': str(e)}

def get_error_context(error: Exception, request: Optional[Request] = None) -> Dict[str, Any]:
    """
    Get error context information.
    
    BEGINNER NOTES:
    - This collects context about an error
    - It includes stack trace, request info, and environment
    - It helps with debugging and error reporting
    """
    
    try:
        context = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'stack_trace': traceback.format_exc(),
            'timestamp': datetime.utcnow().isoformat(),
            'python_path': sys.path,
            'working_directory': os.getcwd()
        }
        
        # Add request information if available
        if request:
            context['request'] = {
                'method': request.method,
                'url': str(request.url),
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'headers': dict(request.headers),
                'client_ip': request.client.host if request.client else None
            }
        
        return context
        
    except Exception as e:
        logger.error(f"Failed to get error context: {str(e)}")
        return {'error': str(e)}

@router.get("/debug/info")
async def get_debug_info(request: Request):
    """
    Get comprehensive debug information.
    
    BEGINNER NOTES:
    - This endpoint provides system and application debug information
    - It's useful for troubleshooting and support
    - It includes hardware, software, and configuration details
    """
    
    try:
        debug_info = DebugInfo(
            timestamp=datetime.utcnow().isoformat(),
            system_info=get_system_info(),
            application_info=get_application_info(),
            request_info={
                'method': request.method,
                'url': str(request.url),
                'path': request.url.path,
                'client_ip': request.client.host if request.client else None,
                'user_agent': request.headers.get('user-agent', 'Unknown')
            }
        )
        
        logger.info("Debug info requested", extra={'extra_fields': {'client_ip': request.client.host if request.client else None}})
        
        return debug_info.dict()
        
    except Exception as e:
        logger.error(f"Failed to get debug info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get debug info: {str(e)}")

@router.get("/debug/logs")
async def get_recent_logs(lines: int = 100, log_file: str = "application.log"):
    """
    Get recent log entries.
    
    BEGINNER NOTES:
    - This endpoint provides recent log entries for debugging
    - It helps with troubleshooting by showing recent activity
    - It's useful for support and debugging
    """
    
    try:
        log_path = Path('logs') / log_file
        
        if not log_path.exists():
            raise HTTPException(status_code=404, detail=f"Log file {log_file} not found")
        
        # Read recent lines
        with open(log_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # Parse log entries (assuming JSON format)
        log_entries = []
        for line in recent_lines:
            try:
                if line.strip():
                    log_entry = json.loads(line.strip())
                    log_entries.append(log_entry)
            except json.JSONDecodeError:
                # Fallback for non-JSON logs
                log_entries.append({'raw': line.strip()})
        
        return {
            'log_file': log_file,
            'total_lines': len(all_lines),
            'returned_lines': len(recent_lines),
            'entries': log_entries
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recent logs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent logs: {str(e)}")

@router.post("/debug/report-error")
async def report_error(error_report: ErrorReport, request: Request):
    """
    Report an error for debugging and support.
    
    BEGINNER NOTES:
    - This endpoint allows clients to report errors
    - It collects comprehensive error information
    - It helps with debugging and improving the application
    """
    
    try:
        # Log the error report
        logger.error(f"Error report received: {error_report.error_id}", extra={
            'extra_fields': {
                'error_report': error_report.dict(),
                'client_ip': request.client.host if request.client else None
            }
        })
        
        # Save error report to file
        reports_dir = Path('logs/error_reports')
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"{error_report.error_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(error_report.dict(), f, indent=2, default=str)
        
        # Send notification (in a real application, this might send an email or create a ticket)
        logger.info(f"Error report saved: {report_file}")
        
        return {
            'success': True,
            'error_id': error_report.error_id,
            'message': 'Error report received and saved',
            'report_file': str(report_file)
        }
        
    except Exception as e:
        logger.error(f"Failed to process error report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process error report: {str(e)}")

@router.get("/debug/health-check")
async def detailed_health_check():
    """
    Detailed health check with system information.
    
    BEGINNER NOTES:
    - This provides a detailed health check
    - It includes system metrics and application status
    - It's useful for monitoring and diagnostics
    """
    
    try:
        health_info = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'system': get_system_info(),
            'application': get_application_info(),
            'checks': {}
        }
        
        # Perform various health checks
        checks = {}
        
        # File system check
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=True) as f:
                f.write(b"health_check")
            checks['file_system'] = {'status': 'healthy', 'message': 'File system accessible'}
        except Exception as e:
            checks['file_system'] = {'status': 'unhealthy', 'message': str(e)}
            health_info['status'] = 'degraded'
        
        # Memory check
        if PSUTIL_AVAILABLE:
            try:
                memory = psutil.virtual_memory()
                if memory.percent > 90:
                    checks['memory'] = {'status': 'warning', 'message': f'High memory usage: {memory.percent}%'}
                else:
                    checks['memory'] = {'status': 'healthy', 'message': f'Memory usage: {memory.percent}%'}
            except Exception as e:
                checks['memory'] = {'status': 'error', 'message': str(e)}
        else:
            checks['memory'] = {'status': 'warning', 'message': 'Memory monitoring not available (psutil not installed)'}
        
        # Disk space check
        if PSUTIL_AVAILABLE:
            try:
                disk = psutil.disk_usage('.')
                if disk.percent > 90:
                    checks['disk_space'] = {'status': 'warning', 'message': f'Low disk space: {disk.percent}% used'}
                else:
                    checks['disk_space'] = {'status': 'healthy', 'message': f'Disk usage: {disk.percent}%'}
            except Exception as e:
                checks['disk_space'] = {'status': 'error', 'message': str(e)}
        else:
            checks['disk_space'] = {'status': 'warning', 'message': 'Disk monitoring not available (psutil not installed)'}
        
        # Application directories check
        for dir_name, dir_path in [('logs', 'logs'), ('uploads', 'uploads'), ('data', 'data')]:
            try:
                path = Path(dir_path)
                if path.exists() and path.is_dir():
                    checks[f'{dir_name}_directory'] = {'status': 'healthy', 'message': f'{dir_name} directory exists'}
                else:
                    checks[f'{dir_name}_directory'] = {'status': 'warning', 'message': f'{dir_name} directory missing'}
            except Exception as e:
                checks[f'{dir_name}_directory'] = {'status': 'error', 'message': str(e)}
        
        health_info['checks'] = checks
        
        # Determine overall status
        unhealthy_checks = [check for check in checks.values() if check['status'] in ['unhealthy', 'error']]
        if unhealthy_checks:
            health_info['status'] = 'unhealthy'
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'unhealthy',
            'error': str(e)
        }

@router.get("/debug/performance")
async def get_performance_metrics():
    """
    Get performance metrics and statistics.
    
    BEGINNER NOTES:
    - This provides performance metrics for monitoring
    - It includes system and application performance data
    - It's useful for performance analysis and optimization
    """
    
    try:
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': {},
            'application': {}
        }
        
        # System metrics
        if PSUTIL_AVAILABLE:
            try:
                metrics['system'] = {
                    'cpu_percent': psutil.cpu_percent(interval=1),
                    'memory': {
                        'total': psutil.virtual_memory().total,
                        'available': psutil.virtual_memory().available,
                        'percent': psutil.virtual_memory().percent,
                        'used': psutil.virtual_memory().used
                    },
                    'disk': {
                        'total': psutil.disk_usage('.').total,
                        'used': psutil.disk_usage('.').used,
                        'free': psutil.disk_usage('.').free,
                        'percent': psutil.disk_usage('.').percent
                    },
                    'network': {
                        'connections': len(psutil.net_connections()),
                        'interfaces': list(psutil.net_if_addrs().keys())
                    }
                }
            except Exception as e:
                metrics['system'] = {'error': str(e)}
        else:
            metrics['system'] = {'error': 'psutil not available'}
        
        # Application metrics (basic)
        metrics['application'] = {
            'python_version': sys.version,
            'platform': platform.platform(),
            'uptime': 'N/A',  # Could be calculated if we track start time
            'memory_usage': sys.getsizeof({})  # Basic memory usage
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

# Utility functions for error reporting
def create_error_report(error: Exception, context: Dict[str, Any] = None, 
                       user_info: Dict[str, Any] = None) -> ErrorReport:
    """
    Create a comprehensive error report.
    
    BEGINNER NOTES:
    - This creates a standardized error report
    - It includes all relevant context and system information
    - It's useful for debugging and support
    """
    
    import uuid
    
    error_id = str(uuid.uuid4())[:8]
    context = context or {}
    user_info = user_info or {}
    
    return ErrorReport(
        error_id=error_id,
        timestamp=datetime.utcnow().isoformat(),
        error_type=type(error).__name__,
        error_message=str(error),
        stack_trace=traceback.format_exc(),
        context=context,
        user_info=user_info,
        system_info=get_system_info()
    )

def save_error_report(error_report: ErrorReport) -> str:
    """
    Save error report to file.
    
    BEGINNER NOTES:
    - This saves error reports for later analysis
    - It creates a unique filename for each report
    - It's useful for tracking and debugging issues
    """
    
    reports_dir = Path('logs/error_reports')
    reports_dir.mkdir(exist_ok=True)
    
    report_file = reports_dir / f"{error_report.error_id}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(error_report.dict(), f, indent=2, default=str)
    
    logger.info(f"Error report saved: {report_file}")
    return str(report_file)
