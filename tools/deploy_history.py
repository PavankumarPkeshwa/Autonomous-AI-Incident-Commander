"""
Tool for querying CI/CD deployment history and correlating with incidents.
"""
import json
from typing import Dict, Any, List
from datetime import datetime


def load_deployments() -> Dict[str, Any]:
    """Load mock deployments from JSON file."""
    try:
        with open("mock_data/deployments.json", "r") as f:
            return json.load(f)
    except Exception as e:
        return {"deployments": [], "error": f"Failed to load deployments: {str(e)}"}


def get_deployment_history() -> str:
    """
    Retrieve recent deployment history (last 24 hours).
    
    Returns:
        JSON string of recent deployments
    """
    data = load_deployments()
    deployments = data.get("deployments", [])
    
    return json.dumps({
        "deployments": deployments,
        "count": len(deployments)
    }, indent=2)


def correlate_deployment_to_incident(incident_timestamp: str) -> str:
    """
    Check if any recent deployments correlate with incident timing.
    Looks for deployments within 30 minutes before incident.
    
    Args:
        incident_timestamp: ISO format timestamp of incident start
    
    Returns:
        JSON string with correlation analysis
    """
    data = load_deployments()
    deployments = data.get("deployments", [])
    
    try:
        incident_time = datetime.fromisoformat(incident_timestamp.replace("Z", "+00:00"))
    except:
        return json.dumps({"error": "Invalid timestamp format"})
    
    suspicious = []
    for deploy in deployments:
        deploy_time = datetime.fromisoformat(deploy.get("timestamp", "").replace("Z", "+00:00"))
        minutes_before = (incident_time - deploy_time).total_seconds() / 60
        
        # Flag deployments within 30 minutes before incident
        if 0 < minutes_before <= 30:
            suspicious.append({
                **deploy,
                "minutes_before_incident": round(minutes_before, 2)
            })
    
    return json.dumps({
        "incident_timestamp": incident_timestamp,
        "suspicious_deployments": suspicious,
        "correlation_found": len(suspicious) > 0,
        "recommendation": "Consider rollback if correlation is strong" if suspicious else "No suspicious deployments found"
    }, indent=2)


def get_deployment_changes(service: str = None) -> str:
    """
    Get changes made in recent deployments.
    
    Args:
        service: Filter by service name (optional)
    
    Returns:
        JSON string with deployment changes
    """
    data = load_deployments()
    deployments = data.get("deployments", [])
    
    if service:
        deployments = [d for d in deployments if d.get("service") == service]
    
    return json.dumps({
        "service_filter": service,
        "deployments": deployments,
        "count": len(deployments)
    }, indent=2)
