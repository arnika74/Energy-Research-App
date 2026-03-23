"""
LLM Model loader and wrapper for generating research reports.
Uses HuggingFace Transformers with a free open-source model.
Primary: google/flan-t5-base (fast, reliable on CPU)
Fallback: any seq2seq or causal LM on HuggingFace
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

_pipeline = None


def get_llm_pipeline():
    """
    Load the HuggingFace text generation pipeline (singleton).
    Uses T5-based seq2seq for reliable summarization on CPU.
    """
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    from config.settings import LLM_MODEL_NAME, LLM_MAX_NEW_TOKENS, LLM_DEVICE

    logger.info(f"Loading LLM model: {LLM_MODEL_NAME}")

    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

        tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(LLM_MODEL_NAME)

        _pipeline = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            device=-1,  # CPU
            max_new_tokens=LLM_MAX_NEW_TOKENS,
        )
        logger.info(f"LLM model loaded successfully: {LLM_MODEL_NAME}")
        return _pipeline

    except Exception as e:
        logger.error(f"Failed to load primary model {LLM_MODEL_NAME}: {e}")
        # Fallback to a simpler model
        logger.info("Falling back to google/flan-t5-small")
        from transformers import pipeline

        _pipeline = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",
            device=-1,
            max_new_tokens=256,
        )
        return _pipeline


def generate_text(prompt: str, max_tokens: Optional[int] = None) -> str:
    """
    Generate text from a prompt using the loaded LLM.

    Args:
        prompt: The input text/instruction for the model
        max_tokens: Optional override for max new tokens

    Returns:
        Generated text string
    """
    try:
        pipe = get_llm_pipeline()
        from config.settings import LLM_MAX_NEW_TOKENS

        kwargs = {}
        if max_tokens:
            kwargs["max_new_tokens"] = max_tokens
        else:
            kwargs["max_new_tokens"] = LLM_MAX_NEW_TOKENS

        # Truncate prompt to avoid token limit issues
        prompt = prompt[:3000]

        result = pipe(prompt, **kwargs)

        if isinstance(result, list) and len(result) > 0:
            output = result[0].get("generated_text", "")
            return output.strip()

        return ""

    except Exception as e:
        logger.error(f"Text generation error: {e}")
        return f"Error generating text: {str(e)}"
