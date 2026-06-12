# uawos_weaverouter.py
import json
import os
import urllib.error
import urllib.request
import uawos_budget

WEAVEROUTER_BASE_URL = os.environ.get("WEAVEROUTER_BASE_URL", "http://127.0.0.1:8092")
WEAVEROUTER_API_KEY = os.environ.get("WEAVEROUTER_API_KEY", "rk_uawos_dev_key")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")


def uawos_generate_response(
    prompt: str,
    model: str = "tinyllama",
    stream: bool = False,
    format: str = None,
    agent_name: str = "Weaverouter Proxy",
) -> str:
    """Unified LLM generation gateway that queries Weaverouter with automatic Ollama fallback."""
    # 1. Attempt to query Weaverouter
    try:
        url = f"{WEAVEROUTER_BASE_URL}/v1/chat/completions"
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        
        if format == "json":
            payload["response_format"] = {"type": "json_object"}
            
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {WEAVEROUTER_API_KEY}"
            }
        )
        
        # Weave Router should respond quickly
        with urllib.request.urlopen(req, timeout=5.0) as response:
            resp_body = response.read().decode("utf-8")
            resp_json = json.loads(resp_body)
            
            content = resp_json["choices"][0]["message"]["content"]
            
            # Extract token usage and update UAWOS budget ledger
            usage = resp_json.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            if prompt_tokens > 0 or completion_tokens > 0:
                try:
                    uawos_budget.record_agent_cost(
                        agent_name=agent_name,
                        model_name=model,
                        input_tokens=prompt_tokens,
                        output_tokens=completion_tokens,
                    )
                except Exception as e:
                    print(f"[Weaverouter Warning] Failed to log budget cost: {e}")
                    
            return content

    except Exception as wr_err:
        print(f"[Weaverouter Fallback Active] Routing failed via Weaverouter: {wr_err}. falling back to local Ollama...")
        
        # 2. Fallback to local Ollama
        try:
            url = f"{OLLAMA_BASE_URL}/api/generate"
            ollama_payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
            }
            if format == "json":
                ollama_payload["format"] = "json"
                
            req_data = json.dumps(ollama_payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=10.0) as response:
                resp_body = response.read().decode("utf-8")
                resp_json = json.loads(resp_body)
                
                content = resp_json.get("response", "")
                
                # Extract Ollama usage stats and update budget ledger
                prompt_tokens = resp_json.get("prompt_eval_count", 0)
                completion_tokens = resp_json.get("eval_count", 0)
                
                if prompt_tokens > 0 or completion_tokens > 0:
                    try:
                        uawos_budget.record_agent_cost(
                            agent_name=agent_name,
                            model_name=model,
                            input_tokens=prompt_tokens,
                            output_tokens=completion_tokens,
                        )
                    except Exception as e:
                        print(f"[Weaverouter Fallback Warning] Failed to log budget cost: {e}")
                        
                return content
                
        except Exception as ollama_err:
            print(f"[Weaverouter Error] Fallback to Ollama also failed: {ollama_err}")
            raise ollama_err
