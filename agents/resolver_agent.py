"""
Resolver agent - first-level resolution using FAQ and remediation tools.
"""
from graph.state import IncidentState
from prompts.resolver_prompt import format_resolver_prompt
from tools.faq_retriever import search_faq, get_solution_for_symptom
from tools.deploy_history import correlate_deployment_to_incident


async def resolution_node(state: IncidentState, llm) -> dict:
    """
    Resolver agent attempts initial remediation and FAQ-based solutions.
    
    Args:
        state: Current incident state
        llm: Language model instance
    
    Returns:
        Update dict for state
    """
    
    # Search FAQ for solutions
    faq_results = search_faq(state["alert_message"])
    
    # Get solution for symptom
    symptom_solutions = get_solution_for_symptom(state["alert_message"])
    
    root_cause = state.get("root_cause", "Unknown - requires deeper analysis")
    
    prompt = format_resolver_prompt(
        severity=state["severity"],
        alert_message=state["alert_message"],
        root_cause=root_cause
    )
    
    # Include FAQ and available solutions
    full_prompt = f"""{prompt}

FAQ Search Results:
{faq_results}

Solution Recommendations:
{symptom_solutions}

Previous Agent Findings:
- Commander Analysis: {state.get('commander_analysis', 'N/A')[:200]}
- Log Findings: {state.get('logs_findings', ['N/A'])[0][:200] if state.get('logs_findings') else 'N/A'}
- Metrics Findings: {state.get('metrics_findings', ['N/A'])[0][:200] if state.get('metrics_findings') else 'N/A'}

Based on the above, provide:
1. Recommended remediation actions (in priority order)
2. Which FAQ solution is most applicable
3. Whether automatic remediation should be attempted
4. Risks and rollback plan for each action
5. Success criteria for resolution
"""
    
    # Call LLM for resolution strategy
    response = llm.generate(full_prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "resolver_agent",
        "action": "resolution_planning",
        "recommendations": analysis
    }
    
    return {
        "resolver_suggestions": [analysis],
        "recommended_actions": [analysis],
        "resolution_status": "IN_PROGRESS",
        "chain_of_thought": [chain_of_thought]
    }


def resolution_node_sync(state: IncidentState, llm) -> dict:
    """
    Synchronous version of resolution node.
    """
    
    # Search FAQ for solutions
    faq_results = search_faq(state["alert_message"])
    
    # Get solution for symptom
    symptom_solutions = get_solution_for_symptom(state["alert_message"])
    
    root_cause = state.get("root_cause", "Unknown - requires deeper analysis")
    
    prompt = format_resolver_prompt(
        severity=state["severity"],
        alert_message=state["alert_message"],
        root_cause=root_cause
    )
    
    # Include FAQ and available solutions
    full_prompt = f"""{prompt}

FAQ Search Results:
{faq_results}

Solution Recommendations:
{symptom_solutions}

Previous Agent Findings:
- Commander Analysis: {state.get('commander_analysis', 'N/A')[:200]}
- Log Findings: {state.get('logs_findings', ['N/A'])[0][:200] if state.get('logs_findings') else 'N/A'}
- Metrics Findings: {state.get('metrics_findings', ['N/A'])[0][:200] if state.get('metrics_findings') else 'N/A'}

Based on the above, provide:
1. Recommended remediation actions (in priority order)
2. Which FAQ solution is most applicable
3. Whether automatic remediation should be attempted
4. Risks and rollback plan for each action
5. Success criteria for resolution
"""
    
    # Call LLM for resolution strategy
    response = llm.generate(full_prompt)
    analysis = response.generations[0][0].text if response.generations else ""
    
    # Log reasoning
    chain_of_thought = {
        "agent": "resolver_agent",
        "action": "resolution_planning",
        "recommendations": analysis
    }
    
    return {
        "resolver_suggestions": [analysis],
        "recommended_actions": [analysis],
        "resolution_status": "IN_PROGRESS",
        "chain_of_thought": [chain_of_thought]
    }
