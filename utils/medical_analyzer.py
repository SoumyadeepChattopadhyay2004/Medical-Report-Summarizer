"""
Medical Analyzer Module
Core analysis logic for medical reports
"""

import re
import logging
from typing import Dict, List, Any, Optional
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class MedicalAnalyzer:
    """Analyze medical reports and extract structured information"""
    
    def __init__(self):
        """Initialize medical analyzer"""
        self.config = Config
        
    def analyze_report(self, report_text: str, patient_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of medical report
        
        Args:
            report_text: Raw medical report text
            patient_info: Patient demographic information
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            logger.info("Starting medical report analysis")
            
            # Extract test values
            test_values = self._extract_test_values(report_text)
            
            # Categorize findings
            categorized = self._categorize_findings(test_values)
            
            # Extract key findings
            key_findings = self._extract_key_findings(report_text)
            
            analysis = {
                "success": True,
                "patient_info": patient_info,
                "test_values": test_values,
                "categorized_findings": categorized,
                "key_findings": key_findings,
                "total_tests": len(test_values)
            }
            
            logger.info(f"Analysis complete. Found {len(test_values)} test values")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in medical analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_test_values(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract test names and values from report text
        
        Args:
            text: Medical report text
            
        Returns:
            List of test value dictionaries
        """
        test_values = []
        
        # Common medical test patterns
        patterns = [
            # Pattern: Test Name: Value Unit
            r'([A-Za-z\s\-]+)[:\s]+(\d+\.?\d*)\s*([a-zA-Z/%µ]+)',
            # Pattern: Test Name Value Unit
            r'([A-Za-z\s\-]+)\s+(\d+\.?\d*)\s+([a-zA-Z/%µ]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                test_name = match.group(1).strip()
                try:
                    value = float(match.group(2))
                    unit = match.group(3).strip() if match.group(3) else ""
                    
                    # Filter out false positives
                    if self._is_valid_test_name(test_name):
                        test_values.append({
                            "test_name": test_name,
                            "value": value,
                            "unit": unit,
                            "raw_text": match.group(0)
                        })
                except ValueError:
                    continue
        
        # Remove duplicates
        seen = set()
        unique_tests = []
        for test in test_values:
            key = (test["test_name"].lower(), test["value"])
            if key not in seen:
                seen.add(key)
                unique_tests.append(test)
        
        return unique_tests
    
    def _is_valid_test_name(self, name: str) -> bool:
        """
        Validate if extracted text is likely a test name
        
        Args:
            name: Potential test name
            
        Returns:
            True if valid test name
        """
        # Must be between 3 and 50 characters
        if len(name) < 3 or len(name) > 50:
            return False
        
        # Should not be all numbers
        if name.replace('.', '').replace('-', '').isdigit():
            return False
        
        # Should contain at least one letter
        if not any(c.isalpha() for c in name):
            return False
        
        # Common false positives to exclude
        exclude_words = ['page', 'date', 'time', 'report', 'lab', 'hospital', 'doctor', 'patient']
        if any(word in name.lower() for word in exclude_words):
            return False
        
        return True
    
    def _categorize_findings(self, test_values: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize test results by body system/category
        
        Args:
            test_values: List of test results
            
        Returns:
            Dictionary of categorized findings
        """
        categories = {
            "Blood Tests": [],
            "Lipid Profile": [],
            "Liver Function": [],
            "Kidney Function": [],
            "Thyroid Function": [],
            "Diabetes Markers": [],
            "Other": []
        }
        
        # Keywords for categorization
        category_keywords = {
            "Blood Tests": ["hemoglobin", "hb", "wbc", "rbc", "platelet", "hematocrit", "mcv", "mch"],
            "Lipid Profile": ["cholesterol", "hdl", "ldl", "triglyceride", "vldl"],
            "Liver Function": ["sgpt", "sgot", "alt", "ast", "bilirubin", "alp", "ggt"],
            "Kidney Function": ["creatinine", "urea", "bun", "uric acid", "egfr"],
            "Thyroid Function": ["tsh", "t3", "t4", "thyroid"],
            "Diabetes Markers": ["glucose", "hba1c", "sugar", "insulin"]
        }
        
        for test in test_values:
            test_name_lower = test["test_name"].lower()
            categorized = False
            
            for category, keywords in category_keywords.items():
                if any(keyword in test_name_lower for keyword in keywords):
                    categories[category].append(test)
                    categorized = True
                    break
            
            if not categorized:
                categories["Other"].append(test)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _extract_key_findings(self, text: str) -> List[str]:
        """
        Extract key findings and observations from report
        
        Args:
            text: Medical report text
            
        Returns:
            List of key findings
        """
        findings = []
        
        # Look for sections with findings
        finding_patterns = [
            r'(?:Findings?|Observations?|Impressions?|Conclusions?)[:\s]+(.*?)(?:\n\n|\Z)',
            r'(?:Summary|Results?)[:\s]+(.*?)(?:\n\n|\Z)',
        ]
        
        for pattern in finding_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                finding_text = match.group(1).strip()
                if finding_text and len(finding_text) > 10:
                    # Split into sentences
                    sentences = re.split(r'[.!?]+', finding_text)
                    findings.extend([s.strip() for s in sentences if len(s.strip()) > 10])
        
        return findings[:10]  # Return top 10 findings
    
    def identify_abnormal_patterns(self, test_values: List[Dict[str, Any]]) -> List[str]:
        """
        Identify patterns in abnormal values
        
        Args:
            test_values: List of test results
            
        Returns:
            List of identified patterns
        """
        patterns = []
        
        # Check for multiple abnormal values in same category
        categories = self._categorize_findings(test_values)
        
        for category, tests in categories.items():
            if len(tests) >= 3:
                patterns.append(f"Multiple {category.lower()} values detected")
        
        return patterns
    
    def calculate_completeness_score(self, test_values: List[Dict[str, Any]]) -> float:
        """
        Calculate how complete the medical report is
        
        Args:
            test_values: List of test results
            
        Returns:
            Completeness score (0-100)
        """
        # Common tests that should be present in a comprehensive report
        common_tests = [
            "hemoglobin", "wbc", "platelet", "glucose", "creatinine",
            "cholesterol", "sgpt", "sgot"
        ]
        
        found_tests = set()
        for test in test_values:
            test_name_lower = test["test_name"].lower()
            for common in common_tests:
                if common in test_name_lower:
                    found_tests.add(common)
        
        score = (len(found_tests) / len(common_tests)) * 100
        return round(score, 2)
    
    def extract_recommendations(self, text: str) -> List[str]:
        """
        Extract recommendations from report
        
        Args:
            text: Medical report text
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Look for recommendation sections
        rec_patterns = [
            r'(?:Recommendations?|Advice|Suggestions?)[:\s]+(.*?)(?:\n\n|\Z)',
        ]
        
        for pattern in rec_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                rec_text = match.group(1).strip()
                if rec_text:
                    # Split into individual recommendations
                    recs = re.split(r'[.!?]+|\n', rec_text)
                    recommendations.extend([r.strip() for r in recs if len(r.strip()) > 10])
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def generate_summary_stats(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary statistics from analysis
        
        Args:
            analysis: Analysis results
            
        Returns:
            Summary statistics
        """
        test_values = analysis.get("test_values", [])
        
        stats = {
            "total_tests": len(test_values),
            "categories": len(analysis.get("categorized_findings", {})),
            "key_findings": len(analysis.get("key_findings", [])),
            "completeness_score": self.calculate_completeness_score(test_values)
        }
        
        return stats

# Made with Bob
