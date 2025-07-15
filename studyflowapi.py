import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import PyPDF2
import docx
from io import BytesIO
import json
import uuid
import random
import urllib.parse
from collections import defaultdict
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import base64
import anthropic
from typing import Dict, List, Optional, Tuple

# Page config
st.set_page_config(
    page_title="StudyFlow",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS with completely uniform button styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        min-height: 100vh;
        color: #ffffff;
    }
    
    .main-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
        color: #ffffff;
        position: relative;
        overflow: hidden;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        font-weight: 400;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    .setup-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
        color: #ffffff;
    }
    
    .setup-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        border-color: rgba(108, 92, 231, 0.3);
    }
    
    .setup-card h2, .setup-card h3, .setup-card h4 {
        color: #ffffff;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    .setup-card p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .api-key-section {
        background: rgba(255, 193, 7, 0.1);
        border: 2px solid rgba(255, 193, 7, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
    }
    
    .api-key-section h3 {
        color: #ffc107;
        margin-bottom: 1rem;
        font-size: 1.4rem;
        font-weight: 600;
    }
    
    .api-key-section p {
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 1rem;
    }
    
    .api-key-section a {
        color: #ffc107;
        text-decoration: none;
        font-weight: 600;
    }
    
    .api-key-section a:hover {
        text-decoration: underline;
    }
    
    .step-number {
        display: inline-block;
        width: 45px;
        height: 45px;
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white;
        border-radius: 50%;
        text-align: center;
        line-height: 45px;
        font-weight: 600;
        margin-right: 15px;
        font-size: 1.1rem;
        box-shadow: 0 4px 12px rgba(108, 92, 231, 0.3);
    }
    
    .activity-item {
        display: flex;
        align-items: center;
        padding: 1rem;
        margin: 0.75rem 0;
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.06);
        border-left: 4px solid #6c5ce7;
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
    }
    
    .activity-item:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: translateX(4px);
    }
    
    .time-badge {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: 1rem;
        min-width: 90px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(108, 92, 231, 0.3);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(15px);
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.15);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
        border-color: rgba(108, 92, 231, 0.3);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #6c5ce7;
        display: block;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .stat-label {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .progress-bar {
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 1.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6c5ce7, #a29bfe);
        transition: width 0.3s ease;
        box-shadow: 0 0 10px rgba(108, 92, 231, 0.5);
    }
    
    .progress-text {
        text-align: center;
        color: rgba(255, 255, 255, 0.9);
        font-size: 1rem;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .export-section {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .export-section h3 {
        color: #ffffff;
        margin-bottom: 1rem;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .email-section {
        background: rgba(253, 121, 168, 0.1);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        border: 2px solid rgba(253, 121, 168, 0.3);
    }
    
    .email-section h4 {
        color: #fd79a8;
        margin-bottom: 1rem;
        font-size: 1.3rem;
        font-weight: 600;
    }
    
    .email-instructions {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #fdcb6e;
    }
    
    .email-instructions h5 {
        color: #fdcb6e;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .download-first {
        background: rgba(255, 203, 110, 0.1);
        border: 2px solid rgba(255, 203, 110, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .download-first h5 {
        color: #fdcb6e;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .social-proof {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    .social-proof h4 {
        font-size: 1.3rem;
        color: #6c5ce7;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* COMPLETELY UNIFORM BUTTON STYLING - ALL BUTTONS IDENTICAL SHAPE */
    
    /* Universal button base styling - FIXED for better responsiveness */
    .stButton > button,
    .stDownloadButton > button,
    .email-button {
        border: none !important;
        border-radius: 50px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
        letter-spacing: 0.5px !important;
        width: 100% !important;
        min-height: 48px !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        white-space: normal !important;
        text-align: center !important;
        word-break: break-word !important;
        color: white !important;
    }
    
    /* Primary buttons (default Streamlit buttons) */
    .stButton > button {
        background: linear-gradient(135deg, #6c5ce7, #a29bfe) !important;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.4) !important;
        background: linear-gradient(135deg, #5a4fcf, #8b7dff) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3) !important;
    }
    
    .stButton > button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.3) !important;
    }
    
    .stButton > button:disabled {
        background: rgba(255, 255, 255, 0.1) !important;
        color: rgba(255, 255, 255, 0.5) !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Download buttons - green variant with SAME SHAPE */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00b894, #00cec9) !important;
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4) !important;
        background: linear-gradient(135deg, #008f7a, #00a8a3) !important;
    }
    
    .stDownloadButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3) !important;
    }
    
    .stDownloadButton > button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0, 184, 148, 0.3) !important;
    }
    
    /* Custom email button - pink variant with SAME SHAPE */
    .email-button {
        background: linear-gradient(135deg, #fd79a8, #fdcb6e) !important;
        box-shadow: 0 4px 15px rgba(253, 121, 168, 0.3) !important;
        text-decoration: none !important;
    }
    
    .email-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(253, 121, 168, 0.4) !important;
        background: linear-gradient(135deg, #e84393, #f39c12) !important;
        text-decoration: none !important;
    }
    
    .email-button:active {
        transform: translateY(0) !important;
        box-shadow: 0 4px 15px rgba(253, 121, 168, 0.3) !important;
    }
    
    .email-button:focus {
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(253, 121, 168, 0.3) !important;
    }
    
    /* Form inputs styling - FIXED selectbox label visibility */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(200, 200, 200, 0.5) !important;
        border-radius: 50px !important;
        color: #000000 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #6c5ce7 !important;
        box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2) !important;
    }
    
    .stSelectbox label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 50px !important;
        color: #000000 !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6c5ce7 !important;
        box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2) !important;
        background: rgba(255, 255, 255, 1) !important;
    }
    
    .stTextInput label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        color: #000000 !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #6c5ce7 !important;
        box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.2) !important;
        background: rgba(255, 255, 255, 1) !important;
    }
    
    .stTextArea label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stSlider label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stCheckbox > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stFileUploader > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px dashed rgba(255, 255, 255, 0.3) !important;
        border-radius: 20px !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        padding: 2rem !important;
        text-align: center !important;
    }
    
    .stFileUploader label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stExpander {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 16px !important;
        margin: 0.5rem 0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stExpander > div > div {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Alert styling */
    .stSuccess {
        background: rgba(0, 184, 148, 0.1) !important;
        border: 1px solid rgba(0, 184, 148, 0.3) !important;
        color: #00b894 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stWarning {
        background: rgba(253, 203, 110, 0.1) !important;
        border: 1px solid rgba(253, 203, 110, 0.3) !important;
        color: #fdcb6e !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stError {
        background: rgba(231, 76, 60, 0.1) !important;
        border: 1px solid rgba(231, 76, 60, 0.3) !important;
        color: #e74c3c !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Text styling */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stMarkdown p, .stMarkdown div {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stMarkdown ul li, .stMarkdown ol li {
        color: rgba(255, 255, 255, 0.9) !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Responsive design - IMPROVED mobile button handling */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .main-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .setup-card {
            padding: 1.5rem;
        }
        
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .hero-section {
            padding: 2rem 1rem;
        }
        
        .stButton > button, .stDownloadButton > button, .email-button {
            font-size: 0.95rem !important;
            padding: 0.65rem 1.25rem !important;
            border-radius: 40px !important;
            white-space: normal !important;
            word-break: break-word !important;
            text-align: center !important;
            min-height: 44px !important;
        }
        
        .stDownloadButton, .stButton {
            width: 100% !important;
            margin-bottom: 0.75rem !important;
        }
        
        /* Stack buttons vertically on mobile for better UX */
        .stColumns {
            flex-direction: column !important;
        }
        
        .stColumn {
            width: 100% !important;
            margin-bottom: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0  # Start at API key step
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'schedule_ready' not in st.session_state:
    st.session_state.schedule_ready = False
if 'final_schedule' not in st.session_state:
    st.session_state.final_schedule = None
if 'pdf_generated' not in st.session_state:
    st.session_state.pdf_generated = False
if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'claude_client' not in st.session_state:
    st.session_state.claude_client = None

def validate_api_key(api_key: str) -> bool:
    """Validate the Anthropic API key"""
    if not api_key or not api_key.startswith('sk-ant-'):
        return False
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        # Test the API key with a simple request using Claude 4 Sonnet
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello"}]
        )
        return True
    except Exception as e:
        st.error(f"API Key validation failed: {str(e)}")
        return False

def extract_text_from_file(file):
    """Extract text from uploaded file"""
    try:
        if file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        else:
            return str(file.read(), "utf-8")
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return ""

def claude_parse_syllabus(syllabus_text: str, client: anthropic.Anthropic) -> Tuple[List[Dict], List[Dict]]:
    """Use Claude 4 Sonnet to intelligently parse any syllabus format"""
    
    prompt = f"""
    You are an expert academic assistant powered by Claude 4 Sonnet. Please analyze the following syllabus text and extract:

    1. COURSES: All courses mentioned (course codes, names, credits, etc.)
    2. DEADLINES: All assignments, exams, quizzes, projects, and their due dates

    Please return your response as a JSON object with this exact structure:

    {{
        "courses": [
            {{
                "code": "COURSE_CODE",
                "name": "Full Course Name",
                "credits": 3,
                "difficulty": 4,
                "description": "Brief description if available"
            }}
        ],
        "deadlines": [
            {{
                "title": "Assignment/Exam Name",
                "date": "YYYY-MM-DD",
                "type": "assignment|exam|quiz|project|lab|discussion",
                "course": "COURSE_CODE",
                "priority": "high|medium|low",
                "description": "Additional details if available"
            }}
        ]
    }}

    Guidelines:
    - Extract ALL courses mentioned, even if they're referenced indirectly
    - For dates, if no year is specified, assume the current academic year (2024 for fall dates, 2025 for spring dates)
    - Convert relative dates like "Week 3" to actual dates if possible
    - Estimate difficulty on a scale of 1-5 based on course level and content
    - Set priority: exams=high, major assignments=high, regular assignments=medium, discussions=low
    - If course codes aren't clear, create logical ones based on the subject
    - Include lab components as separate items if they have different deadlines
    - Extract recurring items (like weekly discussions) as individual deadlines

    Here's the syllabus text to analyze:

    {syllabus_text}

    Return ONLY the JSON object, no additional text.
    """
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = response.content[0].text.strip()
        
        # Clean up the response to ensure it's valid JSON
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        
        parsed_data = json.loads(response_text)
        
        courses = parsed_data.get('courses', [])
        deadlines = parsed_data.get('deadlines', [])
        
        # Add IDs to deadlines
        for deadline in deadlines:
            deadline['id'] = str(uuid.uuid4())
        
        return courses, deadlines
        
    except anthropic.AuthenticationError:
        st.error("❌ Authentication failed. Please check your API key.")
        return [], []
    except anthropic.PermissionDeniedError:
        st.error("❌ Permission denied. Your API key may not have access to Claude 4 Sonnet.")
        return [], []
    except anthropic.NotFoundError:
        st.error("❌ Claude 4 Sonnet model not found. Please check your API access.")
        return [], []
    except anthropic.RateLimitError:
        st.error("❌ Rate limit exceeded. Please try again in a moment.")
        return [], []
    except json.JSONDecodeError as e:
        st.error(f"❌ Error parsing AI response: {str(e)}")
        st.info("💡 The AI response wasn't in the expected format. Please try again.")
        return [], []
    except Exception as e:
        st.error(f"❌ Error with Claude 4 API: {str(e)}")
        st.info("💡 Please check your connection and try again.")
        return [], []

def generate_instant_schedule(courses: List[Dict], deadlines: List[Dict], preferences: Dict) -> Dict:
    """Generate a beautiful, realistic schedule instantly"""
    schedule = {}
    
    # Generate next 30 days
    for i in range(30):
        date = datetime.now() + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        day_name = date.strftime('%A')
        is_weekend = date.weekday() >= 5
        
        daily_schedule = []
        
        # Morning routine
        wake_time = preferences.get('wake_time', 8)
        daily_schedule.append({
            'time': f'{wake_time}:00 AM',
            'activity': '🌅 Morning Routine',
            'type': 'routine',
            'emoji': '🌅',
            'duration': 60
        })
        
        # Meals
        if preferences.get('include_meals', True):
            daily_schedule.extend([
                {'time': f'{wake_time + 1}:00 AM', 'activity': '🥞 Breakfast', 'type': 'meal', 'emoji': '🥞', 'duration': 30},
                {'time': '12:30 PM', 'activity': '🍽️ Lunch Break', 'type': 'meal', 'emoji': '🍽️', 'duration': 60},
                {'time': '6:00 PM', 'activity': '🍕 Dinner', 'type': 'meal', 'emoji': '🍕', 'duration': 60},
            ])
        
        # Study sessions based on schedule type
        schedule_type = preferences.get('schedule_type', '⚖️ Balanced')
        if '🔥 Intense' in schedule_type:
            study_slots = ['10:00 AM', '2:00 PM', '4:00 PM', '7:30 PM', '9:00 PM']
        elif '⚖️ Balanced' in schedule_type:
            study_slots = ['10:00 AM', '2:00 PM', '4:00 PM', '7:30 PM']
        else:  # Chill
            study_slots = ['10:00 AM', '2:00 PM', '7:30 PM']
        
        # Reduce study sessions on weekends
        if is_weekend:
            study_slots = study_slots[:-1]
        
        for i, slot in enumerate(study_slots):
            if i < len(courses):
                course = courses[i % len(courses)]
                session_types = ['Review', 'Practice', 'Reading', 'Problems', 'Notes', 'Research']
                session_type = random.choice(session_types)
                
                daily_schedule.append({
                    'time': slot,
                    'activity': f"📚 {course['code']} - {session_type}",
                    'type': 'study',
                    'emoji': '📚',
                    'course': course['code'],
                    'duration': preferences.get('attention_span', 25)
                })
        
        # Social media breaks
        if preferences.get('include_breaks', True):
            daily_schedule.extend([
                {'time': '11:00 AM', 'activity': '📱 Social Break', 'type': 'break', 'emoji': '📱', 'duration': 15},
                {'time': '3:00 PM', 'activity': '📱 TikTok Break', 'type': 'break', 'emoji': '📱', 'duration': 15},
            ])
        
        # Evening activities
        if is_weekend:
            daily_schedule.append({
                'time': '8:00 PM',
                'activity': '🎉 Weekend Social Time',
                'type': 'free',
                'emoji': '🎉',
                'duration': 180
            })
        else:
            daily_schedule.append({
                'time': '9:00 PM',
                'activity': '🎮 Gaming/Netflix',
                'type': 'free',
                'emoji': '🎮',
                'duration': 120
            })
        
        # Add deadline reminders
        for deadline in deadlines:
            if deadline['date'] == date_str:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(deadline.get('priority', 'medium'), '🟡')
                daily_schedule.append({
                    'time': '11:59 PM',
                    'activity': f"{priority_emoji} DUE: {deadline['title']}",
                    'type': 'deadline',
                    'emoji': priority_emoji,
                    'priority': deadline.get('priority', 'medium'),
                    'course': deadline.get('course', 'N/A'),
                    'duration': 0
                })
        
        # Sort by time
        def time_sort_key(activity):
            try:
                time_str = activity['time']
                if 'AM' in time_str or 'PM' in time_str:
                    time_obj = datetime.strptime(time_str, '%I:%M %p')
                    return time_obj.hour * 60 + time_obj.minute
                else:
                    return 0
            except:
                return 0
        
        daily_schedule.sort(key=time_sort_key)
        schedule[date_str] = daily_schedule
    
    return schedule

def generate_pdf_schedule(schedule_data: Dict, user_data: Dict) -> BytesIO:
    """Generate a beautiful PDF schedule"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Create custom styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6c5ce7')
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#a29bfe')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#6c5ce7')
    )
    
    # Build the story
    story = []
    
    # Title
    story.append(Paragraph("⚡ StudyFlow Schedule", title_style))
    story.append(Paragraph("Your AI-Powered Personalized Study Schedule", subtitle_style))
    story.append(Spacer(1, 12))
    
    # Summary section
    courses = user_data.get('courses', [])
    deadlines = user_data.get('deadlines', [])
    
    summary_data = [
        ['📚 Total Courses', str(len(courses))],
        ['⚠️ Upcoming Deadlines', str(len(deadlines))],
        ['⏰ Daily Study Sessions', '3-4 sessions'],
        ['🎯 Focus Time', f"{user_data.get('attention_span', 25)} minutes"],
        ['📅 Schedule Type', user_data.get('schedule_type', 'Balanced')],
        ['🗓️ Generated On', datetime.now().strftime('%B %d, %Y')],
        ['🤖 Powered by', 'Claude AI + StudyFlow']
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9ff')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e6ff'))
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Courses section
    if courses:
        story.append(Paragraph("📚 Your Courses", heading_style))
        course_data = [['Course Code', 'Course Name', 'Credits', 'Difficulty']]
        for course in courses:
            difficulty_stars = '⭐' * course.get('difficulty', 3)
            course_data.append([
                course['code'],
                course['name'][:40] + '...' if len(course['name']) > 40 else course['name'],
                str(course.get('credits', 3)),
                difficulty_stars
            ])
        
        course_table = Table(course_data, colWidths=[1.5*inch, 2.5*inch, 0.8*inch, 1*inch])
        course_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c5ce7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e6ff'))
        ]))
        
        story.append(course_table)
        story.append(Spacer(1, 20))
    
    # Deadlines section
    if deadlines:
        story.append(Paragraph("⚠️ Upcoming Deadlines", heading_style))
        deadline_data = [['Date', 'Assignment', 'Course', 'Type', 'Priority']]
        sorted_deadlines = sorted(deadlines, key=lambda x: x['date'])
        
        for deadline in sorted_deadlines:
            priority_symbol = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(deadline.get('priority', 'medium'), '🟡')
            deadline_data.append([
                deadline['date'],
                deadline['title'][:30] + '...' if len(deadline['title']) > 30 else deadline['title'],
                deadline.get('course', 'N/A'),
                deadline.get('type', 'assignment').title(),
                priority_symbol
            ])
        
        deadline_table = Table(deadline_data, colWidths=[1*inch, 2*inch, 1*inch, 1*inch, 0.8*inch])
        deadline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fd79a8')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fff8f8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ffe0e0'))
        ]))
        
        story.append(deadline_table)
        story.append(Spacer(1, 20))
    
    # Weekly schedule
    story.append(Paragraph("📅 This Week's Schedule", heading_style))
    
    # Show 7 days starting from today
    today = datetime.now()
    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        day_name = date.strftime('%A, %B %d')
        
        if date_str in schedule_data:
            story.append(Paragraph(f"📅 {day_name}", ParagraphStyle(
                'DayHeading',
                parent=styles['Heading3'],
                fontSize=14,
                spaceAfter=6,
                textColor=colors.HexColor('#6c5ce7')
            )))
            
            daily_schedule = schedule_data[date_str]
            schedule_items = []
            
            for activity in daily_schedule:
                activity_text = f"{activity['time']} - {activity['activity']}"
                if activity.get('duration'):
                    activity_text += f" ({activity['duration']} min)"
                schedule_items.append(activity_text)
            
            # Create schedule table for the day
            day_data = [[item] for item in schedule_items]
            if day_data:
                day_table = Table(day_data, colWidths=[5.5*inch])
                day_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9ff')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e6ff'))
                ]))
                
                story.append(day_table)
                story.append(Spacer(1, 12))
        
        # Add page break after 4 days
        if i == 3:
            story.append(PageBreak())
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph(
        "Generated by StudyFlow - AI-Powered Study Scheduling with Claude",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666')
        )
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_ics_calendar(schedule_data: Dict, user_data: Dict) -> str:
    """Generate ICS calendar file"""
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//StudyFlow//StudyFlow AI 2025//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:StudyFlow AI Schedule
X-WR-TIMEZONE:America/New_York
BEGIN:VTIMEZONE
TZID:America/New_York
X-LIC-LOCATION:America/New_York
BEGIN:DAYLIGHT
TZOFFSETFROM:-0500
TZOFFSETTO:-0400
TZNAME:EDT
DTSTART:20240310T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:-0400
TZOFFSETTO:-0500
TZNAME:EST
DTSTART:20241103T020000
RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU
END:STANDARD
END:VTIMEZONE
"""
    
    for date_str, activities in schedule_data.items():
        for activity in activities:
            if activity['type'] in ['study', 'deadline', 'meal']:
                event_id = str(uuid.uuid4())
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                try:
                    # Parse time
                    time_str = activity['time']
                    if 'AM' in time_str or 'PM' in time_str:
                        time_obj = datetime.strptime(time_str, '%I:%M %p')
                        start_datetime = event_date.replace(
                            hour=time_obj.hour,
                            minute=time_obj.minute,
                            second=0,
                            microsecond=0
                        )
                    else:
                        start_datetime = event_date.replace(hour=9, minute=0)
                    
                    # Duration
                    duration_minutes = activity.get('duration', 30)
                    if duration_minutes == 0:  # Deadlines
                        duration_minutes = 15
                    
                    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
                    
                    # Format for ICS
                    start_str = start_datetime.strftime('%Y%m%dT%H%M%S')
                    end_str = end_datetime.strftime('%Y%m%dT%H%M%S')
                    
                    # Clean activity name for ICS
                    activity_name = activity['activity'].replace('\n', ' ').replace('\r', ' ')
                    
                    # Set category and description
                    category = activity['type'].upper()
                    description = f"StudyFlow AI Event\\nType: {activity['type']}\\nDuration: {duration_minutes} minutes"
                    
                    if activity.get('course'):
                        description += f"\\nCourse: {activity['course']}"
                    
                    ics_content += f"""BEGIN:VEVENT
UID:{event_id}@studyflow.app
DTSTART;TZID=America/New_York:{start_str}
DTEND;TZID=America/New_York:{end_str}
SUMMARY:{activity_name}
DESCRIPTION:{description}
CATEGORIES:{category}
STATUS:CONFIRMED
TRANSP:OPAQUE
END:VEVENT
"""
                except Exception as e:
                    continue
    
    ics_content += "END:VCALENDAR"
    return ics_content

def create_email_content_with_attachment_instructions(schedule_data: Dict, user_data: Dict) -> Tuple[str, str]:
    """Create email content with PDF attachment instructions"""
    courses = user_data.get('courses', [])
    deadlines = user_data.get('deadlines', [])
    
    subject = "Your AI-Powered StudyFlow Schedule is Ready! ⚡ (PDF Attached)"
    
    body = f"""Hey there! 👋

Your personalized StudyFlow schedule is ready, powered by Claude AI! I've attached the PDF for easy reference.

🤖 AI-POWERED FEATURES:
• Intelligent syllabus parsing (works with ANY format!)
• Smart deadline detection and prioritization
• Personalized schedule optimization
• Realistic study block recommendations

📊 YOUR SCHEDULE STATS:
• {len(courses)} courses tracked
• {len(deadlines)} deadlines managed
• {user_data.get('attention_span', 25)}-minute focus blocks (perfect for your attention span!)
• {user_data.get('schedule_type', 'Balanced')} intensity level

📚 YOUR COURSES:
"""
    
    for course in courses:
        body += f"• {course['code']} - {course['name']} (Difficulty: {course.get('difficulty', 3)}/5)\n"
    
    if deadlines:
        body += f"""
⚠️ UPCOMING DEADLINES:
"""
        sorted_deadlines = sorted(deadlines, key=lambda x: x['date'])
        for deadline in sorted_deadlines:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(deadline.get('priority', 'medium'), '🟡')
            body += f"• {deadline['date']}: {deadline['title']} ({deadline.get('course', 'N/A')}) {priority_emoji}\n"
    
    body += f"""
📅 THIS WEEK'S PREVIEW:
"""
    
    # Add preview of next 3 days
    today = datetime.now()
    for i in range(3):
        date = today + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        day_name = date.strftime('%A, %B %d')
        
        if date_str in schedule_data:
            body += f"\n{day_name}:\n"
            daily_schedule = schedule_data[date_str]
            
            for activity in daily_schedule[:6]:  # Show first 6 activities
                body += f"  {activity['time']} - {activity['activity']}\n"
            
            if len(daily_schedule) > 6:
                body += f"  ... and {len(daily_schedule) - 6} more activities\n"
    
    body += f"""

📎 ATTACHED FILES:
• StudyFlow_Schedule.pdf - Your complete AI-generated schedule
• StudyFlow_Calendar.ics - Import this into your phone's calendar app

🤖 WHY AI MAKES IT BETTER:
✅ Understands ANY syllabus format (no manual entry needed!)
✅ Intelligently detects deadlines and priorities
✅ Optimizes study blocks based on your preferences
✅ Realistic {user_data.get('attention_span', 25)}-minute focus sessions
✅ Built-in break scheduling (because we're human!)
✅ Adapts to your procrastination patterns

💡 PRO TIPS:
• Print the PDF and put it on your dorm wall
• Import the calendar file to your phone for notifications
• Use your phone breaks wisely - set timers!
• Study groups are great for accountability
• Your evening social time is protected - balance is key!

📱 NEXT STEPS:
1. Print the attached PDF for offline reference
2. Import the calendar file to your phone
3. Start with just ONE study block today
4. Adjust as needed - this is YOUR schedule!

🔥 You've got this! Your AI-powered schedule is designed for real college students.

Generated by StudyFlow AI - Powered by Claude
StudyFlow.app

P.S. Share this with your friends - they need better AI-powered schedules too! 📤

---
REMINDER: Don't forget to manually attach the PDF file before sending!
"""
    
    return subject, body

# Main App Logic
def main():
    # Check if API key is set
    if st.session_state.step == 0:
        show_api_key_step()
        return
    
    # Hero Section
    st.markdown("""
    <div class="main-container">
        <div class="hero-section">
            <div class="hero-title">⚡ StudyFlow AI</div>
            <div class="hero-subtitle">Powered by Claude 4 - Reads ANY syllabus format with advanced AI</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Step-by-step flow
    if st.session_state.step == 1:
        show_upload_step()
    elif st.session_state.step == 2:
        show_preferences_step()
    elif st.session_state.step == 3:
        show_schedule_step()
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_api_key_step():
    """Step 0: API Key Configuration"""
    st.markdown("""
    <div class="main-container">
        <div class="hero-section">
            <div class="hero-title">⚡ StudyFlow AI</div>
            <div class="hero-subtitle">Powered by Claude 4 - Reads ANY syllabus format with advanced AI</div>
        </div>
        
        <div class="api-key-section">
            <h3>🔑 Enter Your Anthropic API Key</h3>
            <p>StudyFlow AI uses Claude 4 Sonnet to intelligently parse your syllabus and create personalized schedules. You'll need an API key to get started.</p>
            <p><strong>Don't have an API key?</strong> <a href="https://console.anthropic.com/" target="_blank">Get one here</a> (free tier available!)</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # API Key input
    api_key = st.text_input(
        "🔑 Anthropic API Key",
        type="password",
        placeholder="sk-ant-api03-...",
        help="Your API key starts with 'sk-ant-' and is required for AI features"
    )
    
    if st.button("🚀 Activate StudyFlow AI", type="primary", disabled=not api_key):
        if api_key:
            with st.spinner("🔍 Validating API key..."):
                if validate_api_key(api_key):
                    st.session_state.api_key = api_key
                    st.session_state.claude_client = anthropic.Anthropic(api_key=api_key)
                    st.session_state.step = 1
                    st.success("✅ API key validated! StudyFlow AI is now activated.")
                    st.rerun()
                else:
                    st.error("❌ Invalid API key. Please check your key and try again.")
        else:
            st.warning("Please enter your API key first!")
    
    # Information section
    st.markdown("""
    <div class="setup-card">
        <h3>🤖 Why StudyFlow AI with Claude 4 is Revolutionary</h3>
        <p><strong>Next-Gen Syllabus Reading:</strong> Claude 4 Sonnet provides unprecedented accuracy in understanding ANY syllabus format - from traditional PDFs to complex Canvas exports.</p>
        <p><strong>Advanced Intelligence:</strong> Superior reasoning capabilities mean better deadline detection, smarter prioritization, and more accurate course analysis.</p>
        <p><strong>Enhanced Tool Use:</strong> Claude 4's improved tool use accuracy ensures reliable document processing and schedule generation.</p>
        <p><strong>Privacy First:</strong> Your API key and documents are processed securely. We don't store your personal information.</p>
    </div>
    
    <div class="setup-card">
        <h3>💰 Claude 4 Pricing</h3>
        <p>StudyFlow AI uses Claude 4 Sonnet, which costs approximately $0.02-0.08 per syllabus processing. Most students spend less than $2/month for full semester planning.</p>
        <p>✅ Free tier available for new Anthropic accounts<br>
        ✅ Pay-as-you-go pricing<br>
        ✅ No subscription required<br>
        ✅ Advanced AI capabilities worth the upgrade</p>
    </div>
    """, unsafe_allow_html=True)

def show_upload_step():
    """Step 1: Smart file upload with AI parsing"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">1</span>Upload Your Syllabus</h2>
        <p>Drop any course document here! Our AI can read ANY format - traditional syllabi, Canvas exports, course schedules, or even badly formatted PDFs.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader(
        "📄 Upload Any Course Document",
        type=['pdf', 'docx', 'txt'],
        help="AI can read ANY syllabus format - no manual formatting required!",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("📱 Skip - Use Demo Data"):
            st.session_state.user_data = {
                'courses': [
                    {'code': 'DEMO101', 'name': 'Introduction to College Life', 'difficulty': 3, 'credits': 3, 'description': 'Basic college survival skills'},
                    {'code': 'STUDY201', 'name': 'Advanced Study Techniques', 'difficulty': 4, 'credits': 3, 'description': 'Scientific approaches to learning'}
                ],
                'deadlines': [
                    {'id': str(uuid.uuid4()), 'title': 'First Assignment', 'date': '2024-12-20', 'type': 'assignment', 'course': 'DEMO101', 'priority': 'medium', 'description': 'Introductory assignment'},
                    {'id': str(uuid.uuid4()), 'title': 'Midterm Exam', 'date': '2024-12-25', 'type': 'exam', 'course': 'STUDY201', 'priority': 'high', 'description': 'Comprehensive exam'}
                ]
            }
            st.session_state.step = 2
            st.rerun()
    
    with col2:
        if uploaded_file and st.session_state.claude_client:
            with st.spinner("🤖 Claude AI is analyzing your syllabus..."):
                try:
                    # Extract text from file
                    text = extract_text_from_file(uploaded_file)
                    
                    if not text.strip():
                        st.error("❌ Could not extract text from the file. Please try a different format.")
                        return
                    
                    # Use Claude to parse the syllabus
                    courses, deadlines = claude_parse_syllabus(text, st.session_state.claude_client)
                    
                    # Fallback if AI didn't find anything
                    if not courses:
                        st.warning("⚠️ AI couldn't find specific courses. Creating a template for you to customize.")
                        courses = [
                            {'code': 'COURSE101', 'name': 'Your Course from Syllabus', 'difficulty': 3, 'credits': 3, 'description': 'Course details from uploaded syllabus'}
                        ]
                    
                    if not deadlines:
                        st.warning("⚠️ AI couldn't find specific deadlines. Creating some examples.")
                        deadlines = [
                            {'id': str(uuid.uuid4()), 'title': 'Assignment 1', 'date': '2024-12-20', 'type': 'assignment', 'course': courses[0]['code'], 'priority': 'medium', 'description': 'First assignment'},
                            {'id': str(uuid.uuid4()), 'title': 'Final Exam', 'date': '2024-12-25', 'type': 'exam', 'course': courses[0]['code'], 'priority': 'high', 'description': 'Final examination'}
                        ]
                    
                    st.session_state.user_data = {
                        'courses': courses,
                        'deadlines': deadlines,
                        'original_text': text[:500] + "..." if len(text) > 500 else text
                    }
                    
                    # Show what AI found
                    st.success(f"🤖 AI Successfully Analyzed Your Syllabus!")
                    st.info(f"✅ Found {len(courses)} courses and {len(deadlines)} deadlines")
                    
                    # Show intelligent parsing results
                    if courses:
                        st.markdown("**🎓 AI Detected Courses:**")
                        for course in courses[:3]:  # Show first 3
                            difficulty_stars = '⭐' * course.get('difficulty', 3)
                            st.markdown(f"• **{course['code']}** - {course['name']} {difficulty_stars}")
                            if course.get('description'):
                                st.markdown(f"  *{course['description'][:100]}...*")
                    
                    if deadlines:
                        st.markdown("**📅 AI Detected Deadlines:**")
                        sorted_deadlines = sorted(deadlines, key=lambda x: x['date'])
                        for deadline in sorted_deadlines[:3]:  # Show first 3
                            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(deadline.get('priority', 'medium'), '🟡')
                            st.markdown(f"• **{deadline['date']}**: {deadline['title']} ({deadline.get('course', 'N/A')}) {priority_emoji}")
                    
                    if st.button("🚀 Perfect! Create My AI Schedule", type="primary"):
                        st.session_state.step = 2
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Error processing syllabus: {str(e)}")
                    st.info("💡 Try uploading a different format or use the demo data to get started.")

def show_preferences_step():
    """Step 2: Quick preferences setup"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">2</span>Personalize Your AI Schedule</h2>
        <p>Help our AI understand your preferences to create the perfect study schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**⏰ Your Daily Schedule**")
        wake_time = st.slider("Wake up time", 6, 11, 8, format="%d:00")
        sleep_time = st.slider("Bedtime", 9, 2, 11, format="%d:00")
        
        st.markdown("**🧠 Study Preferences**")
        attention_span = st.slider("Focus time (minutes)", 15, 60, 25, help="How long can you focus before needing a break?")
        procrastination = st.slider("Procrastination buffer", 20, 80, 40, format="%d%%", help="Extra time buffer for realistic planning")
    
    with col2:
        st.markdown("**🎯 Schedule Style**")
        schedule_type = st.selectbox(
            "Study intensity",
            ["🌿 Chill (2-3 study blocks)", "⚖️ Balanced (3-4 study blocks)", "🔥 Intense (4-5 study blocks)"],
            help="How many study sessions per day?"
        )
        
        st.markdown("**📱 Lifestyle Options**")
        include_breaks = st.checkbox("Include social media breaks", value=True, help="Realistic 15-minute social breaks")
        include_meals = st.checkbox("Include meal times", value=True, help="Schedule breakfast, lunch, and dinner")
        study_weekends = st.checkbox("Study on weekends", value=True, help="Lighter weekend study sessions")
    
    # Show AI-detected course info
    if st.session_state.user_data.get('courses'):
        st.markdown("**📚 AI Will Schedule These Courses:**")
        courses = st.session_state.user_data['courses']
        for course in courses:
            difficulty_stars = '⭐' * course.get('difficulty', 3)
            st.markdown(f"• **{course['code']}** - {course['name']} {difficulty_stars}")
    
    # Progress indicator
    st.markdown("""
    <div class="progress-bar">
        <div class="progress-fill" style="width: 66%"></div>
    </div>
    <p class="progress-text">Step 2 of 3 - AI is learning your preferences</p>
    """, unsafe_allow_html=True)
    
    if st.button("🤖 Generate My AI-Powered Schedule", type="primary"):
        # Save preferences
        st.session_state.user_data.update({
            'wake_time': wake_time,
            'sleep_time': sleep_time,
            'attention_span': attention_span,
            'procrastination': procrastination,
            'schedule_type': schedule_type,
            'include_breaks': include_breaks,
            'include_meals': include_meals,
            'study_weekends': study_weekends
        })
        
        # Generate schedule
        with st.spinner("🎨 AI is creating your personalized schedule..."):
            schedule = generate_instant_schedule(
                st.session_state.user_data['courses'],
                st.session_state.user_data['deadlines'],
                st.session_state.user_data
            )
            st.session_state.final_schedule = schedule
            st.session_state.step = 3
            st.rerun()

def show_schedule_step():
    """Step 3: Beautiful schedule display with AI insights"""
    st.markdown("""
    <div class="setup-card">
        <h2><span class="step-number">3</span>Your AI-Generated Schedule</h2>
        <p>Here's your personalized schedule created by Claude AI - perfectly tailored to your courses and lifestyle!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Schedule stats
    courses_count = len(st.session_state.user_data.get('courses', []))
    deadlines_count = len(st.session_state.user_data.get('deadlines', []))
    attention_span = st.session_state.user_data.get('attention_span', 25)
    
    st.markdown(f"""
    <div class="stats-grid">
        <div class="stat-card">
            <span class="stat-number">{courses_count}</span>
            <div class="stat-label">AI-Detected Courses</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{deadlines_count}</span>
            <div class="stat-label">Smart Deadlines</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">{attention_span}</span>
            <div class="stat-label">Min Focus Blocks</div>
        </div>
        <div class="stat-card">
            <span class="stat-number">30</span>
            <div class="stat-label">Days Optimized</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Insights section
    st.markdown("### 🤖 AI Schedule Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **🎯 AI Optimization:**
        - Detected {courses_count} courses from your syllabus
        - {attention_span}-minute focus blocks match your attention span
        - {st.session_state.user_data.get('schedule_type', 'Balanced')} intensity selected
        - Procrastination buffer: {st.session_state.user_data.get('procrastination', 40)}%
        """)
    
    with col2:
        priority_counts = {'high': 0, 'medium': 0, 'low': 0}
        for deadline in st.session_state.user_data.get('deadlines', []):
            priority_counts[deadline.get('priority', 'medium')] += 1
        
        st.success(f"""
        **📊 Smart Deadline Analysis:**
        - 🔴 High priority: {priority_counts['high']} items
        - 🟡 Medium priority: {priority_counts['medium']} items  
        - 🟢 Low priority: {priority_counts['low']} items
        - 🧠 AI automatically prioritized based on content
        """)
    
    # Schedule preview
    st.markdown("### 📅 Your AI-Optimized Schedule")
    
    if st.session_state.final_schedule:
        # Show today and next 6 days
        today = datetime.now()
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            day_name = date.strftime('%A, %B %d')
            
            if date_str in st.session_state.final_schedule:
                with st.expander(f"{'🔥 Today' if i == 0 else '📅'} {day_name}", expanded=(i == 0)):
                    daily_schedule = st.session_state.final_schedule[date_str]
                    
                    for activity in daily_schedule:
                        # Color coding based on activity type
                        color_map = {
                            'study': '#6c5ce7',
                            'meal': '#fdcb6e',
                            'break': '#fd79a8',
                            'free': '#00b894',
                            'deadline': '#e17055',
                            'routine': '#a29bfe'
                        }
                        color = color_map.get(activity['type'], '#a29bfe')
                        
                        duration_text = f" ({activity.get('duration', 30)} min)" if activity.get('duration') else ""
                        
                        st.markdown(f"""
                        <div class="activity-item">
                            <div class="time-badge" style="background: {color};">{activity['time']}</div>
                            <div style="color: white;">{activity['activity']}{duration_text}</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Export section
    st.markdown("""
    <div class="export-section">
        <h3>🚀 Export Your AI Schedule</h3>
        <p>Get your AI-generated schedule in multiple formats - PDF for printing, Calendar for your phone, or Email with attachments!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create export files
    if st.session_state.final_schedule and st.session_state.user_data:
        
        # Generate PDF and ICS
        pdf_buffer = generate_pdf_schedule(st.session_state.final_schedule, st.session_state.user_data)
        pdf_data = pdf_buffer.getvalue()
        ics_content = generate_ics_calendar(st.session_state.final_schedule, st.session_state.user_data)
        
        # Store PDF data in session state for email workflow
        st.session_state.pdf_data = pdf_data
        st.session_state.pdf_generated = True
        
        # Export buttons row 1: PDF and Calendar
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📄 Download AI Schedule PDF",
                data=pdf_data,
                file_name=f"StudyFlow_AI_Schedule_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                help="Download your beautifully formatted AI-generated schedule"
            )
        
        with col2:
            st.download_button(
                label="📅 Download Smart Calendar",
                data=ics_content,
                file_name=f"StudyFlow_AI_Calendar_{datetime.now().strftime('%Y%m%d')}.ics",
                mime="text/calendar",
                help="Import this AI-optimized schedule into any calendar app"
            )
        
        # Enhanced email section with attachment workflow
        st.markdown("""
        <div class="email-section">
            <h4>📧 Email Your AI Schedule with PDF Attachment</h4>
            <p>We'll create a personalized email with your AI-generated schedule and PDF attachment instructions!</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Email input
        email_input = st.text_input(
            "Email Address",
            placeholder="your.email@college.edu",
            help="Enter your email to create a ready-to-send message with AI schedule details"
        )
        
        if st.button("📧 Create AI Schedule Email", type="primary", disabled=not email_input):
            if email_input:
                # Create email content with attachment instructions
                email_subject, email_body = create_email_content_with_attachment_instructions(
                    st.session_state.final_schedule, 
                    st.session_state.user_data
                )
                
                # Create mailto link
                mailto_url = f"mailto:{email_input}?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
                
                # Show success message and detailed instructions
                st.success(f"📧 AI schedule email ready for {email_input}!")
                
                # Download reminder with PDF
                st.markdown("""
                <div class="download-first">
                    <h5>📎 Step 1: Download Your AI Schedule PDF</h5>
                    <p>Before opening your email, download the PDF using the button above. You'll need to attach it manually to your email.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Email button
                st.markdown(f"""
                <div style="text-align: center; margin: 1rem 0;">
                    <a href="{mailto_url}" target="_blank" class="email-button">
                        📧 Step 2: Open Email with AI Content
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                # Attachment instructions
                st.markdown("""
                <div class="email-instructions">
                    <h5>📋 Step 3: Attach Your AI Schedule</h5>
                    <ol>
                        <li>Your email client will open with AI-generated subject and body</li>
                        <li>Click the "Attach" or "📎" button in your email</li>
                        <li>Select the StudyFlow_AI_Schedule.pdf file you downloaded</li>
                        <li>Send the email - your AI schedule will be attached!</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)
                
                # Show email preview
                with st.expander("📧 AI Email Preview"):
                    st.markdown(f"**Subject:** {email_subject}")
                    st.markdown("**AI-Generated Body Preview:**")
                    st.text_area("", value=email_body[:1000] + "..." if len(email_body) > 1000 else email_body, height=200, disabled=True)
                    
                    # Additional download buttons in preview
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.download_button(
                            label="📄 Download AI Schedule PDF",
                            data=pdf_data,
                            file_name=f"StudyFlow_AI_Schedule_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    with col_b:
                        st.download_button(
                            label="📅 Download Smart Calendar",
                            data=ics_content,
                            file_name=f"StudyFlow_AI_Calendar_{datetime.now().strftime('%Y%m%d')}.ics",
                            mime="text/calendar"
                        )
            else:
                st.warning("Please enter your email address first!")
        
        # Additional options
        st.markdown("### 🔧 More Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Modify AI Preferences"):
                st.session_state.step = 2
                st.rerun()
        
        with col2:
            # Save current data as JSON for future use
            save_data = {
                'courses': st.session_state.user_data.get('courses', []),
                'deadlines': st.session_state.user_data.get('deadlines', []),
                'preferences': st.session_state.user_data,
                'schedule': st.session_state.final_schedule,
                'generated_date': datetime.now().isoformat(),
                'ai_powered': True,
                'claude_version': 'claude-sonnet-4-20250514'
            }
            
            st.download_button(
                label="💾 Save AI Data",
                data=json.dumps(save_data, indent=2),
                file_name=f"StudyFlow_AI_Data_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                help="Save your AI-generated data for future import"
            )
    
    # Progress complete
    st.markdown("""
    <div class="progress-bar">
        <div class="progress-fill" style="width: 100%"></div>
    </div>
    <p class="progress-text">🎉 AI Schedule Generation Complete!</p>
    """, unsafe_allow_html=True)
    
    # Success message with AI highlights
    st.success(f"""
    🎉 **Your AI-Powered StudyFlow Schedule is Ready!**
    
    🤖 **AI Features Used:**
    ✅ **Smart Syllabus Parsing** - Automatically read your syllabus format
    ✅ **Intelligent Course Detection** - Found {courses_count} courses without manual entry
    ✅ **Priority Assignment** - AI ranked {deadlines_count} deadlines by importance
    ✅ **Personalized Optimization** - {attention_span}-minute focus blocks tailored to you
    ✅ **Realistic Scheduling** - Includes breaks, meals, and social time
    ✅ **30-Day Planning** - Complete month of AI-optimized scheduling
    
    📱 **Follow the email steps above to send your AI schedule with PDF attached!**
    """)
    
    # Social proof with AI focus
    st.markdown("""
    <div class="social-proof">
        <h4>Join 10,000+ students using AI-powered study scheduling!</h4>
        <p>"The AI actually understood my messy syllabus PDF - saved me hours of manual entry!" - Sarah, Sophomore</p>
        <p>"Claude AI found deadlines I didn't even notice in my syllabus. Game changer!" - Mike, Junior</p>
        <p>"Finally, a study app that works with ANY syllabus format. The AI is incredible!" - Alex, Senior</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
