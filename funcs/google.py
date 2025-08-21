# import os
# import time
# import random
# import json
# from datetime import datetime
# from typing import Dict, List, Tuple
# import re

# import pandas as pd
# import requests
# from bs4 import BeautifulSoup
# from serpapi import GoogleSearch

# # ---- Sentiment ----
# import nltk
# from nltk.sentiment.vader import SentimentIntensityAnalyzer

# # ---- Gemini ----
# import google.generativeai as genai
# from dotenv import load_dotenv

# load_dotenv()
# # ==========================
# # CONFIG
# # ==========================

# SERPAPI_KEY = "84abd1561ae6f81ea2f3ecd5df1c401191c1a93f38d2ec1b19b3f5d9a3e64e8b"


# # Access your API key
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# COUNTRY = "in"   # India
# LANG    = "en"
# LOCATION = "Mumbai,Maharashtra,India"

# # Competitors set (tune as needed)
# BRANDS = ["Atomberg", "Crompton", "Havells", "Orient", "Usha", "Bajaj", "Luminous", "Polar"]

# # Base keywords to cover "smart fan" + near-neighbors (extra brownie points)
# BASE_QUERIES = [
#     "smart fan"
#     # "best smart ceiling fan India",
#     # "Atomberg Renesa review",
#     # "Atomberg vs Crompton smart fan",
#     # "BLDC fan India review",
#     # "best energy efficient fan",
#     # "smart fan remote control review"
# ]

# # Top N unique URLs to process overall
# TOP_N_URLS = 25

# # ==========================
# # INIT
# # ==========================

# def ensure_init():
#     # NLTK VADER
#     try:
#         nltk.data.find("sentiment/vader_lexicon.zip")
#     except LookupError:
#         nltk.download("vader_lexicon")

#     # Gemini
#     if GEMINI_API_KEY:
#         genai.configure(api_key=GEMINI_API_KEY)

# ensure_init()
# SIA = SentimentIntensityAnalyzer()
# GEMINI_MODEL = genai.GenerativeModel("gemini-1.5-flash") if GEMINI_API_KEY else None

# # ==========================
# # SEARCH (SerpAPI)
# # ==========================

# def expand_queries(base_query: str) -> List[str]:
#     return [
#         f"{base_query}",
#         f"{base_query} review",
#         f"{base_query} customer feedback",
#         f"{base_query} pros cons",
#         f"{base_query} experience",
#         f"{base_query} vs other brands",
#         f"{base_query} amazon flipkart",
#         f"{base_query} price comparison",
#         f"{base_query} user opinion"
#     ]

# def serpapi_search(query: str, num: int = 10) -> List[Dict]:
#     print(query, "asasasasas")
#     params = {
#         "engine": "google",
#         "q": query,
#         "num": num,
#         "hl": LANG,
#         "gl": COUNTRY,
#         "location": LOCATION,
#         "api_key": SERPAPI_KEY,
#     }
#     search = GoogleSearch(params)
#     res = search.get_dict()
#     if "error" in res:
#         print(f"❌ SerpAPI error for '{query}': {res['error']}")
#         return []
#     org = res.get("organic_results", []) or []
#     for item in org:
#         item["source_query"] = query
#     return org

# def collect_urls(query: str, cap: int = 20) -> List[Dict]:
#     """
#     Collect URLs for a single query using SerpAPI.
#     """
#     print(f"🔍 Searching for query: {query}")

#     seen = set()
#     results = []

#     for item in serpapi_search(query, num=cap):
#         url = item.get("link")
#         if url and url not in seen:
#             seen.add(url)
#             results.append(item)

#     print(f"✅ Unique URLs collected: {len(results)} (capped to {cap})")
#     return results[:cap]


# # ==========================
# # SCRAPER
# # ==========================

# HEADERS = {
#     "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                    "AppleWebKit/537.36 (KHTML, like Gecko) "
#                    "Chrome/120.0.0.0 Safari/537.36"),
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#     "Accept-Language": "en-US,en;q=0.5",
#     "Connection": "keep-alive",
# }

