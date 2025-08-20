# from serpapi import GoogleSearch
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# import time
# import os
# import google.generativeai as genai
# import random
# from urllib.parse import urljoin, urlparse

# # 🔑 API Keys
# SERP_API_KEY = "84abd1561ae6f81ea2f3ecd5df1c401191c1a93f38d2ec1b19b3f5d9a3e64e8b"
# GEMINI_KEY = "AIzaSyC6BoubGrOh_hCN_oBLFrRhTOweaNZFzUY" 

# # Configure Gemini
# genai.configure(api_key=GEMINI_KEY)
# gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# # ------------------ ENHANCED SEARCH ------------------
# def check_serpapi_key():
#     if not SERP_API_KEY:
#         print("❌ SERP_API_KEY not found!")
#         return False
#     return True

# def google_search_serpapi_multiple_queries(base_query, num_results=15):
#     """Search with multiple related queries to get more diverse results"""
    
#     # Create variations of the query for better coverage
#     query_variations = [
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
    
#     all_results = []
#     seen_urls = set()
    
#     for i, query in enumerate(query_variations):
#         print(f"🔍 Query {i+1}/{len(query_variations)}: {query}")
        
#         try:
#             search = GoogleSearch({
#                 "q": query,
#                 "engine": "google",
#                 "num": 10,  # Get 10 per query
#                 "hl": "en",
#                 "gl": "in",
#                 "api_key": SERP_API_KEY,
#                 "location": "Mumbai,Maharashtra,India"
#             })
#             results = search.get_dict()
            
#             if "error" in results:
#                 print(f"❌ SerpAPI Error for '{query}': {results['error']}")
#                 continue
                
#             organic_results = results.get("organic_results", [])
            
#             # Add unique results
#             for result in organic_results:
#                 url = result.get("link", "")
#                 if url and url not in seen_urls:
#                     seen_urls.add(url)
#                     result["source_query"] = query
#                     all_results.append(result)
                    
#             time.sleep(1)  # Rate limiting
            
#         except Exception as e:
#             print(f"❌ Error in search '{query}': {str(e)}")
#             continue
    
#     print(f"✅ Total unique results found: {len(all_results)}")
#     return all_results[:num_results]  # Return requested number

# # ------------------ ENHANCED SCRAPER ------------------
# def scrape_page_enhanced(url):
#     """Enhanced scraping with better comment/review detection"""
#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                           "AppleWebKit/537.36 (KHTML, like Gecko) "
#                           "Chrome/120.0.0.0 Safari/537.36",
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
#             "Accept-Language": "en-US,en;q=0.5",
#             "Accept-Encoding": "gzip, deflate",
#             "Connection": "keep-alive",
#             "Upgrade-Insecure-Requests": "1",
#         }
        
#         response = requests.get(url, headers=headers, timeout=15)
#         if response.status_code != 200:
#             print(f"⚠️ Status {response.status_code} for {url}")
#             return {"url": url, "content": "", "reviews": [], "ratings": [], "pros_cons": []}

#         soup = BeautifulSoup(response.text, "html.parser")

#         # Remove unwanted elements
#         for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
#             script.decompose()

#         # Extract main content
#         content_selectors = ['article', 'main', '[role="main"]', '.content', '.post-content', '.entry-content']
#         main_content = ""
        
#         for selector in content_selectors:
#             content_elem = soup.select_one(selector)
#             if content_elem:
#                 paragraphs = [p.get_text(strip=True) for p in content_elem.find_all("p") if len(p.get_text(strip=True)) > 20]
#                 main_content = " ".join(paragraphs[:25])  # More content
#                 break
        
#         if not main_content:
#             # Fallback to all paragraphs
#             paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 20]
#             main_content = " ".join(paragraphs[:25])

#         # Enhanced comment/review extraction
#         reviews = []
#         review_selectors = [
#             # General review patterns
#             "div[class*='review']", "div[class*='comment']", "div[class*='feedback']",
#             "div[class*='testimonial']", "div[class*='opinion']", "div[class*='experience']",
            
