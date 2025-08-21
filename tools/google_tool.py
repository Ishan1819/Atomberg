# google_tool.py
from crewai.tools import BaseTool
from pydantic import Field
from funcs.google import main
import json

class GoogleTool(BaseTool):
    name: str = "google_search_tool"
    description: str = "Search Google for Atomberg fans related queries and analyze brand mentions and sentiment."

    def _run(self, query: str, num_results: int = 15) -> str:

        try:
            results = main(query, num_results)
            
            if "error" in results:
                return f"Error: {results['error']}"
            
            # Format results for the agent
            formatted_output = f"""
SEARCH ANALYSIS FOR: {results['query']}
RESULTS: {results['total_results']} pages analyzed

TOP BRANDS BY SHARE OF VOICE:
"""
            
            for brand, data in results['top_brands'].items():
                formatted_output += f"• {brand}: {data['sov_percentage']}% ({data['mentions']} mentions, {data['pages_mentioned']} pages)\n"
            
            formatted_output += f"""
ATOMBERG PERFORMANCE:
• Share of Voice: {results['summary']['atomberg_sov']}%
• Total Mentions: {results['summary']['atomberg_mentions']}
• Brand Ranking: #{list(results['top_brands'].keys()).index('Atomberg') + 1 if 'Atomberg' in results['top_brands'] else 'Not in top 5'}

KEY FINDINGS:
"""
            
            # Add key findings from top results
            for i, result in enumerate(results['results'][:3], 1):
                brands_found = ', '.join(result['brands_found']) if result['brands_found'] else 'None'
                formatted_output += f"{i}. {result['title'][:80]}...\n   Brands mentioned: {brands_found} | Sentiment: {result['sentiment']}\n"
            
            # Add raw data for further processing
            formatted_output += f"\nRAW DATA:\n{json.dumps(results['summary'], indent=2)}"
            
            return formatted_output
            
        except Exception as e:
            return f"Error in Google search tool: {str(e)}"