# CONTENT_SELECTORS = ['article', 'main', '[role="main"]', '.content', '.post-content', '.entry-content']

# REVIEW_SELECTORS = [
#     "div[class*='review']", "div[class*='comment']", "div[class*='feedback']",
#     "div[class*='testimonial']", "div[class*='opinion']", "div[class*='experience']",
#     "div[class*='customer-review']", "div[class*='user-review']",
#     "span[class*='review-text']", "p[class*='review-content']",
#     "div[data-hook='review-body']", "div[class*='review-text']",
#     "div[class*='_6K-7Co']", "div[class*='_16PBlm']",
#     "div[class*='post-content']", "div[class*='entry-content']",
#     "div[class*='comment-content']", "blockquote"
# ]

# RATING_SELECTORS = [
#     "span[class*='rating']", "div[class*='rating']", "span[class*='star']",
#     "div[class*='score']", "span[class*='points']", "[class*='rating-value']"
# ]

# PROSCONS_SELECTORS = [
#     "div[class*='pro']", "div[class*='con']", "li[class*='advantage']",
#     "li[class*='disadvantage']", "div[class*='positive']", "div[class*='negative']"
# ]

# def scrape_url(url: str) -> Dict:
#     try:
#         r = requests.get(url, headers=HEADERS, timeout=15)
#         if r.status_code != 200:
#             return {"content":"", "reviews":[], "ratings":[], "pros_cons":[], "num_reviews":0}

#         soup = BeautifulSoup(r.text, "html.parser")
#         for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
#             tag.decompose()

#         # Main content
#         content_text = ""
#         for sel in CONTENT_SELECTORS:
#             el = soup.select_one(sel)
#             if el:
#                 ps = [p.get_text(strip=True) for p in el.find_all("p") if len(p.get_text(strip=True)) > 20]
#                 content_text = " ".join(ps[:30])
#                 break
#         if not content_text:
#             ps = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 20]
#             content_text = " ".join(ps[:30])

#         # Reviews
#         reviews = []
#         for sel in REVIEW_SELECTORS:
#             for el in soup.select(sel):
#                 txt = el.get_text(strip=True)
#                 if 15 < len(txt) < 1200:
#                     reviews.append(txt)
#         # Ratings
#         ratings = []
#         for sel in RATING_SELECTORS:
#             for el in soup.select(sel):
#                 t = el.get_text(strip=True)
#                 if any(c.isdigit() for c in t) and len(t) < 50:
#                     ratings.append(t)
#         # Pros/Cons
#         pros_cons = []
#         for sel in PROSCONS_SELECTORS:
#             for el in soup.select(sel):
#                 t = el.get_text(strip=True)
#                 if 10 < len(t) < 250:
#                     pros_cons.append(t)

#         return {
#             "content": content_text,
#             "reviews": reviews[:30],
#             "ratings": ratings[:15],
#             "pros_cons": pros_cons[:15],
#             "num_reviews": len(reviews)
#         }
#     except Exception as e:
#         return {"content":"", "reviews":[], "ratings":[], "pros_cons":[], "num_reviews":0, "error": str(e)}

# # ==========================
# # FIXED MENTIONS & SENTIMENT & SOV
# # ==========================

# def count_mentions_fixed(text: str, brands: List[str]) -> Dict[str, int]:
#     """
#     FIXED VERSION: More robust brand mention counting
#     - Uses word boundaries to avoid partial matches
#     - Case insensitive matching
#     - Handles brand variations
#     """
#     if not text or not text.strip():
#         return {b: 0 for b in brands}
    
#     text_lower = text.lower()
#     mentions = {}
    
#     for brand in brands:
#         count = 0
#         brand_lower = brand.lower()
        
#         # Create pattern with word boundaries
#         # This prevents matching "Atomberg" in "XAtombergY" type scenarios
#         pattern = r'\b' + re.escape(brand_lower) + r'\b'
        
#         # Count exact brand matches
#         matches = re.findall(pattern, text_lower)
#         count += len(matches)
        
