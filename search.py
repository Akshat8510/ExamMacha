import os
from langchain_community.tools.tavily_search import TavilySearchResults

def perform_web_search(query):
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Search skipped: No Tavily API key."
    try:
        search = TavilySearchResults(api_key=api_key)
        results = search.invoke(query)
        # Convert list of dicts to a single string for the LLM
        return str(results)
    except Exception as e:
        return f"Search Error: {str(e)}"