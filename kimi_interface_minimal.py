"""kimi_interface_minimal.py

Reusable, minimal Kimi (Moonshot) API interface.

Features
- Reads your API key from a local file (recommended) or env var.
- Chat-completions style call via requests.
- Robust retries (429/5xx) with exponential backoff.
- Optional on-disk caching keyed by request payload hash.
- Helpers for strict-JSON prompting and parsing.

Install
    pip install requests

Usage (quick)
    from kimi_interface_minimal import KimiClient

    client = KimiClient.from_key_file(
        key_file="kimi_key.txt",
        base_url="https://api.moonshot.cn/v1",
        model="moonshot-v1-8k",
    )

    msg = "Return STRICT JSON: {\"ok\": true}"
    text = client.chat_text([{"role": "user", "content": msg}])
    print(text)

    obj = client.chat_json([
        {"role": "system", "content": client.strict_json_system_prompt()},
        {"role": "user", "content": "Return JSON: {\"x\": 1}"},
    ])
    print(obj)

Notes
- If your Kimi deployment uses a different endpoint or response schema, adjust:
    - endpoint path in _chat_completions_url()
    - content extraction in _extract_content()
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


@dataclass
class KimiConfig:
    api_key: str
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "moonshot-v1-8k"
    timeout_s: int = 60
    max_retries: int = 6
    backoff_base_s: float = 0.8
    backoff_max_s: float = 20.0
    temperature: float = 0.1
    default_max_tokens: int = 512


class KimiClient:
    def __init__(self, cfg: KimiConfig, cache_dir: str | Path = ".kimi_cache"):
        self.cfg = cfg
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.cfg.api_key}",
                "Content-Type": "application/json",
            }
        )

    # -------------------------
    # Constructors
    # -------------------------
    @classmethod
    def from_key_file(
        cls,
        key_file: str | Path,
        *,
        base_url: str = "https://api.moonshot.cn/v1",
        model: str = "moonshot-v1-8k",
        cache_dir: str | Path = ".kimi_cache",
        timeout_s: int = 60,
    ) -> "KimiClient":
        api_key = Path(key_file).read_text(encoding="utf-8").strip()
        if not api_key:
            raise RuntimeError(f"Empty API key file: {key_file}")
        cfg = KimiConfig(api_key=api_key, base_url=base_url, model=model, timeout_s=timeout_s)
        return cls(cfg, cache_dir=cache_dir)

    @classmethod
    def from_env(
        cls,
        env_var: str = "KIMI_API_KEY",
        *,
        base_url: str = "https://api.moonshot.cn/v1",
        model: str = "moonshot-v1-8k",
        cache_dir: str | Path = ".kimi_cache",
        timeout_s: int = 60,
    ) -> "KimiClient":
        api_key = os.getenv(env_var, "").strip()
        if not api_key:
            raise RuntimeError(f"Missing environment variable: {env_var}")
        cfg = KimiConfig(api_key=api_key, base_url=base_url, model=model, timeout_s=timeout_s)
        return cls(cfg, cache_dir=cache_dir)

    # -------------------------
    # Endpoint + response helpers
    # -------------------------
    def _chat_completions_url(self) -> str:
        return f"{self.cfg.base_url.rstrip('/')}/chat/completions"

    @staticmethod
    def _extract_content(resp_json: Dict[str, Any]) -> str:
        # Typical Chat Completions schema: choices[0].message.content
        try:
            return resp_json["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Unexpected response schema: {resp_json.keys()}") from e

    # -------------------------
    # Caching
    # -------------------------
    @staticmethod
    def _payload_hash(payload: Dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _cache_path(self, payload_hash: str) -> Path:
        return self.cache_dir / f"{payload_hash}.json"

    # -------------------------
    # Core call
    # -------------------------
    def chat(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Low-level call. Returns the raw JSON response."""

        payload: Dict[str, Any] = {
            "model": self.cfg.model,
            "messages": messages,
            "temperature": self.cfg.temperature if temperature is None else temperature,
            "max_tokens": self.cfg.default_max_tokens if max_tokens is None else max_tokens,
        }
        if extra:
            payload.update(extra)

        h = self._payload_hash(payload)
        cpath = self._cache_path(h)

        if use_cache and cpath.exists():
            return json.loads(cpath.read_text(encoding="utf-8"))

        url = self._chat_completions_url()
        last_err: Optional[Exception] = None

        for attempt in range(self.cfg.max_retries):
            try:
                r = self.session.post(url, json=payload, timeout=self.cfg.timeout_s)

                # Retry on common transient conditions
                if r.status_code in (429, 500, 502, 503, 504):
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")

                r.raise_for_status()
                data = r.json()

                if use_cache:
                    cpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

                return data

            except Exception as e:
                last_err = e
                sleep_s = min(self.cfg.backoff_max_s, self.cfg.backoff_base_s * (2**attempt))
                time.sleep(sleep_s)

        raise RuntimeError(f"Kimi request failed after retries: {last_err}")

    # -------------------------
    # Convenience wrappers
    # -------------------------
    def chat_text(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        return self._extract_content(self.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache,
            extra=extra,
        ))

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_cache: bool = True,
        extra: Optional[Dict[str, Any]] = None,
        allow_code_fence_cleanup: bool = True,
    ) -> Any:
        """Calls chat_text() then parses strict JSON."""
        text = self.chat_text(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=use_cache,
            extra=extra,
        )

        cleaned = text.strip()
        if allow_code_fence_cleanup and cleaned.startswith("```"):
            # best-effort cleanup if the model violates instructions
            cleaned = cleaned.strip("`")
            # try to find first JSON bracket
            i_obj = cleaned.find("{")
            i_arr = cleaned.find("[")
            idxs = [i for i in (i_obj, i_arr) if i != -1]
            if idxs:
                cleaned = cleaned[min(idxs):]

        return json.loads(cleaned)

    # -------------------------
    # Prompt helpers
    # -------------------------
    @staticmethod
    def strict_json_system_prompt() -> str:
        return (
            "You are a data-extraction engine. "
            "Return STRICT JSON only. "
            "No prose. No markdown. No code fences. "
            "Use double quotes for all keys and strings. "
            "If unsure, use null."
        )


if __name__ == "__main__":
    # Smoke test (requires a valid key file)
    # 1) Create a file kimi_key.txt containing ONLY your API key.
    # 2) Run: python kimi_interface_minimal.py

    client = KimiClient.from_key_file("moonshot_api_key.txt")

    text = client.chat_text([
        {"role": "system", "content": client.strict_json_system_prompt()},
        {"role": "user", "content": "Return JSON: {\"ok\": true}"},
    ], max_tokens=64)

    print(text)
