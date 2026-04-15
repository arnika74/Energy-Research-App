"""
HuggingFace LLM wrapper.
Model is loaded once at startup and reused for all requests.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_pipeline = None


def load_model() -> None:
    """Preload the LLM pipeline. Call this once at server startup."""
    global _pipeline
    if _pipeline is not None:
        return

    from config.settings import LLM_MODEL_NAME, LLM_MAX_NEW_TOKENS

    logger.info(f"Loading LLM: {LLM_MODEL_NAME}")
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

        tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(LLM_MODEL_NAME)
        _pipeline = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            device=-1,
            max_new_tokens=LLM_MAX_NEW_TOKENS,
        )
        logger.info("LLM loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load {LLM_MODEL_NAME}: {e} — falling back to flan-t5-small")
        from transformers import pipeline as hf_pipeline
        _pipeline = hf_pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            device=-1,
            max_new_tokens=128,
        )


def generate_text(prompt: str, max_tokens: Optional[int] = None) -> str:
    """Generate text from a prompt. Returns empty string on error."""
    global _pipeline
    if _pipeline is None:
        load_model()

    try:
        from config.settings import LLM_MAX_NEW_TOKENS
        kwargs = {"max_new_tokens": max_tokens or LLM_MAX_NEW_TOKENS}
        result = _pipeline(prompt[:2500], **kwargs)
        if isinstance(result, list) and result:
            return result[0].get("generated_text", "").strip()
    except Exception as e:
        logger.error(f"Text generation error: {e}")
    return ""
