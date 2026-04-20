"""
Simplified FastAPI backend for Autonomous Incident Commander Dashboard.
Uses mock data - no WebSocket complexity needed.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from graph.state import IncidentState
from agents.commander import commander_node_sync
from agents.logs_agent import logs_analysis_node_sync
from agents.metrics_agent import metrics_analysis_node_sync
from agents.deploy_agent import deploy_analysis_node_sync
from agents.resolver_agent import resolution_node_sync
from tools.rollback_action import trigger_rollback, get_action_log


# ============= Pydantic Models =============
class IncidentAlertRequest(BaseModel):
    alert_message: str
    severity: str = "critical"


# ============= FastAPI App =============
app = FastAPI(
    title="Autonomous Incident Commander API",
    description="Simple incident response orchestration with mock data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= Global State =============
incidents: Dict[str, Dict[str, Any]] = {}


# ============= Mock LLM (No real API calls needed) =============
class MockLLM:
    """Mock LLM for incident analysis with mock data."""
    
    def generate(self, prompt: str):
        class Generation:
            def __init__(self, text):
                self.text = text
        
        class Generations:
            def __init__(self, text):
                self.generations = [[Generation(text)]]
        
        if "commander" in prompt.lower():
            text = "INCIDENT ASSESSMENT: Critical checkout service issue. Payment gateway timeouts detected."
        elif "logs" in prompt.lower():
            text = "ERROR PATTERNS: Connection timeouts (12:32:10), Payment failures (12.5%), DB pool exhaustion"
        elif "metrics" in prompt.lower():
            text = "METRICS: CPU 87.5% | Memory 78.2% | P99 Latency 5234ms | Error Rate 12.5%"
        elif "deploy" in prompt.lower():
            text = "DEPLOYMENT: config-service v2.3.1 deployed 17 min before incident. Timeout threshold changed 3000ms→2000ms"
        elif "resolver" in prompt.lower():
            text = "RESOLUTION: Rollback config-service to v2.3.0. Risk: LOW. Success probability: 95%+"
        else:
            text = "Analysis in progress..."
        
        return Generations(text)


llm = MockLLM()


# ============= Helper Functions =============
def run_incident_workflow(incident_state: IncidentState, incident_id: str):
    """Run entire incident workflow synchronously."""
    
    try:
        print(f"\n[API] Starting workflow for incident {incident_id}")
        
        # Step 1: Commander
        print(f"[API] Step 1: Commander Analysis")
        commander_result = commander_node_sync(incident_state, llm)
        incident_state.update(commander_result)
        print(f"[API] ✓ Commander complete")
        
        # Step 2: Logs Analysis
        print(f"[API] Step 2: Logs Analysis")
        logs_result = logs_analysis_node_sync(incident_state, llm)
        incident_state.update(logs_result)
        print(f"[API] ✓ Logs complete")
        
        # Step 3: Metrics Analysis
        print(f"[API] Step 3: Metrics Analysis")
        metrics_result = metrics_analysis_node_sync(incident_state, llm)
        incident_state.update(metrics_result)
        print(f"[API] ✓ Metrics complete")
        
        # Step 4: Deploy Analysis
        print(f"[API] Step 4: Deploy Analysis")
        deploy_result = deploy_analysis_node_sync(incident_state, llm)
        incident_state.update(deploy_result)
        print(f"[API] ✓ Deploy complete")
        
        # Step 5: Resolution
        print(f"[API] Step 5: Resolver Analysis")
        resolver_result = resolution_node_sync(incident_state, llm)
        incident_state.update(resolver_result)
        print(f"[API] ✓ Resolver complete")
        
        # Step 6: Execute Rollback
        print(f"[API] Step 6: Executing Rollback")
        trigger_rollback("config-service", "v2.3.0")
        action_log = get_action_log()
        incident_state.update({"executed_actions": [action_log]})
        incident_state["resolution_status"] = "RESOLVED"
        print(f"[API] ✓ Rollback complete - INCIDENT RESOLVED\n")
        
    except Exception as e:
        print(f"\n[API] ERROR in workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        incident_state["resolution_status"] = "FAILED"
        incident_state["error"] = str(e)
        print()
    
    # Store final state
    incidents[incident_id] = incident_state


# ============= REST Endpoints =============

@app.get("/")
async def root():
    """Health check."""
    return {
        "service": "Autonomous Incident Commander API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/dashboard")
async def get_dashboard():
    """Serve dashboard HTML."""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    return {"error": "Dashboard not found"}


@app.get("/incidents")
async def get_incidents():
    """Get all incidents."""
    return {
        "incidents": [
            {
                "incident_id": id,
                "status": state.get("resolution_status", "PROCESSING"),
                "severity": state.get("severity", "unknown"),
                "timestamp": state.get("timestamp", ""),
                "root_cause": state.get("root_cause", None)
            }
            for id, state in incidents.items()
        ]
    }


@app.get("/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get incident details."""
    if incident_id not in incidents:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    state = incidents[incident_id]
    return {
        "incident_id": incident_id,
        "status": state.get("resolution_status", "PROCESSING"),
        "severity": state.get("severity", "unknown"),
        "timestamp": state.get("timestamp", ""),
        "root_cause": state.get("root_cause", None),
        "logs_findings": state.get("logs_findings", []),
        "metrics_findings": state.get("metrics_findings", []),
        "deploy_findings": state.get("deploy_findings", []),
        "resolver_suggestions": state.get("resolver_suggestions", []),
        "executed_actions": state.get("executed_actions", []),
        "commander_analysis": state.get("commander_analysis")
    }


@app.post("/incidents/trigger")
async def trigger_incident(request: IncidentAlertRequest, background_tasks: BackgroundTasks):
    """Trigger new incident and run workflow."""
    
    incident_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat() + "Z"
    
    # Create initial state
    initial_state = {
        "incident_id": incident_id,
        "alert_message": request.alert_message,
        "severity": request.severity,
        "timestamp": now,
        "logs": [],
        "metrics": [],
        "deployments": [],
        "commander_analysis": None,
        "logs_findings": [],
        "metrics_findings": [],
        "deploy_findings": [],
        "resolver_suggestions": [],
        "root_cause": None,
        "recommended_actions": [],
        "executed_actions": [],
        "resolution_status": "PROCESSING",
        "chain_of_thought": [],
        "error": None
    }
    
    # Store incident
    incidents[incident_id] = initial_state
    
    # Run workflow in background
    background_tasks.add_task(run_incident_workflow, initial_state, incident_id)
    
    return {
        "incident_id": incident_id,
        "status": "created",
        "message": f"Incident {incident_id} created and workflow started"
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("Autonomous Incident Commander API")
    print("="*60)
    print("\n[OK] Dashboard: http://localhost:8000/dashboard")
    print("[OK] API Docs: http://localhost:8000/docs")
    print("[OK] Starting server on http://0.0.0.0:8000\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
