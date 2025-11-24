from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_tavily_client():
    """Initialize the Tavily client with the API key."""
    return TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))