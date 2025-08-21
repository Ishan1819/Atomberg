# import google.generativeai as genai
# import os

# # Configure Gemini / OpenAI / any LLM
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# def generate_final_insights(query, google_data, youtube_data):
#     """
#     Combines Google + YouTube analysis into one unified brand insight report.
#     """
#     prompt = f"""
#     You are a marketing strategist. Analyze brand insights for query: {query}.

#     --- GOOGLE DATA ---
#     {google_data}

#     --- YOUTUBE DATA ---
#     {youtube_data}

#     TASKS:
#     1. Extract common themes & insights across both platforms.
#     2. Highlight customer sentiment (positive, negative, mixed).
#     3. Identify competitor mentions and comparisons.
#     4. Provide clear recommendations for Atomberg’s marketing & content team.
#     5. Suggest at least 3 actionable strategies (SEO keywords, campaign angles, influencer ideas).
#     """

#     model = genai.GenerativeModel("gemini-1.5-flash")
#     response = model.generate_content(prompt)

#     return response.text
