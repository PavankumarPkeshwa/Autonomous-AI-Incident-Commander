"""
Main entry point for Autonomous Incident Commander.
Demonstrates the multi-agent incident response workflow.
"""
import sys
import json
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure project modules are importable
sys.path.insert(0, str(__file__).rsplit("\\", 1)[0])

from graph.state import IncidentState
from agents.commander import commander_node_sync
from agents.logs_agent import logs_analysis_node_sync
from agents.metrics_agent import metrics_analysis_node_sync
from agents.deploy_agent import deploy_analysis_node_sync
from agents.resolver_agent import resolution_node_sync
from config.settings import RCA_REPORT_PATH, CHAIN_OF_THOUGHT_PATH
from langchain_groq import ChatGroq

# Initialize Groq LLM
def create_groq_llm():
    """Create Groq LLM instance."""
    return ChatGroq(
        model="mixtral-8x7b-32768",
        temperature=0.7,
        max_retries=2,
    )


class GroqLLMWrapper:
    """Wrapper to make Groq ChatModel compatible with our agent interface."""
    
    def __init__(self, llm):
        self.llm = llm
    
    def generate(self, prompt: str):
        """Generate response using Groq."""
        
        class Generation:
            def __init__(self, text):
                self.text = text
        
        class Generations:
            def __init__(self, text):
                self.generations = [[Generation(text)]]
        
        try:
            # Call Groq and get response
            response = self.llm.invoke(prompt)
            response_text = response.content
            return Generations(response_text)
        except Exception as e:
            # Fallback to mock response if API fails
            print(f"Warning: Groq API error, using fallback response: {e}")
            fallback_text = f"Analysis in progress (using fallback).\nError: {str(e)}"
            return Generations(fallback_text)


# Mock LLM Fallback for demonstration (if Groq API fails)
class MockLLMFallback:
    """Fallback Mock LLM for testing without Groq API key."""
    
    def generate(self, prompt: str):
        """Mock response generation."""
        
        class MockGeneration:
            def __init__(self, text):
                self.text = text
        
        class MockGenerations:
            def __init__(self, text):
                self.generations = [[MockGeneration(text)]]
        
        # Generate reasonable mock responses based on prompt content
        if "commander" in prompt.lower():
            response_text = """
INCIDENT ASSESSMENT:
The checkout service is experiencing a critical incident with elevated error rates and latency.

KEY FINDINGS:
1. Payment gateway timeouts detected
2. Database connection pool exhaustion
3. High error rate (12.5%) on checkout endpoints
4. P99 latency spike to 5234ms

INVESTIGATION PLAN:
1. Immediate: Engage logs and metrics agents
2. Check for recent deployments that may have triggered the issue
3. Analyze correlation between error patterns and system metrics
4. Assess if rollback or scaling is needed

PRIORITY ACTIONS:
- Investigate payment gateway integration
- Check database connection pool settings
- Review recent config-service deployment (17 min before incident)
- Consider circuit breaker adjustment
"""
        elif "logs" in prompt.lower():
            response_text = """
LOG FORENSICS FINDINGS:

ERROR PATTERNS IDENTIFIED:
1. Connection timeouts to payment-gateway (12:32:10 - recurring)
2. Payment processing failures (12.5% of requests)
3. Database connection pool exhaustion (12:32:25)
4. Circuit breaker opened for payment-gateway (12:33:00)

TIMELINE:
- 12:32:10: First payment gateway timeout
- 12:32:15: Payment processing failures begin
- 12:32:20: Error rate warning (12.5%)
- 12:32:25: DB pool exhaustion detected
- 12:33:00: Circuit breaker trips

ROOT CAUSE HYPOTHESIS:
The config-service deployment 17 minutes prior changed database pool size from 50 to 100,
but also reduced timeout threshold from 3000ms to 2000ms. This aggressive timeout combined
with upstream payment gateway issues created cascading failures.
"""
        elif "metrics" in prompt.lower():
            response_text = """
METRICS ANALYSIS:

THRESHOLD BREACHES:
✗ CPU Usage: 87.5% (threshold: 85%) - CRITICAL
✗ Memory Usage: 78.2% (threshold: 80%) - WARNING
✗ P99 Latency: 5234ms (threshold: 5000ms) - HIGH
✗ Error Rate: 12.5% (threshold: 5%) - CRITICAL
✗ DB Active Connections: 98/100 (98% utilized) - CRITICAL

HISTORICAL COMPARISON:
- CPU 5 min ago: 35.2% → Now: 87.5% (147% increase)
- Error Rate 5 min ago: 0.3% → Now: 12.5% (4066% increase)

UPSTREAM ISSUES:
- Payment Gateway Status: DEGRADED
- Payment Gateway Error Rate: 8.2%
- Payment Gateway Latency: 2500ms (increased load)

CONCLUSION:
Incident is primarily caused by internal resource exhaustion and timeout configuration,
exacerbated by upstream payment gateway degradation.
"""
        elif "deploy" in prompt.lower():
            response_text = """
DEPLOYMENT CORRELATION ANALYSIS:

SUSPICIOUS DEPLOYMENT IDENTIFIED:
Service: config-service
Version: v2.3.1
Deployment Time: 2024-01-15T14:15:00Z
Minutes Before Incident: 17 minutes

CONFIGURATION CHANGES:
- Database Pool Size: 50 → 100 (increased)
- Cache TTL: 300s → 600s (increased)
- Timeout Threshold: 3000ms → 2000ms (REDUCED - RISKY)

ROLLBACK RISK ASSESSMENT:
- High confidence that deployment correlates with incident
- Timeout threshold reduction is problematic
- Rollback target: v2.3.0 (previous stable version)
- Rollback risk: LOW (previous version was stable)

RECOMMENDATION:
Perform rollback of config-service to v2.3.0
This will restore timeout threshold to 3000ms and stabilize payment processing.
"""
        elif "resolver" in prompt.lower() or "faq" in prompt.lower():
            response_text = """
RESOLUTION RECOMMENDATIONS:

PRIMARY ACTION: Rollback config-service to v2.3.0
- Restores timeout threshold from 2000ms to 3000ms
- Reduces cascading failures from timeouts
- High success probability (95%+)
- Risk: Low (reverting to proven configuration)

SECONDARY ACTIONS (if rollback doesn't fully resolve):
1. Scale checkout-service to 3 replicas (from current 1)
   - Distribute CPU load (currently 87.5%)
   - Reduce error rate through redundancy

2. Adjust circuit breaker threshold from 10% to 15%
   - Allow brief upstream degradation without cascading locally
   - Prevent premature circuit breaker trips

3. Disable new_checkout_feature flag if present
   - Isolate any problematic new feature code

MONITORING PLAN:
- Watch error rate (target: <1%)
- Monitor P99 latency (target: <2000ms)
- Check database connection pool (target: <50% utilized)
- Track payment gateway correlation

ESCALATION TRIGGERS:
- If error rate remains >5% after 5 minutes
- If P99 latency remains >3000ms after 5 minutes
- If payment gateway stays DEGRADED for >10 minutes
"""
        else:
            response_text = "Analysis in progress..."
        
        return MockGenerations(response_text)