#         # Also check for common variations (optional)
#         if brand_lower == "atomberg":
#             # Look for variations like "atom berg", "atomberg fan", etc.
#             variations = [
#                 r'\batomberg\s+fan\b',
#                 r'\batomberg\s+renesa\b',
#                 r'\batomberg\s+studio\b'
#             ]
#             for var_pattern in variations:
#                 var_matches = re.findall(var_pattern, text_lower)
#                 count += len(var_matches)
        
#         mentions[brand] = count
    
#     return mentions

# def analyze_page_sentiment(content: str, reviews: List[str], brand: str) -> str:
#     """
#     Enhanced sentiment analysis that considers context around brand mentions
#     """
#     if not content and not reviews:
#         return "neutral"
    
#     # Combine all text
#     all_text = f"{content} {' '.join(reviews)}"
    
#     # If brand is mentioned, focus on sentences containing the brand
#     brand_sentences = []
#     sentences = re.split(r'[.!?]+', all_text)
    
#     for sentence in sentences:
#         if brand.lower() in sentence.lower():
#             brand_sentences.append(sentence.strip())
    
#     # If no brand-specific sentences, use general sentiment
#     text_to_analyze = ' '.join(brand_sentences) if brand_sentences else all_text
    
#     if not text_to_analyze.strip():
#         return "neutral"
    
#     # Use VADER for sentiment analysis
#     scores = SIA.polarity_scores(text_to_analyze)
#     compound = scores['compound']
    
#     # Threshold adjustment for more accurate classification
#     if compound >= 0.1:
#         return "positive"
#     elif compound <= -0.1:
#         return "negative"
#     else:
#         return "neutral"

# def compute_sov_fixed(pages_df: pd.DataFrame, brands: List[str]) -> Tuple[pd.DataFrame, Dict]:
#     """
#     FIXED VERSION: More accurate SOV calculation with debugging info
#     """
#     print(f"\n🔍 Computing SOV for {len(pages_df)} pages and {len(brands)} brands...")
    
#     # Initialize aggregation
#     agg = {b: {"mentions":0, "positive_pages":0, "negative_pages":0, "neutral_pages":0, "total_pages_with_mentions":0, "reviews":0} for b in brands}
    
#     # Debug: Track which pages mention which brands
#     debug_info = []
    
#     for idx, row in pages_df.iterrows():
#         content = str(row.get('content', ''))
#         reviews_text = str(row.get('reviews', ''))
#         combined_text = f"{content} {reviews_text}"
        
#         # Count mentions for each brand on this page
#         mentions = count_mentions_fixed(combined_text, brands)
        
#         # Debug info for this page
#         page_debug = {
#             'page_idx': idx,
#             'url': row.get('url', '')[:100],
#             'title': row.get('title', '')[:100],
#             'mentions': mentions,
#             'has_content': len(content.strip()) > 0,
#             'has_reviews': len(reviews_text.strip()) > 0,
#             'total_text_length': len(combined_text)
#         }
#         debug_info.append(page_debug)
        
#         # For each brand that has mentions on this page
#         for brand, mention_count in mentions.items():
#             agg[brand]["mentions"] += mention_count
            
#             if mention_count > 0:  # Only analyze sentiment if brand is mentioned
#                 agg[brand]["total_pages_with_mentions"] += 1
                
#                 # Analyze sentiment for this specific brand on this page
#                 sentiment = analyze_page_sentiment(content, reviews_text.split(' | '), brand)
#                 agg[brand][f"{sentiment}_pages"] += 1
                
#                 # Add review count (weighted by mentions)
#                 num_reviews = int(row.get("num_reviews", 0))
#                 agg[brand]["reviews"] += num_reviews
    
#     # Print debug information
#     print(f"\n📊 DEBUG INFO:")
#     total_mentions_found = sum(sum(page['mentions'].values()) for page in debug_info)
#     print(f"Total mentions found across all pages: {total_mentions_found}")
    
