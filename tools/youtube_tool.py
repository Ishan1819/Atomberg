# tools/youtube_tool.py
from crewai.tools import BaseTool
from funcs.youtube import youtube_search
import json

class YouTubeTool(BaseTool):
    name: str = "youtube_search_tool"
    description: str = "Search YouTube for Atomberg fans related videos and analyze brand mentions, sentiment, and Share of Voice."

    def _run(self, query: str, num_results: int = 15) -> str:
        try:
            results = youtube_search(query, num_results)
            
            if "error" in results:
                return f"Error: {results['error']}"
            
            # Format results for the agent
            formatted_output = f"""
🎥 YOUTUBE ANALYSIS FOR: {results['query']}
📊 RESULTS: {results['total_videos']} videos analyzed

🏆 TOP BRANDS BY SHARE OF VOICE:
"""
            
            for brand, data in results['top_brands'].items():
                formatted_output += f"• {brand}: {data['sov_percentage']}% ({data['mentions']} mentions, {data['videos_mentioned']} videos)\n"
            
            formatted_output += f"""
🎯 ATOMBERG PERFORMANCE:
• Share of Voice: {results['summary']['atomberg_sov']}%
• Total Mentions: {results['summary']['atomberg_mentions']}
• Videos Mentioned: {results['summary']['atomberg_videos']}
• Brand Ranking: #{list(results['top_brands'].keys()).index('Atomberg') + 1 if 'Atomberg' in results['top_brands'] else 'Not in top 5'}

📹 TOP PERFORMING VIDEOS:
"""
            
            # Add top videos with brand analysis
            for i, video in enumerate(results['videos'][:5], 1):
                brands_found = ', '.join(video['brands_found']) if video['brands_found'] else 'None'
                views_formatted = f"{video['views']:,}" if isinstance(video['views'], int) else video['views']
                formatted_output += f"{i}. {video['title'][:80]}...\n"
                formatted_output += f"   📺 {video['channel']} | 👀 {views_formatted} views | 📅 {video['published_date']}\n"
                formatted_output += f"   🏷️ Brands: {brands_found} | 😊 Sentiment: {video['sentiment']}\n\n"
            
            # Add sentiment analysis
            atomberg_data = results['brand_analysis'].get('Atomberg', {})
            if atomberg_data.get('sentiment_distribution'):
                sentiment_dist = atomberg_data['sentiment_distribution']
                formatted_output += f"""
📈 ATOMBERG SENTIMENT BREAKDOWN:
• Positive: {sentiment_dist.get('positive', 0)} videos
• Neutral: {sentiment_dist.get('neutral', 0)} videos  
• Negative: {sentiment_dist.get('negative', 0)} videos
• Average Score: {atomberg_data.get('avg_sentiment_score', 0)}
"""
            
            # Add competitive insights
            formatted_output += f"""
🔍 COMPETITIVE INSIGHTS:
• Total brand mentions across all videos: {results['summary']['total_mentions']}
• Videos featuring multiple brands: {len([v for v in results['videos'] if len(v['brands_found']) > 1])}
• Most mentioned competitor: {list(results['top_brands'].keys())[0] if results['top_brands'] and list(results['top_brands'].keys())[0] != 'Atomberg' else 'N/A'}
"""
            
            # Add raw data for further processing
            formatted_output += f"\n📊 RAW DATA:\n{json.dumps(results['summary'], indent=2)}"
            
            return formatted_output
            
        except Exception as e:
            return f"Error in YouTube search tool: {str(e)}"