"""
Grok API Client for Medical Report Summarizer
Handles all interactions with the Grok API (X.AI)
"""

import time
import logging
from typing import Optional, Dict, List, Any
from openai import OpenAI
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class GrokClient:
    """Client for interacting with Grok API"""
    
    def __init__(self):
        """Initialize Grok API client"""
        self.client = OpenAI(
            api_key=Config.GROK_API_KEY,
            base_url=Config.GROK_API_BASE
        )
        self.model = Config.GROK_MODEL
        self.temperature = Config.AI_TEMPERATURE
        self.max_tokens = Config.AI_MAX_TOKENS
        
    def generate_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate completion from Grok API
        
        Args:
            prompt: User prompt/question
            system_message: System message to set context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            max_retries: Maximum number of retry attempts
            
        Returns:
            Generated text response or None if failed
        """
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add user prompt
        messages.append({"role": "user", "content": prompt})
        
        # Use provided parameters or defaults
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                logger.info(f"Sending request to Grok API (attempt {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temp,
                    max_tokens=tokens
                )
                
                # Extract and return the response text
                if response.choices and len(response.choices) > 0:
                    result = response.choices[0].message.content
                    logger.info("Successfully received response from Grok API")
                    return result
                else:
                    logger.warning("Empty response from Grok API")
                    return None
                    
            except Exception as e:
                logger.error(f"Error calling Grok API (attempt {attempt + 1}): {str(e)}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Request failed.")
                    return None
        
        return None
    
    def generate_streaming_completion(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Generate streaming completion from Grok API
        
        Args:
            prompt: User prompt/question
            system_message: System message to set context
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            
        Yields:
            Text chunks as they arrive
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens
        
        try:
            logger.info("Starting streaming request to Grok API")
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
                        
        except Exception as e:
            logger.error(f"Error in streaming completion: {str(e)}")
            yield f"Error: {str(e)}"
    
    def analyze_medical_report(self, report_text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze medical report and extract structured information
        
        Args:
            report_text: Raw medical report text
            
        Returns:
            Dictionary containing analysis results
        """
        system_message = """You are an expert medical AI assistant specializing in analyzing medical reports. 
        Your task is to extract and structure information from medical reports accurately and comprehensively."""
        
        prompt = f"""Analyze the following medical report and provide a comprehensive summary:

Report Text:
{report_text}

Please provide:
1. Executive Summary (2-3 sentences highlighting key findings)
2. Patient Information (if available: name, age, gender, date)
3. Test Results Overview (organized by category)
4. Key Findings (most important results)
5. Abnormal Values (values outside normal ranges)
6. Recommendations (if any mentioned in the report)

Format your response in clear sections with proper headings."""
        
        response = self.generate_completion(prompt, system_message)
        
        if response:
            return {
                "success": True,
                "summary": response,
                "raw_text": report_text
            }
        else:
            return {
                "success": False,
                "error": "Failed to analyze report",
                "raw_text": report_text
            }
    
    def simplify_medical_term(self, term: str, context: str = "") -> Optional[str]:
        """
        Simplify medical terminology for layman understanding
        
        Args:
            term: Medical term to simplify
            context: Surrounding context for better explanation
            
        Returns:
            Simplified explanation
        """
        system_message = """You are a medical educator who excels at explaining complex medical terms 
        in simple, easy-to-understand language for non-medical people."""
        
        prompt = f"""Explain the following medical term in simple language:

Medical Term: {term}
Context: {context}

Provide:
1. Simple definition (one sentence)
2. What it means for health (practical implications)
3. Common causes or related factors (if applicable)

Keep the explanation clear, concise, and easy to understand."""
        
        return self.generate_completion(prompt, system_message, max_tokens=500)
    
    def assess_health_risk(
        self,
        abnormal_values: List[Dict[str, Any]],
        patient_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Assess health risks based on abnormal values
        
        Args:
            abnormal_values: List of abnormal test results
            patient_info: Patient demographic information
            
        Returns:
            Risk assessment with explanations
        """
        system_message = """You are a medical risk assessment expert. Analyze test results and provide 
        clear, explainable risk assessments with actionable recommendations."""
        
        # Format abnormal values for prompt
        values_text = "\n".join([
            f"- {v.get('test_name', 'Unknown')}: {v.get('value', 'N/A')} {v.get('unit', '')} "
            f"(Normal: {v.get('normal_range', 'N/A')}, Severity: {v.get('severity', 'Unknown')})"
            for v in abnormal_values
        ])
        
        prompt = f"""Assess the health risks based on the following abnormal test results:

Patient Information:
- Age: {patient_info.get('age', 'Unknown')}
- Gender: {patient_info.get('gender', 'Unknown')}

Abnormal Values:
{values_text}

Please provide:
1. Overall Risk Level (Low/Moderate/High/Critical)
2. Risk Score (0-100)
3. Key Risk Factors (what's contributing to the risk)
4. Explanation (why these values are concerning)
5. Immediate Actions (what should be done urgently)
6. Lifestyle Recommendations (diet, exercise, habits)
7. Follow-up Tests (additional tests that may be needed)

Be specific and provide actionable insights."""
        
        response = self.generate_completion(prompt, system_message, max_tokens=2000)
        
        if response:
            return {
                "success": True,
                "assessment": response,
                "abnormal_count": len(abnormal_values)
            }
        else:
            return {
                "success": False,
                "error": "Failed to assess risk"
            }
    
    def generate_health_insights(
        self,
        report_summary: str,
        abnormal_values: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Generate personalized health insights and recommendations
        
        Args:
            report_summary: Summary of the medical report
            abnormal_values: List of abnormal values
            
        Returns:
            Personalized health insights
        """
        system_message = """You are a health advisor providing personalized, actionable health insights 
        based on medical test results. Focus on practical recommendations."""
        
        values_text = "\n".join([
            f"- {v.get('test_name', 'Unknown')}: {v.get('value', 'N/A')} (Severity: {v.get('severity', 'Unknown')})"
            for v in abnormal_values
        ])
        
        prompt = f"""Based on the following medical report analysis, provide personalized health insights:

Report Summary:
{report_summary}

Abnormal Values:
{values_text}

Please provide:
1. Immediate Actions (urgent steps to take)
2. Lifestyle Modifications (specific diet, exercise, sleep recommendations)
3. Preventive Measures (long-term health strategies)
4. Monitoring Plan (what to track regularly)
5. When to Seek Medical Help (warning signs to watch for)

Make recommendations specific, practical, and easy to follow."""
        
        return self.generate_completion(prompt, system_message, max_tokens=2000)
    
    def chat_response(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        report_context: str
    ) -> Optional[str]:
        """
        Generate chatbot response with context awareness
        
        Args:
            user_query: User's question
            conversation_history: Previous conversation turns
            report_context: Medical report context
            
        Returns:
            Chatbot response
        """
        system_message = f"""You are a helpful medical AI assistant. You have access to the user's medical report.
        Answer questions clearly and accurately. Always:
        1. Be empathetic and supportive
        2. Explain medical terms in simple language
        3. Provide context and explanations
        4. Suggest consulting healthcare providers for medical decisions
        5. Never diagnose or prescribe treatments

Report Context:
{report_context}

Remember: You are providing information, not medical advice. Always recommend consulting with healthcare professionals."""
        
        # Build messages with conversation history
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history (limit to last 10 turns)
        for turn in conversation_history[-10:]:
            messages.append(turn)
        
        # Add current query
        messages.append({"role": "user", "content": user_query})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in chat response: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."

# Made with Bob