#             # E-commerce specific
#             "div[class*='customer-review']", "div[class*='user-review']", 
#             "span[class*='review-text']", "p[class*='review-content']",
            
#             # Amazon/Flipkart specific
#             "div[data-hook='review-body']", "div[class*='review-text']",
#             "div[class*='_6K-7Co']", "div[class*='_16PBlm']",  # Flipkart classes
            
#             # Forum/Blog specific
#             "div[class*='post-content']", "div[class*='entry-content']",
#             "div[class*='comment-content']", "blockquote",
            
#             # Social media patterns
#             "div[class*='tweet-text']", "div[class*='post-text']"
#         ]
        
#         for selector in review_selectors:
#             for element in soup.select(selector):
#                 review_text = element.get_text(strip=True)
#                 if 15 < len(review_text) < 1000:  # Filter reasonable length reviews
#                     reviews.append(review_text)

#         # Extract ratings/scores
#         ratings = []
#         rating_selectors = [
#             "span[class*='rating']", "div[class*='rating']", "span[class*='star']",
#             "div[class*='score']", "span[class*='points']", "[class*='rating-value']"
#         ]
        
#         for selector in rating_selectors:
#             for element in soup.select(selector):
#                 rating_text = element.get_text(strip=True)
#                 if any(char.isdigit() for char in rating_text) and len(rating_text) < 50:
#                     ratings.append(rating_text)

#         # Extract pros/cons if available
#         pros_cons = []
#         pros_cons_selectors = [
#             "div[class*='pro']", "div[class*='con']", "li[class*='advantage']",
#             "li[class*='disadvantage']", "div[class*='positive']", "div[class*='negative']"
#         ]
        
#         for selector in pros_cons_selectors:
#             for element in soup.select(selector):
#                 pc_text = element.get_text(strip=True)
#                 if 10 < len(pc_text) < 200:
#                     pros_cons.append(pc_text)

#         return {
#             "url": url,
#             "content": main_content,
#             "reviews": reviews[:20],  # More reviews
#             "ratings": ratings[:10],
#             "pros_cons": pros_cons[:10],
#             "total_reviews_found": len(reviews)
#         }

#     except Exception as e:
#         print(f"⚠️ Error scraping {url}: {str(e)}")
#         return {"url": url, "content": "", "reviews": [], "ratings": [], "pros_cons": [], "error": str(e)}

# # ------------------ ENHANCED GEMINI SUMMARIZER ------------------
# def summarize_with_gemini_enhanced(query, content, reviews, ratings, pros_cons, source_query):
#     """Enhanced Gemini summarization with structured output"""
#     try:
#         # Prepare data for summarization
#         reviews_text = "\n".join([f"- {review}" for review in reviews[:15]])  # More reviews
#         ratings_text = ", ".join(ratings[:8])
#         pros_cons_text = "\n".join([f"- {pc}" for pc in pros_cons[:8]])
        
#         text_to_summarize = f"""
#         Original Query: {query}
#         Source Query: {source_query}
        
#         CONTENT:
#         {content}
        
#         CUSTOMER REVIEWS ({len(reviews)} found):
#         {reviews_text}
        
#         RATINGS/SCORES:
#         {ratings_text}
        
#         PROS/CONS:
#         {pros_cons_text}
        
#         TASK:
#         Please provide a structured summary in the following format:
        
#         **Key Points:**
#         - [Main factual information]
        
#         **Customer Sentiment:**
#         - [Overall sentiment from reviews]
        
#         **Common Praise:**
#         - [What customers like]
        
#         **Common Complaints:**
#         - [What customers complain about]
        
#         **Ratings Summary:**
#         - [Rating information if available]
        
#         **Recommendation:**
#         - [Brief recommendation based on the data]
        
#         Keep it concise but informative.
#         """
        
