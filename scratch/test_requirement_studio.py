# scratch/test_requirement_studio.py
import urllib.request
import json
import sys

URL_BASE = "http://127.0.0.1:8099"

def post_json(path, data):
    req_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(
        f"{URL_BASE}{path}",
        data=req_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5.0) as response:
        return json.loads(response.read().decode('utf-8'))

def get_json(path):
    req = urllib.request.Request(f"{URL_BASE}{path}")
    with urllib.request.urlopen(req, timeout=5.0) as response:
        return json.loads(response.read().decode('utf-8'))

def verify_end_to_end():
    print("Starting Requirement Intelligence Studio end-to-end API tests...")
    
    # 1. Reset state
    print("  Resetting studio state...")
    reset_res = post_json("/api/requirement/reset", {})
    assert reset_res.get("status") == "SUCCESS", "Reset failed."
    
    # 2. Submit new requirement
    print("  Submitting SSO requirement...")
    req_body = {
        "title": "Enterprise SSO Integration",
        "text": "Add multi-tenant SSO support to the enterprise control plane to solve the security vulnerability problem. Scope includes SAML and OIDC protocol interfaces, and excludes legacy LDAP protocols. Success metrics: user sign-in latency under 100ms. Business constraints: must deploy within the next 3 weeks with a budget of $5000. Technical constraints: must integrate with our Postgres database."
    }
    submit_res = post_json("/api/requirement/submit", req_body)
    req_id = submit_res.get("requirement_id")
    print(f"    Created requirement: {req_id}")
    assert req_id == "REQ-001", f"Unexpected requirement ID: {req_id}"
    assert submit_res["completeness_score"] == 100, f"Expected 100% completeness, got: {submit_res['completeness_score']}"
    assert len(submit_res["clarification_questions"]) == 10, "Should generate exactly 10 questions."
    
    # 3. Complete clarifications (waive them)
    print("  Applying CPO executive waiver on questions...")
    clarify_res = post_json("/api/requirement/clarify", {
        "requirement_id": req_id,
        "answers": {},
        "waive": True
    })
    assert clarify_res["readiness_score"] >= 85, "Readiness score should be boosted after waiver."
    
    # 4. Author strategic product proposition
    print("  Compiling authored strategic proposition (A to Q)...")
    author_res = post_json("/api/requirement/author", {"requirement_id": req_id})
    assert "A_Executive_Summary" in author_res, "Strategic proposition missing Section A."
    assert "Q_Future_Enhancements" in author_res, "Strategic proposition missing Section Q."
    print("    Proposition sections A to Q successfully compiled.")
    
    # 5. Absorb and prioritize
    print("  Absorbing requirement candidate...")
    absorb_res = post_json("/api/requirement/absorb", {"requirement_id": req_id})
    
    # Validate the complete Output Contract
    contract_keys = [
        "requirement_analysis",
        "completeness_score",
        "alignment_score",
        "clarification_questions",
        "product_proposition",
        "roadmap_candidate",
        "portfolio_comparison",
        "sequencing_changes",
        "dependency_changes",
        "roadmap_absorption_result",
        "executive_recommendation"
    ]
    for key in contract_keys:
        assert key in absorb_res, f"Output contract missing key: {key}"
        
    cand = absorb_res["roadmap_candidate"]
    assert cand["roadmap_id"] == "RD-05", f"Expected candidate RD-05, got {cand['roadmap_id']}"
    assert cand["priority_score"] > 0, "Candidate priority score must be > 0."
    assert absorb_res["portfolio_comparison"]["new_rank"] > 0, "Should receive portfolio rank placement."
    
    print(f"    Candidate generated: {cand['roadmap_id']} with Priority Score: {cand['priority_score']} at Rank: {absorb_res['portfolio_comparison']['new_rank']}")
    
    # 6. Publish Candidate
    print("  Publishing candidate to active roadmap...")
    publish_res = post_json("/api/requirement/publish", {"roadmap_id": "RD-05"})
    assert publish_res["status"] == "PUBLISHED", "Roadmap item publication failed."
    
    # 7. Verify in master roadmap API
    print("  Verifying candidate presence in master roadmap...")
    roadmap_data = get_json("/api/roadmap")
    assert "RD-05" in roadmap_data, "Published candidate RD-05 missing from roadmap rollup data."
    assert roadmap_data["RD-05"]["name"] == "Enterprise SSO Integration", "Roadmap name mismatch."
    
    # 8. Verify child requirements in traceability matrix
    print("  Verifying child requirements trace in matrix...")
    trace_data = get_json("/api/traceability")
    matrix = trace_data["matrix"]
    
    # Child ID format: FR-REQ-001-001
    assert "FR-REQ-001-001" in matrix, "Child functional requirement missing from traceability matrix."
    assert matrix["FR-REQ-001-001"]["roadmap_item"] == "RD-05", "Child requirement mapped to wrong roadmap item."
    
    print("All verification steps passed successfully! End-to-end API compliance confirmed.")

if __name__ == "__main__":
    try:
        verify_end_to_end()
    except Exception as e:
        print(f"[FAIL] Verification failed: {e}", file=sys.stderr)
        sys.exit(1)
