from __future__ import annotations

import os
from alina.models import SituationAnalysis, SituationInput
from alina.prompts import SYSTEM_PROMPT, user_prompt


class OpenAIProvider:
    name = "openai"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model_name = model or os.getenv("ALINA_OPENAI_MODEL", "gpt-5.6-terra")
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the OpenAI provider.")

    def analyze(self, situation: SituationInput) -> SituationAnalysis:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("OpenAI support is not installed. Run: pip install 'alina-leadership[openai]'") from exc

        client = OpenAI(api_key=self._api_key)
        completion = client.chat.completions.parse(
            model=self.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt(situation)},
            ],
            response_format=SituationAnalysis,
        )
        message = completion.choices[0].message
        parsed = getattr(message, "parsed", None)
        if parsed is None:
            refusal = getattr(message, "refusal", None)
            if refusal:
                raise RuntimeError(f"The model declined to analyze this situation: {refusal}")
            raise RuntimeError("The model returned no structured analysis.")
        parsed.provider = self.name
        parsed.model = self.model_name
        return parsed