#         response = gemini_model.generate_content(text_to_summarize)
#         return response.text.strip()
        
#     except Exception as e:
#         print(f"⚠️ Gemini summarization error: {str(e)}")
#         return f"Summarization failed: {str(e)}"

# # ------------------ ENHANCED PIPELINE ------------------
# def run_enhanced_pipeline(query="Atomberg fan", num_results=20):
#     """Enhanced pipeline with better data collection"""
#     if not check_serpapi_key():
#         return None

#     print(f"🚀 Starting Enhanced Search Pipeline")
#     print(f"🔎 Base Query: '{query}'")
#     print(f"🎯 Target Results: {num_results}")
#     print("=" * 60)

#     # Get diverse search results
#     search_results = google_search_serpapi_multiple_queries(query, num_results)

#     if not search_results:
#         print("❌ No search results found")
#         return None

#     print(f"✅ Processing {len(search_results)} unique URLs")
    
#     data = []
#     successful_scrapes = 0
    
#     for i, result in enumerate(search_results, 1):
#         url = result.get("link")
#         title = result.get("title", "No title")
#         snippet = result.get("snippet", "")
#         source_query = result.get("source_query", query)

#         print(f"\n📑 ({i}/{len(search_results)}) Scraping: {title[:100]}...")
#         print(f"    🔗 URL: {url}")
#         print(f"    🔍 From query: {source_query}")
        
#         page_data = scrape_page_enhanced(url)
        
#         if len(page_data.get("reviews", [])) > 0 or len(page_data.get("content", "")) > 100:
#             successful_scrapes += 1
#             print(f"    ✅ Found {page_data.get('total_reviews_found', 0)} reviews")
#         else:
#             print(f"    ⚠️ Limited content found")

#         # Generate enhanced summary
#         summary = summarize_with_gemini_enhanced(
#             query,
#             page_data.get("content", ""),
#             page_data.get("reviews", []),
#             page_data.get("ratings", []),
#             page_data.get("pros_cons", []),
#             source_query
#         )

#         data.append({
#             "title": title,
#             "url": url,
#             "snippet": snippet,
#             "source_query": source_query,
#             "content": page_data["content"][:800],  # More content
#             "reviews": "; ".join(page_data["reviews"][:10]),  # More reviews
#             "num_reviews": page_data.get("total_reviews_found", 0),
#             "ratings": "; ".join(page_data.get("ratings", [])),
#             "pros_cons": "; ".join(page_data.get("pros_cons", [])),
#             "summary": summary,
#             "scraped_successfully": len(page_data["content"]) > 0 or len(page_data.get("reviews", [])) > 0
#         })

#         # Random delay to be respectful
#         time.sleep(random.uniform(1.5, 3))

#     # Create enhanced DataFrame and save
#     df = pd.DataFrame(data)
#     output_file = f"atomberg_enhanced_results_{int(time.time())}.csv"
#     df.to_csv(output_file, index=False, encoding="utf-8")

#     print(f"\n" + "="*60)
#     print(f"✅ Enhanced Results saved to {output_file}")
#     print(f"📊 Summary:")
#     print(f"   • Total URLs processed: {len(df)}")
#     print(f"   • Successful scrapes: {successful_scrapes}")
#     print(f"   • URLs with reviews: {(df['num_reviews'] > 0).sum()}")
#     print(f"   • Total reviews collected: {df['num_reviews'].sum()}")
#     print(f"   • Average reviews per page: {df['num_reviews'].mean():.1f}")
    
#     return df

# def analyze_enhanced_results(df):
#     """Enhanced analysis of results"""
#     if df is None or df.empty:
#         return
        
#     print("\n📈 DETAILED ANALYSIS:")
#     print("=" * 40)
    
