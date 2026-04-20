"""
Tool for triggering remediation actions (rollback, scaling, etc).
This is the ACTION phase of incident response.
"""
import json
from datetime import datetime
from typing import Dict, Any


# In-memory action log for demo purposes
action_log = []


def trigger_rollback(service: str, target_version: str) -> str:
    """
    Trigger a rollback of a service to a previous version.
    
    Args:
        service: Service name to rollback
        target_version: Target version to rollback to
    
    Returns:
        JSON string with rollback status
    """
    action = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action_type": "ROLLBACK",
        "service": service,
        "target_version": target_version,
        "status": "INITIATED"
    }
    action_log.append(action)
    
    return json.dumps({
        "status": "success",
        "action": action,
        "message": f"Rollback of {service} to {target_version} initiated"
    }, indent=2)


def scale_service(service: str, target_replicas: int) -> str:
    """
    Scale a service horizontally.
    
    Args:
        service: Service name to scale
        target_replicas: Target number of replicas
    
    Returns:
        JSON string with scaling status
    """
    action = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action_type": "SCALE",
        "service": service,
        "target_replicas": target_replicas,
        "status": "INITIATED"
    }
    action_log.append(action)
    
    return json.dumps({
        "status": "success",
        "action": action,
        "message": f"Scaling {service} to {target_replicas} replicas"
    }, indent=2)


def disable_feature(feature_flag: str) -> str:
    """
    Disable a feature flag to mitigate incident.
    
    Args:
        feature_flag: Name of feature flag to disable
    
    Returns:
        JSON string with feature flag status
    """
    action = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action_type": "FEATURE_FLAG",
        "feature_flag": feature_flag,
        "action": "DISABLED",
        "status": "COMPLETED"
    }
    action_log.append(action)
    
    return json.dumps({
        "status": "success",
        "action": action,
        "message": f"Feature flag '{feature_flag}' disabled"
    }, indent=2)


def adjust_circuit_breaker(service: str, failure_threshold: float) -> str:
    """
    Adjust circuit breaker threshold for a service.
    
    Args:
        service: Service name
        failure_threshold: New failure threshold (as percentage 0-100)
    
    Returns:
        JSON string with circuit breaker adjustment status
    """
    action = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action_type": "CIRCUIT_BREAKER_ADJUST",
        "service": service,
        "failure_threshold_percent": failure_threshold,
        "status": "APPLIED"
    }
    action_log.append(action)
    
    return json.dumps({
        "status": "success",
        "action": action,
        "message": f"Circuit breaker for {service} adjusted to {failure_threshold}% threshold"
    }, indent=2)


def get_action_log() -> str:
    """
    Retrieve all remediation actions taken during this incident.
    
    Returns:
        JSON string with action log
    """
    return json.dumps({
        "actions_count": len(action_log),
        "actions": action_log
    }, indent=2)