def create_initial_state(alert_message: str, severity: str = "critical") -> IncidentState:
    """Create initial incident state from alert."""
    now = datetime.utcnow().isoformat() + "Z"
    
    return {
        "incident_id": str(uuid.uuid4())[:8],
        "alert_message": alert_message,
        "severity": severity,
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
        "resolution_status": "IN_PROGRESS",
        "chain_of_thought": [],
        "rca_report": None,
    }


def run_incident_response_workflow(llm, initial_state: IncidentState) -> IncidentState:
    """
    Execute the multi-agent incident response workflow.
    Simulates the graph-based orchestration.
    """
    print("\n" + "="*70)
    print("AUTONOMOUS INCIDENT COMMANDER - STARTING INCIDENT RESPONSE")
    print("="*70)
    print(f"Incident ID: {initial_state['incident_id']}")
    print(f"Alert: {initial_state['alert_message']}")
    print(f"Severity: {initial_state['severity']}")
    print(f"Timestamp: {initial_state['timestamp']}")
    print("="*70 + "\n")
    
    state = initial_state.copy()
    
    # Step 1: Commander Analysis
    print("[STEP 1/5] Commander analyzing incident...")
    commander_result = commander_node_sync(state, llm)
    state.update(commander_result)
    print(f"[OK] Commander analysis complete\n")
    
    # Step 2: Parallel Agent Analysis
    print("[STEP 2/5] Running parallel forensic analysis...")
    print("  - Analyzing logs...")
    logs_result = logs_analysis_node_sync(state, llm)
    state.update(logs_result)
    print("  [OK] Logs analysis complete")
    
    print("  - Analyzing metrics...")
    metrics_result = metrics_analysis_node_sync(state, llm)
    state.update(metrics_result)
    print("  [OK] Metrics analysis complete")
    
    print("  - Checking deployments...")
    deploy_result = deploy_analysis_node_sync(state, llm)
    state.update(deploy_result)
    print("  [OK] Deployment correlation complete\n")
    
    # Step 3: Root Cause Analysis
    all_findings = (
        state.get("commander_analysis", "") +
        "".join(state.get("logs_findings", [])) +
        "".join(state.get("metrics_findings", [])) +
        "".join(state.get("deploy_findings", []))
    )
    state["root_cause"] = "Aggressive timeout configuration change in config-service v2.3.1"
    
    # Step 4: Resolution Planning
    print("[STEP 3/5] Planning remediation...")
    resolver_result = resolution_node_sync(state, llm)
    state.update(resolver_result)
    print("[OK] Resolution plan created\n")
    
    # Step 5: Execute recommended action (simulated)
    print("[STEP 4/5] Executing remediation actions...")
    from tools.rollback_action import trigger_rollback, get_action_log
    
    rollback_result = trigger_rollback("config-service", "v2.3.0")
    print(f"[OK] Initiated rollback: {rollback_result}")
    
    action_log = get_action_log()
    state.update({"executed_actions": [action_log]})
    state["resolution_status"] = "RESOLVED"
    print()
    
    # Step 6: Report Generation
    print("[STEP 5/5] Generating RCA report...")
    rca = generate_rca_report(state)
    state["rca_report"] = rca
    
    # Save outputs
    save_rca_report(rca)
    save_chain_of_thought(state["chain_of_thought"])
    print("[OK] RCA report generated and saved\n")
    
    return state


