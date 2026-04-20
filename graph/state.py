"""
Shared state definition for the incident response graph.
"""
from typing import Annotated, TypedDict, Optional, List, Any
from operator import add


class IncidentState(TypedDict):
    """
    Shared memory across all agents in the incident response workflow.
    Uses Annotated for reducer operations (e.g., accumulating findings).
    """
    
    # Core incident metadata
    incident_id: str
    alert_message: str
    severity: str
    timestamp: str
    
    # Collected data
    logs: Annotated[List[str], add]
    metrics: Annotated[List[str], add]
    deployments: Annotated[List[str], add]
    
    # Agent outputs & reasoning
    commander_analysis: Optional[str]
    logs_findings: Annotated[List[str], add]
    metrics_findings: Annotated[List[str], add]
    deploy_findings: Annotated[List[str], add]
    resolver_suggestions: Annotated[List[str], add]
    
    # Decision tracking
    root_cause: Optional[str]
    recommended_actions: Annotated[List[str], add]
    executed_actions: Annotated[List[str], add]
    resolution_status: str  # "IN_PROGRESS", "RESOLVED", "ESCALATED"
    
    # Chain of thought for traceability
    chain_of_thought: Annotated[List[dict], add]
    
    # Final output
    rca_report: Optional[str]
