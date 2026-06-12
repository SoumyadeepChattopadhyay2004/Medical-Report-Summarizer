"""
Medical Terminology Simplifier Module
Converts medical jargon to layman terms
"""

import json
import logging
from typing import Dict, Optional, List
from pathlib import Path
from utils.grok_client import GrokClient
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class TerminologySimplifier:
    """Simplify medical terminology for better understanding"""
    
    def __init__(self):
        """Initialize terminology simplifier"""
        self.grok_client = GrokClient()
        self.medical_terms = self._load_medical_terms()
        self.simplification_cache = {}
        
    def _load_medical_terms(self) -> Dict[str, str]:
        """
        Load medical terms dictionary
        
        Returns:
            Dictionary of medical terms and their simple explanations
        """
        # Built-in medical terms dictionary
        return {
            "hypertension": "high blood pressure",
            "hypotension": "low blood pressure",
            "hyperlipidemia": "high cholesterol levels",
            "hyperglycemia": "high blood sugar",
            "hypoglycemia": "low blood sugar",
            "anemia": "low red blood cell count or hemoglobin",
            "leukocytosis": "high white blood cell count",
            "leukopenia": "low white blood cell count",
            "thrombocytopenia": "low platelet count",
            "thrombocytosis": "high platelet count",
            "myocardial infarction": "heart attack",
            "cerebrovascular accident": "stroke",
            "diabetes mellitus": "diabetes (high blood sugar disease)",
            "hypokalemia": "low potassium levels",
            "hyperkalemia": "high potassium levels",
            "hyponatremia": "low sodium levels",
            "hypernatremia": "high sodium levels",
            "renal insufficiency": "reduced kidney function",
            "hepatic dysfunction": "liver problems",
            "dyslipidemia": "abnormal cholesterol or fat levels",
            "tachycardia": "fast heart rate",
            "bradycardia": "slow heart rate",
            "arrhythmia": "irregular heartbeat",
            "edema": "swelling due to fluid retention",
            "dyspnea": "difficulty breathing",
            "hemoglobin": "protein in red blood cells that carries oxygen",
            "platelets": "blood cells that help with clotting",
            "creatinine": "waste product filtered by kidneys",
            "bilirubin": "yellow pigment from red blood cell breakdown",
            "cholesterol": "fatty substance in blood",
            "triglycerides": "type of fat in blood",
            "glucose": "blood sugar",
            "albumin": "protein made by liver",
            "electrolytes": "minerals in blood (sodium, potassium, etc.)"
        }
    
    def simplify_term(
        self,
        term: str,
        context: str = "",
        use_ai: bool = True
    ) -> Dict[str, str]:
        """
        Simplify a medical term
        
        Args:
            term: Medical term to simplify
            context: Surrounding context for better explanation
            use_ai: Whether to use AI for explanation
            
        Returns:
            Dictionary with simple explanation and details
        """
        term_lower = term.lower().strip()
        
        # Check cache first
        cache_key = f"{term_lower}_{context[:50]}"
        if cache_key in self.simplification_cache:
            logger.info(f"Using cached simplification for: {term}")
            return self.simplification_cache[cache_key]
        
        # Check built-in dictionary
        if term_lower in self.medical_terms:
            simple_explanation = self.medical_terms[term_lower]
            result = {
                "term": term,
                "simple_explanation": simple_explanation,
                "source": "dictionary"
            }
            
            # Optionally enhance with AI
            if use_ai and context:
                ai_explanation = self._get_ai_explanation(term, context)
                if ai_explanation:
                    result["detailed_explanation"] = ai_explanation
                    result["source"] = "dictionary+ai"
            
            self.simplification_cache[cache_key] = result
            return result
        
        # Use AI for unknown terms
        if use_ai:
            ai_explanation = self._get_ai_explanation(term, context)
            if ai_explanation:
                result = {
                    "term": term,
                    "simple_explanation": ai_explanation[:200],  # Short version
                    "detailed_explanation": ai_explanation,
                    "source": "ai"
                }
                self.simplification_cache[cache_key] = result
                return result
        
        # Fallback
        return {
            "term": term,
            "simple_explanation": f"Medical term: {term}",
            "source": "none"
        }
    
    def _get_ai_explanation(self, term: str, context: str = "") -> Optional[str]:
        """
        Get AI-powered explanation of medical term
        
        Args:
            term: Medical term
            context: Context from report
            
        Returns:
            Simplified explanation
        """
        try:
            explanation = self.grok_client.simplify_medical_term(term, context)
            return explanation
        except Exception as e:
            logger.error(f"Error getting AI explanation: {str(e)}")
            return None
    
    def simplify_text(self, text: str, use_ai: bool = False) -> str:
        """
        Simplify medical terms in a text
        
        Args:
            text: Text containing medical terms
            use_ai: Whether to use AI for unknown terms
            
        Returns:
            Text with simplified terms
        """
        simplified_text = text
        
        # Replace known medical terms
        for medical_term, simple_term in self.medical_terms.items():
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(medical_term), re.IGNORECASE)
            simplified_text = pattern.sub(f"{simple_term} ({medical_term})", simplified_text)
        
        return simplified_text
    
    def create_glossary(
        self,
        report_text: str,
        max_terms: int = 20
    ) -> List[Dict[str, str]]:
        """
        Create a glossary of medical terms found in report
        
        Args:
            report_text: Medical report text
            max_terms: Maximum number of terms to include
            
        Returns:
            List of term definitions
        """
        glossary = []
        report_lower = report_text.lower()
        
        # Find medical terms present in the report
        for term, explanation in self.medical_terms.items():
            if term in report_lower:
                glossary.append({
                    "term": term.title(),
                    "explanation": explanation
                })
        
        # Sort alphabetically and limit
        glossary.sort(key=lambda x: x["term"])
        return glossary[:max_terms]
    
    def get_term_category(self, term: str) -> str:
        """
        Get category of medical term
        
        Args:
            term: Medical term
            
        Returns:
            Category name
        """
        term_lower = term.lower()
        
        categories = {
            "Cardiovascular": ["hypertension", "hypotension", "tachycardia", "bradycardia", 
                              "arrhythmia", "myocardial", "cardiac"],
            "Blood": ["anemia", "leukocytosis", "leukopenia", "thrombocytopenia", 
                     "hemoglobin", "platelets", "wbc", "rbc"],
            "Metabolic": ["diabetes", "hyperglycemia", "hypoglycemia", "glucose", 
                         "hyperlipidemia", "cholesterol", "triglycerides"],
            "Kidney": ["renal", "creatinine", "urea", "kidney"],
            "Liver": ["hepatic", "bilirubin", "liver", "sgpt", "sgot"],
            "Electrolytes": ["hypokalemia", "hyperkalemia", "hyponatremia", 
                           "hypernatremia", "sodium", "potassium"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in term_lower for keyword in keywords):
                return category
        
        return "General"
    
    def explain_test_result(
        self,
        test_name: str,
        value: float,
        unit: str,
        is_abnormal: bool = False
    ) -> str:
        """
        Explain what a test result means
        
        Args:
            test_name: Name of the test
            value: Test value
            unit: Unit of measurement
            is_abnormal: Whether the value is abnormal
            
        Returns:
            Plain language explanation
        """
        # Simplify test name
        simplified = self.simplify_term(test_name, use_ai=False)
        simple_name = simplified.get("simple_explanation", test_name)
        
        explanation = f"{test_name} ({simple_name}): {value} {unit}"
        
        if is_abnormal:
            explanation += " - This value is outside the normal range."
        else:
            explanation += " - This value is within the normal range."
        
        return explanation
    
    def get_common_abbreviations(self) -> Dict[str, str]:
        """
        Get dictionary of common medical abbreviations
        
        Returns:
            Dictionary of abbreviations and their meanings
        """
        return {
            "CBC": "Complete Blood Count",
            "WBC": "White Blood Cell count",
            "RBC": "Red Blood Cell count",
            "Hb": "Hemoglobin",
            "HbA1c": "Glycated Hemoglobin (average blood sugar over 3 months)",
            "FBS": "Fasting Blood Sugar",
            "PPBS": "Post-Prandial Blood Sugar (after meal)",
            "LFT": "Liver Function Test",
            "KFT": "Kidney Function Test",
            "SGPT": "Serum Glutamic Pyruvic Transaminase (liver enzyme)",
            "SGOT": "Serum Glutamic Oxaloacetic Transaminase (liver enzyme)",
            "TSH": "Thyroid Stimulating Hormone",
            "HDL": "High-Density Lipoprotein (good cholesterol)",
            "LDL": "Low-Density Lipoprotein (bad cholesterol)",
            "VLDL": "Very Low-Density Lipoprotein",
            "BUN": "Blood Urea Nitrogen",
            "eGFR": "Estimated Glomerular Filtration Rate (kidney function)",
            "ESR": "Erythrocyte Sedimentation Rate (inflammation marker)",
            "CRP": "C-Reactive Protein (inflammation marker)"
        }

# Made with Bob
