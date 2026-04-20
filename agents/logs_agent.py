"""
Logs forensics agent - investigates error logs and patterns.
"""
from typing import List
import json
from graph.state import IncidentState
from prompts.logs_prompt import format_logs_prompt
from tools.log_search import log_search, get_error_logs, get_logs_by_service


async def logs_analysis_node(state: IncidentState, llm) -> dict:
    """
    Logs agent searches and analyzes error logs.
    
    Args:
        state: Current incident state
        llm: Language model instance
    
    Returns:
        Update dict for state
    """
    
    # Gather initial error logs
    error_logs_result = get_error_logs()
    
    # Extract service from alert or use checkout as default
    service = "checkout-service"
    service_logs = get_logs_by_service(service)
    
    prompt = format_logs_prompt(
        service=service,
        time_window="last 5 minutes",
        alert_message=state["alert_message"]
    )
    
    # Include log data in prompt
    full_prompt = f"""{prompt}

Retrieved Logs:
{error_logs_result}

Service-specific Logs:
{service_logs}

Analyze these logs and identify:
1. Error patterns and frequencies
2. Root cause indicators
3. Services affected
4. Recommended actions
"""
    
    # Call LLM to analyze logs
    response = llm.generate(full_prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "logs_agent",
        "action": "log_analysis",
        "findings": analysis
    }
    
    return {
        "logs_findings": [analysis],
        "logs": [error_logs_result, service_logs],
        "chain_of_thought": [chain_of_thought]
    }


def logs_analysis_node_sync(state: IncidentState, llm) -> dict:
    """
    Synchronous version of logs analysis node.
    """
    
    # Gather initial error logs
    error_logs_result = get_error_logs()
    
    # Extract service from alert or use checkout as default
    service = "checkout-service"
    service_logs = get_logs_by_service(service)
    
    prompt = format_logs_prompt(
        service=service,
        time_window="last 5 minutes",
        alert_message=state["alert_message"]
    )
    
    # Include log data in prompt
    full_prompt = f"""{prompt}

Retrieved Logs:
{error_logs_result}

Service-specific Logs:
{service_logs}

Analyze these logs and identify:
1. Error patterns and frequencies
2. Root cause indicators
3. Services affected
4. Recommended actions
"""
    
    # Call LLM to analyze logs
    response = llm.generate(full_prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "logs_agent",
        "action": "log_analysis",
        "findings": analysis
    }
    
    return {
        "logs_findings": [analysis],
        "logs": [error_logs_result, service_logs],
        "chain_of_thought": [chain_of_thought]
    }
