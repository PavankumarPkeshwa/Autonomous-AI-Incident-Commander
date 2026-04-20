"""
Commander agent - orchestrates incident response.
"""
from typing import Optional
from graph.state import IncidentState
from prompts.commander_prompt import format_commander_prompt


async def commander_node(state: IncidentState, llm) -> dict:
    """
    Commander agent analyzes incident and creates action plan.
    
    Args:
        state: Current incident state
        llm: Language model instance
    
    Returns:
        Update dict for state
    """
    
    prompt = format_commander_prompt(
        incident_id=state["incident_id"],
        alert_message=state["alert_message"],
        severity=state["severity"],
        timestamp=state["timestamp"]
    )
    
    # Call LLM to analyze incident
    response = await llm.agenerate(prompt)
    analysis = response.generations[0][0].text
    
    # Log reasoning
    chain_of_thought = {
        "agent": "commander",
        "action": "incident_analysis",
        "analysis": analysis
    }
    
    return {
        "commander_analysis": analysis,
        "chain_of_thought": [chain_of_thought],
        "resolution_status": "IN_PROGRESS"
    }


def commander_node_sync(state: IncidentState, llm) -> dict:
    """
    Synchronous version of commander node for non-async contexts.
    """
    
    prompt = format_commander_prompt(
        incident_id=state["incident_id"],
        alert_message=state["alert_message"],
        severity=state["severity"],
        timestamp=state["timestamp"]
    )
    
    # Call LLM to analyze incident
    response = llm.generate(prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "commander",
        "action": "incident_analysis",
        "analysis": analysis
    }
    
    return {
        "commander_analysis": analysis,
        "chain_of_thought": [chain_of_thought],
        "resolution_status": "IN_PROGRESS"
    }