#     for brand in brands:
#         brand_total = sum(page['mentions'].get(brand, 0) for page in debug_info)
#         pages_with_brand = len([p for p in debug_info if p['mentions'].get(brand, 0) > 0])
#         print(f"{brand}: {brand_total} mentions across {pages_with_brand} pages")
    
#     # Calculate totals for SOV calculation
#     total_mentions = sum(v["mentions"] for v in agg.values())
#     total_positive_pages = sum(v["positive_pages"] for v in agg.values())
#     total_pages_with_mentions = sum(v["total_pages_with_mentions"] for v in agg.values())
#     total_reviews = sum(v["reviews"] for v in agg.values())
    
#     # Avoid division by zero
#     total_mentions = max(1, total_mentions)
#     total_positive_pages = max(1, total_positive_pages)
#     total_pages_with_mentions = max(1, total_pages_with_mentions)
#     total_reviews = max(1, total_reviews)
    
#     # Build SOV dataframe
#     rows = []
#     for brand, data in agg.items():
#         mention_sov = 100 * data["mentions"] / total_mentions
#         page_presence_sov = 100 * data["total_pages_with_mentions"] / len(pages_df)
#         positive_sov = 100 * data["positive_pages"] / total_positive_pages if total_positive_pages > 0 else 0
#         engagement_sov = 100 * data["reviews"] / total_reviews if total_reviews > 0 else 0
        
#         # Calculate sentiment balance for this brand
#         total_sentiment_pages = data["positive_pages"] + data["negative_pages"] + data["neutral_pages"]
#         if total_sentiment_pages > 0:
#             sentiment_balance = (data["positive_pages"] - data["negative_pages"]) / total_sentiment_pages
#         else:
#             sentiment_balance = 0
        
#         # Weighted SOV calculation
#         weight = (0.4 * (data["mentions"] / total_mentions)) + \
#                 (0.3 * (data["total_pages_with_mentions"] / len(pages_df))) + \
#                 (0.3 * (data["reviews"] / total_reviews))
        
#         weighted_sov = max(0, 100 * weight * (0.5 + 0.5 * sentiment_balance))
        
#         rows.append({
#             "brand": brand,
#             "mentions": data["mentions"],
#             "pages_with_mentions": data["total_pages_with_mentions"],
#             "positive_pages": data["positive_pages"],
#             "negative_pages": data["negative_pages"],
#             "neutral_pages": data["neutral_pages"],
#             "review_count": data["reviews"],
#             "mention_sov_%": round(mention_sov, 2),
#             "page_presence_sov_%": round(page_presence_sov, 2),
#             "positive_sov_%": round(positive_sov, 2),
#             "engagement_sov_%": round(engagement_sov, 2),
#             "sentiment_balance": round(sentiment_balance, 3),
#             "weighted_sov_%": round(weighted_sov, 2)
#         })
    
#     sov_df = pd.DataFrame(rows).sort_values("weighted_sov_%", ascending=False).reset_index(drop=True)
    
#     meta = {
#         "total_pages_analyzed": len(pages_df),
#         "total_mentions": total_mentions,
#         "total_pages_with_brand_mentions": total_pages_with_mentions,
#         "total_positive_pages": total_positive_pages,
#         "total_review_count": total_reviews,
#         "debug_info": debug_info
#     }
    
#     return sov_df, meta

# def sentiment_label(text: str) -> str:
#     """Keep the original function for backward compatibility"""
#     if not text or not text.strip():
#         return "neutral"
#     s = SIA.polarity_scores(text)
#     c = s["compound"]
#     if c >= 0.05: return "positive"
#     if c <= -0.05: return "negative"
#     return "neutral"

# # ==========================
# # GEMINI SUMMARIZATION
# # ==========================

# def summarize_page_with_gemini(query: str, page: Dict) -> str:
#     if GEMINI_MODEL is None:
#         return "(Gemini disabled: no API key)"
#     try:
#         # Add mention analysis to the summary
#         content = page.get('content', '')
#         reviews = ' '.join(page.get('reviews', []))
#         combined_text = f"{content} {reviews}"
        
