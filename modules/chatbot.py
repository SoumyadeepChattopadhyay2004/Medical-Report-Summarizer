"""
AI Chatbot Module
Context-aware medical Q&A chatbot
"""

import logging
from typing import Dict, List, Any, Optional
from utils.grok_client import GrokClient
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class Chatbot:
    """AI-powered medical chatbot with context awareness"""
    
    def __init__(self):
        """Initialize chatbot"""
        self.grok_client = GrokClient()
        self.max_history = Config.MAX_CHAT_HISTORY
        
    def chat(
        self,
        user_query: str,
        conversation_history: List[Dict[str, str]],
        report_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process user query and generate response
        
        Args:
            user_query: User's question
            conversation_history: Previous conversation turns
            report_context: Medical report context
            
        Returns:
            Dictionary containing response and metadata
        """
        try:
            logger.info(f"Processing chatbot query: {user_query[:50]}...")
            
            # Build context string from report
            context_str = self._build_context_string(report_context)
            
            # Get response from Grok
            response = self.grok_client.chat_response(
                user_query=user_query,
                conversation_history=conversation_history,
                report_context=context_str
            )
            
            if response:
                # Generate follow-up suggestions
                suggestions = self._generate_suggestions(user_query, report_context)
                
                return {
                    "success": True,
                    "response": response,
                    "suggestions": suggestions,
                    "timestamp": self._get_timestamp()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate response"
                }
                
        except Exception as e:
            logger.error(f"Error in chatbot: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error. Please try again."
            }
    
    def _build_context_string(self, report_context: Dict[str, Any]) -> str:
        """
        Build context string from report data
        
        Args:
            report_context: Report context dictionary
            
        Returns:
            Formatted context string
        """
        print("REPORT CONTEXT TYPE:", type(report_context))
        print("SUMMARY TYPE:", type(report_context.get("summary")))
        print("SUMMARY VALUE:", report_context.get("summary"))
        context_parts = []
        
        # Add summary
        if report_context.get('summary'):
            summary = report_context['summary']
            if isinstance(summary, str):
                context_parts.append(f"Report Summary:\n{summary[:500]}")
            else:
                context_parts.append(f"Report Summary:\n{summary.get('summary', '')[:500]}")

        
        # Add abnormal values
        if report_context.get('abnormal_values'):
            abnormal_list = []
            for value in report_context['abnormal_values'][:5]:  # Top 5
                abnormal_list.append(
                    f"- {value.get('test_name')}: {value.get('value')} {value.get('unit')} "
                    f"(Severity: {value.get('severity')})"
                )
            if abnormal_list:
                context_parts.append("Abnormal Values:\n" + "\n".join(abnormal_list))
        
        # Add risk assessment
        if report_context.get('risk_assessment'):
            risk = report_context['risk_assessment']
            context_parts.append(
                f"Risk Assessment: {risk.get('risk_level', 'Unknown')} "
                f"(Score: {risk.get('risk_score', 0)})"
            )
        
        return "\n\n".join(context_parts)
    
    def _generate_suggestions(
        self,
        user_query: str,
        report_context: Dict[str, Any]
    ) -> List[str]:
        """
        Generate follow-up question suggestions
        
        Args:
            user_query: User's current query
            report_context: Report context
            
        Returns:
            List of suggested questions
        """
        suggestions = []
        
        # General suggestions
        general_suggestions = [
            "What do my abnormal values mean?",
            "What lifestyle changes should I make?",
            "How serious are my test results?",
            "What should I discuss with my doctor?",
            "Are there any immediate actions I should take?"
        ]
        
        # Context-specific suggestions
        if report_context.get('abnormal_values'):
            test_names = [v.get('test_name') for v in report_context['abnormal_values'][:3]]
            for test_name in test_names:
                if test_name:
                    suggestions.append(f"Tell me more about {test_name}")
        
        # Add general suggestions
        suggestions.extend(general_suggestions)
        
        # Remove duplicates and limit
        suggestions = list(dict.fromkeys(suggestions))
        return suggestions[:5]
    
    def _get_timestamp(self) -> str:
        """
        Get current timestamp
        
        Returns:
            Formatted timestamp string
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def get_predefined_responses(self) -> Dict[str, str]:
        """
        Get predefined responses for common questions
        
        Returns:
            Dictionary of questions and responses
        """
        return {
            "hello": "Hello! I'm here to help you understand your medical report. Feel free to ask me any questions about your test results.",
            "help": "I can help you understand your medical report, explain test results, clarify medical terms, and provide general health information. What would you like to know?",
            "disclaimer": "Please note that I provide information based on your report, but I'm not a substitute for professional medical advice. Always consult with your healthcare provider for medical decisions.",
            "emergency": "If you're experiencing a medical emergency, please call emergency services immediately or visit the nearest emergency room. Do not rely on this chatbot for emergency medical advice."
        }
    
    def detect_intent(self, user_query: str) -> str:
        """
        Detect user's intent from query
        
        Args:
            user_query: User's question
            
        Returns:
            Intent category
        """
        query_lower = user_query.lower()
        
        # Greeting
        if any(word in query_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        
        # Help request
        if any(word in query_lower for word in ['help', 'assist', 'guide']):
            return 'help'
        
        # Explanation request
        if any(word in query_lower for word in ['what is', 'explain', 'mean', 'definition']):
            return 'explanation'
        
        # Recommendation request
        if any(word in query_lower for word in ['should i', 'recommend', 'advice', 'suggest']):
            return 'recommendation'
        
        # Severity/Risk inquiry
        if any(word in query_lower for word in ['serious', 'dangerous', 'risk', 'worry', 'concern']):
            return 'severity'
        
        # Treatment inquiry
        if any(word in query_lower for word in ['treatment', 'cure', 'medicine', 'medication']):
            return 'treatment'
        
        return 'general'
    
    def format_response(self, response: str, intent: str) -> str:
        """
        Format response based on intent
        
        Args:
            response: Raw response text
            intent: Detected intent
            
        Returns:
            Formatted response
        """
        # Add appropriate prefix based on intent
        prefixes = {
            'greeting': "👋 ",
            'help': "ℹ️ ",
            'explanation': "📖 ",
            'recommendation': "💡 ",
            'severity': "⚠️ ",
            'treatment': "💊 "
        }
        
        prefix = prefixes.get(intent, "")
        
        # Add disclaimer for medical advice
        if intent in ['recommendation', 'treatment', 'severity']:
            disclaimer = "\n\n⚠️ Remember: This is general information. Please consult your healthcare provider for personalized medical advice."
            return prefix + response + disclaimer
        
        return prefix + response
    
    def validate_query(self, user_query: str) -> Dict[str, Any]:
        """
        Validate user query
        
        Args:
            user_query: User's question
            
        Returns:
            Validation result
        """
        if not user_query or not user_query.strip():
            return {
                "valid": False,
                "error": "Please enter a question"
            }
        
        if len(user_query) < 3:
            return {
                "valid": False,
                "error": "Question is too short"
            }
        
        if len(user_query) > 500:
            return {
                "valid": False,
                "error": "Question is too long (max 500 characters)"
            }
        
        return {
            "valid": True
        }
    
    def get_conversation_summary(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate summary of conversation
        
        Args:
            conversation_history: List of conversation turns
            
        Returns:
            Summary text
        """
        if not conversation_history:
            return "No conversation yet."
        
        total_turns = len(conversation_history) // 2  # User + Assistant = 1 turn
        
        # Extract topics discussed
        topics = set()
        for turn in conversation_history:
            if turn.get('role') == 'user':
                content = turn.get('content', '').lower()
                if 'glucose' in content or 'sugar' in content:
                    topics.add('blood sugar')
                if 'cholesterol' in content or 'lipid' in content:
                    topics.add('cholesterol')
                if 'pressure' in content:
                    topics.add('blood pressure')
                if 'risk' in content:
                    topics.add('health risks')
        
        summary = f"Conversation: {total_turns} question(s) asked"
        if topics:
            summary += f"\nTopics discussed: {', '.join(topics)}"
        
        return summary

# Made with Bob
