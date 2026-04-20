"""
Tool for searching mock log data.
"""
import json
from typing import List, Dict, Any


def load_logs() -> List[Dict[str, Any]]:
    """Load mock logs from JSON file."""
    try:
        with open("mock_data/logs.json", "r") as f:
            return json.load(f).get("logs", [])
    except Exception as e:
        return [{"error": f"Failed to load logs: {str(e)}"}]


def log_search(query: str, service: str = None, level: str = None) -> str:
    """
    Search mock logs by query string, service name, or log level.
    
    Args:
        query: Free text search query (searches message field)
        service: Filter by service name (optional)
        level: Filter by log level (ERROR, WARN, INFO) (optional)
    
    Returns:
        JSON string of matching log entries
    """
    logs = load_logs()
    results = []
    
    for log in logs:
        # Filter by service if specified
        if service and log.get("service") != service:
            continue
        
        # Filter by level if specified
        if level and log.get("level") != level:
            continue
        
        # Filter by query string in message
        if query.lower() in log.get("message", "").lower():
            results.append(log)
    
    return json.dumps({
        "query": query,
        "service_filter": service,
        "level_filter": level,
        "results": results,
        "count": len(results)
    }, indent=2)


def get_error_logs() -> str:
    """
    Retrieve all ERROR level logs from the system.
    
    Returns:
        JSON string of all error logs
    """
    logs = load_logs()
    error_logs = [log for log in logs if log.get("level") == "ERROR"]
    
    return json.dumps({
        "level": "ERROR",
        "logs": error_logs,
        "count": len(error_logs)
    }, indent=2)


def get_logs_by_service(service: str) -> str:
    """
    Retrieve all logs for a specific service.
    
    Args:
        service: Service name to filter by
    
    Returns:
        JSON string of logs for that service
    """
    logs = load_logs()
    filtered = [log for log in logs if log.get("service") == service]
    
    return json.dumps({
        "service": service,
        "logs": filtered,
        "count": len(filtered)
    }, indent=2)
