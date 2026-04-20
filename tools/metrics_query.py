"""
Tool for querying mock metrics and telemetry data.
"""
import json
from typing import Dict, Any, Optional


def load_metrics() -> Dict[str, Any]:
    """Load mock metrics from JSON file."""
    try:
        with open("mock_data/metrics.json", "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load metrics: {str(e)}"}


def query_metrics(service: str = "checkout_service") -> str:
    """
    Query current metrics for a service.
    
    Args:
        service: Service name to query (default: checkout_service)
    
    Returns:
        JSON string of current metrics for the service
    """
    data = load_metrics()
    metrics_data = data.get("metrics", {})
    service_metrics = metrics_data.get(service, {})
    
    return json.dumps({
        "service": service,
        "timestamp": metrics_data.get("timestamp"),
        "metrics": service_metrics
    }, indent=2)


def check_latency() -> str:
    """
    Get latency metrics (p99, p95, p50) for checkout service.
    
    Returns:
        JSON string with latency percentiles
    """
    data = load_metrics()
    metrics_data = data.get("metrics", {})
    checkout = metrics_data.get("checkout_service", {})
    
    latencies = {
        "p99_latency_ms": checkout.get("p99_latency"),
        "p95_latency_ms": checkout.get("p95_latency"),
        "p50_latency_ms": checkout.get("p50_latency"),
    }
    
    return json.dumps({
        "service": "checkout_service",
        "latencies": latencies,
        "timestamp": metrics_data.get("timestamp")
    }, indent=2)


def check_resource_usage() -> str:
    """
    Get CPU and memory usage metrics.
    
    Returns:
        JSON string with resource utilization data
    """
    data = load_metrics()
    metrics_data = data.get("metrics", {})
    checkout = metrics_data.get("checkout_service", {})
    
    resources = {
        "cpu_usage_percent": checkout.get("cpu_usage"),
        "memory_usage_percent": checkout.get("memory_usage"),
        "error_rate_percent": checkout.get("error_rate"),
    }
    
    return json.dumps({
        "service": "checkout_service",
        "resources": resources,
        "timestamp": metrics_data.get("timestamp")
    }, indent=2)


def check_database_health() -> str:
    """
    Get database connection pool and query performance metrics.
    
    Returns:
        JSON string with database health metrics
    """
    data = load_metrics()
    metrics_data = data.get("metrics", {})
    db = metrics_data.get("database", {})
    
    health = {
        "pool_size": db.get("connection_pool_size"),
        "active_connections": db.get("active_connections"),
        "query_time_p99_ms": db.get("query_time_p99"),
        "slow_query_count": db.get("slow_query_count"),
        "replica_lag_ms": db.get("replica_lag"),
    }
    
    return json.dumps({
        "database": "primary",
        "health": health,
        "timestamp": metrics_data.get("timestamp")
    }, indent=2)


def check_upstream_health() -> str:
    """
    Check health of upstream dependencies (payment gateway, etc).
    
    Returns:
        JSON string with upstream service status
    """
    data = load_metrics()
    metrics_data = data.get("metrics", {})
    gateway = metrics_data.get("payment_gateway", {})
    
    return json.dumps({
        "service": "payment_gateway",
        "upstream_latency_ms": gateway.get("upstream_latency"),
        "error_rate_percent": gateway.get("error_rate"),
        "status": gateway.get("status"),
        "timestamp": metrics_data.get("timestamp")
    }, indent=2)
