from __future__ import annotations

import os
from typing import Any

import requests
from agents import function_tool


@function_tool
def tavily_search(query: str, max_results: int = 3) -> str:
    """
    Search Tavily and return a compact summary of the top results.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Tavily API key is not configured."

    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    response.raise_for_status()

    payload: dict[str, Any] = response.json()
    results = payload.get("results", [])
    if not results:
        return "No relevant Tavily results found."

    return "\n".join(
        f"{index + 1}. {item.get('title', 'Untitled')}: {item.get('content', '')}"
        for index, item in enumerate(results)
    )
