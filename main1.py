import time
import re
import json
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import google.generativeai as genai
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== GEMINI CONFIG =====================
genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your actual API key

# ===================== CONFIGURATION =====================
TARGET_BRAND = 'Atomberg'
COMPETITORS = ['Havells', 'Orient', 'Usha', 'Crompton']
ALL_BRANDS = [TARGET_BRAND] + COMPETITORS

def setup_driver():
    """Setup Chrome driver with proper options"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        logger.error(f"Failed to setup Chrome driver: {e}")
        return None

def is_valid_url(url):
    """Check if URL is valid and not a Google internal link"""
    if not url or not url.startswith('http'):
        return False
    
    exclude_domains = [
        'google.com', 'youtube.com/redirect', 'accounts.google',
        'support.google', 'policies.google', 'webcache.googleusercontent'
    ]
    
    return not any(domain in url for domain in exclude_domains)

def google_search_improved(query, num_results=15):
    """Improved Google search with better element targeting"""
    driver = setup_driver()
    if not driver:
        return []
        
    urls = []
    try:
        logger.info(f"Searching for: {query}")
        driver.get("https://www.google.com")
        
        # Wait for search box and search
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        # Wait for results to load
        time.sleep(3)
        
        # Try multiple selectors for search results
        selectors = [
            'div.g a[href]:not([href^="/"])',  # Standard results
            'div[data-ved] a[href]:not([href^="/"])',  # Alternative
            '.rc .r a',  # Classic selector
            'h3 a[href]'  # Header links
        ]
        
        for selector in selectors:
            try:
                links = driver.find_elements(By.CSS_SELECTOR, selector)
                logger.info(f"Found {len(links)} links with selector: {selector}")
                
                for link in links:
                    try:
                        href = link.get_attribute("href")
                        if is_valid_url(href):
                            urls.append(href)
                            if len(urls) >= num_results:
                                break
                    except:
                        continue
                
                if urls:
                    break
            except Exception as e:
                logger.warning(f"Selector {selector} failed: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Google search failed: {e}")
    finally:
        driver.quit()
        
    logger.info(f"Found {len(urls)} valid URLs")
    return urls[:num_results]

def scrape_page_content(url, max_length=8000):
    """Enhanced page scraping with better error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove unwanted elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.extract()
        
        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text[:max_length]
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return ""

def count_brand_mentions(text):
    """Count mentions of each brand in the text"""
    mentions = {}
    text_lower = text.lower()
    
    for brand in ALL_BRANDS:
        # Count exact matches and variations
        patterns = [
            brand.lower(),
            brand.lower() + ' fan',
            brand.lower() + ' fans',
            brand.lower() + 'fan',  # Sometimes written together
        ]
        
        count = 0
        for pattern in patterns:
            count += len(re.findall(r'\b' + re.escape(pattern) + r'\b', text_lower))
        
        mentions[brand] = count
    
    return mentions

def extract_engagement_metrics(text, url):
    """Extract potential engagement indicators from text"""
    engagement = {
        'url': url,
        'total_words': len(text.split()),
        'has_reviews': bool(re.search(r'review|rating|star|comment', text.lower())),
        'has_prices': bool(re.search(r'₹|rs\.|price|cost|rupee', text.lower())),
        'has_features': bool(re.search(r'speed|remote|led|energy|bldc', text.lower())),
        'social_indicators': len(re.findall(r'like|share|comment|follow', text.lower()))
    }
    
    return engagement

def analyze_with_gemini(scraped_data, query):
    """Send scraped data to Gemini for advanced analysis"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Prepare data for Gemini
    all_text = ""
    total_mentions = {brand: 0 for brand in ALL_BRANDS}
    
    for data in scraped_data:
        all_text += f"\n--- {data['url']} ---\n{data['text']}\n"
        for brand, count in data['mentions'].items():
            total_mentions[brand] += count
    
    prompt = f"""
    Analyze the following scraped content for Share of Voice analysis of {TARGET_BRAND} vs competitors.

    QUERY: {query}
    COMPETITORS: {', '.join(COMPETITORS)}
    TARGET BRAND: {TARGET_BRAND}

    CONTENT FROM {len(scraped_data)} SOURCES:
    {all_text[:15000]}  # Limit to avoid token limits

    QUANTITATIVE DATA:
    Brand mentions found: {json.dumps(total_mentions, indent=2)}

    Please provide a comprehensive analysis in JSON format including:
    {{
        "share_of_voice": {{
            "total_mentions": {{}},
            "percentage_share": {{}},
            "atomberg_sov_percentage": 0
        }},
        "sentiment_analysis": {{
            "atomberg": {{"positive": 0, "negative": 0, "neutral": 0}},
            "competitors": {{"positive": 0, "negative": 0, "neutral": 0}}
        }},
        "key_insights": [
            "insight 1",
            "insight 2"
        ],
        "content_themes": [
            "theme 1",
            "theme 2"
        ],
        "recommendations": [
            "recommendation 1",
            "recommendation 2"
        ],
        "competitive_analysis": {{
            "atomberg_strengths": [],
            "atomberg_weaknesses": [],
            "competitor_strengths": []
        }}
    }}

    Focus on:
    1. Calculate exact Share of Voice percentage for {TARGET_BRAND}
    2. Identify sentiment patterns
    3. Extract key product features mentioned
    4. Note any pricing discussions
    5. Identify content gaps and opportunities
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Gemini analysis failed: {e}")
        return f"Analysis failed: {e}"

