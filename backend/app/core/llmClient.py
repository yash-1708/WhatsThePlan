from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from backend.app.core.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

def get_llm(temperature=0):
    """Returns a configured ChatOpenAI instance."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ValueError("OPENAI_API_KEY not found in .env")

    model = "gpt-4o"
    logger.debug(f"Initializing LLM client (model={model}, temperature={temperature})")

    try:
        client = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key
        )
        logger.debug("LLM client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}", exc_info=True)
        raise
