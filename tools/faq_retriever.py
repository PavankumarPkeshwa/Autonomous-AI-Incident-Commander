"""
Tool for retrieving FAQ-based knowledge and performing simple RAG over KB.
"""
import json
from typing import List, Dict, Any


def load_faq_kb() -> List[Dict[str, Any]]:
    """Load FAQ knowledge base from JSON file."""
    try:
        with open("mock_data/faq_kb.json", "r") as f:
            return json.load(f).get("faq", [])
    except Exception as e:
        return [{"error": f"Failed to load FAQ KB: {str(e)}"}]


def keyword_match(query: str, faq_item: Dict[str, Any], threshold: int = 1) -> bool:
    """
    Simple keyword matching for FAQ retrieval.
    Checks if query contains keywords from FAQ item.
    """
    query_lower = query.lower()
    keywords = faq_item.get("keywords", [])
    
    matches = sum(1 for kw in keywords if kw.lower() in query_lower)
    return matches >= threshold


def search_faq(query: str) -> str:
    """
    Search FAQ knowledge base for relevant solutions.
    Uses keyword matching and simple semantic similarity.
    
    Args:
        query: Question or symptom to search for
    
    Returns:
        JSON string with matching FAQ entries and solutions
    """
    kb = load_faq_kb()
    results = []
    
    query_lower = query.lower()
    
    for faq in kb:
        # Check question match
        if query_lower in faq.get("question", "").lower():
            results.append(faq)
            continue
        
        # Check keyword match
        if keyword_match(query, faq, threshold=1):
            results.append(faq)
    
    return json.dumps({
        "query": query,
        "results": results,
        "count": len(results),
        "solutions": [r.get("solution") for r in results] if results else []
    }, indent=2)


def get_solution_for_symptom(symptom: str) -> str:
    """
    Quick lookup for a specific symptom in FAQ KB.
    
    Args:
        symptom: Incident symptom or error message
    
    Returns:
        JSON string with recommended solutions
    """
    kb = load_faq_kb()
    
    symptom_lower = symptom.lower()
    matches = []
    
    for faq in kb:
        if any(kw.lower() in symptom_lower for kw in faq.get("keywords", [])):
            matches.append({
                "id": faq.get("id"),
                "question": faq.get("question"),
                "solution": faq.get("solution"),
                "severity": faq.get("severity")
            })
    
    return json.dumps({
        "symptom": symptom,
        "matches": matches,
        "count": len(matches)
    }, indent=2)


def get_faq_by_severity(severity: str) -> str:
    """
    Retrieve all FAQ entries for a given severity level.
    
    Args:
        severity: Severity level (critical, high, medium, low)
    
    Returns:
        JSON string with FAQ entries
    """
    kb = load_faq_kb()
    filtered = [faq for faq in kb if faq.get("severity", "").lower() == severity.lower()]
    
    return json.dumps({
        "severity": severity,
        "entries": filtered,
        "count": len(filtered)
    }, indent=2)
