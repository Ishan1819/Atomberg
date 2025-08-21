import re
from serpapi import GoogleSearch
from textblob import TextBlob

SERPAPI_KEY = "84abd1561ae6f81ea2f3ecd5df1c401191c1a93f38d2ec1b19b3f5d9a3e64e8b"   # hope i dont forget to hide this later lol

BRANDS = ["Atomberg", "Crompton", "Havells", "Orient", "Usha", "Bajaj", "Luminous", "Polar"]

def extract_brand_mentions(text):
    if not text:   # safeguard bcz empty text was breaking last time
        return {brand: 0 for brand in BRANDS}
    
    text_lower = text.lower()
    mentions = {}
    
    for brand in BRANDS:
        pattern = r'\b' + re.escape(brand.lower()) + r'\b'   # regex might miss partial words but ok
        matches = re.findall(pattern, text_lower)
        mentions[brand] = len(matches)
    
    return mentions

def analyze_sentiment(text):
    if not text.strip():
        return "neutral"
    
    polarity = TextBlob(text).sentiment.polarity   # using textblob, not perfect but works
    
    if polarity >= 0.1:
        return "positive"
    elif polarity <= -0.1:
        return "negative"
    else:
        return "neutral"

def fetch_youtube_results(query, num_results=5):
    if not SERPAPI_KEY:   # if key missing then nothing works obv
        return []
    
    try:
        search = GoogleSearch({
            "engine": "youtube",
            "search_query": query,
            "api_key": SERPAPI_KEY
        })
        results = search.get_dict()
        
        if "error" in results:   # serpapi sometimes throws random error key
            print(f"SerpAPI error: {results['error']}")
            return []
        
        videos = results.get("video_results", [])[:num_results]
        return videos
    except Exception as e:
        print(f"Error fetching YouTube results: {e}")
        return []

def analyze_videos(videos):
    brand_analysis = {brand: {"mentions": 0, "sentiment": []} for brand in BRANDS}
    processed_videos = []
    
    for i, video in enumerate(videos, 1):
        try:
            title = video.get("title", "")
            description = video.get("description", "")
            channel_name = video.get("channel", {}).get("name", "") if isinstance(video.get("channel"), dict) else ""
            
            combined_text = f"{title} {description} {channel_name}"   # hope channel name is string always
            
            print(f"📹 [{i}] Processing: {title[:60]}...")
            
            mentions = extract_brand_mentions(combined_text)
            sentiment = analyze_sentiment(combined_text)
            
            for brand, count in mentions.items():
                if count > 0:
                    brand_analysis[brand]["mentions"] += count
                    brand_analysis[brand]["sentiment"].append(sentiment)
            
            processed_videos.append({
                "position": i,
                "title": title,
                "link": video.get("link", ""),
                "channel": channel_name,
                "views": video.get("views", 0),   # views might be str sometimes.. risky
                "published_date": video.get("published_date", ""),
                "length": video.get("length", ""),
                "brand_mentions": mentions,
                "sentiment": sentiment,
                "brands_found": [b for b, c in mentions.items() if c > 0]
            })
            
        except Exception as e:
            print(f"Error processing video {i}: {e}")   # need better logging but for now print
            continue
    
    return processed_videos, brand_analysis

def compute_youtube_sov(brand_analysis):
    total_mentions = sum(brand_data["mentions"] for brand_data in brand_analysis.values())
    
    sov_summary = {}
    for brand, data in brand_analysis.items():
        mentions = data["mentions"]
        if total_mentions > 0:
            sov_percentage = (mentions / total_mentions) * 100
        else:
            sov_percentage = 0   # avoid div by zero stuff
            
        sentiments = data["sentiment"]
        sentiment_dist = {
            "positive": sentiments.count("positive"),
            "negative": sentiments.count("negative"),
            "neutral": sentiments.count("neutral")
        }
        
        sentiment_scores = []
        for sent in sentiments:   # converting words to numbers kinda hacky but fine
            if sent == "positive":
                sentiment_scores.append(1)
            elif sent == "negative":
                sentiment_scores.append(-1)
            else:
                sentiment_scores.append(0)
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        sov_summary[brand] = {
            "mentions": mentions,
            "sov_percentage": round(sov_percentage, 2),
            "sentiment_distribution": sentiment_dist,
            "videos_mentioned": len(sentiments),
            "avg_sentiment_score": round(avg_sentiment, 3)
        }
    
    top_brands = sorted(sov_summary.items(), key=lambda x: x[1]["sov_percentage"], reverse=True)
    
    return sov_summary, dict(top_brands[:5])

def youtube_search(query, num_results):
    print(f"YouTube Search: {query}")
    
    if not SERPAPI_KEY:
        return {"error": "Missing SERPAPI_KEY"}
    
    videos = fetch_youtube_results(query, num_results)
    
    if not videos:
        return {"error": "No YouTube results found"}   # sometimes serpapi returns nothing
    
    processed_videos, brand_analysis = analyze_videos(videos)
    sov_summary, top_brands = compute_youtube_sov(brand_analysis)
    
    print(f"\nAnalysis complete! Found {len(processed_videos)} videos")
    print(f"Top brands by mentions: {', '.join(list(top_brands.keys())[:3])}")
    
    return {
        "query": query,
        "total_videos": len(processed_videos),
        "videos": processed_videos,
        "brand_analysis": sov_summary,
        "top_brands": top_brands,
        "summary": {
            "total_mentions": sum(brand_data["mentions"] for brand_data in brand_analysis.values()),
            "atomberg_sov": sov_summary.get("Atomberg", {}).get("sov_percentage", 0),
            "atomberg_mentions": sov_summary.get("Atomberg", {}).get("mentions", 0),
            "atomberg_videos": sov_summary.get("Atomberg", {}).get("videos_mentioned", 0)
        }
    }
