"""
orchestra_call.py — single-shot API orchestra caller using urllib.

Token-aware: pick the right API per task; cache results when possible.
"""
import os
import json
import time
import sys
import urllib.request
import urllib.error
from typing import Optional


def _post_json(url: str, headers: dict, body: dict, timeout: int = 30) -> tuple[bool, dict]:
    """POST JSON, return (ok, parsed_response)."""
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return False, json.loads(e.read().decode("utf-8"))
        except Exception:
            return False, {"error": f"HTTP {e.code}"}
    except Exception as e:
        return False, {"error": f"{type(e).__name__}: {e}"}


def call(task: str, prompt: str, **kwargs) -> dict:
    """Call the right API for the task. Returns {api, latency_ms, ok, response/error}."""
    t0 = time.time()
    handler = _ROUTES.get(task, _groq)  # default to Groq (free, fast)
    if task == "reason":
        # Try Kimi first, fall back to Groq
        result = _kimi(prompt, **kwargs)
        if result is None or not result.get("ok"):
            result = _groq(prompt, **kwargs)
    elif task == "embed":
        result = _cloudflare_embed(prompt, **kwargs)
    elif task == "oracle":
        result = _jev_oracle(prompt, **kwargs)
    else:
        result = handler(prompt, **kwargs)
    result["latency_ms"] = int((time.time() - t0) * 1000)
    return result


def _groq(prompt: str, **kw) -> dict:
    if not os.environ.get("GROQ_TOKEN"):
        return {"api": "groq", "ok": False, "error": "no token"}
    ok, body = _post_json(
        "https://api.groq.com/openai/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['GROQ_TOKEN']}", "Content-Type": "application/json"},
        {"model": "openai/gpt-oss-120b",
         "messages": [{"role": "system", "content": "You are terse. Output exactly what was asked. No preamble."},
                     {"role": "user", "content": prompt}],
         "max_tokens": kw.get("max_tokens", 400),
         "temperature": kw.get("temperature", 0.7)},
    )
    if ok:
        return {"api": "groq", "ok": True, "response": body["choices"][0]["message"]["content"]}
    return {"api": "groq", "ok": False, "error": body.get("error", str(body))[:200]}


def _deepseek(prompt: str, **kw) -> dict:
    if not os.environ.get("DEEPSEEK_TOKEN"):
        return {"api": "deepseek", "ok": False, "error": "no token"}
    ok, body = _post_json(
        "https://api.deepseek.com/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['DEEPSEEK_TOKEN']}", "Content-Type": "application/json"},
        {"model": "deepseek-chat",
         "messages": [{"role": "user", "content": prompt}],
         "max_tokens": kw.get("max_tokens", 600)},
    )
    if ok:
        return {"api": "deepseek", "ok": True, "response": body["choices"][0]["message"]["content"]}
    return {"api": "deepseek", "ok": False, "error": str(body)[:200]}


def _zai(prompt: str, **kw) -> dict:
    if not os.environ.get("ZAI_TOKEN"):
        return {"api": "zai", "ok": False, "error": "no token"}
    ok, body = _post_json(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        {"Authorization": f"Bearer {os.environ['ZAI_TOKEN']}", "Content-Type": "application/json"},
        {"model": "glm-4.5-flash",
         "messages": [{"role": "user", "content": prompt}],
         "max_tokens": kw.get("max_tokens", 500)},
        timeout=45,
    )
    if ok:
        return {"api": "zai", "ok": True, "response": body["choices"][0]["message"]["content"]}
    return {"api": "zai", "ok": False, "error": str(body)[:200]}


def _kimi(prompt: str, **kw) -> Optional[dict]:
    if not os.environ.get("KIMI_TOKEN"):
        return None
    ok, body = _post_json(
        "https://api.moonshot.cn/v1/chat/completions",
        {"Authorization": f"Bearer {os.environ['KIMI_TOKEN']}", "Content-Type": "application/json"},
        {"model": "moonshot-v1-128k",
         "messages": [{"role": "user", "content": prompt}],
         "max_tokens": kw.get("max_tokens", 800), "temperature": 0.3},
    )
    if ok:
        return {"api": "kimi", "ok": True, "response": body["choices"][0]["message"]["content"]}
    return None


def _gemini(prompt: str, **kw) -> dict:
    if not os.environ.get("GEMINI_TOKEN"):
        return {"api": "gemini", "ok": False, "error": "no token"}
    ok, body = _post_json(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        {"Content-Type": "application/json", "X-Goog-Api-Key": os.environ["GEMINI_TOKEN"]},
        {"contents": [{"parts": [{"text": prompt}]}]},
    )
    if ok:
        return {"api": "gemini", "ok": True, "response": body["candidates"][0]["content"]["parts"][0]["text"]}
    return {"api": "gemini", "ok": False, "error": str(body)[:200]}


def _cloudflare_embed(texts, **kw) -> dict:
    if not os.environ.get("CLOUDFLARE_TOKEN") or not os.environ.get("CLOUDFLARE_ACCOUNT_ID"):
        return {"api": "cloudflare", "ok": False, "error": "no token/account_id"}
    if isinstance(texts, str):
        texts = [texts]
    ok, body = _post_json(
        f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/ai/run/@cf/baai/bge-base-en-v1.5",
        {"Authorization": f"Bearer {os.environ['CLOUDFLARE_TOKEN']}", "Content-Type": "application/json"},
        {"text": texts[:5]},
    )
    if ok:
        data = body.get("result", {}).get("data", [])
        return {"api": "cloudflare", "ok": True, "response": f"{len(data)} × {len(data[0]) if data else 0} dims",
                "n_embeddings": len(data), "dimensions": len(data[0]) if data else 0}
    return {"api": "cloudflare", "ok": False, "error": str(body)[:200]}


def _jev_oracle(text: str, **kw) -> dict:
    if not os.environ.get("TYPESAFEAI_KEY"):
        return {"api": "jev", "ok": False, "error": "no token"}
    ok, body = _post_json(
        "https://api.typesafe.ai/v1/evaluate",
        {"Authorization": f"Bearer {os.environ['TYPESAFEAI_KEY']}", "Content-Type": "application/json"},
        {"question": "Is this canon?",
         "text": text[:800],
         "criteria": {"true": "canon, well-established",
                      "false": "speculative, draft, not canon"}},
    )
    if ok:
        score = body.get("probability", body.get("score", 0.5))
        return {"api": "jev", "ok": True, "response": f"canonicity={score:.4f}", "score": score}
    return {"api": "jev", "ok": False, "error": str(body)[:200]}


_ROUTES = {
    "search": _zai, "websearch": _zai,
    "bootstrap": _groq, "iterate": _groq, "rapid": _groq, "draft": _groq,
    "code": _deepseek, "implement": _deepseek,
    "multimodal": _gemini, "longform": _gemini,
}


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        task = sys.argv[1]
        prompt = " ".join(sys.argv[2:])
        result = call(task, prompt)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: orchestra_call.py TASK PROMPT")
        print("  TASK: search, bootstrap, code, reason, multimodal, embed, oracle")
