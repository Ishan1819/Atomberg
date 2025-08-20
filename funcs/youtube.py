import re
from serpapi import GoogleSearch
from textblob import TextBlob

# ✅ Set your SerpAPI key here
SERPAPI_KEY = "84abd1561ae6f81ea2f3ecd5df1c401191c1a93f38d2ec1b19b3f5d9a3e64e8b"

# --------- Utility Functions ---------
def extract_mentions(text):
    """Count mentions of Atomberg vs competitors in given text"""
    text = text.lower()
    brands = {
        "atomberg": len(re.findall(r"\batomberg\b", text)),
        "usha": len(re.findall(r"\busha\b", text)),
        "havells": len(re.findall(r"\bhavells\b", text)),
        "orient": len(re.findall(r"\borient\b", text)),
        "crompton": len(re.findall(r"\bcrompton\b", text)),
        "luminous": len(re.findall(r"\bluminous\b", text)),
    }
    return brands

def sentiment_score(text):
    """Get polarity score from -1 (negative) to +1 (positive)"""
    return TextBlob(text).sentiment.polarity

# --------- Fetch YouTube Results ---------
def fetch_youtube_results(query, num_results=5):
    """Search YouTube videos using SerpAPI"""
    search = GoogleSearch({
        "engine": "youtube",
        "search_query": query,
        "api_key": SERPAPI_KEY
    })
    results = search.get_dict()

    videos = results.get("video_results", [])[:num_results]
    return videos

# --------- Analyze Results ---------
def analyze_videos(videos):
    summary = {
        "mentions": { "atomberg": 0, "usha": 0, "havells": 0, "orient": 0, "crompton": 0, "luminous": 0 },
        "sentiment": { "atomberg": [], "others": [] }
    }

    for vid in videos:
        title = vid.get("title", "")
        desc = vid.get("description", "")
        channel = vid.get("channel", {}).get("name", "")

        text = f"{title} {desc} {channel}"

        # Mentions
        counts = extract_mentions(text)
        for brand, c in counts.items():
            summary["mentions"][brand] += c

        # Sentiment
        score = sentiment_score(text)
        if "atomberg" in text.lower():
            summary["sentiment"]["atomberg"].append(score)
        else:
            summary["sentiment"]["others"].append(score)

    return summary

# --------- Compute SoV ---------
def compute_sov(summary):
    total_mentions = sum(summary["mentions"].values())
    atomberg_mentions = summary["mentions"]["atomberg"]

    if total_mentions == 0:
        mention_sov = 0
    else:
        mention_sov = atomberg_mentions / total_mentions * 100

    atomberg_sent = (
        sum(summary["sentiment"]["atomberg"]) / len(summary["sentiment"]["atomberg"])
        if summary["sentiment"]["atomberg"] else 0
    )
    others_sent = (
        sum(summary["sentiment"]["others"]) / len(summary["sentiment"]["others"])
        if summary["sentiment"]["others"] else 0
    )

    return {
        "mention_sov(%)": mention_sov,
        "atomberg_sentiment": atomberg_sent,
        "others_sentiment": others_sent,
    }

# --------- Main ---------
def youtube_search(query, num_results):
    # query = "best fan in India"
    videos = fetch_youtube_results(query, num_results)

    print(f"🔍 Found {len(videos)} YouTube videos for query '{query}'")

    for i, vid in enumerate(videos, 1):
        title = vid.get("title", "No title")
        link = vid.get("link", "No link")   # ✅ fixed: use link instead of video_id
        print(f"{i}. {title}\n   {link}")

    # Analyze
    summary = analyze_videos(videos)
    sov = compute_sov(summary)

    print("\n📊 Brand Mentions:", summary["mentions"])
    print("😊 Sentiment (Atomberg):", summary["sentiment"]["atomberg"])
    print("😐 Sentiment (Others):", summary["sentiment"]["others"])
    print("\n✅ Share of Voice Results:", sov)


