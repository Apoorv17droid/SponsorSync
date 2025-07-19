import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import Event, SponsorProfile
import logging

class AIMatchmaker:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    
    def calculate_match_score(self, event, sponsor):
        """Calculate match score between an event and a sponsor"""
        try:
            # Initialize scores
            tag_score = 0
            audience_score = 0
            location_score = 0
            industry_score = 0
            
            # Tag similarity score (40% weight)
            if event.tags and sponsor.target_demographics:
                event_text = f"{event.tags} {event.theme} {event.description}"
                sponsor_text = f"{sponsor.target_demographics} {sponsor.industry} {sponsor.description}"
                
                try:
                    vectors = self.vectorizer.fit_transform([event_text, sponsor_text])
                    similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
                    tag_score = similarity * 0.4
                except Exception as e:
                    logging.warning(f"Error calculating text similarity: {e}")
                    tag_score = 0.1
            
            # Audience overlap score (25% weight)
            if event.target_audience and sponsor.target_demographics:
                event_audience = event.target_audience.lower()
                sponsor_audience = sponsor.target_demographics.lower()
                
                # Simple keyword matching
                common_words = set(event_audience.split()) & set(sponsor_audience.split())
                audience_score = min(len(common_words) / 5, 1) * 0.25
            
            # Location relevance score (20% weight)
            if event.location and sponsor.location:
                event_loc = event.location.lower()
                sponsor_loc = sponsor.location.lower()
                
                # Exact match or contains check
                if event_loc == sponsor_loc or event_loc in sponsor_loc or sponsor_loc in event_loc:
                    location_score = 0.2
                else:
                    location_score = 0.05  # Small bonus for any location data
            
            # Industry relevance score (15% weight)
            if event.theme and sponsor.industry:
                industry_keywords = {
                    'technology': ['tech', 'innovation', 'startup', 'coding', 'hackathon', 'ai', 'software'],
                    'finance': ['business', 'finance', 'investment', 'entrepreneur', 'economics'],
                    'healthcare': ['health', 'medical', 'wellness', 'fitness', 'nutrition'],
                    'education': ['academic', 'research', 'scholarship', 'learning', 'study'],
                    'entertainment': ['music', 'arts', 'cultural', 'festival', 'concert', 'performance'],
                    'food_beverage': ['food', 'cooking', 'culinary', 'restaurant', 'dining'],
                    'automotive': ['automotive', 'racing', 'cars', 'vehicles', 'transportation'],
                    'retail': ['fashion', 'shopping', 'retail', 'consumer', 'lifestyle'],
                    'sports': ['sports', 'athletic', 'fitness', 'competition', 'tournament', 'game']
                }
                
                theme_words = event.theme.lower().split()
                if sponsor.industry in industry_keywords:
                    keywords = industry_keywords[sponsor.industry]
                    matches = any(keyword in ' '.join(theme_words) for keyword in keywords)
                    if matches:
                        industry_score = 0.15
            
            # Calculate total score
            total_score = tag_score + audience_score + location_score + industry_score
            
            # Add bonus for event metrics
            if event.expected_footfall:
                if event.expected_footfall >= 500:
                    total_score += 0.1  # High engagement bonus
                elif event.expected_footfall >= 100:
                    total_score += 0.05  # Medium engagement bonus
            
            return min(total_score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logging.error(f"Error calculating match score: {e}")
            return 0.1  # Default low score
    
    def get_sponsor_recommendations(self, event, limit=5):
        """Get recommended sponsors for an event"""
        sponsors = SponsorProfile.query.all()
        recommendations = []
        
        for sponsor in sponsors:
            score = self.calculate_match_score(event, sponsor)
            recommendations.append({
                'sponsor': sponsor,
                'score': score,
                'percentage': int(score * 100)
            })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    def get_event_recommendations(self, sponsor, limit=5):
        """Get recommended events for a sponsor"""
        events = Event.query.all()
        recommendations = []
        
        for event in events:
            score = self.calculate_match_score(event, sponsor)
            recommendations.append({
                'event': event,
                'score': score,
                'percentage': int(score * 100)
            })
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]
    
    def get_match_explanation(self, event, sponsor):
        """Get explanation for why an event and sponsor are matched"""
        explanations = []
        
        # Check tag similarity
        if event.tags and sponsor.target_demographics:
            explanations.append("Relevant tags and demographics match")
        
        # Check location
        if event.location and sponsor.location:
            if event.location.lower() in sponsor.location.lower() or sponsor.location.lower() in event.location.lower():
                explanations.append("Geographic proximity")
        
        # Check industry relevance
        if event.theme and sponsor.industry:
            explanations.append(f"Event theme aligns with {sponsor.industry} industry")
        
        # Check audience size
        if event.expected_footfall and event.expected_footfall >= 200:
            explanations.append("High expected engagement")
        
        return explanations if explanations else ["Basic compatibility factors"]

# Global instance
ai_matcher = AIMatchmaker()
