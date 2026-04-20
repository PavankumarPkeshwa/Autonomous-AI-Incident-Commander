"""
Configuration settings for Autonomous Incident Commander.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Model Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "mixtral-8x7b-32768")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Agent Configuration
MAX_ITERATIONS = 15
TIMEOUT_SECONDS = 300

# Thresholds and Alerts
CPU_THRESHOLD = 85.0  # percentage
MEMORY_THRESHOLD = 80.0  # percentage
P99_LATENCY_THRESHOLD = 5000  # milliseconds
ERROR_RATE_THRESHOLD = 5.0  # percentage

# Vector DB / RAG
FAQ_KB_PATH = "mock_data/faq_kb.json"
EMBEDDING_MODEL = "text-embedding-3-small"

# Incident Severity Levels
SEVERITY_LEVELS = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}

# Output paths
RCA_REPORT_PATH = "output/rca_report.md"
CHAIN_OF_THOUGHT_PATH = "output/chain_of_thought.json"
