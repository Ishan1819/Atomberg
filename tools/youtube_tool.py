# tools/youtube_tool.py
from crewai.tools import BaseTool
from pydantic import Field
from funcs.youtube import youtube_search

class YouTubeTool(BaseTool):
    name: str = "youtube_search_tool"
    description: str = "Searches YouTube and returns top video results."

    query: str = Field(..., description="The search query for YouTube")
    num_results: int = Field(5, description="Number of results to fetch from YouTube")

    def _run(self, query: str, num_results: int = 5):
        try:
            results = youtube_search(query, num_results)
            return results
        except Exception as e:
            return {"error": str(e)}
