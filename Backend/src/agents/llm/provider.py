"""
Multi-LLM Routing and Failover Engine powered by LiteLLM.
Routes between Gemini (Primary), GLM (Fallback 1), and Mistral/Groq (Fallback 2).
"""

import time
from typing import List, Dict, Any, Optional, Tuple
import litellm
from src.config.settings import settings
from src.rag.prompts.templates import (
    RAG_SYSTEM_PROMPT,
    GENERAL_KNOWLEDGE_SYSTEM_PROMPT,
    build_rag_user_prompt,
    build_general_knowledge_prompt,
)
from src.utils.logger import logger

# Suppress overly verbose litellm logs unless debug
litellm.suppress_debug_info = not settings.DEBUG


class LLMResponse:
    def __init__(
        self,
        content: str,
        model_used: str,
        execution_time_ms: float,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        success: bool = True,
        error: Optional[str] = None
    ):
        self.content = content
        self.model_used = model_used
        self.execution_time_ms = execution_time_ms
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.success = success
        self.error = error


class MultiLLMRouter:
    def __init__(self):
        # Configure model candidates with automatic sub-model fallbacks
        self.model_candidates = [
            {
                "name": "Mistral (High Performance)",
                "models": [
                    "mistral/open-mistral-nemo",
                    "mistral/open-mistral-7b",
                    "mistral/ministral-8b-latest",
                    "mistral/codestral-latest",
                ],
                "api_key": settings.MISTRAL_API_KEY or settings.MIST_API_KEY,
                "api_base": None,
                "kwargs": {"temperature": 0.1, "max_tokens": 2048}
            },
            {
                "name": "Gemini (Primary)",
                "models": [
                    settings.PRIMARY_MODEL,
                    "gemini/gemini-2.5-flash",
                    "gemini/gemini-2.0-flash",
                    "gemini/gemini-1.5-flash",
                ],
                "api_key": settings.GEMINI_API_KEY,
                "api_base": None,
                "kwargs": {"temperature": 0.1, "max_tokens": 2048}
            },
            {
                "name": "Groq (Fast Fallback)",
                "models": [
                    settings.FALLBACK_MODEL_2,
                    "groq/llama-3.1-8b-instant",
                    "groq/llama-3.3-70b-versatile",
                    "groq/mixtral-8x7b-32768",
                    "groq/gemma2-9b-it",
                ],
                "api_key": settings.GROQ_API_KEY,
                "api_base": None,
                "kwargs": {"temperature": 0.1, "max_tokens": 2048}
            },
            {
                "name": "GLM / Zhipu (Fallback)",
                "models": [
                    "openai/glm-4-flash",
                    settings.FALLBACK_MODEL_1,
                ],
                "api_key": settings.ZHIPUAI_API_KEY or settings.GLM_API_KEY,
                "api_base": "https://open.bigmodel.cn/api/paas/v4",
                "kwargs": {"temperature": 0.1, "max_tokens": 2048}
            },
            {
                "name": "OpenAI (Fallback)",
                "models": [
                    "openai/gpt-4o-mini",
                    "openai/gpt-3.5-turbo",
                ],
                "api_key": settings.OPENAI_API_KEY,
                "api_base": None,
                "kwargs": {"temperature": 0.1, "max_tokens": 2048}
            }
        ]

    async def _call_with_failover(
        self,
        messages: List[Dict[str, str]],
        model_override: Optional[str] = None,
        temperature_override: Optional[float] = None,
    ) -> LLMResponse:
        """
        Core failover engine: try each LLM provider in order until one succeeds.
        """
        candidates = list(self.model_candidates)
        if model_override:
            override_candidate = {
                "name": f"Override ({model_override})",
                "model": model_override,
                "api_key": None,
                "api_base": None,
                "kwargs": {"temperature": temperature_override or 0.1, "max_tokens": 2048}
            }
            if "gemini" in model_override.lower():
                override_candidate["api_key"] = settings.GEMINI_API_KEY
            elif "mistral" in model_override.lower():
                override_candidate["api_key"] = settings.MISTRAL_API_KEY or settings.MIST_API_KEY
            elif "glm" in model_override.lower():
                override_candidate["api_key"] = settings.ZHIPUAI_API_KEY or settings.GLM_API_KEY
                override_candidate["api_base"] = "https://open.bigmodel.cn/api/paas/v4"
            elif "groq" in model_override.lower():
                override_candidate["api_key"] = settings.GROQ_API_KEY
            elif "openai" in model_override.lower() or "gpt" in model_override.lower():
                override_candidate["api_key"] = settings.OPENAI_API_KEY
            candidates.insert(0, override_candidate)

        last_error = None

        for candidate in candidates:
            models_to_try = candidate.get("models") or [candidate.get("model")]
            provider_label = candidate["name"]
            api_key = candidate.get("api_key")
            api_base = candidate.get("api_base")
            kwargs = candidate.get("kwargs", {})

            if temperature_override is not None:
                kwargs = {**kwargs, "temperature": temperature_override}

            # Skip if no API key is available for this provider
            if not api_key:
                logger.debug(f"Skipping {provider_label} - no API key configured.")
                continue

            for model_name in models_to_try:
                if not model_name:
                    continue
                logger.info(f"Attempting generation with {provider_label} (model: {model_name})...")
                start_time = time.perf_counter()

                try:
                    call_args: Dict[str, Any] = {
                        "model": model_name,
                        "messages": messages,
                        "api_key": api_key,
                        "timeout": 20,
                        **kwargs
                    }
                    if api_base:
                        call_args["api_base"] = api_base

                    response = await litellm.acompletion(**call_args)
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

                    reply_content = response.choices[0].message.content or ""
                    usage = getattr(response, "usage", None)
                    p_tokens = usage.prompt_tokens if usage else 0
                    c_tokens = usage.completion_tokens if usage else 0

                    logger.info(f"Successfully generated answer with {provider_label} [{model_name}] in {elapsed_ms}ms")
                    return LLMResponse(
                        content=reply_content.strip(),
                        model_used=model_name,
                        execution_time_ms=elapsed_ms,
                        prompt_tokens=p_tokens,
                        completion_tokens=c_tokens,
                        success=True
                    )

                except Exception as e:
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    last_error = e
                    logger.warning(
                        f"LLM Provider {provider_label} ({model_name}) failed after {elapsed_ms}ms: {str(e)}. "
                        f"Trying next candidate model..."
                    )

        error_detail = str(last_error) if last_error else "All LLM providers unavailable or no valid API keys configured"
        return LLMResponse(
            content=f"⚠️ LLM Generation Error: {error_detail}. Please verify your GEMINI_API_KEY or GROQ_API_KEY in .env.",
            model_used="fallback-exhausted",
            execution_time_ms=0.0,
            success=False,
            error=error_detail
        )

    async def generate_response(
        self,
        question: str,
        context_str: str,
        model_override: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate grounded answer with automated failover through the model hierarchy.
        """
        user_prompt = build_rag_user_prompt(question, context_str)
        messages = [
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        return await self._call_with_failover(messages, model_override)

    async def generate_general_response(
        self,
        question: str,
        model_override: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate a general-knowledge answer (no RAG context).
        Uses GENERAL_KNOWLEDGE_SYSTEM_PROMPT instead of the strict RAG grounding prompt.
        """
        user_prompt = build_general_knowledge_prompt(question)
        messages = [
            {"role": "system", "content": GENERAL_KNOWLEDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        return await self._call_with_failover(
            messages, model_override, temperature_override=0.3
        )

    async def generate_from_messages(
        self,
        messages: List[Dict[str, str]],
        model_override: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> LLMResponse:
        """
        Generate a response from pre-built messages (used by agents).
        """
        return await self._call_with_failover(
            messages, model_override, temperature_override=temperature
        )
