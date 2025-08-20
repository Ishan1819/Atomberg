from langchain_core.language_models.llms import LLM
from typing import Optional, List
from litellm import completion
from dotenv import load_dotenv
import os
from pydantic import Field

load_dotenv()

class LiteLLMWrapper(LLM):
    model: str = Field(default="gemini/gemini-1.5-flash")

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        messages = [{"role": "user", "content": prompt}]
        try:
            response = completion(model=self.model, messages=messages)
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"[LiteLLMWrapper Error]: {str(e)}"

    def supports_stop_words(self) -> bool:
        return False

    @property
    def _llm_type(self) -> str:
        return "litellm-wrapper"
