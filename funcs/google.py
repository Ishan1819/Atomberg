import os
import time
import random
import re
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from serpapi import GoogleSearch
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = "84abd1561ae6f81ea2f3ecd5df1c401191c1a93f38d2ec1b19b3f5d9a3e64e8b"
COUNTRY = "in"
LANG = "en"
LOCATION = "Mumbai,Maharashtra,India"
BRANDS = ["Atomberg", "Crompton", "Havells", "Orient", "Usha", "Bajaj", "Luminous", "Polar"]

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

SIA = SentimentIntensityAnalyzer()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def serpapi_search(query: str, num: int = 10) -> List[Dict]:
    # search using serp api
    params = {
        "engine": "google",
        "q": query,
        "num": num,
        "hl": LANG,
        "gl": COUNTRY,
        "location": LOCATION,
        "api_key": SERPAPI_KEY,
    }
    
    try:
        search = GoogleSearch(params)
        res = search.get_dict()
        return res.get("organic_results", [])
    except Exception as e:
        print(f"SerpAPI error: {e}")
        return []

def scrape_basic_content(url: str) -> Dict:
    # basic scraping (may miss some cases)
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return {"content": "", "reviews": []}

        soup = BeautifulSoup(r.text, "html.parser")
        
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        content = ""
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 20:  # kinda arbitrary
                content += text + " "

        reviews = []
        review_selectors = ["div[class*='review']", "div[class*='comment']", "div[class*='feedback']"]
        for sel in review_selectors:
            for el in soup.select(sel):
                text = el.get_text(strip=True)
                if 15 < len(text) < 500:  # ignoring too small/too big
                    reviews.append(text)

        return {
            "content": content[:1000],  
            "reviews": reviews[:5]     
        }
    except Exception as e:
        return {"content": "", "reviews": [], "error": str(e)}

def count_brand_mentions(text: str) -> Dict[str, int]:
    # check brand mentions
    if not text:
        return {brand: 0 for brand in BRANDS}
    
    text_lower = text.lower()
    mentions = {}
    
    for brand in BRANDS:
        pattern = r'\b' + re.escape(brand.lower()) + r'\b'
        matches = re.findall(pattern, text_lower)
        mentions[brand] = len(matches)
    
    return mentions

def analyze_sentiment(text: str) -> str:
    # quick sentiment check (not very deep)
    if not text.strip():
        return "neutral"
    
    scores = SIA.polarity_scores(text)
    compound = scores['compound']
    
    if compound >= 0.1:
        return "positive"
    elif compound <= -0.1:
        return "negative"
    else:
        return "neutral"

def main(query: str, num_results: int = 5) -> Dict:
    print(f"Searching for: {query}")
    
    if not SERPAPI_KEY:
        return {"error": "Missing SERPAPI_KEY"}
    
    search_results = serpapi_search(query, num_results)
    
    if not search_results:
        return {"error": "No search results found"}
    
    processed_results = []
    brand_analysis = {brand: {"mentions": 0, "sentiment": []} for brand in BRANDS}
    
    for i, result in enumerate(search_results[:num_results], 1):
        try:
            title = result.get("title", "")
            url = result.get("link", "")
            snippet = result.get("snippet", "")
            
            print(f"[{i}] Processing: {title[:50]}...")
            
            scraped = scrape_basic_content(url)
            
            all_text = f"{title} {snippet} {scraped['content']} {' '.join(scraped['reviews'])}"
            
            mentions = count_brand_mentions(all_text)
            
            sentiment = analyze_sentiment(all_text)
            
            for brand, count in mentions.items():
                if count > 0:
                    brand_analysis[brand]["mentions"] += count
                    brand_analysis[brand]["sentiment"].append(sentiment)
            
            processed_results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
                "content_preview": scraped['content'][:200],
                "review_count": len(scraped['reviews']),
                "brand_mentions": mentions,
                "sentiment": sentiment,
                "brands_found": [b for b, c in mentions.items() if c > 0]
            })
            
        except Exception as e:
            print(f"Error processing result {i}: {e}")
            continue
        
        time.sleep(random.uniform(0.5, 1.0))  # just to avoid blocking
    
    try:
        total_mentions = sum(brand_data["mentions"] for brand_data in brand_analysis.values())
        print(f"Total mentions calculated: {total_mentions}")
    except Exception as e:
        print(f"Error calculating total mentions: {e}")
        total_mentions = 1  
    
    sov_summary = {}
    for brand, data in brand_analysis.items():
        mentions = data["mentions"]
        if total_mentions > 0:
            sov_percentage = (mentions / total_mentions) * 100
        else:
            sov_percentage = 0
            
        sentiments = data["sentiment"]
        sentiment_dist = {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral")
        }
        
        sov_summary[brand] = {
            "mentions": mentions,
            "sov_percentage": round(sov_percentage, 2),
            "sentiment_distribution": sentiment_dist,
            "pages_mentioned": len(sentiments)
        }
    
    top_brands = sorted(sov_summary.items(), key=lambda x: x[1]["sov_percentage"], reverse=True)
    
    return {
        "query": query,
        "total_results": len(processed_results),
        "results": processed_results,
        "brand_analysis": sov_summary,
        "top_brands": dict(top_brands[:5]),
        "summary": {
            "total_mentions": total_mentions,
            "atomberg_sov": sov_summary.get("Atomberg", {}).get("sov_percentage", 0),
            "atomberg_mentions": sov_summary.get("Atomberg", {}).get("mentions", 0)
        }
    }