def calculate_sov_metrics(scraped_data):
    """Calculate Share of Voice metrics from scraped data"""
    total_mentions = {brand: 0 for brand in ALL_BRANDS}
    url_mentions = []
    
    for data in scraped_data:
        url_mentions.append({
            'url': data['url'],
            'mentions': data['mentions'],
            'engagement': data['engagement']
        })
        
        for brand, count in data['mentions'].items():
            total_mentions[brand] += count
    
    # Calculate percentages
    total_all_mentions = sum(total_mentions.values())
    sov_percentages = {}
    
    if total_all_mentions > 0:
        for brand, count in total_mentions.items():
            sov_percentages[brand] = (count / total_all_mentions) * 100
    else:
        sov_percentages = {brand: 0 for brand in ALL_BRANDS}
    
    return {
        'total_mentions': total_mentions,
        'sov_percentages': sov_percentages,
        'atomberg_sov': sov_percentages.get(TARGET_BRAND, 0),
        'url_breakdown': url_mentions,
        'total_sources': len(scraped_data)
    }

def main():
    """Main function to run the Share of Voice analysis"""
    
    # Keywords to analyze - you can modify these
    keywords = [
        "smart fan reviews India",
        "best BLDC fan 2024",
        "ceiling fan with remote control",
        "energy efficient fans India",
        "smart home fans with app control"
    ]
    
    all_results = {}
    
    for keyword in keywords:
        print(f"\n{'='*60}")
        print(f"ANALYZING KEYWORD: {keyword}")
        print(f"{'='*60}")
        
        # Step 1: Get URLs from Google search
        urls = google_search_improved(keyword, num_results=12)
        
        if not urls:
            print(f"No URLs found for keyword: {keyword}")
            continue
        
        print(f"Found {len(urls)} URLs to scrape")
        
        # Step 2: Scrape content from each URL
        scraped_data = []
        for i, url in enumerate(urls, 1):
            print(f"Scraping {i}/{len(urls)}: {url[:80]}...")
            
            text = scrape_page_content(url)
            if text:
                mentions = count_brand_mentions(text)
                engagement = extract_engagement_metrics(text, url)
                
                scraped_data.append({
                    'url': url,
                    'text': text,
                    'mentions': mentions,
                    'engagement': engagement
                })
            
            time.sleep(1)  # Be respectful to servers
        
        print(f"Successfully scraped {len(scraped_data)} pages")
        
        # Step 3: Calculate metrics
        metrics = calculate_sov_metrics(scraped_data)
        
        # Step 4: Get AI insights
        print("\nGetting AI analysis...")
        ai_insights = analyze_with_gemini(scraped_data, keyword)
        
        # Store results
        all_results[keyword] = {
            'metrics': metrics,
            'ai_insights': ai_insights,
            'scraped_urls': len(urls)
        }
        
        # Print summary for this keyword
        print(f"\n--- SUMMARY FOR '{keyword}' ---")
        print(f"Atomberg Share of Voice: {metrics['atomberg_sov']:.1f}%")
        print(f"Total brand mentions found: {sum(metrics['total_mentions'].values())}")
        print(f"Brand breakdown: {metrics['total_mentions']}")
        print("\nAI Insights:")
        print(ai_insights[:1000] + "..." if len(ai_insights) > 1000 else ai_insights)
    
    # Final consolidated report
    print(f"\n{'='*80}")
    print("CONSOLIDATED SHARE OF VOICE REPORT")
    print(f"{'='*80}")
    
    overall_mentions = {brand: 0 for brand in ALL_BRANDS}
    total_keywords = len([k for k in all_results.keys() if all_results[k]['scraped_urls'] > 0])
    
    for keyword, results in all_results.items():
        if results['scraped_urls'] > 0:
            for brand, count in results['metrics']['total_mentions'].items():
                overall_mentions[brand] += count
    
    # Calculate overall SOV
    total_overall = sum(overall_mentions.values())
    if total_overall > 0:
        overall_sov = (overall_mentions[TARGET_BRAND] / total_overall) * 100
    else:
        overall_sov = 0
    
    print(f"\nOVERALL RESULTS ACROSS {total_keywords} KEYWORDS:")
    print(f"Atomberg Overall Share of Voice: {overall_sov:.1f}%")
    print(f"Total mentions across all keywords: {overall_mentions}")
    
    for brand in ALL_BRANDS:
        if total_overall > 0:
            pct = (overall_mentions[brand] / total_overall) * 100
            print(f"{brand}: {overall_mentions[brand]} mentions ({pct:.1f}%)")
    
    return all_results

if __name__ == "__main__":
    results = main()