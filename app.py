"""
Health Guardian: Medical Report Summarizer - Main Application
A comprehensive AI-powered medical report analysis tool
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import io

# Import utilities
from utils.grok_client import GrokClient
from utils.file_processor import FileProcessor
from utils.medical_analyzer import MedicalAnalyzer
from utils.translator import Translator
from utils.export_handler import ExportHandler

# Import modules
from modules.summarizer import Summarizer
from modules.abnormal_detector import AbnormalDetector
from modules.terminology import TerminologySimplifier
from modules.risk_assessor import RiskAssessor
from modules.insights_generator import InsightsGenerator
from modules.chatbot import Chatbot

# Import config
from config import Config

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.APP_ICON,
    layout=Config.PAGE_LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: blue;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-top: 1rem;
    }
    .info-box {
        background-color: blue;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FFA726;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #2196F3;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #E53935;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #43A047;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    .chat-message {
      background: #1565C0;
      color: white;
      border-radius: 10px;
      padding: 15px;
    }
    .user-message {
        background-color: blue;
        text-align: right;
    }
    .bot-message {
        background-color: skyblue;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'report_text' not in st.session_state:
        st.session_state.report_text = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Home'


def create_sidebar():
    """Create sidebar navigation"""
    with st.sidebar:
        st.markdown(f"<h2 style='color: #1E88E5;'>{Config.APP_ICON} Health-Guardian: Medical Report Summarizer</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Language selector
        translator = Translator()
        language = st.selectbox(
            translator.get_ui_text('language', st.session_state.language),
            options=list(Config.SUPPORTED_LANGUAGES.keys()),
            format_func=lambda x: Config.SUPPORTED_LANGUAGES[x],
            key='language_selector'
        )
        st.session_state.language = language
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### Navigation")
        pages = {
            'Home': '🏠 Home',
            'Upload': '📤 Upload Report',
            'Summary': '📊 View Summary',
            'Chatbot': '💬 Ask Questions',
            'Export': '📥 Export Report'
        }
        
        for page_key, page_label in pages.items():
            if st.button(page_label, key=f'nav_{page_key}'):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # About section
        st.markdown("### About")
        st.info(
            "This AI-powered tool helps you understand your medical reports "
            "by providing summaries, highlighting abnormal values, and offering "
            "personalized health insights."
        )
        
        # Disclaimer
        st.warning(
            "⚠️ **Disclaimer**: This tool is for informational purposes only. "
            "Always consult healthcare professionals for medical advice."
        )


def show_home_page():
    """Display home page"""
    translator = Translator()
    lang = st.session_state.language
    
    st.markdown(f"<div class='main-header'>{translator.get_ui_text('app_title', lang)}</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
        <h3>Welcome to Medical Report Summarizer! 🏥</h3>
        <p>Your AI-powered assistant for understanding medical reports.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features
    st.markdown("<div class='sub-header'>Key Features</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Report Analysis
        - Comprehensive summarization
        - Key findings extraction
        - Test result categorization
        """)
    
    with col2:
        st.markdown("""
        ### ⚠️ Abnormal Detection
        - Automatic value comparison
        - Severity classification
        - Color-coded highlights
        """)
    
    with col3:
        st.markdown("""
        ### 💡 Health Insights
        - Risk assessment
        - Personalized recommendations
        - Lifestyle guidance
        """)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        ### 📖 Term Simplification
        - Medical jargon explained
        - Easy-to-understand language
        - Interactive glossary
        """)
    
    with col5:
        st.markdown("""
        ### 💬 AI Chatbot
        - Ask questions
        - Get clarifications
        - Context-aware responses
        """)
    
    with col6:
        st.markdown("""
        ### 🌐 Multilingual
        - English & Hindi support
        - Easy language switching
        - Translated insights
        """)
    
    # How to use
    st.markdown("<div class='sub-header'>How to Use</div>", unsafe_allow_html=True)
    
    st.markdown("""
    1. **Upload Report**: Click on 'Upload Report' and select your medical report (PDF, image, or text)
    2. **View Analysis**: Review the comprehensive summary and abnormal values
    3. **Ask Questions**: Use the chatbot to get clarifications
    4. **Export Results**: Download your analysis as PDF or text
    """)
    
    # Get started button
    if st.button("🚀 Get Started - Upload Your Report", type="primary"):
        st.session_state.current_page = 'Upload'
        st.rerun()


def show_upload_page():
    """Display upload page"""
    translator = Translator()
    lang = st.session_state.language
    
    st.markdown(f"<div class='main-header'>{translator.get_ui_text('upload_report', lang)}</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
        <p>Upload your medical report in PDF, image (JPG, PNG), or text format. Maximum file size: 10MB</p>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'jpg', 'jpeg', 'png', 'txt'],
        help="Supported formats: PDF, JPG, PNG, TXT"
    )
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        # Analyze button
        if st.button("🔍 Analyze Report", type="primary"):
            with st.spinner(translator.get_ui_text('analyzing', lang)):
                analyze_report(uploaded_file)


def analyze_report(uploaded_file):
    """Analyze uploaded medical report"""
    try:
        # Initialize processors
        file_processor = FileProcessor()
        medical_analyzer = MedicalAnalyzer()
        summarizer = Summarizer()
        abnormal_detector = AbnormalDetector()
        risk_assessor = RiskAssessor()
        insights_generator = InsightsGenerator()
        terminology_simplifier = TerminologySimplifier()
        
        # Step 1: Extract text
        st.info("📄 Extracting text from file...")
        extraction_result = file_processor.extract_text(uploaded_file, uploaded_file.name)
        
        if not extraction_result['success']:
            st.error(f"❌ Error: {extraction_result['error']}")
            return
        
        report_text = extraction_result['text']
        st.session_state.report_text = report_text
        st.success(f"✅ Extracted {len(report_text)} characters")
        
        # Step 2: Extract patient info
        st.info("👤 Extracting patient information...")
        patient_info = file_processor.extract_patient_info(report_text)
        
        # Step 3: Analyze report
        st.info("🔬 Analyzing medical report...")
        analysis = medical_analyzer.analyze_report(report_text, patient_info)
        
        # Step 4: Generate summary
        st.info("📝 Generating summary...")
        summary_result = summarizer.generate_summary(report_text, patient_info)
        
        # Step 5: Detect abnormal values
        st.info("⚠️ Detecting abnormal values...")
        test_values = file_processor.extract_test_values(report_text)
        abnormal_values = abnormal_detector.detect_abnormal_values(
            test_values,
            patient_info.get('gender')
        )
        
        # Step 6: Risk assessment
        st.info("📊 Performing risk assessment...")
        risk_assessment = risk_assessor.assess_risk(abnormal_values, patient_info)
        
        # Step 7: Generate insights
        st.info("💡 Generating health insights...")
        insights = insights_generator.generate_insights(
            summary_result.get('summary', ''),
            abnormal_values,
            patient_info,
            risk_assessment
        )
        
        # Store results
        st.session_state.analysis_results = {
            'patient_info': patient_info,
            'summary': summary_result,
            'test_values': test_values,
            'abnormal_values': abnormal_values,
            'risk_assessment': risk_assessment,
            'insights': insights,
            'report_text': report_text
        }
        
        st.success("✅ Analysis complete!")
        st.balloons()
        
        # Navigate to summary page
        if st.button("📊 View Results"):
            st.session_state.current_page = 'Summary'
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.exception(e)


def show_summary_page():
    """Display summary page"""
    if st.session_state.analysis_results is None:
        st.warning("⚠️ No analysis results available. Please upload and analyze a report first.")
        if st.button("📤 Go to Upload"):
            st.session_state.current_page = 'Upload'
            st.rerun()
        return
    
    results = st.session_state.analysis_results
    translator = Translator()
    lang = st.session_state.language
    
    st.markdown(f"<div class='main-header'>{translator.get_ui_text('summary', lang)}</div>", unsafe_allow_html=True)
    
    # Patient Information
    if results.get('patient_info'):
        st.markdown("<div class='sub-header'>👤 Patient Information</div>", unsafe_allow_html=True)
        patient_info = results['patient_info']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if patient_info.get('age'):
                st.metric("Age", patient_info['age'])
        with col2:
            if patient_info.get('gender'):
                st.metric("Gender", patient_info['gender'])
        with col3:
            if patient_info.get('date'):
                st.metric("Report Date", patient_info['date'])
        with col4:
            if patient_info.get('id'):
                st.metric("Patient ID", patient_info['id'])
    
    # Executive Summary
    st.markdown("<div class='sub-header'>📋 Executive Summary</div>", unsafe_allow_html=True)
    summary = results.get('summary', {})
    if summary.get('executive_summary'):
        st.markdown(f"<div class='info-box'>{summary['executive_summary']}</div>", unsafe_allow_html=True)
    elif summary.get('summary'):
        st.write(summary['summary'][:500] + "...")
    
    # Risk Assessment
    st.markdown("<div class='sub-header'>📊 Risk Assessment</div>", unsafe_allow_html=True)
    risk = results.get('risk_assessment', {})
    
    if risk.get('success'):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Risk gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=risk.get('risk_score', 0),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Risk Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': risk.get('risk_color', '#1E88E5')},
                    'steps': [
                        {'range': [0, 30], 'color': "#E8F5E9"},
                        {'range': [30, 60], 'color': "#FFF9C4"},
                        {'range': [60, 85], 'color': "#FFCCBC"},
                        {'range': [85, 100], 'color': "#FFCDD2"}
                    ],
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
            
            st.metric("Risk Level", risk.get('risk_level', 'Unknown').upper())
        
        with col2:
            st.markdown("**Risk Explanation:**")
            st.write(risk.get('explanation', 'No explanation available'))
            
            if risk.get('recommendations'):
                st.markdown("**Recommendations:**")
                for rec in risk['recommendations'][:5]:
                    st.write(f"• {rec}")
    
    # Abnormal Values
    st.markdown("<div class='sub-header'>⚠️ Abnormal Values</div>", unsafe_allow_html=True)
    abnormal_values = results.get('abnormal_values', [])
    
    if abnormal_values:
        # Group by severity
        critical = [v for v in abnormal_values if v.get('severity') == 'critical']
        abnormal = [v for v in abnormal_values if v.get('severity') == 'abnormal']
        borderline = [v for v in abnormal_values if v.get('severity') == 'borderline']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Critical", len(critical), delta=None, delta_color="inverse")
        with col2:
            st.metric("Abnormal", len(abnormal))
        with col3:
            st.metric("Borderline", len(borderline))
        
        # Display abnormal values
        for value in abnormal_values[:10]:  # Show top 10
            severity = value.get('severity', 'abnormal')
            color_map = {
                'critical': 'danger-box',
                'abnormal': 'warning-box',
                'borderline': 'info-box'
            }
            box_class = color_map.get(severity, 'info-box')
            
            st.markdown(f"""
            <div class='{box_class}'>
                <strong>{value.get('test_name')}</strong><br>
                Value: {value.get('value')} {value.get('unit')}<br>
                Normal Range: {value.get('normal_range')}<br>
                Severity: {severity.upper()}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No abnormal values detected!")
    
    # Health Insights
    st.markdown("<div class='sub-header'>💡 Health Insights</div>", unsafe_allow_html=True)
    insights = results.get('insights', {})
    
    if insights.get('success'):
        tab1, tab2, tab3, tab4 = st.tabs([
            "Lifestyle", "Diet", "Exercise", "Monitoring"
        ])
        
        with tab1:
            if insights.get('lifestyle_recommendations'):
                for rec in insights['lifestyle_recommendations']:
                    st.write(f"• {rec}")
        
        with tab2:
            if insights.get('dietary_recommendations'):
                for rec in insights['dietary_recommendations']:
                    st.write(f"• {rec}")
        
        with tab3:
            if insights.get('exercise_recommendations'):
                for rec in insights['exercise_recommendations']:
                    st.write(f"• {rec}")
        
        with tab4:
            if insights.get('monitoring_plan'):
                for item in insights['monitoring_plan']:
                    st.markdown(f"""
                    **{item.get('parameter')}**
                    - Frequency: {item.get('frequency')}
                    - Method: {item.get('method')}
                    - Target: {item.get('target')}
                    """)


