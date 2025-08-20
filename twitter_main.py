import os
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

# --------- Fetch Twitter Results ---------
def fetch_twitter_results(query, num_results=10):
    """Search recent tweets using SerpAPI"""
    search = GoogleSearch({
        "engine": "twitter",
        "q": query,
        "api_key": SERPAPI_KEY
    })
    results = search.get_dict()
    tweets = results.get("tweets", [])[:num_results]
    return tweets

# --------- Analyze Results ---------
def analyze_tweets(tweets):
    summary = {
        "mentions": { "atomberg": 0, "usha": 0, "havells": 0, "orient": 0, "crompton": 0, "luminous": 0 },
        "sentiment": { "atomberg": [], "others": [] }
    }

    for tweet in tweets:
        text = tweet.get("content", "") or tweet.get("text", "")
        username = tweet.get("username", "")
        full_text = f"{text} {username}"

        # Mentions
        counts = extract_mentions(full_text)
        for brand, c in counts.items():
            summary["mentions"][brand] += c

        # Sentiment
        score = sentiment_score(full_text)
        if "atomberg" in full_text.lower():
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
def main():
    query = "Atomberg reviews"
    tweets = fetch_twitter_results(query, num_results=15)

    print(f"🔍 Found {len(tweets)} tweets for query '{query}'")

    for i, tweet in enumerate(tweets, 1):
        text = tweet.get("content", "") or tweet.get("text", "")
        username = tweet.get("username", "")
        link = tweet.get("link", "No link")
        print(f"{i}. @{username}: {text[:100]}...\n   {link}")

    # Analyze
    summary = analyze_tweets(tweets)
    sov = compute_sov(summary)

    print("\n📊 Brand Mentions:", summary["mentions"])
    print("😊 Sentiment (Atomberg):", summary["sentiment"]["atomberg"])
    print("😐 Sentiment (Others):", summary["sentiment"]["others"])
    print("\n✅ Share of Voice Results:", sov)


if __name__ == "__main__":
    main()