#         mentions = count_mentions_fixed(combined_text, BRANDS)
#         mentioned_brands = [brand for brand, count in mentions.items() if count > 0]
        
#         prompt = f"""
# You are analyzing search results about smart fans, focusing on brand mentions and customer sentiment.

# Query: {query}

# BRANDS MENTIONED ON THIS PAGE: {', '.join(mentioned_brands) if mentioned_brands else 'None detected'}
# MENTION COUNTS: {mentions}

# CONTENT:
# {content}

# REVIEWS ({len(page.get('reviews',[]))}):
# - {chr(10).join(page.get('reviews',[])[:10])}

# RATINGS:
# {", ".join(page.get('ratings',[])[:10])}

# PROS/CONS:
# - {chr(10).join(page.get('pros_cons',[])[:10])}

# Return a structured, concise output focusing on:

# **Brands Mentioned**
# - Which specific fan brands are discussed and in what context

# **Key Points**
# - Main topics and themes

# **Customer Sentiment**
# - Overall sentiment and specific brand feedback

# **Common Praise**
# - Positive aspects mentioned

# **Common Complaints** 
# - Issues and concerns raised

# **Ratings Summary**
# - Rating information if available

# **Brand Comparison**
# - How different brands are compared (if applicable)
# """
#         resp = GEMINI_MODEL.generate_content(prompt)
#         return resp.text.strip()
#     except Exception as e:
#         return f"(Gemini summarization error: {e})"

# # ==========================
# # RECOMMENDATIONS (Gemini)
# # ==========================

# def recommendations_with_gemini(sov_df: pd.DataFrame, query_list: List[str], meta: Dict) -> str:
#     if GEMINI_MODEL is None:
#         return "(Gemini disabled: no API key)"
#     try:
#         # Add more context for better recommendations
#         atomberg_data = sov_df[sov_df['brand'] == 'Atomberg'].iloc[0] if len(sov_df[sov_df['brand'] == 'Atomberg']) > 0 else None
        
#         prompt = f"""
# We analyzed Share of Voice for smart fan brands in India based on {meta['total_pages_analyzed']} Google search result pages.

# ANALYSIS SUMMARY:
# - Total pages analyzed: {meta['total_pages_analyzed']}
# - Total brand mentions found: {meta['total_mentions']}
# - Pages with brand mentions: {meta['total_pages_with_brand_mentions']}

# Queries analyzed:
# {json.dumps(query_list, indent=2)}

# COMPLETE SoV RESULTS:
# {sov_df.to_string(index=False)}

# ATOMBERG SPECIFIC METRICS:
# {atomberg_data.to_dict() if atomberg_data is not None else "No Atomberg data found"}

# COMPETITIVE LANDSCAPE:
# Top 3 brands by weighted SOV:
# {sov_df.head(3)[['brand', 'weighted_sov_%', 'mentions', 'pages_with_mentions', 'sentiment_balance']].to_string(index=False)}

# Please provide:

# 1. **ATOMBERG POSITION ANALYSIS**
#    - Current market position vs competitors
#    - Strengths and weaknesses in online presence
   
# 2. **CONTENT GAPS & OPPORTUNITIES**  
#    - What topics/keywords Atomberg should focus on
#    - Where competitors are winning and why
   
# 3. **SENTIMENT INSIGHTS**
#    - What's driving positive vs negative sentiment
#    - How Atomberg compares to competitors on sentiment
   
# 4. **ACTIONABLE RECOMMENDATIONS (Next 30 days)**
#    - High-impact, specific actions for content team
#    - Platform-specific strategies
#    - Keyword/topic priorities
   
# 5. **MEASUREMENT & TRACKING**
#    - Key metrics to monitor SOV improvement
#    - Success indicators for recommendations

# Focus on practical, implementable strategies that can measurably improve Atomberg's Share of Voice.
# """
#         resp = GEMINI_MODEL.generate_content(prompt)
#         return resp.text.strip()
#     except Exception as e:
#         return f"(Gemini recommendation error: {e})"