def show_chatbot_page():
    """Display chatbot page"""
    if st.session_state.analysis_results is None:
        st.warning("⚠️ Please upload and analyze a report first to use the chatbot.")
        if st.button("📤 Go to Upload"):
            st.session_state.current_page = 'Upload'
            st.rerun()
        return
    
    st.markdown("<div class='main-header'>💬 Ask Questions</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
        <p>Ask me anything about your medical report. I'm here to help you understand your results!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize chatbot
    chatbot = Chatbot()
    
    # Display chat history
    for message in st.session_state.chat_history:
        role = message.get('role')
        content = message.get('content')
        
        if role == 'user':
            st.markdown(f"<div class='chat-message user-message'><strong>You:</strong><br>{content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-message bot-message'><strong>Assistant:</strong><br>{content}</div>", unsafe_allow_html=True)
    
    # Chat input
    user_input = st.text_input("Type your question here...", key="chat_input")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Send", type="primary"):
            if user_input:
                # Add user message
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Get bot response
                with st.spinner("Thinking..."):
                    response = chatbot.chat(
                        user_input,
                        st.session_state.chat_history,
                        st.session_state.analysis_results
                    )
                    print("=" * 50)
                    print("CHATBOT RESPONSE:")
                    print(type(response))
                    print(response)
                    print("=" * 50)
                
                if response is None:
                    st.error("Chatbot returned no response.")
                elif isinstance(response, dict):
                    if response.get("success"):
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response.get("response", "")
                        })
                        st.rerun()
                    else:
                        st.error(response.get("error", "Unknown chatbot error"))
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": str(response)
                    })
                    st.rerun()
    
    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Suggested questions
    if not st.session_state.chat_history:
        st.markdown("### Suggested Questions:")
        suggestions = [
            "What do my abnormal values mean?",
            "How serious are my test results?",
            "What lifestyle changes should I make?",
            "What should I discuss with my doctor?"
        ]
        for suggestion in suggestions:
            if st.button(suggestion, key=f"suggest_{suggestion}"):
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': suggestion
                })
                st.rerun()


