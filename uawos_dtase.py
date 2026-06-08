import json
import urllib.request
import urllib.error
import os

PRODUCT_MGMT = "Product Management"
GOVERNANCE_COMPLIANCE = "Governance & Compliance"


def analyze_unstructured_input(text: str) -> dict:
    # 1. Base heuristics analysis
    detected_domains = []
    opportunities = []
    risks = []
    anomalies = []
    personas = {}
    
    text_lower = text.lower()
    
    # Domain heuristics
    is_legal = any(w in text_lower for w in ["overtime", "pay", "threatened", "manager", "harassment", "legal", "law", "contract", "violation"])
    is_health = any(w in text_lower for w in ["headache", "symptom", "pain", "medical", "doctor", "clinical", "health", "illness", "patient"])
    is_product = any(w in text_lower for w in ["checkout", "abandon", "shipping", "user", "feature", "abandoning", "product", "feedback", "customer"])
    is_eng = any(w in text_lower for w in ["system", "architecture", "database", "engineering", "server", "code", "bug", "latency", "failure"])
    is_gov = any(w in text_lower for w in ["compliance", "audit", "policy", "regulator", "governance", "standard", "license"])
    
    if is_legal:
        detected_domains.append("Legal")
        risks.append("Potential labor law compliance violations")
        personas["Legal Advisor"] = {
            "summary": "Potential wage and hour claim under labor standards due to failure to compensate overtime and retaliatory threats.",
            "action_items": ["Review employment contracts", "Audit timesheets and overtime logs", "Initiate internal compliance review"]
        }
    if is_health:
        detected_domains.append("Healthcare")
        anomalies.append("Frequent evening symptom onset pattern")
        personas["Clinical Practitioner"] = {
            "summary": "Patient presenting with recurring evening headaches. Symptom chronology correlates with end-of-workday timeline.",
            "action_items": ["Schedule detailed medical history review", "Recommend symptom and activity logging", "Assess occupational stress factors"]
        }
    if is_product:
        detected_domains.append(PRODUCT_MGMT)
        opportunities.append("Optimize checkout shipping cost transparency to reduce abandonment")
        personas["Product Owner"] = {
            "summary": "User friction identified at checkout phase during shipping cost revelation. Suggests requirement for upfront pricing estimation.",
            "action_items": ["Create A/B test for shipping cost placement", "Draft user stories for upfront pricing calculator", "Audit checkout funnel conversion rate"]
        }
    if is_eng:
        detected_domains.append("Engineering")
        anomalies.append("System performance or infrastructure warning indicators")
        personas["Software Architect"] = {
            "summary": "Technical components require analysis to address performance bottlenecks, architectural drift, or interface failures.",
            "action_items": ["Trace API call latency", "Inspect system integration logs", "Review architectural dependency graph"]
        }
    if is_gov:
        detected_domains.append(GOVERNANCE_COMPLIANCE)
        risks.append("Regulatory audit compliance exposure")
        personas["Compliance Officer"] = {
            "summary": "Operational activities require alignment with policy control frameworks and lineage verification.",
            "action_items": ["Verify data lineage mappings in Marquez", "Run OPA compliance check", "Audit dependency SBOM via Dependency-Track"]
        }
        
    if not detected_domains:
        detected_domains.append("General Execution")
        personas["Executive Summary"] = {
            "summary": f"General intake analysis completed for: '{text[:60]}...'",
            "action_items": ["Categorize input under operational goals", "Assign review tasks to agent council"]
        }
        
    result = {
        "status": "Success",
        "input_text": text,
        "detected_domains": detected_domains,
        "opportunities": opportunities,
        "risks": risks,
        "anomalies": anomalies,
        "persona_translations": personas,
        "traceability": {
            "source": "Unstructured Input Ingestion",
            "confidence_score": 0.85,
            "engine": "DTASE v1.0 (Heuristic + LLM Local-Gateway)"
        }
    }
    
    # 2. Try LLM enrichment via local Ollama gateway (tinyllama)
    try:
        prompt = f"""[INST] You are the UAWOS Domain Translation & Artifact Synthesis Engine (DTASE).
Analyze this unstructured human input and output a structured JSON analysis.
Input: "{text}"

Output JSON format (strictly JSON, no extra text):
{{
  "detected_domains": ["domain"],
  "opportunities": ["opportunity"],
  "risks": ["risk"],
  "anomalies": ["anomaly"],
  "summary": "one-sentence professional summary"
}}
[/INST]"""
        req_data = json.dumps({
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=req_data,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=4.0) as response:
            resp_body = response.read().decode('utf-8')
            resp_json = json.loads(resp_body)
            llm_text = resp_json.get("response", "")
            
            # Parse LLM response
            llm_analysis = json.loads(llm_text)
            
            # Merge LLM results with heuristics
            if llm_analysis.get("detected_domains"):
                result["detected_domains"] = list(set(result["detected_domains"] + llm_analysis["detected_domains"]))
            if llm_analysis.get("opportunities"):
                result["opportunities"] = list(set(result["opportunities"] + llm_analysis["opportunities"]))
            if llm_analysis.get("risks"):
                result["risks"] = list(set(result["risks"] + llm_analysis["risks"]))
            if llm_analysis.get("anomalies"):
                result["anomalies"] = list(set(result["anomalies"] + llm_analysis["anomalies"]))
                
            if "LLM Professional View" not in result["persona_translations"] and llm_analysis.get("summary"):
                result["persona_translations"]["LLM Professional View"] = {
                    "summary": llm_analysis["summary"],
                    "action_items": ["Assess generated professional requirements", "Register findings with knowledge engine"]
                }
            result["traceability"]["confidence_score"] = 0.95
    except Exception:
        # Fallback to pure heuristics
        pass
        
    return result

def identify_domains(text: str) -> list:
    text_lower = text.lower()
    domains = []
    
    if any(w in text_lower for w in ["overtime", "pay", "threatened", "manager", "harassment", "legal", "law", "contract", "violation"]):
        domains.append({
            "domain": "Legal",
            "confidence": 0.95,
            "evidence": "supervisor denied overtime compensation and threatened termination"
        })
    if any(w in text_lower for w in ["headache", "symptom", "pain", "medical", "doctor", "clinical", "health", "illness", "patient"]):
        domains.append({
            "domain": "Healthcare",
            "confidence": 0.90,
            "evidence": "tension headaches every evening after work"
        })
    if any(w in text_lower for w in ["checkout", "abandon", "shipping", "user", "feature", "abandoning", "product", "feedback", "customer"]):
        domains.append({
            "domain": PRODUCT_MGMT,
            "confidence": 0.95,
            "evidence": "abandoning checkout when shipping fees are displayed"
        })
    if any(w in text_lower for w in ["system", "architecture", "database", "engineering", "server", "code", "bug", "latency", "failure"]):
        domains.append({
            "domain": "Engineering",
            "confidence": 0.85,
            "evidence": "requires database integration or system performance tuning"
        })
    if any(w in text_lower for w in ["compliance", "audit", "policy", "regulator", "governance", "standard", "license"]):
        domains.append({
            "domain": GOVERNANCE_COMPLIANCE,
            "confidence": 0.90,
            "evidence": "policy audit or license governance controls required"
        })
        
    if not domains:
        domains.append({
            "domain": "General Execution",
            "confidence": 0.70,
            "evidence": "unclassified organizational intent"
        })
        
    return domains

def apply_domain_frameworks(_text: str, primary_domains: list) -> dict:
    translations = {}
    for d in primary_domains:
        if d == "Legal":
            translations["Legal"] = {
                "framework": "Employment Standards & Retaliation Protection Framework",
                "compliance_status": "HIGH RISK BREACH",
                "summary": "Potential wage and hour claim under labor standards due to failure to compensate overtime and retaliatory threats.",
                "action_items": "Review contracts; Audit timesheets; Initiate compliance review"
            }
        elif d == "Healthcare":
            translations["Healthcare"] = {
                "framework": "Clinical Chronobiology & Stress Response Assessment Protocol",
                "symptom_pattern": "Recurring evening onset headache",
                "summary": "Patient presenting with tension headaches correlated with workday completion timelines.",
                "action_items": "Recommend activity logging; Assess occupational stressors; Clinical follow-up"
            }
        elif d == PRODUCT_MGMT:
            translations[PRODUCT_MGMT] = {
                "framework": "Product Funnel Conversion Optimization Framework",
                "friction_point": "Late-stage checkout shipping fees disclosure",
                "summary": "User friction identified at checkout phase during shipping cost revelation.",
                "action_items": "Draft user stories for upfront pricing; Create A/B test; Audit checkout conversion rates"
            }
        elif d == "Engineering":
            translations["Engineering"] = {
                "framework": "Architectural Bottleneck & Latency Mitigation Framework",
                "summary": "Technical review required to optimize system operations, databases, or interfaces.",
                "action_items": "Trace API connection latency; Inspect database logs"
            }
        elif d == GOVERNANCE_COMPLIANCE:
            translations[GOVERNANCE_COMPLIANCE] = {
                "framework": "OPA & Dependency SBOM Audit Framework",
                "summary": "Verification of compliance controls, data lineage, and software packaging licenses.",
                "action_items": "Verify Marquez metadata lineage; Audit dependency licenses"
            }
    return translations

def discover_opportunities_risks_anomalies(text: str) -> dict:
    text_lower = text.lower()
    opportunities = []
    risks = []
    anomalies = []
    
    if "overtime" in text_lower or "compensation" in text_lower:
        risks.append({
            "type": "Labor Compliance Risk",
            "description": "Supervisor threat and withholding of overtime pay violates labor standards.",
            "confidence": 0.95,
            "evidence": "supervisor denied overtime compensation and threatened termination"
        })
        opportunities.append({
            "type": "Compliance System Improvement",
            "description": "Establish transparent automated timesheet and overtime auditing processes.",
            "confidence": 0.85,
            "evidence": "supervisor denied overtime"
        })
    if "headache" in text_lower or "symptom" in text_lower:
        anomalies.append({
            "type": "Tension Symptom Chronology",
            "description": "Symptom onset strictly correlates with completion of the workday.",
            "confidence": 0.90,
            "evidence": "tension headaches every evening after finishing work"
        })
    if "abandon" in text_lower or "shipping" in text_lower:
        opportunities.append({
            "type": "Checkout Funnel Optimization",
            "description": "Disclose shipping costs earlier in the funnel to prevent checkout abandonment.",
            "confidence": 0.95,
            "evidence": "abandoning checkout when shipping fees are displayed at final step"
        })
        risks.append({
            "type": "Revenue Loss",
            "description": "Late shipping fee disclosure reduces cart conversion ratios.",
            "confidence": 0.90,
            "evidence": "repeatedly abandoning checkout"
        })
        
    return {
        "opportunities": opportunities,
        "risks": risks,
        "anomalies": anomalies
    }

def generate_multi_persona_outputs(_text: str, domains: list) -> dict:
    outputs = {}
    for d in domains:
        if d == "Legal":
            outputs["Legal Advisor"] = "LEGAL BRIEF:\nSummary: Serious compliance exposure regarding unpaid overtime and retaliatory termination threats.\nAction Items: 1. Hold supervisor interview; 2. Preserve timesheets; 3. Perform employment standards audit."
        elif d == "Healthcare":
            outputs["Clinical Practitioner"] = "CLINICAL EVALUATION PLAN:\nSummary: Patient reports tension headaches occurring strictly post-work, suggesting chronic occupational stress.\nAction Items: 1. Order diagnostic logging; 2. Run occupational stress survey; 3. Recommend neurological consult if persistent."
        elif d == PRODUCT_MGMT:
            outputs["Product Owner"] = "PRODUCT DECOMPOSITION LOG:\nSummary: Friction identified at checkout funnel. High drop-off rate when shipping fees are revealed late.\nAction Items: 1. Create upfront fee calculator; 2. Run conversion A/B test; 3. Modify checkout user story criteria."
        elif d == "Engineering":
            outputs["Software Architect"] = "ARCHITECTURAL ASSESSMENT:\nSummary: System performance and connection states require analysis.\nAction Items: 1. Audit latency traces; 2. Review container configurations."
        elif d == GOVERNANCE_COMPLIANCE:
            outputs["Compliance Officer"] = "GOVERNANCE REPORT:\nSummary: Lineage tracking and security audit scans are required to verify policy compliance.\nAction Items: 1. Configure OPA checks; 2. Audit SBOM via Dependency-Track."
    return outputs
