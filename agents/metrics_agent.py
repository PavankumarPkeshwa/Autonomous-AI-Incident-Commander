"""
Metrics analyst agent - detects anomalies and analyzes telemetry.
"""
from graph.state import IncidentState
from prompts.metrics_prompt import format_metrics_prompt
from tools.metrics_query import (
    check_latency,
    check_resource_usage,
    check_database_health,
    check_upstream_health
)


async def metrics_analysis_node(state: IncidentState, llm) -> dict:
    """
    Metrics agent analyzes telemetry and detects anomalies.
    
    Args:
        state: Current incident state
        llm: Language model instance
    
    Returns:
        Update dict for state
    """
    
    # Gather metrics from multiple sources
    latency_data = check_latency()
    resource_data = check_resource_usage()
    db_health = check_database_health()
    upstream_health = check_upstream_health()
    
    prompt = format_metrics_prompt(
        severity=state["severity"],
        time_window="last 10 minutes",
        alert_message=state["alert_message"]
    )
    
    # Include metrics data in prompt
    full_prompt = f"""{prompt}

Current System Metrics:

Latency Metrics:
{latency_data}

Resource Utilization:
{resource_data}

Database Health:
{db_health}

Upstream Dependencies:
{upstream_health}

Analyze these metrics and determine:
1. Which thresholds are breached
2. Correlation between metrics
3. Whether issue is upstream or internal
4. Scaling or performance recommendations
"""
    
    # Call LLM to analyze metrics
    response = llm.generate(full_prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "metrics_agent",
        "action": "anomaly_detection",
        "findings": analysis
    }
    
    return {
        "metrics_findings": [analysis],
        "metrics": [latency_data, resource_data, db_health, upstream_health],
        "chain_of_thought": [chain_of_thought]
    }


def metrics_analysis_node_sync(state: IncidentState, llm) -> dict:
    """
    Synchronous version of metrics analysis node.
    """
    
    # Gather metrics from multiple sources
    latency_data = check_latency()
    resource_data = check_resource_usage()
    db_health = check_database_health()
    upstream_health = check_upstream_health()
    
    prompt = format_metrics_prompt(
        severity=state["severity"],
        time_window="last 10 minutes",
        alert_message=state["alert_message"]
    )
    
    # Include metrics data in prompt
    full_prompt = f"""{prompt}

Current System Metrics:

Latency Metrics:
{latency_data}

Resource Utilization:
{resource_data}

Database Health:
{db_health}

Upstream Dependencies:
{upstream_health}

Analyze these metrics and determine:
1. Which thresholds are breached
2. Correlation between metrics
3. Whether issue is upstream or internal
4. Scaling or performance recommendations
"""
    
    # Call LLM to analyze metrics
    response = llm.generate(full_prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "metrics_agent",
        "action": "anomaly_detection",
        "findings": analysis
    }
    
    return {
        "metrics_findings": [analysis],
        "metrics": [latency_data, resource_data, db_health, upstream_health],
        "chain_of_thought": [chain_of_thought]
    }