def show_export_page():
    """Display export page"""
    if st.session_state.analysis_results is None:
        st.warning("⚠️ No analysis results available to export.")
        if st.button("📤 Go to Upload"):
            st.session_state.current_page = 'Upload'
            st.rerun()
        return
    
    st.markdown("<div class='main-header'>📥 Export Report</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
        <p>Download your medical report analysis in PDF or text format.</p>
    </div>
    """, unsafe_allow_html=True)
    
    results = st.session_state.analysis_results
    export_handler = ExportHandler()
    
    # Prepare export data
    export_data = {
        'patient_info': results.get('patient_info', {}),
        'summary': results.get('summary', {}).get('summary', ''),
        'abnormal_values': results.get('abnormal_values', []),
        'risk_assessment': results.get('risk_assessment', {}).get('explanation', ''),
        'health_insights': results.get('insights', {}).get('ai_insights', '')
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 PDF Export")
        st.write("Download a professionally formatted PDF report")
        
        if st.button("Generate PDF", type="primary"):
            with st.spinner("Generating PDF..."):
                try:
                    pdf_buffer = export_handler.export_to_pdf(export_data)
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_buffer,
                        file_name=export_handler.generate_filename('pdf'),
                        mime="application/pdf"
                    )
                    st.success("✅ PDF generated successfully!")
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
    
    with col2:
        st.markdown("### 📝 Text Export")
        st.write("Download a plain text version of your report")
        
        if st.button("Generate Text", type="primary"):
            with st.spinner("Generating text..."):
                try:
                    text_content = export_handler.export_to_text(export_data)
                    st.download_button(
                        label="📥 Download Text",
                        data=text_content,
                        file_name=export_handler.generate_filename('txt'),
                        mime="text/plain"
                    )
                    st.success("✅ Text file generated successfully!")
                except Exception as e:
                    st.error(f"Error generating text: {str(e)}")


def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Create sidebar
    create_sidebar()
    
    # Route to appropriate page
    page = st.session_state.current_page
    
    if page == 'Home':
        show_home_page()
    elif page == 'Upload':
        show_upload_page()
    elif page == 'Summary':
        show_summary_page()
    elif page == 'Chatbot':
        show_chatbot_page()
    elif page == 'Export':
        show_export_page()
    else:
        show_home_page()


if __name__ == "__main__":
    main()

# Made with Bob
