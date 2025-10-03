"""
Configuration API endpoints for managing rules.json and detector settings.
"""

import json
import os
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/api/config", tags=["configuration"])

# Configuration file path
CONFIG_FILE = "data/rules.json"
BACKUP_DIR = "data/backups"

# Ensure backup directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# Pydantic models for configuration
class DetectorRule(BaseModel):
    """Individual rule within a detector."""
    keywords: Optional[List[str]] = None
    patterns: Optional[List[str]] = None
    triggers: Optional[List[str]] = None
    required_with: Optional[List[str]] = None
    pairs: Optional[List[List[str]]] = None
    similarity_threshold: Optional[float] = None
    context_required: Optional[bool] = None
    description: str

class DetectorConfig(BaseModel):
    """Configuration for a single detector."""
    enabled: bool
    severity: str = Field(..., pattern="^(low|medium|high|critical|blocker)$")
    description: str
    rules: Dict[str, DetectorRule]

class GlobalSettings(BaseModel):
    """Global configuration settings."""
    case_sensitive: bool = False
    ignore_comments: bool = True
    min_requirement_length: int = Field(ge=1, le=1000)
    max_similarity_check: int = Field(ge=1, le=1000)

class ConfigurationUpdate(BaseModel):
    """Request model for updating configuration."""
    detectors: Optional[Dict[str, DetectorConfig]] = None
    global_settings: Optional[GlobalSettings] = None
    severity_mapping: Optional[Dict[str, int]] = None

