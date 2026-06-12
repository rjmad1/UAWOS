# scratch/test_weaverouter_fallback.py
import sys
sys.path.append('.')

import uawos_dtase
import uawos_budget

print("1. Running DTASE unstructured input ingestion...")
text = "OBJ-101: The system is experiencing high latency on checkout. We need to optimize the database queries."
res = uawos_dtase.analyze_unstructured_input(text)

print("\n2. DTASE Analysis Output:")
print(f"Title: {res.get('title')}")
print(f"Priority: {res.get('priority')}")
print(f"Detected Domains: {res.get('detected_domains')}")
print(f"Traceability Score: {res.get('traceability', {}).get('confidence_score')}")

print("\n3. Budget Ledger Summary (verifying token logging):")
summary = uawos_budget.get_summary()
print("Agent Costs recorded:")
for agent, cost_info in summary.get("agent_costs", {}).items():
    print(f"  {agent}: {cost_info}")

print("\nIntegration test complete!")
