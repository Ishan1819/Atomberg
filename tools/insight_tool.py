from crewai.tools import BaseTool
import json
import google.generativeai as genai
import os

# Configuration of Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

class InsightTool(BaseTool):
    name: str = "insight_tool"
    description: str = (
        "Combine Google and YouTube brand analysis, extract insights, "
        "and generate recommendations for Atomberg's marketing team."
    )

    def _run(self, combined_data: dict) -> str:
        """
        combined_data example:
        {
            "google": { ... },
            "youtube": { ... }
        }
        """
        try:
            prompt = f"""
You are a senior brand strategist. Analyze the following Google + YouTube data for Atomberg:

{json.dumps(combined_data, indent=2)}

Please provide:
1. Share of Voice comparison (Google vs YouTube).
2. Sentiment comparison across both.
3. Competitors gaining traction where Atomberg is weak.
4. Actionable recommendations for Atomberg’s content & marketing team.
5. Key insights in 4–5 crisp bullet points.
"""

            response = model.generate_content(prompt)
            insights_text = response.text.strip()

            final_output = {
                "data": combined_data,
                "insights": insights_text
            }
            return json.dumps(final_output, indent=2)

        except Exception as e:
            return json.dumps({"error": str(e)})
