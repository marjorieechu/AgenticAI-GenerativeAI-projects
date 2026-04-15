from __future__ import annotations

import os
from typing import TypedDict

import requests
from agents import function_tool


class TavilySearchParams(TypedDict):
    query: str
    max_results: int


@function_tool
def tavily_search(params: TavilySearchParams) -> str:
    """Search the web via Tavily and return a compact newline-joined summary."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "TAVILY_API_KEY is not configured."

    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": params["query"],
            "max_results": params.get("max_results", 3),
        },
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    if response.status_code != 200:
        return f"Tavily API error: {response.status_code}"

    results = response.json().get("results", [])
    lines = [f"- {item['title']}: {item['content']}" for item in results]
    return "\n".join(lines) if lines else "No relevant results found."
