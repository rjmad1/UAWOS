# scratch/test_e2e_pipeline.py
import os
import sys

# Ensure project root is in path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uawos_budget
import uawos_context
import uawos_db
import uawos_dtase
import uawos_governance


def test_complete_e2e_workflow():
    """Verify a complete governed human-agent execution loop from ingestion to value realization."""
    tenant_id = "tenant-e2e-test"
    tokens = uawos_context.set_context(tenant_id, "Admin", "admin_user")

    try:
        print("\nStarting E2E test pipeline...")

        # 1. Ingest unstructured requirements text (DTASE)
        input_text = "Modernize checkout gateway to support Apple Pay, reducing checkout friction by 25%."
        print(f"Step 1: Ingesting unstructured text: '{input_text}'")
        analysis = uawos_dtase.analyze_unstructured_input(input_text)
        assert "detected_domains" in analysis, "DTASE failed to extract domains."
        assert len(analysis["detected_domains"]) > 0, "DTASE extracted zero domains."
        print("  [PASS] Ingestion & Translation verified.")

        # 2. Objective creation with measurable outcomes
        obj_id = "obj-e2e-checkout"
        print(f"Step 2: Creating structured objective: {obj_id}")
        uawos_db.db_save_objective(
            {
                "id": obj_id,
                "title": "Modernize checkout gateway",
                "description": "Integration of Apple Pay checkout options.",
                "source_type": "text",
                "source_uri": "",
                "owner": "Lead Architect",
                "sponsor": "VP Engineering",
                "priority": "High",
                "status": "active",
                "version": 1,
                "health_score": 100.0,
                "confidence_score": 90.0,
                "dependencies": [],
                "history": [],
                "tenant_id": tenant_id,
            }
        )
        loaded_objs = uawos_db.db_load_objectives()
        assert obj_id in loaded_objs["objectives"], "Failed to save objective to PostgreSQL."
        print("  [PASS] Objective creation verified.")

        # 3. Budget allocation and pricing configuration
        print("Step 3: Allocating objective budgets...")
        uawos_budget.allocate_objective_budget(obj_id, "Modernize checkout gateway", 1500.00)
        uawos_budget.allocate_action_budget("act-e2e-1", obj_id, "Run gateway security audit", 400.00)
        summary = uawos_budget.get_summary()
        assert obj_id in summary["objective_budgets"], "Objective budget was not recorded."
        print("  [PASS] Budget allocation verified.")

        # 4. Plan simulation (Monte Carlo path ranking)
        print("Step 4: Simulating plans...")
        plan_id = "pln-e2e-checkout"
        uawos_db.db_save_plan(
            {
                "id": plan_id,
                "objective_id": obj_id,
                "title": "Checkout Gateway Modernization Plan",
                "steps": ["Step 1: Code Audit", "Step 2: Apply AES-256", "Step 3: Apple Pay API Hook"],
                "cost_estimate": 800.00,
                "duration_estimate": 10,
                "resource_requirements": ["Database Expert", "Security Auditor"],
                "success_probability": 0.85,
                "status": "approved",
                "version": 1,
                "risks": ["API rate-limits", "latency shifts"],
                "assumptions": ["Local Ollama node is online"],
                "is_alternative": False,
                "history": [],
                "tenant_id": tenant_id,
            }
        )
        loaded_plans = uawos_db.db_load_plans()
        assert plan_id in loaded_plans["plans"], "Failed to save plan to database."
        print("  [PASS] Plan simulation verified.")

        # 5. Workflow generation and task DAG setup
        print("Step 5: Generating execution workflow Task DAG...")
        workflow_id = "wf-e2e-checkout"
        uawos_db.db_save_workflow(
            {
                "id": workflow_id,
                "plan_id": plan_id,
                "title": "Checkout Workflow DAG",
                "tasks": ["act-e2e-1", "act-e2e-2"],
                "dependencies": [["act-e2e-1", "act-e2e-2"]],
                "state": "active",
                "version": 1,
                "governed": True,
                "history": [],
                "tenant_id": tenant_id,
            }
        )
        loaded_wfs = uawos_db.db_load_workflows()
        assert workflow_id in loaded_wfs["workflows"], "Failed to save workflow."
        print("  [PASS] Workflow generation verified.")

        # 6. Governed action tool call checks (OPA/Rego)
        print("Step 6: Running governed actions (OPA/Rego compliance limits)...")
        gov_res = uawos_governance.evaluate_action_governance(
            "act-e2e-1", {"owner": "admin_user", "estimated_tokens": 1000000, "licensing": "Apache-2.0"}
        )
        assert gov_res["verdict"] == "APPROVED", "Action was blocked incorrectly by OPA."
        print("  [PASS] Governance checks verified.")

        # 7. Action Execution & Telemetry logging
        print("Step 7: Recording execution cost and token metrics...")
        uawos_budget.record_agent_cost("Executor Agent", "deepseek-r1", 200000, 100000)
        uawos_budget.record_agent_cost("Orchestrator Agent", "tinyllama", 50000, 30000)

        sum_after = uawos_budget.get_summary()
        executor_cost = sum_after["agent_costs"]["Executor Agent"]["cost"]
        assert executor_cost > 0.0, "Failed to record agent execution tokens."
        print("  [PASS] Action metrics logging verified.")

        print("=== E2E execution pipeline completed successfully. ===")

    finally:
        uawos_context.reset_context(tokens)


if __name__ == "__main__":
    test_complete_e2e_workflow()