#     # Overall stats
#     print(f"📊 Overall Statistics:")
#     print(f"   • Total pages: {len(df)}")
#     print(f"   • Successfully scraped: {df['scraped_successfully'].sum()}")
#     print(f"   • Pages with reviews: {(df['num_reviews'] > 0).sum()}")
#     print(f"   • Total reviews: {df['num_reviews'].sum()}")
#     print(f"   • Average content length: {df['content'].str.len().mean():.0f} characters")
    
#     # Top performing pages
#     top_review_pages = df.nlargest(5, 'num_reviews')
#     print(f"\n🏆 Top 5 Pages by Review Count:")
#     for idx, row in top_review_pages.iterrows():
#         print(f"   • {row['num_reviews']} reviews: {row['title'][:80]}...")
    
#     # Query analysis
#     query_stats = df.groupby('source_query')['num_reviews'].agg(['count', 'sum', 'mean']).sort_values('sum', ascending=False)
#     print(f"\n🔍 Best Performing Queries:")
#     for query, stats in query_stats.head(5).iterrows():
#         print(f"   • '{query}': {stats['sum']} total reviews from {stats['count']} pages")

# # ------------------ RUN ENHANCED VERSION ------------------
# if __name__ == "__main__":
#     print("🚀 ENHANCED ATOMBERG FAN DATA COLLECTION")
#     print("=" * 60)
    
#     # Run enhanced pipeline with more results
#     df = run_enhanced_pipeline("Atomberg fan", num_results=25)
    
#     if df is not None:
#         analyze_enhanced_results(df)
        
#         print("\n📋 Sample of Enhanced Results:")
#         sample_df = df[df['num_reviews'] > 0].head(3)
#         for idx, row in sample_df.iterrows():
#             print(f"\n📄 {row['title'][:100]}...")
#             print(f"   🔢 Reviews: {row['num_reviews']}")
#             print(f"   📝 Summary: {row['summary'][:200]}...")
#     else:
#         print("❌ Pipeline failed - no data collected")









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

# # ==========================
# # CONFIG
# # ==========================

# SERPAPI_KEY = "84abd1561ae6f81ea2f3ecd5df1c401191c1a93f38d2ec1b19b3f5d9a3e64e8b"
# GEMINI_API_KEY = "AIzaSyC6BoubGrOh_hCN_oBLFrRhTOweaNZFzUY"

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

# def collect_urls(queries: List[str], cap: int) -> List[Dict]:
#     seen = set()
#     results = []
#     for i, q in enumerate(queries, 1):
#         print(f"🔍 [{i}/{len(queries)}] {q}")
#         for item in serpapi_search(q, num=10):
#             url = item.get("link")
#             if url and url not in seen:
#                 seen.add(url)
#                 results.append(item)
#         time.sleep(1.0)
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

# def main():
#     if not SERPAPI_KEY:
#         print("❌ Missing SERPAPI_KEY.")
#         return
#     if not GEMINI_API_KEY:
#         print("⚠️ Warning: Missing GEMINI_API_KEY. Summaries & recommendations will be disabled.")

#     print(f"🚀 Starting SOV analysis for brands: {', '.join(BRANDS)}")
#     print(f"📝 Base queries: {len(BASE_QUERIES)}")

#     # Build diversified query list
#     queries = []
#     for base in BASE_QUERIES:
#         queries += expand_queries(base)

#     print(f"📈 Total queries to process: {len(queries)}")

#     # Collect URLs
#     results = collect_urls(queries, cap=TOP_N_URLS)

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

# if __name__ == "__main__":
#     main()













from agents.agent import create_google_crew, create_youtube_crew

if __name__ == "__main__":
    query = "Atomberg fan reviews"   # you can make this dynamic later

    # Run Google Crew
    google_crew = create_google_crew(query, num_results=15)
    google_results = google_crew.kickoff()
    print("\n🔍 Google Results:\n", google_results)

    # Run YouTube Crew
    youtube_crew = create_youtube_crew(query, num_results=15)
    youtube_results = youtube_crew.kickoff()
    print("\n📺 YouTube Results:\n", youtube_results)


