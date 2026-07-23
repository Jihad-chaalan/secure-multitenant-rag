# backend/app/security/llm_client.py

import os
import json
import logging
from typing import Dict, Any
from dotenv import load_dotenv

from groq import Groq

load_dotenv()

from app.config import GROQ_API_KEY

print("🔥 NEW VERSION OF LLM_CLIENT LOADED!")  # Marker

logger = logging.getLogger(__name__)

_groq_client = Groq(api_key=GROQ_API_KEY)
_SECURITY_MODEL = "llama-3.1-8b-instant"


def call_llm_for_classification(prompt: str) -> Dict[str, Any]:
    print("🔥 call_llm_for_classification called")
    try:
        completion = _groq_client.chat.completions.create(
            model=_SECURITY_MODEL,
            messages=[
                {"role": "system", "content": "You are a security classifier. Always respond with a single valid JSON object. Do not include any explanations, markdown formatting, or extra text. Output ONLY the JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=250,
            response_format={"type": "json_object"},
        )

        raw = completion.choices[0].message.content
        print(f"RAW LLM RESPONSE:\n{raw}\n")

        # Try to parse JSON
        try:
            data = json.loads(raw)
            print("JSON parsed successfully")
            return data
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            # Fallback: try to extract JSON using regex
            import re
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    print("Extracted JSON via regex")
                    return data
                except:
                    pass
            raise ValueError(f"Invalid JSON response: {raw[:100]}...")

    except Exception as e:
        print(f"Exception in llm_client: {e}")
        return {
            "decision": "ALLOW",
            "category": "none",
            "reason": f"LLM error: {e}",
            "risk_score": 0,
        }