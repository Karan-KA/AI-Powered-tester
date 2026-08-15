import json
import re
from typing import Any, Dict, List

import requests

from app.core.config import get_llm_config


class LLMUnavailable(Exception):
    pass


def _clean_output(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    if "</think>" in text.lower():
        text = re.split(r"</think>", text, flags=re.IGNORECASE)[-1]
    if "<think>" in text.lower():
        text = re.split(r"<think>", text, flags=re.IGNORECASE)[0]
    text = re.sub(r"^\s*(final answer|answer)\s*:\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def chat(
    messages: List[Dict[str, str]],
    *,
    json_mode: bool = False,
    num_predict: int = 700,
    timeout: int = None,
) -> str:
    config = get_llm_config()
    payload: Dict[str, Any] = {
        "model": config["model"],
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {"temperature": 0.1, "num_predict": num_predict},
    }
    if json_mode:
        payload["format"] = "json"

    try:
        response = requests.post(
            f"{config['base_url'].rstrip('/')}/api/chat",
            json=payload,
            timeout=timeout or config["timeout"],
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMUnavailable(str(exc)) from exc

    content = (response.json().get("message", {}).get("content") or "").strip()
    if not content:
        raise LLMUnavailable("Ollama returned an empty answer.")
    return _clean_output(content)


def chat_json(system: str, user: str, *, num_predict: int = 700, timeout: int = None) -> dict:
    text = chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        json_mode=True,
        num_predict=num_predict,
        timeout=timeout,
    )
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise ValueError("LLM did not return JSON.")
        return json.loads(match.group(0))


def llm_status() -> dict:
    config = get_llm_config()
    try:
        response = requests.get(f"{config['base_url'].rstrip('/')}/api/tags", timeout=3)
        response.raise_for_status()
        models = [model.get("name") for model in response.json().get("models", [])]
        return {
            "available": True,
            "provider": "ollama",
            "model": config["model"],
            "model_installed": config["model"] in models,
        }
    except requests.RequestException as exc:
        return {"available": False, "provider": "ollama", "model": config["model"], "error": str(exc)}
