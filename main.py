from agents.agent import create_google_crew, create_youtube_crew, create_insight_crew
import json

if __name__ == "__main__":
    query = "Atomberg ceiling fans reviews"

    print("Starting Multi-Platform Brand Analysis...")
    print(f"Query: {query}")
    print("="*80)


    print("\nGOOGLE ANALYSIS - Starting...")
    google_crew = create_google_crew(query, num_results=15)
    google_results = google_crew.kickoff()

    # extract JSON from CrewOutput
    try:
        google_json = google_results.json()
    except Exception:
        google_json = str(google_results)  

    print("\nGoogle Results:\n", google_json)
    print("="*80)

    print("\nYOUTUBE ANALYSIS - Starting...")
    youtube_crew = create_youtube_crew(query, num_results=15)
    youtube_results = youtube_crew.kickoff()

    print("\nMULTI-PLATFORM INSIGHTS")
    print("="*80)

    # extracting raw dicts from CrewOutput
    google_data = google_results.raw if hasattr(google_results, "raw") else google_results
    youtube_data = youtube_results.raw if hasattr(youtube_results, "raw") else youtube_results

    if isinstance(google_data, str):
        google_data = json.loads(google_data)
    if isinstance(youtube_data, str):
        youtube_data = json.loads(youtube_data)

    insight_crew = create_insight_crew(google_data, youtube_data)
    final_report = insight_crew.kickoff()

    print("\nFinal Brand Insights & Recommendations:\n")
    print(final_report)

    # Convert CrewOutput to string to save in .txt file
    report_text = str(final_report)  # or final_report.text if that works

    file_path = "Atomberg_Brand_Insights.txt"

    with open(file_path, "w", encoding="utf-8") as file:
        file.write("Final Brand Insights & Recommendations:\n\n")
        file.write(report_text)

    print(f"\nReport successfully saved to {file_path}")
