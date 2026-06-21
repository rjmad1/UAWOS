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
    provider: str = None,
    api_key: str = None,
    api_url: str = None,
) -> str:
    """Unified LLM generation gateway that queries Weaverouter, NVIDIA NIM, or OpenRouter with automatic Ollama fallback."""
    # If provider is nvidia or openrouter, route accordingly
    if provider == "nvidia":
        try:
            url = api_url if api_url else "https://integrate.api.nvidia.com/v1/chat/completions"
            key = api_key if api_key else os.environ.get("NVIDIA_NIM_API_KEY", "")
            if not key:
                raise ValueError("NVIDIA NIM API key is missing or empty.")

            target_model = model if model and model != "tinyllama" else "meta/llama3-70b-instruct"

            payload = {
                "model": target_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": stream,
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, data=req_data, headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
            )
            with urllib.request.urlopen(req, timeout=10.0) as response:
                resp_body = response.read().decode("utf-8")
                resp_json = json.loads(resp_body)
                content = resp_json["choices"][0]["message"]["content"]
                return content
        except Exception as e:
            import sys

            print(
                f"[NVIDIA NIM Gateway Error] Failed to route request: {e}. Falling back to Ollama...", file=sys.stderr
            )
            try:
                import uawos_observability

                uawos_observability.emit_telemetry(
                    "gateway_fallback", {"provider": "nvidia", "error": str(e), "model": model}
                )
            except Exception:
                pass
            # Fallback to local Ollama directly
            provider = None

    elif provider == "openrouter":
        try:
            url = api_url if api_url else "https://openrouter.ai/api/v1/chat/completions"
            key = api_key if api_key else os.environ.get("OPENROUTER_API_KEY", "")
            if not key:
                raise ValueError("OpenRouter API key is missing or empty.")

            target_model = model if model and model != "tinyllama" else "meta-llama/llama-3-70b-instruct:free"

            payload = {
                "model": target_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": stream,
            }
            req_data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {key}",
                    "HTTP-Referer": "http://localhost:8099",
                    "X-Title": "UAWOS Meeting Hub",
                },
            )
            with urllib.request.urlopen(req, timeout=10.0) as response:
                resp_body = response.read().decode("utf-8")
                resp_json = json.loads(resp_body)
                content = resp_json["choices"][0]["message"]["content"]
                return content
        except Exception as e:
            import sys

            print(
                f"[OpenRouter Gateway Error] Failed to route request: {e}. Falling back to Ollama...", file=sys.stderr
            )
            try:
                import uawos_observability

                uawos_observability.emit_telemetry(
                    "gateway_fallback", {"provider": "openrouter", "error": str(e), "model": model}
                )
            except Exception:
                pass
            # Fallback to local Ollama directly
            provider = None

    # Fallback / Default: Attempt to query Weaverouter first, then Ollama
    if not provider:
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
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {WEAVEROUTER_API_KEY}"},
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
            print(
                f"[Weaverouter Fallback Active] Routing failed via Weaverouter: {wr_err}. falling back to local Ollama..."
            )

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
                req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})

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
