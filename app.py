import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from backend import MoodChatAI

# Page configuration
st.set_page_config(
    page_title="Mood-Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
            font-weight: 600;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Initialize AI backend
@st.cache_resource
def get_ai_engine():
    return MoodChatAI()

ai = get_ai_engine()

# Sidebar navigation
st.sidebar.title("🧠 Mood-Chat")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📝 Log Mood", "📊 Dashboard", "📈 Analytics", "⚠️ Health Alert", "ℹ️ About"]
)

st.sidebar.markdown("---")
st.sidebar.info("💙 Your mental health matters. Track, monitor, and improve your wellbeing.")

# ============= PAGE: LOG MOOD =============
if page == "📝 Log Mood":
    st.title("📝 How Are You Feeling Today?")
    
    st.markdown("""
    Share your thoughts and feelings with Mood-Chat. Our AI will analyze your mood 
    and provide personalized suggestions to support your mental wellbeing.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mood_entry = st.text_area(
            "Write about your feelings:",
            placeholder="I'm feeling... Today was...",
            height=200,
            key="mood_input"
        )
    
    with col2:
        st.markdown("### Tips for better entries:")
        st.markdown("""
        - Be honest and specific
        - Write at least 1-2 sentences
        - Include context if possible
        - No judgment - all feelings are valid
        """)
    
    if st.button("🚀 Analyze Mood", use_container_width=True):
        if mood_entry.strip():
            with st.spinner("🤖 Analyzing your mood..."):
                mood, confidence, advice = ai.log_mood(mood_entry)
                
                # Display results
                st.success("✅ Mood logged successfully!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    emoji = "😊" if mood == "POSITIVE" else "😔" if mood == "NEGATIVE" else "😐"
                    st.metric(f"{emoji} Detected Mood", mood)
                
                with col2:
                    st.metric("🎯 Confidence", f"{confidence:.1%}")
                
                with col3:
                    st.metric("📅 Date", datetime.today().strftime("%Y-%m-%d"))
                
                st.info(f"💡 **Suggestion:** {advice}")
                
                # Check for alerts
                alert, severity, msg = ai.check_alert()
                if alert:
                    if severity == "CRITICAL":
                        st.error(f"🚨 **CRITICAL ALERT:** {msg}\n\nPlease reach out to a mental health professional.")
                    elif severity == "HIGH":
                        st.warning(f"⚠️ **HIGH ALERT:** {msg}\n\nConsider speaking with a therapist.")
                    else:
                        st.info(f"ℹ️ **Gentle Reminder:** {msg}")
        else:
            st.error("❌ Please write something about your feelings first!")

# ============= PAGE: DASHBOARD =============
elif page == "📊 Dashboard":
    st.title("📊 Your Mood Dashboard")
    
    stats = ai.get_mood_stats()
    
    # Statistics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📚 Total Entries",
            stats['total_entries'],
            delta="Keep tracking!" if stats['total_entries'] < 30 else "Great consistency!"
        )
    
    with col2:
        st.metric(
            "😊 Positive Days",
            stats['positive_days'],
            delta=f"{stats['positive_percentage']:.1f}%"
        )
    
    with col3:
        st.metric(
            "📈 Trend",
            stats['trend'],
        )
    
    with col4:
        st.metric(
            "🎯 AI Accuracy",
            f"{stats['avg_confidence']:.1%}",
            delta="High confidence"
        )
    
    st.markdown("---")
    
    # Mood distribution pie chart
    if stats['total_entries'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Mood Distribution")
            mood_data = {
                "😊 Positive": stats['positive_days'],
                "😔 Negative": stats['negative_days'],
                "😐 Neutral": stats['neutral_days']
            }
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = ['#90EE90', '#FFB6C1', '#87CEEB']
            ax.pie(
                mood_data.values(),
                labels=mood_data.keys(),
                autopct='%1.1f%%',
                colors=colors,
                startangle=90
            )
            st.pyplot(fig)
        
        with col2:
            st.subheader("Recent Entries")
            recent = ai.get_mood_history(days=7)
            if len(recent) > 0:
                for idx, row in recent.tail(5).iterrows():
                    emoji = "😊" if row['mood'] == "POSITIVE" else "😔" if row['mood'] == "NEGATIVE" else "😐"
                    st.markdown(f"**{emoji} {row['date'].strftime('%Y-%m-%d')}** - {row['mood']}")
                    st.caption(row['entry'])
                    st.divider()
            else:
                st.info("No entries yet. Start logging to see your history!")
    else:
        st.info("📝 Start logging your mood entries to see your dashboard!")

# ============= PAGE: ANALYTICS =============
elif page == "📈 Analytics":
    st.title("📈 Mood Analytics")
    
    history = ai.get_mood_history(days=30)
    
    if len(history) > 0:
        st.subheader("30-Day Mood Trend")
        
        # Prepare data for line chart
        history_sorted = history.sort_values('date')
        mood_numeric = history_sorted['mood'].map({'POSITIVE': 1, 'NEUTRAL': 0, 'NEGATIVE': -1})
        
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(history_sorted['date'], mood_numeric, marker='o', linestyle='-', linewidth=2, color='#4CAF50')
        ax.fill_between(history_sorted['date'], mood_numeric, alpha=0.3, color='#4CAF50')
        ax.set_ylim(-1.5, 1.5)
        ax.set_yticks([-1, 0, 1])
        ax.set_yticklabels(['Negative', 'Neutral', 'Positive'])
        ax.set_xlabel('Date')
        ax.set_ylabel('Mood')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Weekly breakdown
        st.subheader("Weekly Breakdown")
        history_sorted['week'] = history_sorted['date'].dt.isocalendar().week
        weekly_stats = history_sorted.groupby('week')['mood'].value_counts().unstack(fill_value=0)
        
        if len(weekly_stats) > 0:
            st.bar_chart(weekly_stats)
        
        # Confidence trend
        st.subheader("AI Confidence Over Time")
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.plot(history_sorted['date'], history_sorted['confidence'], marker='o', color='#FF9800', linewidth=2)
        ax.fill_between(history_sorted['date'], history_sorted['confidence'], alpha=0.3, color='#FF9800')
        ax.set_xlabel('Date')
        ax.set_ylabel('Confidence Score')
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Insights
        st.markdown("---")
        st.subheader("📊 Key Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            best_day = history_sorted[history_sorted['mood'] == 'POSITIVE']
            if len(best_day) > 0:
                st.success(f"✨ **Best Day:** {best_day.iloc[-1]['date'].strftime('%Y-%m-%d')}")
            else:
                st.info("No positive days yet. Stay positive! 💫")
        
        with col2:
            avg_conf = history_sorted['confidence'].mean()
            st.info(f"🎯 **Avg AI Confidence:** {avg_conf:.1%}")
        
        with col3:
            streak_positive = sum(history_sorted.tail(7)['mood'] == 'POSITIVE')
            st.warning(f"📈 **Positive Days (Last 7):** {streak_positive}/7")
    
    else:
        st.info("📝 Log more entries to see detailed analytics!")

# ============= PAGE: HEALTH ALERT =============
elif page == "⚠️ Health Alert":
    st.title("⚠️ Health & Alert Status")
    
    alert, severity, msg = ai.check_alert()
    report = ai.export_report()
    
    st.markdown("---")
    
    if alert:
        if severity == "CRITICAL":
            st.error(f"🚨 **CRITICAL ALERT**")
        elif severity == "HIGH":
            st.warning(f"⚠️ **HIGH ALERT**")
        else:
            st.info(f"ℹ️ **MEDIUM ALERT**")
        
        st.markdown(f"**Status:** {msg}")
    else:
        st.success("✅ **Your mood is stable. Great job!**")
    
    st.markdown("---")
    
    # Detailed metrics
    st.subheader("📋 Detailed Report")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Statistics**")
        for key, value in report['statistics'].items():
            st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
    
    with col2:
        st.markdown("**Alert Information**")
        for key, value in report['alert'].items():
            st.markdown(f"- **{key.title()}:** {value}")
    
    st.markdown("---")
    st.subheader("💬 Recommendation")
    st.success(report['recommendation'])
    
    # Resources
    st.markdown("---")
    st.subheader("🆘 Mental Health Resources")
    st.markdown("""
    - **National Suicide Prevention Lifeline:** 1-800-273-8255
    - **Crisis Text Line:** Text HOME to 741741
    - **International Association for Suicide Prevention:** https://www.iasp.info/resources/Crisis_Centres/
    - **NAMI Helpline:** 1-800-950-NAMI (6264)
    """)

# ============= PAGE: ABOUT =============
elif page == "ℹ️ About":
    st.title("ℹ️ About Mood-Chat")
    
    st.markdown("""
    ## 🧠 Mood-Chat: AI-Powered Mental Health Monitoring
    
    Mood-Chat is an intelligent mental health companion that helps you track your emotional wellbeing 
    and receive personalized support.
    
    ### ✨ Features
    
    - **AI Mood Detection:** Advanced sentiment analysis using transformer models
    - **Daily Tracking:** Log your mood and get personalized suggestions
    - **Alert System:** Notifications for prolonged negative moods
    - **Analytics:** Visual insights into your mood patterns over time
    - **Privacy First:** Your data is stored locally and never shared
    
    ### 🔧 Technology Stack
    
    - **AI Models:** HuggingFace Transformers (DistilBERT)
    - **Frontend:** Streamlit
    - **Data Storage:** CSV-based local storage
    - **Language:** Python
    
    ### 📊 How It Works
    
    1. **You Share:** Write about your feelings in natural language
    2. **AI Analyzes:** Our model detects emotional patterns
    3. **Get Insights:** Receive personalized advice and recommendations
    4. **Track Progress:** Monitor your mood trends over weeks and months
    5. **Stay Alert:** Receive warnings if patterns suggest you need support
    
    ### ⚠️ Important Notice
    
    Mood-Chat is a support tool, **not a replacement for professional mental health care**. 
    If you're experiencing a mental health crisis, please reach out to:
    
    - **National Suicide Prevention Lifeline:** 1-800-273-8255
    - **Crisis Text Line:** Text HOME to 741741
    - **Your local emergency services:** 911
    
    ### 📈 Tips for Better Results
    
    - Log your mood consistently (daily is ideal)
    - Be honest and detailed in your entries
    - Include context about your day
    - Review your trends weekly
    - Share insights with your therapist
    
    ### 🎯 Privacy & Security
    
    Your mood data is stored locally on your device. We don't collect, store, or share your 
    personal information with any third parties. You have full control over your data.
    
    ---
    
    **Made with ❤️ for your mental wellbeing**
    """)
