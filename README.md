# Autonomous Incident Commander 🚨

**A Multi-Agent AI System for Automated Production Incident Response**

An intelligent, autonomous incident response platform that detects production issues, analyzes root causes across logs/metrics/deployments, and recommends (or executes) remediation actions—all without human intervention.

---

## 📋 Table of Contents

1. [What This Application Does](#-what-this-application-does)
2. [Real-World Use Cases](#-real-world-use-cases)
3. [Key Benefits](#-key-benefits)
4. [Architecture Overview](#-architecture-overview)
5. [File Structure & Connections](#-file-structure--connections)
6. [Data Flow](#-data-flow)
7. [Getting Started](#-getting-started)
8. [How It Works (Step-by-Step)](#-how-it-works-step-by-step)
9. [Configuration](#️-configuration)
10. [Extending the System](#-extending-the-system)

---

## 🎯 What This Application Does

### Core Purpose

The **Autonomous Incident Commander** is a production incident response system that automates the historically manual, time-consuming process of incident diagnosis and resolution.

**Traditional Approach:**
```
Alert → On-call engineer woken up → Manual log analysis → Slack discussions 
→ Manual metrics review → Find deployment correlation → Decide on action 
→ Execute fix → Write RCA report (4-24 hours)
```

**Autonomous Incident Commander Approach:**
```
Alert → Parallel forensic analysis → Root cause identified → Remediation recommended/executed 
→ RCA report generated (seconds to minutes)
```

### What It Handles

✅ **Incident Triage**: Analyzes alert severity and context
✅ **Multi-Source Forensics**: Investigates logs, metrics, and recent deployments simultaneously
✅ **Root Cause Analysis**: Identifies what went wrong and why
✅ **Remediation Recommendations**: Suggests fixes with risk assessment
✅ **Automated Execution**: Can execute safe fixes (rollbacks, scaling, feature flags)
✅ **Documentation**: Generates detailed RCA reports with reasoning traces

---

## 🌍 Real-World Use Cases

### 1. **E-Commerce Platforms**
**Scenario**: Black Friday sale - sudden spike in traffic causes checkout service to fail

**What Happens**:
- Payment gateway timeout alert triggers
- System analyzes: logs show connection pool exhaustion, metrics show CPU 95%, deployment correlation finds aggressive timeout config change 10 min ago
- **Action**: Rolls back the deployment → System recovers in 30 seconds
- **Without automation**: On-call engineer spends 15+ minutes diagnosing the issue

**Impact**: Prevents revenue loss, avoids customer friction

### 2. **Streaming Services**
**Scenario**: Video encoding service degradation during peak hours

**What Happens**:
- Latency metric breach alert (p99 > 10s)
- System analyzes: logs show external transcoding API returning errors, metrics show queued jobs backing up
- **Action**: Scales encoding workers horizontally + adjusts circuit breaker
- **RCA**: Upstream vendor experiencing DDoS

**Impact**: Continuous service availability, reduced buffering

### 3. **SaaS Platforms**
**Scenario**: Database query performance degradation

**What Happens**:
- Error rate spike detected (from 0.1% → 8%)
- System analyzes: slow query logs identified, metrics show connection pool at 100%, deploy correlation shows new ORM query pattern from recent release
- **Action**: Rolls back release or disables problematic feature flag
- **RCA**: N+1 query pattern introduced in new code

**Impact**: Prevents cascading failures, reduces customer complaints

### 4. **Financial Systems**
**Scenario**: Payment processing timeout during settlement window

**What Happens**:
- Transaction queue backing up alert
- System analyzes: timeout threshold reduced in config update, metrics show network latency increased to upstream bank
- **Action**: Rolls back timeout config, triggers retry mechanism
- **RCA**: Configuration drift + downstream latency spike

**Impact**: Ensures settlement window compliance, prevents financial penalties

### 5. **Kubernetes/Container Environments**
**Scenario**: Crash loop indicating bad deployment

**What Happens**:
- Pod restart loop detected
- System analyzes: logs show out-of-memory errors, metrics show memory usage spike
- **Action**: Scales deployment horizontally, possible rollback
- **RCA**: Memory leak or insufficient resource allocation

**Impact**: Self-healing infrastructure, improved reliability

---

## 💡 Key Benefits

| Benefit | Impact | Example |
|---------|--------|---------|
| **Reduced MTTR** (Mean Time To Resolution) | Incidents resolved in seconds instead of hours | 4-hour incident → 2-minute incident |
| **No Human Dependency** | Works 24/7 without on-call escalation | Incident resolved at 3 AM without waking engineer |
| **Parallel Analysis** | Multiple investigation paths simultaneously | Logs + Metrics + Deploy checked in parallel, not sequentially |
| **Consistent Quality** | No human fatigue or mistakes | Same diagnostic quality at 3 AM as 3 PM |
| **Cost Savings** | Reduced on-call pages = less burnout = better retention | $500/month on-call stipend saved |
| **Better RCA Reports** | Full reasoning trace and audit trail | Full chain-of-thought saved for compliance/learning |
| **Faster Customer Resolution** | Customers experience shorter outages | 95% reduction in incident duration |
| **Scalability** | Handles any number of incidents simultaneously | Company grows, incident response capability scales |

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTONOMOUS INCIDENT COMMANDER                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  INPUT: Production Alert (from monitoring system)      │   │
│  │  Example: "Checkout service error rate: 12.5%"        │   │
│  └────────────────────┬────────────────────────────────────┘   │
│                       ▼                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1️⃣  COMMANDER AGENT (Orchestrator)                    │   │
│  │     - Analyzes alert severity                           │   │
│  │     - Creates investigation strategy                    │   │
│  │     - Delegates to specialist agents                    │   │
│  └────────────────────┬────────────────────────────────────┘   │
│                       │                                          │
│      Parallel ▼▼▼▼▼ Analysis                                    │
│  ┌─────────────┬──────────────┬──────────────┬──────────────┐  │
│  │             │              │              │              │  │
│  ▼             ▼              ▼              ▼              ▼  │
│  2️⃣ LOGS     3️⃣ METRICS    4️⃣ DEPLOY    5️⃣ RESOLVER   │
│  Agent       Agent          Agent         Agent         │
│  │             │              │              │              │  │
│  ├─ Error   ├─ CPU          ├─ Timeline  ├─ FAQ Search  │
│  │  patterns │              │  analysis   ├─ Solutions   │  │
│  ├─ Traces  ├─ Memory       ├─ Config    ├─ Risk assess │
│  ├─ Timeline├─ Latency      │  changes    └─ Fix select  │
│  └─ Service ├─ Error rate   └─ Rollback                   │
│    flows    └─ Databases       plan                        │
│                                                              │
│  All findings → ACCUMULATED IN SHARED STATE                │
│                                                              │
│                       ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  ROOT CAUSE IDENTIFIED (synthesized from all agents)   │   │
│  └────────────────────┬────────────────────────────────────┘  │
│                       ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  REMEDIATION EXECUTED (or recommended)                 │   │
│  │  ├─ Rollback deployment                                │   │
│  │  ├─ Scale service horizontally                         │   │
│  │  ├─ Adjust circuit breaker                            │   │
│  │  └─ Disable feature flag                              │   │
│  └────────────────────┬────────────────────────────────────┘  │
│                       ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  OUTPUT:                                                │   │
│  │  ✅ RCA Report (rca_report.md)                         │   │
│  │  ✅ Chain of Thought (chain_of_thought.json)           │   │
│  │  ✅ Incident Status RESOLVED                           │   │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Technology Stack

```
Python 3.13 + LangChain + LangGraph
    ↓
FastAPI REST API
    ↓
React Frontend Dashboard (HTML/CDN)
    ↓
Mock Data + Optional Groq LLM
```

---

## 📁 File Structure & Connections

### Directory Tree

```
autonomous_incident_commander/
│
├── 📌 ENTRY POINTS
│   ├── main.py                      # CLI: Full incident workflow
│   ├── api.py                       # FastAPI: REST API + Dashboard backend
│   └── dashboard.html               # Frontend: Interactive UI
│
├── 📊 SHARED STATE & CONFIGURATION
│   ├── graph/
│   │   └── state.py                 # IncidentState (shared memory across all agents)
│   ├── config/
│   │   └── settings.py              # Configuration: thresholds, API keys, paths
│   └── prompts/
│       ├── commander_prompt.py      # System prompts for each agent
│       ├── logs_prompt.py
│       ├── metrics_prompt.py
│       ├── deploy_prompt.py
│       └── resolver_prompt.py
│
├── 🤖 AGENTS (Specialized AI Analyzers)
│   ├── agents/
│   │   ├── commander.py             # Orchestrator: analyzes alert, delegates work
│   │   ├── logs_agent.py            # Forensics: analyzes error logs & traces
│   │   ├── metrics_agent.py         # Telemetry: detects metric anomalies
│   │   ├── deploy_agent.py          # CI/CD: finds suspicious deployments
│   │   └── resolver_agent.py        # Resolution: recommends/executes fixes
│   └── agents/__init__.py
│
├── 🛠️ TOOLS (Functions Agents Can Call)
│   ├── tools/
│   │   ├── log_search.py            # Query log database
│   │   ├── metrics_query.py         # Fetch system metrics
│   │   ├── deploy_history.py        # Get deployment timeline
│   │   ├── faq_retriever.py         # Search knowledge base
│   │   ├── rollback_action.py       # Execute remediation
│   │   └── tools/__init__.py
│
├── 📚 MOCK DATA (Realistic Test Data)
│   ├── mock_data/
│   │   ├── logs.json                # Sample error logs
│   │   ├── metrics.json             # Current system metrics
│   │   ├── deployments.json         # Deployment history
│   │   └── faq_kb.json              # Incident solutions database
│
├── 📄 OUTPUT & DOCUMENTATION
│   ├── output/
│   │   ├── rca_report.md            # Generated RCA report
│   │   └── chain_of_thought.json    # Agent reasoning trace
│   ├── DASHBOARD_GUIDE.md           # How to use the dashboard
│   └── requirements.txt             # Python dependencies
│
├── 🔧 CONFIGURATION
│   ├── .env                         # Environment variables (Groq API key)
│   └── README.md                    # This file
│
└── 📦 MISC
    └── __init__.py                  # Package initialization
```

---

## 🔗 File Connections & Data Flow

### How Files Talk to Each Other

```
┌──────────────────────────────────────────────────────────────────────┐
│                        INCIDENT ALERT RECEIVED                        │
└──────────────────┬───────────────────────────────────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────────────────────┐
    │  main.py / api.py                                   │
    │  ├─ Imports: config/settings.py (get thresholds)   │
    │  ├─ Imports: graph/state.py (create IncidentState)│
    │  └─ Calls: agents/* (5 specialized analyzers)     │
    └──────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┬──────────┐
        │          │          │          │          │
        ▼          ▼          ▼          ▼          ▼
   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
   │Commander│ │  Logs  │ │Metrics │ │ Deploy │ │Resolver│
   │  Agent  │ │ Agent  │ │ Agent  │ │ Agent  │ │ Agent  │
   └────┬───┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
        │         │          │          │          │
        │ Each agent:        │          │          │
        │ ├─ Loads prompt from prompts/*     │
        │ ├─ Calls tools from tools/*        │
        │ ├─ Updates shared IncidentState    │
        │ └─ Returns findings               │
        │         │          │          │          │
        └─────────┼──────────┼──────────┼──────────┘
                  │
                  ▼
        ┌──────────────────────────────────┐
        │ ALL FINDINGS MERGED IN STATE     │
        │ (graph/state.py IncidentState)   │
        └──────────────┬───────────────────┘
                       │
                       ▼
        ┌──────────────────────────────────┐
        │ OUTPUTS GENERATED:               │
        │ ├─ output/rca_report.md         │
        │ └─ output/chain_of_thought.json │
        └──────────────────────────────────┘
```

### Agent → Tool Relationships

```
Commander Agent
    ├─ Uses: No direct tools (orchestrator role)
    
Logs Agent
    └─ Calls: log_search.py
        ├─ get_error_logs()
        ├─ get_logs_by_service()
        └─ log_search()
    
Metrics Agent
    └─ Calls: metrics_query.py
        ├─ query_metrics()
        ├─ check_latency()
        ├─ check_resource_usage()
        ├─ check_database_health()
        └─ check_upstream_health()
    
Deploy Agent
    └─ Calls: deploy_history.py
        ├─ get_deployment_history()
        ├─ correlate_deployment_to_incident()
        └─ get_deployment_changes()
    
Resolver Agent
    ├─ Calls: faq_retriever.py
    │   ├─ search_faq()
    │   ├─ get_solution_for_symptom()
    │   └─ get_faq_by_severity()
    └─ Calls: rollback_action.py
        ├─ trigger_rollback()
        ├─ scale_service()
        ├─ disable_feature()
        ├─ adjust_circuit_breaker()
        └─ get_action_log()
```

---

## 📊 Data Flow (Example Incident)

### Real Example: Checkout Service Timeout

```
1. ALERT INGESTED
   Input: "Checkout service error rate 12.5%, P99 latency 5.2s"
   ↓
   Creates IncidentState with:
   - incident_id: "abc123"
   - alert_message: "..."
   - severity: "critical"
   - timestamp: "2026-04-10T12:32:10Z"

2. COMMANDER AGENT ANALYZES
   Prompt: "You are an expert incident commander. Analyze this alert..."
   Decision: "This looks like a service capacity or configuration issue"
   Output: commander_analysis = "..."

3. PARALLEL ANALYSIS PHASE

   LOGS AGENT:
   - Calls: log_search("error", "checkout")
   - MockData: logs.json returns error patterns
   - Analysis: "Connection timeouts to payment-gateway at 12:32:10"
   - Updates State: logs_findings = [...]

   METRICS AGENT:
   - Calls: query_metrics()
   - MockData: metrics.json returns current metrics
   - Analysis: "CPU 87.5%, Error rate 12.5%, P99 latency 5234ms"
   - Updates State: metrics_findings = [...]

   DEPLOY AGENT:
   - Calls: get_deployment_history()
   - MockData: deployments.json shows recent changes
   - Analysis: "config-service v2.3.1 deployed 17 min ago"
   - Correlation: "Timeout threshold changed 3000ms → 2000ms"
   - Updates State: deploy_findings = [...]

   RESOLVER AGENT:
   - Calls: search_faq("payment timeout checkout")
   - MockData: faq_kb.json returns solution
   - Calls: trigger_rollback("config-service", "v2.3.0")
   - MockData: rollback_action returns action log
   - Updates State: resolver_suggestions = [...], executed_actions = [...]

4. ALL FINDINGS MERGED INTO SINGLE STATE

5. RCA REPORT GENERATED
   Compiled From State → output/rca_report.md
   Content:
   ```
   # RCA Report
   
   Root Cause: Aggressive timeout configuration change
   - config-service v2.3.1 reduced timeout from 3s to 2s
   - Combined with payment-gateway degradation
   - Created cascading failures
   
   Impact: 12.5% error rate, $50K/min revenue loss
   
   Resolution: Rolled back config-service to v2.3.0
   Result: Error rate → 0.1%, All systems nominal
   ```

6. STATUS: RESOLVED ✅
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **pip** (or uv)
- **Groq API Key** (optional, system falls back to mock)

### Installation

```bash
# Clone/navigate to repository
cd autonomous_incident_commander

# Install dependencies
pip install -r requirements.txt

# (Optional) Configure Groq API Key
# Edit .env file:
# GROQ_API_KEY=gsk_your_groq_api_key_here
```

### Quick Start

**Option 1: Run CLI (Full Workflow)**
```bash
python main.py
```
Output:
- Console trace of all 5 agent analyses
- `output/rca_report.md` - Full RCA report
- `output/chain_of_thought.json` - Agent reasoning trace

**Option 2: Run FastAPI + Dashboard (Interactive)**
```bash
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```
Then open: `http://localhost:8000/dashboard`

---

## 🔄 How It Works (Step-by-Step)

### Full Incident Response Workflow

```
STEP 1: Alert Ingestion (Automatic)
├─ Monitoring system sends alert
├─ Create IncidentState with incident details
└─ Assign incident_id, severity, timestamp

STEP 2: Commander Analysis
├─ Read alert message
├─ Create investigation strategy
├─ Output: commander_analysis

STEP 3: Parallel Forensic Analysis (All Simultaneous)
├─ Logs Agent: Analyze error patterns, traces, timelines
├─ Metrics Agent: Check CPU, memory, latency, error rates
├─ Deploy Agent: Find suspicious deployments, config changes
├─ Resolver Agent: Search FAQ, assess remediation options
└─ All findings accumulated in shared IncidentState

STEP 4: Root Cause Identification
├─ Synthesize all agent findings
├─ Identify what failed
├─ Determine why it failed
└─ Output: root_cause

STEP 5: Resolution Planning
├─ Resolver Agent reviews all findings
├─ Searches FAQ knowledge base for solutions
├─ Assesses remediation options
├─ Evaluates risks and rollback plans
└─ Output: resolver_suggestions, recommended_actions

STEP 6: Remediation Execution
├─ Execute low-risk actions (rollbacks, scaling, etc)
├─ Roll back suspicious deployment
├─ Scale service if needed
├─ Adjust circuit breakers
└─ Output: executed_actions

STEP 7: Report Generation
├─ Compile all findings into structured report
├─ Generate RCA in markdown format
├─ Export chain-of-thought JSON (for debugging/learning)
└─ Output files saved to output/

STEP 8: Incident Resolved
└─ Status: RESOLVED ✅
```

### Parallel vs Sequential

**Without Parallelization (Bad - Traditional Approach):**
```
Logs Analysis (2s) → Metrics Analysis (2s) → Deploy Analysis (2s) → Total: 6s
```

**With Parallelization (What We Do - Modern Approach):**
```
Logs Analysis (2s)
Metrics Analysis (2s)  } All run simultaneously → Total: 2s
Deploy Analysis (2s)
```

**Time Savings: 3x Faster Analysis** ⚡

---

## ⚙️ Configuration

### config/settings.py

```python
# LLM Model Selection
LLM_MODEL = "mixtral-8x7b-32768"  # Groq model (free tier)
GROQ_API_KEY = "gsk_..."          # From .env

# Agent Settings
MAX_ITERATIONS = 15
TIMEOUT_SECONDS = 300

# Incident Thresholds (when to alert)
CPU_THRESHOLD = 85.0              # %
MEMORY_THRESHOLD = 80.0           # %
P99_LATENCY_THRESHOLD = 5000      # milliseconds
ERROR_RATE_THRESHOLD = 5.0        # %

# Output Paths
RCA_REPORT_PATH = "output/rca_report.md"
CHAIN_OF_THOUGHT_PATH = "output/chain_of_thought.json"

# Data Sources
FAQ_KB_PATH = "mock_data/faq_kb.json"
```

### .env File

```env
# Groq API Key (Get free at console.groq.com)
GROQ_API_KEY=gsk_your_actual_key

# Optional: Override default model
LLM_MODEL=mixtral-8x7b-32768
```

---

## 🔧 Extending the System

### Adding a New Agent

1. Create `agents/your_agent.py`:
```python
from graph.state import IncidentState

def your_analysis_node_sync(state: IncidentState, llm) -> dict:
    """Your agent's analysis logic"""
    
    # Load prompt
    prompt = format_your_prompt(...)
    
    # Call LLM
    response = llm.generate(prompt)
    analysis = response.generations[0][0].text
    
    # Return findings
    return {
        "your_findings": [analysis],
        "chain_of_thought": [{
            "agent": "your_agent",
            "action": "analysis",
            "result": analysis
        }]
    }
```

2. Create prompt in `prompts/your_prompt.py`:
```python
def format_your_prompt(incident_state):
    return f"""You are a specialist agent for XYZ analysis.
    
    Incident: {incident_state['alert_message']}
    
    Analyze and provide findings..."""
```

3. Call in `main.py` or `api.py`:
```python
your_result = your_analysis_node_sync(state, llm)
state.update(your_result)
```

### Adding a New Tool

1. Create `tools/your_tool.py`:
```python
def your_function(param1: str, param2: str):
    """Query your data source"""
    # Your logic here
    return findings
```

2. Use in agent:
```python
from tools.your_tool import your_function

findings = your_function("param1", "param2")
```

---

## 📝 Example Output

### RCA Report (output/rca_report.md)

```markdown
# Incident Root Cause Analysis Report

## Incident Summary
- **Incident ID**: c01ad225
- **Severity**: CRITICAL
- **Timestamp**: 2026-04-10T09:51:48.891358Z
- **Status**: RESOLVED

## Alert
CRITICAL: Checkout service experiencing high error rate (12.5%)...

## Root Cause
Aggressive timeout configuration change in config-service v2.3.1

## Findings Summary

### Commander Analysis
Critical checkout service issue. Payment gateway timeouts detected.

### Log Forensics
ERROR PATTERNS: Connection timeouts, Payment failures, DB pool exhaustion

### Metrics Analysis
CPU 87.5% | Memory 78.2% | P99 Latency 5234ms | Error Rate 12.5%

### Deployment Correlation
config-service v2.3.1 deployed 17 min before incident.
Timeout threshold changed 3000ms → 2000ms.

## Resolution Actions Taken
✓ Rolled back config-service to v2.3.0
✓ Error rate normalized to < 0.1%
```

---

## 🎓 Learning Outcomes

By studying this project, you'll learn:

✅ **Multi-Agent Systems**: How specialized AI agents collaborate
✅ **State Management**: Shared state patterns in distributed systems
✅ **LLM Integration**: Calling LLMs effectively from Python
✅ **Parallel Execution**: Concurrent task orchestration
✅ **REST APIs**: FastAPI for building scalable backends
✅ **Frontend Integration**: React with REST APIs
✅ **System Design**: Real incident response patterns

---

## 🚀 Why This Matters

### The Problem

Production incidents cost money:
- **Shopify**: Every minute of downtime = $500K+ lost revenue
- **AWS**: Average response time to incident = 30-60 minutes
- **Healthcare**: 4-6 hours to resolve critical systems incident

### The Solution

Autonomous incident response:
- **Reduces MTTR** from hours to minutes
- **No human escalation** needed for common issues
- **Parallel analysis** instead of sequential investigation
- **Always available** at 3 AM without waking anyone

This system demonstrates the future of DevOps and SRE practices.

---

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Groq API Docs](https://console.groq.com)
- [FastAPI Guide](https://fastapi.tiangolo.com/)

---

## 📄 License

This project is provided as-is for educational and demonstration purposes.

---

**Built with ❤️ for demonstrating autonomous incident response**
# Autonomous Incident Commander

A multi-agent incident response orchestration system built with **LangGraph** and **LangChain**. This project demonstrates how specialized AI agents can collaborate to diagnose, analyze, and resolve production incidents autonomously.

## 🎯 Overview

The Autonomous Incident Commander is a sophisticated incident response system that:

- **Ingests alerts** from monitoring systems
- **Orchestrates parallel forensic analysis** across logs, metrics, and deployments
- **Identifies root causes** through multi-agent reasoning
- **Recommends and executes remediation** actions
- **Generates detailed RCA reports** with chain-of-thought reasoning traces

### Key Features

✅ **Multi-Agent Architecture**: Specialized agents for logs, metrics, deployments, and resolution
✅ **Parallel Analysis**: Simultaneous investigation across multiple data sources
✅ **LangGraph-Based Workflow**: Structured state machine for incident orchestration
✅ **Mock Data Integration**: Complete mock datasets (logs, metrics, deployments, FAQ KB)
✅ **Remediation Tools**: Rollback, scaling, feature flags, circuit breaker adjustments
✅ **RCA Report Generation**: Markdown reports with full chain-of-thought traces
✅ **Extensible Design**: Easy to add new agents, tools, and data sources

---

## 📁 Project Structure

```
autonomous_incident_commander/
│
├── main.py                    # Entry point: orchestrates the full workflow
│
├── graph/
│   ├── state.py                 # IncidentState TypedDict (shared memory)
│   ├── transitions.py           # Conditional routing functions
│   └── incident_graph.py        # LangGraph StateGraph definition
│
├── agents/
│   ├── commander.py             # Orchestrator agent
│   ├── logs_agent.py            # Log forensics specialist
│   ├── metrics_agent.py         # Telemetry analyst
│   ├── deploy_agent.py          # CI/CD correlation expert
│   └── resolver_agent.py        # First-level resolver
│
├── tools/
│   ├── log_search.py            # Query mock log API
│   ├── metrics_query.py         # Fetch telemetry (CPU, latency, etc)
│   ├── deploy_history.py        # Get CI/CD timeline and correlations
│   ├── rollback_action.py       # Remediation actions
│   └── faq_retriever.py         # Knowledge base lookup
│
├── prompts/
│   ├── commander_prompt.py      # Commander system prompt
│   ├── logs_prompt.py           # Logs agent prompt
│   ├── metrics_prompt.py        # Metrics agent prompt
│   ├── deploy_prompt.py         # Deployment agent prompt
│   └── resolver_prompt.py       # Resolver agent prompt
│
├── mock_data/
│   ├── logs.json                # Sample error logs
│   ├── metrics.json             # Current system metrics
│   ├── deployments.json         # Recent deployment history
│   └── faq_kb.json              # Incident FAQ knowledge base
│
├── output/
│   ├── rca_report.md            # Generated RCA report
│   └── chain_of_thought.json    # Agent reasoning trace
│
├── config/
│   └── settings.py              # Configuration (thresholds, API keys, etc)
│
├── requirements.txt              # Project dependencies
├── .env                         # Environment variables (API keys)
└── README.md                    # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- pip or uv package manager
- **Groq API Key** (free at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone/Navigate to project**:
   ```bash
   cd autonomous_incident_commander
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # OR using uv:
   uv pip install -e .
   ```

3. **Configure Groq API Key**:
   ```bash
   # Edit .env with your Groq API key
   # Get free API key at: https://console.groq.com
   
   # .env file:
   LLM_MODEL=mixtral-8x7b-32768
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```
   
   Available Groq models:
   - `mixtral-8x7b-32768` (recommended - free tier)
   - `llama-2-70b-4096`
   - `gemma-7b-it`

### Running the Demo

```bash
python main.py
```

This will:
1. ✅ Connect to Groq API (or use fallback mock responses if API unavailable)
2. ✅ Simulate an incident alert (checkout service with high error rate)
3. ✅ Run the complete incident response workflow
4. ✅ Execute all agent analyses in parallel
5. ✅ Generate an RCA report and reasoning trace
6. ✅ Output findings to `output/rca_report.md` and `output/chain_of_thought.json`

> **Note**: If Groq API is unavailable or key is missing, the system automatically falls back to using mock LLM responses so you can see the workflow in action.

---

## 🔄 Incident Response Workflow

### Phase 1: Alert Ingestion
```
Alert → Create IncidentState → Initialize incident_id, timestamp, severity
```

### Phase 2: Commander Analysis
```
Commander Agent analyzes alert
→ Creates investigation plan
→ Delegates to specialized agents
```

### Phase 3: Parallel Forensics (Concurrent)
```
├─ Logs Agent: Analyze error patterns & trace logs
├─ Metrics Agent: Detect anomalies (CPU, latency, error rate)
├─ Deploy Agent: Find suspicious deployments in timeline
└─ All findings accumulated in shared IncidentState
```

### Phase 4: Root Cause Identification
```
Synthesize all findings
→ Identify root cause
→ Assess severity and impact
```

### Phase 5: Resolution Planning
```
Resolver Agent reviews findings
→ Searches FAQ knowledge base
→ Plans remediation actions
→ Assesses risks and rollback plans
```

### Phase 6: Remediation Execution
```
Execute recommended actions (mock):
├─ Rollback problematic deployment
├─ Scale service horizontally
├─ Adjust circuit breaker
└─ Disable feature flags
```

### Phase 7: RCA Report Generation
```
Compile all findings
→ Generate markdown RCA report
→ Export chain-of-thought JSON
→ Save artifacts
```

---

## 🧠 Agent Descriptions

### Commander Agent
**Role**: Orchestrator and decision maker
- Analyzes alert severity and context
- Creates investigation strategy
- Synthesizes findings from other agents
- Assigns work and prioritizes investigation

### Logs Agent (Forensics Specialist)
**Role**: Error log and trace analysis
- Searches error logs for patterns
- Identifies error codes and timelines
- Traces service dependencies through logs
- Finds cascade failure indicators

**Tools**:
- `log_search()`: Search logs by query, service, level
- `get_error_logs()`: Retrieve all ERROR level logs
- `get_logs_by_service()`: Filter logs by service

### Metrics Agent (Telemetry Analyst)
**Role**: System metrics and anomaly detection
- Analyzes CPU, memory, latency, error rates
- Compares current vs historical baselines
- Detects threshold breaches
- Checks upstream dependencies

**Tools**:
- `query_metrics()`: Get current service metrics
- `check_latency()`: Get p99, p95, p50 latency
- `check_resource_usage()`: CPU, memory, error rate
- `check_database_health()`: Connection pool, query time
- `check_upstream_health()`: External dependencies

### Deploy Agent (CI/CD Historian)
**Role**: Deployment timeline correlation
- Retrieves recent deployment history
- Finds deployments near incident timestamp
- Analyzes configuration changes
- Assesses rollback feasibility

**Tools**:
- `get_deployment_history()`: Recent deploys
- `correlate_deployment_to_incident()`: Find suspicious deploys
- `get_deployment_changes()`: Review what changed

### Resolver Agent (First-Level Responder)
**Role**: Rapid resolution and remediation
- Searches FAQ knowledge base for solutions
- Recommends remediation actions
- Plans rollback strategies
- Executes low-risk fixes

**Tools**:
- `search_faq()`: Search KB by query
- `get_solution_for_symptom()`: Find relevant solutions
- `trigger_rollback()`: Rollback a service
- `scale_service()`: Scale horizontally
- `disable_feature()`: Turn off feature flag
- `adjust_circuit_breaker()`: Tune circuit breaker

---

## ⚙️ Configuration

Edit `config/settings.py` to adjust:

```python
# Groq Model Configuration
LLM_MODEL = "mixtral-8x7b-32768"  # Default Groq model (free tier)
GROQ_API_KEY = "your_groq_api_key_here"

# Agent Configuration
MAX_ITERATIONS = 15
TIMEOUT_SECONDS = 300

# Alert Thresholds
CPU_THRESHOLD = 85.0  # %
MEMORY_THRESHOLD = 80.0  # %
P99_LATENCY_THRESHOLD = 5000  # ms
ERROR_RATE_THRESHOLD = 5.0  # %

# Output Paths
RCA_REPORT_PATH = "output/rca_report.md"
CHAIN_OF_THOUGHT_PATH = "output/chain_of_thought.json"
```

### Getting a Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free, no credit card required for testing)
3. Create an API key in the console
4. Add to `.env`: `GROQ_API_KEY=gsk_...`

**Available Groq Models:**
- `mixtral-8x7b-32768` - Excellent for general purpose (recommended)
- `llama-2-70b-4096` - Strong reasoning capabilities
- `gemma-7b-it` - Faster, lightweight option

---

## 📊 Mock Data

The project includes realistic mock data:

### logs.json
Simulated error logs with timestamps, services, error codes, and traces.

### metrics.json
Current system metrics including:
- CPU/memory usage
- Latency percentiles (p99, p95, p50)
- Error rates
- Database connection pool
- Upstream service health

### deployments.json
Recent CI/CD deployments with:
- Deployment timestamp and service
- Configuration changes
- Deployment status
- Correlation window analysis

### faq_kb.json
FAQ knowledge base with incident solutions:
- Common incident patterns
- Recommended solutions
- Severity levels
- Keywords for matching

---

## 🔧 Extending the System

### Adding a New Agent

1. Create `agents/new_agent.py`:
```python
from graph.state import IncidentState

async def new_analysis_node(state: IncidentState, llm) -> dict:
    """Your agent's logic here"""
    # Gather data, call LLM, return findings
    return {
        "new_findings": [analysis],
        "chain_of_thought": [reasoning_trace]
    }
```

2. Add to graph in `graph/incident_graph.py`

3. Create prompt in `prompts/new_prompt.py`

### Adding a New Tool

1. Create `tools/new_tool.py`:
```python
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description"""
    # Implementation
    return json.dumps(result)
```

2. Import in agent and call from prompt

### Connecting to Real Data

Replace mock data loaders with real APIs:

```python
# In tools/log_search.py
def load_logs():
    # Replace with actual log API call
    response = requests.get("https://elastic.acme.com/logs")
    return response.json()
```

---

## 📈 Output Examples

### RCA Report (output/rca_report.md)
```markdown
# Incident Root Cause Analysis Report

## Incident Summary
- Incident ID: abc12345
- Severity: CRITICAL
- Status: RESOLVED

## Root Cause
Aggressive timeout configuration change in config-service v2.3.1
deployed 17 minutes before incident...

## Timeline
1. Alert Received: 2024-01-15T14:32:00Z
2. Commander Analysis: 30 seconds
3. Parallel Forensics: 60 seconds
4. Resolution Planning: 30 seconds
5. Total MTTR: ~2.5 minutes
```

### Chain of Thought (output/chain_of_thought.json)
```json
[
  {
    "agent": "commander",
    "action": "incident_analysis",
    "analysis": "Critical incident in checkout service..."
  },
  {
    "agent": "logs_agent",
    "action": "log_analysis",
    "findings": "Payment gateway timeouts detected..."
  }
]
```

---

## 🧪 Testing

Run tests (when test suite is added):
```bash
pytest tests/
```

Test individual agents:
```bash
python -c "from agents.logs_agent import logs_analysis_node_sync; ..."
```

---

## 📚 Dependencies

Core dependencies:
- **langgraph**: Graph-based agent orchestration
- **langchain**: LLM abstractions and tools
- **langchain-groq**: Groq API integration (free tier available)
- **pydantic**: Type validation and configuration
- **python-dotenv**: Environment variable management

See `pyproject.toml` for full dependency list.

**Why Groq?**
- ✅ Free API tier (no credit card required for testing)
- ✅ Fast inference (optimized hardware)
- ✅ Great for rapid prototyping
- ✅ Production-ready models (Mixtral, Llama 2, Gemma)

---

## 🎓 Learning Resource

This project demonstrates:

✅ **Agent Architecture**: How to design specialized agents with clear responsibilities
✅ **Graph-Based Workflows**: Using LangGraph for structured incident orchestration
✅ **Parallel Execution**: Concurrent agent analysis within a state machine
✅ **Tool Integration**: Connecting agents to real (or mock) APIs
✅ **Prompt Engineering**: Crafting effective prompts for different agent roles
✅ **State Management**: Using TypedDict for shared multi-agent memory
✅ **Reasoning Traces**: Capturing chain-of-thought for explainability

---

## 🚀 Future Enhancements

- [ ] Integrate with actual monitoring systems (Datadog, New Relic, Prometheus)
- [ ] Add PagerDuty/Slack notifications for incident escalation
- [ ] Implement human-in-the-loop approval for critical remediation actions
- [ ] Add vector database for semantic FAQ search
- [ ] Support for multiple incident types (not just checkout)
- [ ] Web dashboard for monitoring incident response in real-time
- [ ] Continuous learning: train on past incidents to improve detection
- [ ] Multi-model support (easily switch between Groq models or other providers)

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## 📧 Support

For questions or issues:
- Check existing issues on GitHub
- Review the documentation above
- Examine mock data examples
- Check agent prompts for context

---

## 🎯 Key Takeaways

The Autonomous Incident Commander shows how AI agents can:

1. **Collaborate Effectively**: Each agent has specialized knowledge
2. **Work in Parallel**: Multiple investigations happen simultaneously
3. **Share Context**: Central state enables agent coordination
4. **Reason Systematically**: Prompts guide investigation approach
5. **Take Actions**: Tools enable real-world incident remediation
6. **Explain Reasoning**: Chain-of-thought traces show decision-making
7. **Provide Actionable Insights**: RCA reports guide human teams

This architecture can be adapted for many domains requiring multi-agent reasoning and coordination!

---

**Built with ❤️ using LangGraph and LangChain**
