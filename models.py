# Add this to your models.py file
from pydantic import BaseModel
from typing import Dict, Any, List

class InsightOutput(BaseModel):
    google_data: Dict[str, Any]
    youtube_data: Dict[str, Any]
    share_of_voice_comparison: Dict[str, Any]
    sentiment_comparison: Dict[str, Any]
    competitive_insights: List[str]
    recommendations: List[str]
    key_insights: List[str]
    atomberg_performance: Dict[str, Any]