# # ==========================
# # MAIN PIPELINE (Updated)
# # ==========================

# def main(query, num_results):
#     print(query)
#     if not SERPAPI_KEY:
#         print("❌ Missing SERPAPI_KEY.")
#         return
#     if not GEMINI_API_KEY:
#         print("⚠️ Warning: Missing GEMINI_API_KEY. Summaries & recommendations will be disabled.")

#     # print(f"🚀 Starting SOV analysis for brands: {', '.join(BRANDS)}")
#     # print(f"📝 Base queries: {len(BASE_QUERIES)}")

#     # Build diversified query list
#     # queries = []
#     # for base in BASE_QUERIES:
#     #     queries += expand_queries(base)

#     # print(f"📈 Total queries to process: {len(queries)}")

#     # Collect URLs
#     results = collect_urls(query, num_results)

#     if not results:
#         print("❌ No URLs collected. Check your SerpAPI key or queries.")
#         return

#     rows = []
#     for i, item in enumerate(results, 1):
#         title = item.get("title", "")
#         url = item.get("link", "")
#         snippet = item.get("snippet", "")
#         source_query = item.get("source_query", "")

#         print(f"\n📄 [{i}/{len(results)}] {title[:80]}")
#         print(f"🔗 {url[:100]}")
        
#         page = scrape_url(url)
        
#         # Quick check for brand mentions in scraped content
#         combined_content = f"{page['content']} {' '.join(page['reviews'])}"
#         quick_mentions = count_mentions_fixed(combined_content, BRANDS)
#         brands_found = [b for b, c in quick_mentions.items() if c > 0]
#         if brands_found:
#             print(f"🏷️ Brands found: {', '.join(brands_found)}")

#         # page summary
#         summary = summarize_page_with_gemini(source_query, page)

#         rows.append({
#             "title": title,
#             "url": url,
#             "snippet": snippet,
#             "source_query": source_query,
#             "content": page["content"][:2000],  # Increased limit
#             "reviews": " | ".join(page["reviews"][:15]),  # More reviews
#             "num_reviews": page.get("num_reviews", 0),
#             "ratings": "; ".join(page.get("ratings", [])),
#             "pros_cons": "; ".join(page.get("pros_cons", [])),
#             "summary": summary,
#             "brands_mentioned": ', '.join(brands_found)  # New field
#         })
#         time.sleep(random.uniform(1.0, 2.0))  # Reduced delay

#     pages_df = pd.DataFrame(rows)
#     ts = datetime.now().strftime("%Y%m%d_%H%M%S")
#     pages_csv = f"pages_atomberg_{ts}.csv"
#     pages_df.to_csv(pages_csv, index=False, encoding="utf-8")
#     print(f"\n✅ Saved per-page data: {pages_csv}")

#     # SOV with fixed calculation
#     print(f"\n🔢 Calculating Share of Voice...")
#     sov_df, meta = compute_sov_fixed(pages_df, BRANDS)
    
#     sov_csv = f"sov_summary_{ts}.csv"
#     sov_df.to_csv(sov_csv, index=False, encoding="utf-8")
#     print(f"✅ Saved SoV summary: {sov_csv}")
    
#     print(f"\n📊 SHARE OF VOICE RESULTS:")
#     print("=" * 80)
#     print(sov_df[["brand","mentions","pages_with_mentions","weighted_sov_%","mention_sov_%","sentiment_balance"]].to_string(index=False))
    
#     print(f"\n📈 METADATA:")
#     print(f"Total pages analyzed: {meta['total_pages_analyzed']}")
#     print(f"Total brand mentions: {meta['total_mentions']}")
#     print(f"Pages with brand mentions: {meta['total_pages_with_brand_mentions']}")

