import os
from langchain_community.tools.tavily_search import TavilySearchResults


def perform_web_search(query: str) -> str:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Search skipped: No Tavily API key found in environment."
    try:
        search_tool = TavilySearchResults(api_key=api_key, max_results=4)
        results = search_tool.invoke(query)
        if not results:
            return "No web results found for this query."
        formatted = []
        for i, r in enumerate(results, 1):
            url = r.get("url", "")
            content = r.get("content", "")
            formatted.append(f"[Source {i}] {url}\n{content}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search error: {str(e)}"