import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from transformers import pipeline
import warnings

warnings.filterwarnings("ignore")

class MoodChatAI:
    """
    Advanced AI-powered mood tracking and mental health monitoring system.
    """
    
    def __init__(self, csv_file="mood_log.csv"):
        """Initialize the AI pipelines and load/create mood log."""
        self.csv_file = csv_file
        self.emotion_analyzer = pipeline(
            "text-classification",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        
        # Try to load existing mood log
        try:
            self.df = pd.read_csv(csv_file)
            self.df['date'] = pd.to_datetime(self.df['date'])
        except FileNotFoundError:
            self.df = pd.DataFrame(
                columns=["date", "entry", "mood", "confidence", "advice", "alert_level"]
            )
        
        # Enhanced advice mapping with personalization
        self.advice_map = {
            "POSITIVE": [
                "Amazing! Keep channeling this positive energy! 🌟",
                "Your optimism is contagious. Share it with others!",
                "Keep doing what you're doing. You're thriving!"
            ],
            "NEGATIVE": [
                "It's okay to feel down. Consider talking to someone. 💙",
                "Take a 15-minute walk or practice deep breathing.",
                "Reach out to a friend or therapist. You're not alone.",
                "Try journaling or meditation to process these feelings."
            ],
            "NEUTRAL": [
                "Keep journaling daily for better insights! 📝",
                "How can you make today a bit better?",
                "Your feelings matter. Keep tracking them."
            ]
        }
    
    def analyze_mood(self, entry):
        """
        Analyze user's mood using multiple AI models.
        Returns mood label, confidence score, and personalized advice.
        """
        if not entry.strip():
            return None, 0, "Please enter your feelings to get started."
        
        # Run sentiment analysis
        sentiment_result = self.sentiment_analyzer(entry[:512])[0]
        emotion_result = self.emotion_analyzer(entry[:512])[0]
        
        label = emotion_result['label']
        confidence = emotion_result['score']
        
        # Map model output to mood labels
        mood_label = "POSITIVE" if label == "POSITIVE" else (
            "NEGATIVE" if label == "NEGATIVE" else "NEUTRAL"
        )
        
        # Select personalized advice
        import random
        advice = random.choice(self.advice_map.get(mood_label, ["Stay mindful."]))
        
        return mood_label, confidence, advice
    
    def log_mood(self, entry):
        """Log mood entry to CSV with timestamp and analysis."""
        mood_label, confidence, advice = self.analyze_mood(entry)
        
        if mood_label is None:
            return None, 0, advice
        
        today = datetime.today()
        new_entry = pd.DataFrame({
            "date": [today],
            "entry": [entry[:200]],  # Store truncated entry
            "mood": [mood_label],
            "confidence": [confidence],
            "advice": [advice],
            "alert_level": ["LOW"]  # Will be updated if needed
        })
        
        self.df = pd.concat([self.df, new_entry], ignore_index=True)
        self.df.to_csv(self.csv_file, index=False)
        
        return mood_label, confidence, advice
    
    def check_alert(self):
        """
        Check for prolonged negative mood (2+ weeks).
        Returns alert status and severity.
        """
        if len(self.df) < 7:
            return False, "LOW", "Not enough data yet."
        
        # Analyze last 14 days
        fourteen_days_ago = datetime.today() - timedelta(days=14)
        recent_df = self.df[self.df['date'] >= fourteen_days_ago]
        
        if len(recent_df) < 7:
            return False, "LOW", "Not enough data for 2-week analysis."
        
        negative_count = sum(recent_df['mood'] == "NEGATIVE")
        total_count = len(recent_df)
        negative_percentage = (negative_count / total_count) * 100
        
        # Alert logic
        if negative_percentage >= 70:
            return True, "CRITICAL", f"{negative_percentage:.0f}% negative days detected."
        elif negative_percentage >= 50:
            return True, "HIGH", f"{negative_percentage:.0f}% negative days detected."
        elif negative_percentage >= 30:
            return True, "MEDIUM", f"{negative_percentage:.0f}% negative days detected."
        
        return False, "LOW", "Mood is stable."
    
    def get_mood_stats(self):
        """Generate mood statistics for dashboard."""
        if len(self.df) == 0:
            return {
                "total_entries": 0,
                "positive_days": 0,
                "negative_days": 0,
                "neutral_days": 0,
                "trend": "No data"
            }
        
        total = len(self.df)
        positive = sum(self.df['mood'] == "POSITIVE")
        negative = sum(self.df['mood'] == "NEGATIVE")
        neutral = sum(self.df['mood'] == "NEUTRAL")
        
        # Calculate trend
        if len(self.df) >= 2:
            recent = self.df.tail(7)['mood'].value_counts()
            past = self.df.iloc[:-7]['mood'].value_counts()
            
            recent_positive = recent.get("POSITIVE", 0) / len(self.df.tail(7))
            past_positive = past.get("POSITIVE", 0) / len(self.df.iloc[:-7]) if len(self.df.iloc[:-7]) > 0 else 0
            
            trend = "Improving 📈" if recent_positive > past_positive else (
                "Declining 📉" if recent_positive < past_positive else "Stable ➡️"
            )
        else:
            trend = "Not enough data"
        
        return {
            "total_entries": total,
            "positive_days": positive,
            "negative_days": negative,
            "neutral_days": neutral,
            "positive_percentage": round((positive / total) * 100, 1) if total > 0 else 0,
            "trend": trend,
            "avg_confidence": round(self.df['confidence'].mean(), 3) if len(self.df) > 0 else 0
        }
    
    def get_mood_history(self, days=30):
        """Get mood history for the last N days."""
        cutoff = datetime.today() - timedelta(days=days)
        history = self.df[self.df['date'] >= cutoff].sort_values('date')
        return history
    
    def export_report(self):
        """Export comprehensive mental health report."""
        stats = self.get_mood_stats()
        alert, severity, message = self.check_alert()
        
        report = {
            "timestamp": datetime.today().isoformat(),
            "statistics": stats,
            "alert": {
                "triggered": alert,
                "severity": severity,
                "message": message
            },
            "recommendation": self._get_recommendation(stats)
        }
        
        return report
    
    def _get_recommendation(self, stats):
        """Generate recommendations based on stats."""
        if stats["total_entries"] < 7:
            return "Keep logging your mood daily to get personalized insights!"
        
        if stats["positive_percentage"] >= 70:
            return "Great work! Maintain your current positive momentum! 🎉"
        elif stats["positive_percentage"] <= 30:
            return "Consider reaching out to a mental health professional. Your wellbeing matters! 💙"
        else:
            return "Your mood is balanced. Keep tracking and stay mindful!"


# ============= MAIN DEMO & TESTING =============
if __name__ == "__main__":
    ai = MoodChatAI()
    
    # Sample mood entries for testing
    sample_entries = [
        "I'm feeling great today! Everything is going well.",
        "I'm really sad and don't know what to do.",
        "Just another regular day, nothing special.",
        "I feel so happy and excited about the future!",
        "I'm struggling with anxiety today.",
    ]
    
    print("🧠 Mood-Chat AI Backend Demo\n")
    print("=" * 50)
    
    for entry in sample_entries:
        mood, confidence, advice = ai.log_mood(entry)
        print(f"\n📝 Entry: {entry[:50]}...")
        print(f"🎭 Mood: {mood} (Confidence: {confidence:.2f})")
        print(f"💡 Advice: {advice}")
    
    print("\n" + "=" * 50)
    print("\n📊 Statistics:")
    stats = ai.get_mood_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n⚠️  Alert Check:")
    alert, severity, msg = ai.check_alert()
    print(f"  Alert Triggered: {alert}")
    print(f"  Severity: {severity}")
    print(f"  Message: {msg}")
    
    print("\n📋 Full Report:")
    report = ai.export_report()
    print(json.dumps(report, indent=2, default=str))