class ConfigurationResponse(BaseModel):
    """Response model for configuration data."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class DetectorToggleRequest(BaseModel):
    """Request model for toggling detector enabled state."""
    enabled: bool

class RuleUpdateRequest(BaseModel):
    """Request model for updating individual rules."""
    rule_data: Dict[str, Any]

class ImportExportResponse(BaseModel):
    """Response model for import/export operations."""
    success: bool
    message: str
    file_path: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

def load_configuration() -> Dict[str, Any]:
    """Load configuration from rules.json file."""
    try:
        if not os.path.exists(CONFIG_FILE):
            raise HTTPException(status_code=404, detail="Configuration file not found")
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in configuration file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load configuration: {str(e)}")

def save_configuration(config: Dict[str, Any]) -> None:
    """Save configuration to rules.json file with backup."""
    try:
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"rules_backup_{timestamp}.json")
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                backup_data = f.read()
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(backup_data)
        
        # Save new configuration
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save configuration: {str(e)}")

@router.get("/", response_model=ConfigurationResponse)
async def get_configuration():
    """Get current configuration."""
    try:
        config = load_configuration()
        return ConfigurationResponse(
            success=True,
            message="Configuration loaded successfully",
            data=config
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get configuration: {str(e)}")

@router.put("/", response_model=ConfigurationResponse)
async def update_configuration(update: ConfigurationUpdate):
    """Update configuration with validation."""
    try:
        config = load_configuration()
        
        # Update detectors if provided
        if update.detectors:
            config["detectors"] = {name: detector.dict() for name, detector in update.detectors.items()}
        
        # Update global settings if provided
        if update.global_settings:
            config["global_settings"] = update.global_settings.dict()
        
        # Update severity mapping if provided
        if update.severity_mapping:
            config["severity_mapping"] = update.severity_mapping
        
        # Validate configuration
        validate_configuration(config)
        
        # Save configuration
        save_configuration(config)
        
        return ConfigurationResponse(
            success=True,
            message="Configuration updated successfully",
            data=config
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")

@router.get("/detectors", response_model=ConfigurationResponse)
async def get_detectors():
    """Get all detector configurations."""
    try:
        config = load_configuration()
        detectors = config.get("detectors", {})
        
        return ConfigurationResponse(
            success=True,
            message="Detectors loaded successfully",
            data={"detectors": detectors}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detectors: {str(e)}")

@router.put("/detectors/{detector_name}/toggle", response_model=ConfigurationResponse)
async def toggle_detector(detector_name: str, request: DetectorToggleRequest):
    """Enable or disable a specific detector."""
    try:
        config = load_configuration()
        
        if detector_name not in config.get("detectors", {}):
            raise HTTPException(status_code=404, detail=f"Detector '{detector_name}' not found")
        
        config["detectors"][detector_name]["enabled"] = request.enabled
        save_configuration(config)
        
        return ConfigurationResponse(
            success=True,
            message=f"Detector '{detector_name}' {'enabled' if request.enabled else 'disabled'} successfully",
            data={"detector": config["detectors"][detector_name]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle detector: {str(e)}")

@router.put("/detectors/{detector_name}/severity", response_model=ConfigurationResponse)
async def update_detector_severity(detector_name: str, severity: str):
    """Update severity level for a specific detector."""
    try:
        if severity not in ["low", "medium", "high", "critical", "blocker"]:
            raise HTTPException(status_code=400, detail="Invalid severity level")
        
        config = load_configuration()
        
        if detector_name not in config.get("detectors", {}):
            raise HTTPException(status_code=404, detail=f"Detector '{detector_name}' not found")
        
        config["detectors"][detector_name]["severity"] = severity
        save_configuration(config)
        
        return ConfigurationResponse(
            success=True,
            message=f"Detector '{detector_name}' severity updated to '{severity}'",
            data={"detector": config["detectors"][detector_name]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update severity: {str(e)}")

@router.put("/detectors/{detector_name}/rules/{rule_name}", response_model=ConfigurationResponse)
async def update_detector_rule(detector_name: str, rule_name: str, request: RuleUpdateRequest):
    """Update a specific rule within a detector."""
    try:
        config = load_configuration()
        
        if detector_name not in config.get("detectors", {}):
            raise HTTPException(status_code=404, detail=f"Detector '{detector_name}' not found")
        
        if rule_name not in config["detectors"][detector_name].get("rules", {}):
            raise HTTPException(status_code=404, detail=f"Rule '{rule_name}' not found in detector '{detector_name}'")
        
        # Update rule data
        config["detectors"][detector_name]["rules"][rule_name].update(request.rule_data)
        
        # Validate updated configuration
        validate_configuration(config)
        
        save_configuration(config)
        
        return ConfigurationResponse(
            success=True,
            message=f"Rule '{rule_name}' updated successfully",
            data={"rule": config["detectors"][detector_name]["rules"][rule_name]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {str(e)}")

@router.get("/global-settings", response_model=ConfigurationResponse)
async def get_global_settings():
    """Get global configuration settings."""
    try:
        config = load_configuration()
        global_settings = config.get("global_settings", {})
        
        return ConfigurationResponse(
            success=True,
            message="Global settings loaded successfully",
            data={"global_settings": global_settings}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get global settings: {str(e)}")

@router.put("/global-settings", response_model=ConfigurationResponse)
async def update_global_settings(settings: GlobalSettings):
    """Update global configuration settings."""
    try:
        config = load_configuration()
        config["global_settings"] = settings.dict()
        
        validate_configuration(config)
        save_configuration(config)
        
        return ConfigurationResponse(
            success=True,
            message="Global settings updated successfully",
            data={"global_settings": config["global_settings"]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update global settings: {str(e)}")

@router.get("/severity-mapping", response_model=ConfigurationResponse)
async def get_severity_mapping():
    """Get severity level mapping."""
    try:
        config = load_configuration()
        severity_mapping = config.get("severity_mapping", {})
        
        return ConfigurationResponse(
            success=True,
            message="Severity mapping loaded successfully",
            data={"severity_mapping": severity_mapping}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get severity mapping: {str(e)}")

@router.put("/severity-mapping", response_model=ConfigurationResponse)
async def update_severity_mapping(mapping: Dict[str, int]):
    """Update severity level mapping."""
    try:
        # Validate severity mapping
        valid_levels = ["low", "medium", "high", "critical", "blocker"]
        for level in mapping.keys():
            if level not in valid_levels:
                raise HTTPException(status_code=400, detail=f"Invalid severity level: {level}")
        
        for value in mapping.values():
            if not isinstance(value, int) or value < 1 or value > 10:
                raise HTTPException(status_code=400, detail="Severity values must be integers between 1 and 10")
        
        config = load_configuration()
        config["severity_mapping"] = mapping
        
        validate_configuration(config)
        save_configuration(config)
        
        return ConfigurationResponse(
            success=True,
            message="Severity mapping updated successfully",
            data={"severity_mapping": config["severity_mapping"]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update severity mapping: {str(e)}")

@router.post("/export", response_model=ImportExportResponse)
async def export_configuration():
    """Export current configuration to a downloadable file."""
    try:
        config = load_configuration()
        
        # Create export file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = os.path.join(BACKUP_DIR, f"rules_export_{timestamp}.json")
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return ImportExportResponse(
            success=True,
            message="Configuration exported successfully",
            file_path=export_file,
            data=config
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export configuration: {str(e)}")

@router.post("/import", response_model=ImportExportResponse)
async def import_configuration(file: UploadFile = File(...)):
    """Import configuration from uploaded file."""
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read and parse file content
        content = await file.read()
        try:
            imported_config = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON file: {str(e)}")
        
        # Validate imported configuration
        validate_configuration(imported_config)
        
        # Save imported configuration
        save_configuration(imported_config)
        
        return ImportExportResponse(
            success=True,
            message="Configuration imported successfully",
            data=imported_config
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import configuration: {str(e)}")

@router.get("/backups", response_model=ConfigurationResponse)
async def list_backups():
    """List available configuration backups."""
    try:
        if not os.path.exists(BACKUP_DIR):
            return ConfigurationResponse(
                success=True,
                message="No backups found",
                data={"backups": []}
            )
        
        backups = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(BACKUP_DIR, filename)
                stat = os.stat(file_path)
                backups.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return ConfigurationResponse(
            success=True,
            message="Backups listed successfully",
            data={"backups": backups}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")

@router.post("/restore/{backup_filename}", response_model=ConfigurationResponse)
async def restore_backup(backup_filename: str):
    """Restore configuration from a backup file."""
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        # Load backup configuration
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_config = json.load(f)
        
        # Validate backup configuration
        validate_configuration(backup_config)
        
        # Restore configuration
        save_configuration(backup_config)
        
        return ConfigurationResponse(
            success=True,
            message=f"Configuration restored from backup '{backup_filename}'",
            data=backup_config
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restore backup: {str(e)}")

def validate_configuration(config: Dict[str, Any]) -> None:
    """Validate configuration structure and values."""
    required_keys = ["version", "detectors", "severity_mapping", "global_settings"]
    
    for key in required_keys:
        if key not in config:
            raise HTTPException(status_code=400, detail=f"Missing required configuration key: {key}")
    
    # Validate detectors
    detectors = config.get("detectors", {})
    for detector_name, detector_config in detectors.items():
        if not isinstance(detector_config, dict):
            raise HTTPException(status_code=400, detail=f"Invalid detector configuration for '{detector_name}'")
        
        required_detector_keys = ["enabled", "severity", "description", "rules"]
        for key in required_detector_keys:
            if key not in detector_config:
                raise HTTPException(status_code=400, detail=f"Missing required key '{key}' in detector '{detector_name}'")
        
        # Validate severity
        if detector_config["severity"] not in ["low", "medium", "high", "critical", "blocker"]:
            raise HTTPException(status_code=400, detail=f"Invalid severity level in detector '{detector_name}'")
        
        # Validate rules
        rules = detector_config.get("rules", {})
        for rule_name, rule_config in rules.items():
            if not isinstance(rule_config, dict):
                raise HTTPException(status_code=400, detail=f"Invalid rule configuration for '{rule_name}' in detector '{detector_name}'")
            
            if "description" not in rule_config:
                raise HTTPException(status_code=400, detail=f"Missing description for rule '{rule_name}' in detector '{detector_name}'")
    
    # Validate severity mapping
    severity_mapping = config.get("severity_mapping", {})
    valid_levels = ["low", "medium", "high", "critical", "blocker"]
    for level in severity_mapping.keys():
        if level not in valid_levels:
            raise HTTPException(status_code=400, detail=f"Invalid severity level in mapping: {level}")
    
    # Validate global settings
    global_settings = config.get("global_settings", {})
    if "min_requirement_length" in global_settings:
        if not isinstance(global_settings["min_requirement_length"], int) or global_settings["min_requirement_length"] < 1:
            raise HTTPException(status_code=400, detail="Invalid min_requirement_length value")
    
    if "max_similarity_check" in global_settings:
        if not isinstance(global_settings["max_similarity_check"], int) or global_settings["max_similarity_check"] < 1:
            raise HTTPException(status_code=400, detail="Invalid max_similarity_check value")
