from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature=0):
    """Returns a configured ChatOpenAI instance."""
    return ChatOpenAI(
        model="gpt-4o",  #"gpt-3.5-turbo" to save cost TODO - send to .env
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY")
    )