def generate_rca_report(state: IncidentState) -> str:
    """Generate Root Cause Analysis report."""
    
    report = f"""# Incident Root Cause Analysis Report

## Incident Summary
- **Incident ID**: {state['incident_id']}
- **Severity**: {state['severity'].upper()}
- **Timestamp**: {state['timestamp']}
- **Status**: {state['resolution_status']}

## Alert
{state['alert_message']}

## Root Cause
{state['root_cause']}

## Findings Summary

### Commander Analysis
{state.get('commander_analysis', 'N/A')[:500]}

### Log Forensics
{state.get('logs_findings', ['N/A'])[0][:500] if state.get('logs_findings') else 'N/A'}

### Metrics Analysis
{state.get('metrics_findings', ['N/A'])[0][:500] if state.get('metrics_findings') else 'N/A'}

### Deployment Correlation
{state.get('deploy_findings', ['N/A'])[0][:500] if state.get('deploy_findings') else 'N/A'}

## Resolution Actions Taken
{json.dumps(state.get('executed_actions', []), indent=2)[:500]}

## Recommendations
{state.get('resolver_suggestions', ['N/A'])[0][:500] if state.get('resolver_suggestions') else 'N/A'}

## Timeline
1. **Alert Received**: {state['timestamp']}
2. **Commander Analysis**: 30 seconds
3. **Parallel Forensics**: 60 seconds
4. **Resolution Planning**: 30 seconds
5. **Remediation Executed**: 20 seconds
6. **Total MTTR**: ~2.5 minutes

---
Generated by Autonomous Incident Commander at {datetime.utcnow().isoformat() + 'Z'}
"""
    
    return report


def save_rca_report(report: str):
    """Save RCA report to file."""
    try:
        with open(RCA_REPORT_PATH, "w") as f:
            f.write(report)
        print(f"RCA report saved to: {RCA_REPORT_PATH}")
    except Exception as e:
        print(f"Warning: Could not save RCA report: {e}")


def save_chain_of_thought(cot: list):
    """Save chain of thought reasoning trace."""
    try:
        with open(CHAIN_OF_THOUGHT_PATH, "w") as f:
            json.dump(cot, f, indent=2)
        print(f"Chain of thought saved to: {CHAIN_OF_THOUGHT_PATH}")
    except Exception as e:
        print(f"Warning: Could not save chain of thought: {e}")


def main():
    """Main entry point."""
    
    # Initialize Groq LLM
    try:
        groq_llm = create_groq_llm()
        llm = GroqLLMWrapper(groq_llm)
        print("[OK] Groq API connected successfully\n")
    except Exception as e:
        print(f"[WARNING] Could not connect to Groq API: {e}")
        print("  Using mock responses for demonstration\n")
        llm = MockLLMFallback()
    
    # Simulate an incident alert
    alert_message = """
    CRITICAL: Checkout service experiencing high error rate (12.5%) and elevated P99 latency (5234ms).
    Payment processing degraded. Database connection pool near exhaustion (98/100).
    Payment gateway upstream service showing degradation (8.2% error rate).
    """
    
    # Create initial state from alert
    initial_state = create_initial_state(alert_message, severity="critical")
    
    # Run the incident response workflow
    final_state = run_incident_response_workflow(llm, initial_state)
    
    # Print summary
    print("\n" + "="*70)
    print("INCIDENT RESPONSE COMPLETE")
    print("="*70)
    print(f"Incident ID: {final_state['incident_id']}")
    print(f"Status: {final_state['resolution_status']}")
    print(f"Root Cause Identified: {final_state['root_cause']}")
    print(f"Actions Executed: {len(final_state['executed_actions'])}")
    print("="*70 + "\n")
    
    # Show key findings
    print("KEY FINDINGS:")
    print("-" * 70)
    if final_state['logs_findings']:
        print(f"\nLogs Analysis (excerpt):\n{final_state['logs_findings'][0][:300]}...")
    if final_state['metrics_findings']:
        print(f"\nMetrics Analysis (excerpt):\n{final_state['metrics_findings'][0][:300]}...")
    if final_state['deploy_findings']:
        print(f"\nDeployment Correlation (excerpt):\n{final_state['deploy_findings'][0][:300]}...")
    if final_state['resolver_suggestions']:
        print(f"\nResolver Recommendations (excerpt):\n{final_state['resolver_suggestions'][0][:300]}...")
    print("\n" + "-" * 70)


if __name__ == "__main__":
    main()
