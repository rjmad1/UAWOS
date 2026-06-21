# tests/unit/test_weaverouter.py
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import uawos_weaverouter
import uawos_observability


def test_weaverouter_nvidia_missing_key(monkeypatch):
    """Verify that if NVIDIA_NIM_API_KEY is not set, a warning is logged, telemetry emitted, and fallback occurs."""
    monkeypatch.delenv("NVIDIA_NIM_API_KEY", raising=False)

    # Mock urllib.request.urlopen to return an Ollama fallback response
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"response": "Fallback Ollama response", "prompt_eval_count": 5, "eval_count": 10}'
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        res = uawos_weaverouter.uawos_generate_response(
            prompt="Test prompt",
            provider="nvidia",
            model="tinyllama"
        )

        assert res == "Fallback Ollama response"
        assert mock_urlopen.call_count >= 1

        # Verify telemetry was emitted in observability state
        state = uawos_observability.load_state(
            state_file=uawos_observability.STATE_FILE,
            default_state_func=uawos_observability.get_default_state
        )
        events = [e for e in state["telemetry_events"] if e["name"] == "gateway_fallback"]
        assert len(events) >= 1
        assert events[-1]["details"]["provider"] == "nvidia"
        assert "API key is missing or empty" in events[-1]["details"]["error"]


def test_weaverouter_openrouter_missing_key(monkeypatch):
    """Verify that if OPENROUTER_API_KEY is not set, a warning is logged, telemetry emitted, and fallback occurs."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    # Mock urllib.request.urlopen to return an Ollama fallback response
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"response": "Fallback Ollama response 2", "prompt_eval_count": 2, "eval_count": 3}'
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        res = uawos_weaverouter.uawos_generate_response(
            prompt="Test prompt",
            provider="openrouter",
            model="tinyllama"
        )

        assert res == "Fallback Ollama response 2"
        assert mock_urlopen.call_count >= 1

        state = uawos_observability.load_state(
            state_file=uawos_observability.STATE_FILE,
            default_state_func=uawos_observability.get_default_state
        )
        events = [e for e in state["telemetry_events"] if e["name"] == "gateway_fallback"]
        assert len(events) >= 1
        assert events[-1]["details"]["provider"] == "openrouter"
        assert "API key is missing or empty" in events[-1]["details"]["error"]


def test_weaverouter_nvidia_success():
    """Verify successful response path from simulated NVIDIA NIM API."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"choices": [{"message": {"content": "NVIDIA success response"}}]}'
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        res = uawos_weaverouter.uawos_generate_response(
            prompt="Test prompt",
            provider="nvidia",
            api_key="mock_key",
            model="meta/llama3-70b-instruct"
        )

        assert res == "NVIDIA success response"
        assert mock_urlopen.call_count == 1


def test_weaverouter_openrouter_success():
    """Verify successful response path from simulated OpenRouter API."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"choices": [{"message": {"content": "OpenRouter success response"}}]}'
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
        res = uawos_weaverouter.uawos_generate_response(
            prompt="Test prompt",
            provider="openrouter",
            api_key="mock_key",
            model="meta-llama/llama-3-70b-instruct:free"
        )

        assert res == "OpenRouter success response"
        assert mock_urlopen.call_count == 1


def test_weaverouter_default_fallback_to_ollama():
    """Verify that if default Weaverouter gateway fails, it falls back to local Ollama."""
    mock_ollama_success = MagicMock()
    mock_ollama_success.read.return_value = b'{"response": "Ollama success", "prompt_eval_count": 1, "eval_count": 2}'
    mock_ollama_success.__enter__.return_value = mock_ollama_success

    def urlopen_side_effect(req, *args, **kwargs):
        # If calling local Weaverouter, fail
        if "127.0.0.1:8092" in req.full_url:
            raise Exception("Weaverouter connection failed")
        # If calling Ollama, succeed
        elif "127.0.0.1:11434" in req.full_url:
            return mock_ollama_success
        raise Exception(f"Unexpected url: {req.full_url}")

    with patch("urllib.request.urlopen", side_effect=urlopen_side_effect) as mock_urlopen:
        res = uawos_weaverouter.uawos_generate_response(
            prompt="Test prompt",
            provider=None
        )
        assert res == "Ollama success"
