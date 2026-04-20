"""
Deployment analyst agent - correlates deployments with incidents.
"""
from graph.state import IncidentState
from prompts.deploy_prompt import format_deploy_prompt
from tools.deploy_history import (
    get_deployment_history,
    correlate_deployment_to_incident,
    get_deployment_changes
)


async def deploy_analysis_node(state: IncidentState, llm) -> dict:
    """
    Deployment analyst checks for correlation with recent deployments.
    
    Args:
        state: Current incident state
        llm: Language model instance
    
    Returns:
        Update dict for state
    """
    
    # Get deployment history and correlation
    deployment_history = get_deployment_history()
    correlation_result = correlate_deployment_to_incident(state["timestamp"])
    deployment_changes = get_deployment_changes()
    
    prompt = format_deploy_prompt(
        incident_timestamp=state["timestamp"],
        service="checkout-service",
        alert_message=state["alert_message"]
    )
    
    # Include deployment data in prompt
    full_prompt = f"""{prompt}

Recent Deployment History:
{deployment_history}

Deployment Correlation Analysis:
{correlation_result}

Deployment Changes:
{deployment_changes}

Based on this timeline, assess:
1. Is rollback recommended?
2. Which deployment is most suspicious?
3. What configuration changes were made?
4. Risk-benefit of rollback
"""
    
    # Call LLM to analyze deployments
    response = llm.generate(full_prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "deploy_agent",
        "action": "deployment_correlation",
        "findings": analysis
    }
    
    return {
        "deploy_findings": [analysis],
        "deployments": [deployment_history, correlation_result],
        "chain_of_thought": [chain_of_thought]
    }


def deploy_analysis_node_sync(state: IncidentState, llm) -> dict:
    """
    Synchronous version of deployment analysis node.
    """
    
    # Get deployment history and correlation
    deployment_history = get_deployment_history()
    correlation_result = correlate_deployment_to_incident(state["timestamp"])
    deployment_changes = get_deployment_changes()
    
    prompt = format_deploy_prompt(
        incident_timestamp=state["timestamp"],
        service="checkout-service",
        alert_message=state["alert_message"]
    )
    
    # Include deployment data in prompt
    full_prompt = f"""{prompt}

Recent Deployment History:
{deployment_history}

Deployment Correlation Analysis:
{correlation_result}

Deployment Changes:
{deployment_changes}

Based on this timeline, assess:
1. Is rollback recommended?
2. Which deployment is most suspicious?
3. What configuration changes were made?
4. Risk-benefit of rollback
"""
    
    # Call LLM to analyze deployments
    response = llm.generate(full_prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "deploy_agent",
        "action": "deployment_correlation",
        "findings": analysis
    }
    
    return {
        "deploy_findings": [analysis],
        "deployments": [deployment_history, correlation_result],
        "chain_of_thought": [chain_of_thought]
    }
