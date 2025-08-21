from crewai import Agent, Task, Crew
from tools.google_tool import GoogleTool
from tools.youtube_tool import YouTubeTool
from tools.amazon_tool import AmazonTool
from tools.insight_tool import InsightTool
from llm.litellm_wrapper import LiteLLMWrapper
from models import InsightOutput  # Import both models
import json

gemini_llm = LiteLLMWrapper(model="gemini/gemini-1.5-flash")

def create_google_crew(user_query: str, num_results: int) -> Crew:
    google_ai = Agent(
        role="Google Intelligence Agent",
        goal="Search Google for Atomberg fan queries and analyze insights from them. You have to deal with the fan companies and specifically Atomberg",
        backstory="Expert in web search and competitive analysis.",
        tools=[GoogleTool(query=user_query, num_results=num_results)],
        verbose=True,
        llm=gemini_llm
    )

    task = Task(
        description=f"Search Google for '{user_query}' (top {num_results} results), "
                    "extract content, analyze mentions, perform sentiment analysis, "
                    "and compute Share of Voice (SoV).",
        agent=google_ai,
        expected_output="A structured report with: mentions count, sentiment distribution, and Atomberg's SoV.",
        output_json=InsightOutput
    )

    return Crew(
        agents=[google_ai],
        tasks=[task],
        process="sequential",
        verbose=True
    )

def create_youtube_crew(user_query: str, num_results: int = 5) -> Crew:
    youtube_ai = Agent(
        role="YouTube Intelligence Agent",
        goal="Search YouTube for results and analyze insights from them.",
        backstory="Expert in analyzing YouTube content and extracting insights.",
        tools=[YouTubeTool(query=user_query, num_results=num_results)],
        verbose=True,
        llm=gemini_llm
    )

    task = Task(
        description=f"Search YouTube for '{user_query}' (top {num_results} results), "
                    "extract video content/metadata, analyze mentions, perform sentiment analysis, "
                    "and compute Share of Voice (SoV).",
        agent=youtube_ai,
        expected_output="Structured JSON output",
        output_json=InsightOutput
    )

    return Crew(
        agents=[youtube_ai],
        tasks=[task],
        process="sequential",
        verbose=True
    )

def create_insight_crew(google_dict: dict, youtube_dict: dict) -> Crew:
    insight_ai = Agent(
        role="Insight Strategist Agent",
        goal="Combine Google and YouTube data, generate insights, and recommend marketing actions.",
        backstory="Expert brand strategist specializing in digital presence and competitor benchmarking.",
        tools=[InsightTool()],
        verbose=True,
        llm=gemini_llm
    )

    task = Task(
        description=f"""Analyze the provided Google and YouTube data for Atomberg ceiling fans:
        
        Google Data: {json.dumps(google_dict, indent=2)}
        YouTube Data: {json.dumps(youtube_dict, indent=2)}
        
        Generate comprehensive insights including:
        1. Share of Voice comparison between platforms
        2. Sentiment analysis comparison
        3. Competitive landscape insights
        4. Actionable marketing recommendations
        5. Key strategic insights for Atomberg's team""",
        agent=insight_ai,
        expected_output="A comprehensive report with combined data analysis, insights, and marketing recommendations."
        # Removed output_json parameter
    )

    return Crew(
        agents=[insight_ai],
        tasks=[task],
        process="sequential",
        verbose=True
    )