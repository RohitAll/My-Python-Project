"""
Browser & Web Search Tools
Allows web browsing, URL opening, and live web/Wikipedia searching.
"""

import webbrowser
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List

from tools.registry import BaseTool, tool_registry


class OpenWebsiteTool(BaseTool):
    name = "open_website"
    description = "Open a URL or website domain in the default desktop browser."
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The target URL or domain to open (e.g. 'https://google.com' or 'youtube.com').",
            }
        },
        "required": ["url"],
    }

    async def execute(self, url: str, **kwargs) -> Dict[str, Any]:
        if not url.startswith("http://") and not url.startswith("https://"):
            target_url = "https://" + url
        else:
            target_url = url

        try:
            webbrowser.open(target_url)
            return {"success": True, "message": f"Opened website: {target_url}"}
        except Exception as e:
            return {"success": False, "error": f"Failed to open website '{url}': {str(e)}"}


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the live web for current information, news, or answers."
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search term or query string.",
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to retrieve (default: 5).",
            },
        },
        "required": ["query"],
    }

    async def execute(self, query: str, num_results: int = 5, **kwargs) -> Dict[str, Any]:
        results: List[Dict[str, str]] = []

        # Try Google Search library first if installed
        try:
            from googlesearch import search

            for url in search(query, num_results=num_results):
                results.append({"title": url, "link": url, "snippet": f"Web result for {query}"})
        except Exception:
            pass

        # Fallback to DuckDuckGo HTML scraping if googlesearch is empty or fails
        if not results:
            try:
                encoded = urllib.parse.quote_plus(query)
                url = f"https://html.duckduckgo.com/html/?q={encoded}"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
                }
                resp = requests.get(url, headers=headers, timeout=5)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.find_all("a", class_="result__url", limit=num_results):
                        link = a.get("href", "")
                        snippet_div = a.find_parent("div", class_="result__body")
                        snippet = snippet_div.get_text().strip() if snippet_div else ""
                        results.append({"title": link, "link": link, "snippet": snippet[:200]})
            except Exception as e:
                return {"success": False, "error": f"Web search error: {str(e)}"}

        if not results:
            # Fallback to Wikipedia summary search
            try:
                import wikipedia

                wiki_summary = wikipedia.summary(query, sentences=3)
                results.append({"title": query, "link": "https://wikipedia.org", "snippet": wiki_summary})
            except Exception:
                pass

        return {
            "success": True,
            "query": query,
            "results_count": len(results),
            "results": results,
        }


def register_browser_tools():
    tool_registry.register(OpenWebsiteTool())
    tool_registry.register(WebSearchTool())


register_browser_tools()
