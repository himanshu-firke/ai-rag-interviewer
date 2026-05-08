"""
LLM Client abstraction layer.
Supports both Groq (free, fast) and Gemini (Google).
All services use this instead of directly calling provider SDKs.
"""

import json
from backend.config import settings


def get_llm_response(prompt: str, system_prompt: str = None) -> str:
    """
    Get a text response from the configured LLM provider.

    Args:
        prompt: User prompt / question
        system_prompt: Optional system instruction

    Returns:
        Response text string
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "groq":
        return _groq_generate(prompt, system_prompt)
    elif provider == "gemini":
        return _gemini_generate(prompt, system_prompt)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def get_json_response(prompt: str, system_prompt: str = None) -> dict:
    """
    Get a JSON-parsed response from the LLM.
    Handles markdown code block stripping.
    """
    raw = get_llm_response(prompt, system_prompt)
    return _parse_json(raw)


def _groq_generate(prompt: str, system_prompt: str = None) -> str:
    """Generate text using Groq API (Llama 3.3 70B)."""
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
    )

    return response.choices[0].message.content


def _gemini_generate(prompt: str, system_prompt: str = None) -> str:
    """Generate text using Google Gemini API."""
    from google import genai

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    full_prompt = prompt
    if system_prompt:
        full_prompt = f"{system_prompt}\n\n{prompt}"

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=full_prompt,
    )

    return response.text


def _parse_json(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown code blocks."""
    text = text.strip()

    # Strip markdown code block wrapping
    if text.startswith("```"):
        # Remove first line (```json or ```)
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        # Remove trailing ```
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        return {"error": "Failed to parse JSON", "raw": text[:500]}
