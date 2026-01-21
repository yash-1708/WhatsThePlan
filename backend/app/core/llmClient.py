from typing import Optional

from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from backend.app.core import config
from backend.app.core.logger import get_logger

logger = get_logger(__name__)


def get_llm(temperature: Optional[float] = None):
    """
    Returns a configured ChatOpenAI instance.

    Args:
        temperature: Override for LLM temperature. If None, uses LLM_TEMPERATURE from config.
    """
    if not config.OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY not found in .env")

    temp = temperature if temperature is not None else config.LLM_TEMPERATURE
    model = config.LLM_MODEL

    logger.debug(f"Initializing LLM client (model={model}, temperature={temp})")

    try:
        client = ChatOpenAI(model=model, temperature=temp, api_key=SecretStr(config.OPENAI_API_KEY))
        logger.debug("LLM client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}", exc_info=True)
        raise
