# UAWOS - Python Script Provider for Promptfoo Evaluations
# This script runs offline and simulates LLM responses based on prompt ID and variables.

def call_api(prompt, options, context):
    prompt_id = context.get('prompt', {}).get('id', '')
    prompt_raw = prompt.lower()
    
    if "coder" in prompt_id or "coding" in prompt_raw:
        task = context.get('vars', {}).get('task', '')
        return {
            "output": f"Mock Coder Response: Here is the Python implementation for the task: '{task}'."
        }
    elif "planner" in prompt_id or "plan" in prompt_raw:
        objective = context.get('vars', {}).get('objective', '')
        return {
            "output": f"Mock Planner Response: Here is the step-by-step plan to achieve: '{objective}'."
        }
    elif "researcher" in prompt_id or "research" in prompt_raw:
        topic = context.get('vars', {}).get('topic', '')
        return {
            "output": f"Mock Researcher Response: Detailed research on '{topic}' covering Zero Trust security principles."
        }
    elif "reviewer" in prompt_id or "review" in prompt_raw:
        code = context.get('vars', {}).get('code', '')
        return {
            "output": f"Mock Reviewer Response: Warning: The code '{code}' contains security vulnerabilities (e.g. command injection)."
        }
    elif "system" in prompt_id or "uawos" in prompt_raw:
        return {
            "output": "Mock System Response: UAWOS Core Coordinator initialized and ready."
        }
    else:
        return {
            "output": "Mock Default Response."
        }
