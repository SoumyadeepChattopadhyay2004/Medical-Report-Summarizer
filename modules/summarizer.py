"""
Report Summarizer Module
Generates comprehensive summaries of medical reports
"""

import logging
from typing import Dict, Any, Optional
from utils.grok_client import GrokClient
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class Summarizer:
    """Generate medical report summaries"""
    
    def __init__(self):
        """Initialize summarizer"""
        self.grok_client = GrokClient()
        
    def generate_summary(
        self,
        report_text: str,
        patient_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive summary of medical report
        
        Args:
            report_text: Raw medical report text
            patient_info: Optional patient information
            
        Returns:
            Dictionary containing summary and structured information
        """
        try:
            logger.info("Generating medical report summary")
            
            # Build context with patient info if available
            context = ""
            if patient_info:
                context = f"""
Patient Information:
- Age: {patient_info.get('age', 'Unknown')}
- Gender: {patient_info.get('gender', 'Unknown')}
- Report Date: {patient_info.get('date', 'Unknown')}
"""
            
            # Create comprehensive prompt
            system_message = """You are an expert medical AI assistant specializing in analyzing and summarizing medical reports. 
Your summaries should be clear, comprehensive, and organized."""
            
            prompt = f"""{context}

Analyze the following medical report and provide a comprehensive summary:

{report_text}

Please provide:

1. **Executive Summary** (2-3 sentences highlighting the most important findings)

2. **Key Findings** (bullet points of significant results)

3. **Test Results by Category** (organize results by body system or test type)

4. **Notable Observations** (any patterns, trends, or concerning findings)

5. **Mentioned Recommendations** (if any recommendations are present in the report)

Format your response with clear section headings and make it easy to understand."""
            
            # Get AI-generated summary
            response = self.grok_client.generate_completion(
                prompt=prompt,
                system_message=system_message,
                max_tokens=2000
            )
            
            if response:
                # Parse the response into structured format
                structured_summary = self._parse_summary(response)
                
                return {
                    "success": True,
                    "summary": response,
                    "structured": structured_summary,
                    "executive_summary": structured_summary.get("executive_summary", ""),
                    "key_findings": structured_summary.get("key_findings", []),
                    "test_results": structured_summary.get("test_results", {}),
                    "observations": structured_summary.get("observations", []),
                    "recommendations": structured_summary.get("recommendations", [])
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to generate summary"
                }
                
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_summary(self, summary_text: str) -> Dict[str, Any]:
        """
        Parse AI-generated summary into structured format
        
        Args:
            summary_text: Raw summary text from AI
            
        Returns:
            Structured dictionary
        """
        structured = {
            "executive_summary": "",
            "key_findings": [],
            "test_results": {},
            "observations": [],
            "recommendations": []
        }
        
        try:
            # Split into sections
            sections = summary_text.split('\n\n')
            
            current_section = None
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                
                # Identify section type
                section_lower = section.lower()
                
                if 'executive summary' in section_lower:
                    current_section = 'executive_summary'
                    # Extract content after the heading
                    lines = section.split('\n')
                    content = '\n'.join(lines[1:]) if len(lines) > 1 else section
                    structured['executive_summary'] = content.strip()
                    
                elif 'key finding' in section_lower:
                    current_section = 'key_findings'
                    # Extract bullet points
                    lines = section.split('\n')[1:]  # Skip heading
                    for line in lines:
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                            structured['key_findings'].append(line.lstrip('-•* '))
                            
                elif 'observation' in section_lower or 'notable' in section_lower:
                    current_section = 'observations'
                    lines = section.split('\n')[1:]
                    for line in lines:
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                            structured['observations'].append(line.lstrip('-•* '))
                            
                elif 'recommendation' in section_lower:
                    current_section = 'recommendations'
                    lines = section.split('\n')[1:]
                    for line in lines:
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                            structured['recommendations'].append(line.lstrip('-•* '))
                            
        except Exception as e:
            logger.error(f"Error parsing summary: {str(e)}")
        
        return structured
    
    def generate_quick_summary(self, report_text: str) -> str:
        """
        Generate a quick, concise summary (1-2 sentences)
        
        Args:
            report_text: Medical report text
            
        Returns:
            Quick summary string
        """
        try:
            prompt = f"""Provide a very brief 1-2 sentence summary of this medical report, highlighting only the most critical information:

{report_text[:1000]}"""
            
            response = self.grok_client.generate_completion(
                prompt=prompt,
                max_tokens=150
            )
            
            return response if response else "Unable to generate quick summary."
            
        except Exception as e:
            logger.error(f"Error generating quick summary: {str(e)}")
            return "Error generating summary."
    
    def extract_critical_findings(self, report_text: str) -> list:
        """
        Extract only critical/urgent findings from report
        
        Args:
            report_text: Medical report text
            
        Returns:
            List of critical findings
        """
        try:
            prompt = f"""Identify any CRITICAL or URGENT findings in this medical report that require immediate attention:

{report_text}

List only critical findings. If none, respond with "No critical findings identified."
Format as bullet points."""
            
            response = self.grok_client.generate_completion(
                prompt=prompt,
                max_tokens=500
            )
            
            if response and "no critical" not in response.lower():
                # Parse bullet points
                findings = []
                for line in response.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                        findings.append(line.lstrip('-•* '))
                return findings
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error extracting critical findings: {str(e)}")
            return []

# Made with Bob
