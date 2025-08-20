# google_tool.py
from crewai.tools import BaseTool
from pydantic import Field
from funcs.google import main

class GoogleTool(BaseTool):
    name: str = "google_search_tool"
    description: str = "Search Google for Atomberg fans related query and return the top results."

    query: str = Field(..., description="The search query")
    num_results: int = Field(5, description="Number of results to fetch")

    def _run(self, query: str = None, num_results: int = None):
        search_query = query or self.query
        results_count = num_results or self.num_results

        try:
            results = main(search_query, results_count)
            return results
        except Exception as e:
            return {"error": str(e)}