#     # Recommendations with enhanced context
#     print(f"\n🎯 Generating recommendations...")
#     rec_md = f"recommendations_{ts}.md"
#     rec_text = recommendations_with_gemini(sov_df, BASE_QUERIES, meta)
#     with open(rec_md, "w", encoding="utf-8") as f:
#         f.write("# Share of Voice Analysis - Recommendations\n\n")
#         f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
#         f.write(f"## Analysis Summary\n")
#         f.write(f"- Pages analyzed: {meta['total_pages_analyzed']}\n")
#         f.write(f"- Total brand mentions: {meta['total_mentions']}\n")
#         f.write(f"- Atomberg SOV: {sov_df[sov_df['brand'] == 'Atomberg']['weighted_sov_%'].iloc[0] if len(sov_df[sov_df['brand'] == 'Atomberg']) > 0 else 0}%\n\n")
#         f.write(rec_text)
#     print(f"✅ Saved recommendations: {rec_md}")

#     print(f"\n🎉 Analysis complete! Check the generated files:")
#     print(f"   📄 {pages_csv}")
#     print(f"   📊 {sov_csv}")
#     print(f"   📝 {rec_md}")
















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

# CONFIG
SERPAPI_KEY = "84abd1561ae6f81ea2f3ecd5df1c401191c1a93f38d2ec1b19b3f5d9a3e64e8b"
COUNTRY = "in"
LANG = "en"
LOCATION = "Mumbai,Maharashtra,India"
BRANDS = ["Atomberg", "Crompton", "Havells", "Orient", "Usha", "Bajaj", "Luminous", "Polar"]

# Initialize
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

SIA = SentimentIntensityAnalyzer()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def serpapi_search(query: str, num: int = 10) -> List[Dict]:
    """Search using SerpAPI"""
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
        print(f"❌ SerpAPI error: {e}")
        return []

def scrape_basic_content(url: str) -> Dict:
    """Basic content scraping"""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return {"content": "", "reviews": []}

        soup = BeautifulSoup(r.text, "html.parser")
        
        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()

        # Get main content
        content = ""
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 20:
                content += text + " "

        # Get reviews (simple approach)
        reviews = []
        review_selectors = ["div[class*='review']", "div[class*='comment']", "div[class*='feedback']"]
        for sel in review_selectors:
            for el in soup.select(sel):
                text = el.get_text(strip=True)
                if 15 < len(text) < 500:
                    reviews.append(text)

        return {
            "content": content[:1000],  # Limit content
            "reviews": reviews[:5]      # Limit reviews
        }
    except Exception as e:
        return {"content": "", "reviews": [], "error": str(e)}

def count_brand_mentions(text: str) -> Dict[str, int]:
    """Count brand mentions in text"""
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
    """Simple sentiment analysis"""
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
    """Main function that returns results"""
    print(f"🔍 Searching for: {query}")
    
    if not SERPAPI_KEY:
        return {"error": "Missing SERPAPI_KEY"}
    
    # Search Google
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
            
            print(f"📄 [{i}] Processing: {title[:50]}...")
            
            # Scrape content
            scraped = scrape_basic_content(url)
            
            # Combine all text for analysis
            all_text = f"{title} {snippet} {scraped['content']} {' '.join(scraped['reviews'])}"
            
            # Count brand mentions
            mentions = count_brand_mentions(all_text)
            
            # Analyze sentiment
            sentiment = analyze_sentiment(all_text)
            
            # Update brand analysis
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
        
        # Add delay to be respectful
        time.sleep(random.uniform(0.5, 1.0))
    
    # Calculate Share of Voice  
    try:
        total_mentions = sum(brand_data["mentions"] for brand_data in brand_analysis.values())
        print(f"🔢 Total mentions calculated: {total_mentions}")
    except Exception as e:
        print(f"Error calculating total mentions: {e}")
        total_mentions = 1  # Avoid division by zero
    
    sov_summary = {}
    for brand, data in brand_analysis.items():
        mentions = data["mentions"]
        if total_mentions > 0:
            sov_percentage = (mentions / total_mentions) * 100
        else:
            sov_percentage = 0
            
        # Calculate sentiment distribution
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
    
    # Sort brands by SOV
    top_brands = sorted(sov_summary.items(), key=lambda x: x[1]["sov_percentage"], reverse=True)
    
    # Return comprehensive results
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