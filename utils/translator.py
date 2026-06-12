"""
Translation Module for Medical Report Summarizer
Handles multilingual support (English and Hindi)
"""

import logging
from typing import Optional, Dict
from deep_translator import GoogleTranslator
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class Translator:
    """Handle translation between English and Hindi"""
    
    def __init__(self):
        """Initialize translator"""
        self.supported_languages = Config.SUPPORTED_LANGUAGES
        self.translation_cache = {}
        
    def translate(
        self,
        text: str,
        source_lang: str = "en",
        target_lang: str = "hi"
    ) -> Optional[str]:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None if failed
        """
        if not Config.ENABLE_TRANSLATION:
            logger.warning("Translation is disabled")
            return text
        
        # Return original if same language
        if source_lang == target_lang:
            return text
        
        # Check cache
        cache_key = f"{source_lang}_{target_lang}_{text[:50]}"
        if cache_key in self.translation_cache:
            logger.info("Using cached translation")
            return self.translation_cache[cache_key]
        
        try:
            logger.info(f"Translating from {source_lang} to {target_lang}")
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated = translator.translate(text)
            
            # Cache the translation
            self.translation_cache[cache_key] = translated
            
            logger.info("Translation successful")
            return translated
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text  # Return original text on error
    
    def translate_to_hindi(self, text: str) -> Optional[str]:
        """
        Translate English text to Hindi
        
        Args:
            text: English text
            
        Returns:
            Hindi translation
        """
        return self.translate(text, source_lang="en", target_lang="hi")
    
    def translate_to_english(self, text: str) -> Optional[str]:
        """
        Translate Hindi text to English
        
        Args:
            text: Hindi text
            
        Returns:
            English translation
        """
        return self.translate(text, source_lang="hi", target_lang="en")
    
    def detect_language(self, text: str) -> str:
        """
        Detect language of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code ('en' or 'hi')
        """
        try:
            # Simple heuristic: check for Hindi characters
            hindi_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
            total_chars = len([c for c in text if c.isalpha()])
            
            if total_chars > 0 and (hindi_chars / total_chars) > 0.3:
                return "hi"
            else:
                return "en"
                
        except Exception as e:
            logger.error(f"Language detection error: {str(e)}")
            return "en"  # Default to English
    
    def get_ui_text(self, key: str, language: str = "en") -> str:
        """
        Get UI text in specified language
        
        Args:
            key: Text key
            language: Language code
            
        Returns:
            Translated UI text
        """
        ui_texts = {
            "en": {
                "app_title": "<i>Health-Guardian<i>: Medical Report Summarizer",
                "upload_report": "Upload Medical Report",
                "analyze": "Analyze Report",
                "summary": "Summary",
                "abnormal_values": "Abnormal Values",
                "risk_assessment": "Risk Assessment",
                "health_insights": "Health Insights",
                "chatbot": "Ask Questions",
                "export": "Export Report",
                "language": "Language",
                "processing": "Processing...",
                "success": "Success!",
                "error": "Error",
                "no_file": "Please upload a file",
                "file_uploaded": "File uploaded successfully",
                "analyzing": "Analyzing your report...",
                "disclaimer": "This is for informational purposes only. Consult a healthcare professional for medical advice.",
                "patient_info": "Patient Information",
                "test_results": "Test Results",
                "recommendations": "Recommendations",
                "normal": "Normal",
                "borderline": "Borderline",
                "abnormal": "Abnormal",
                "critical": "Critical",
                "low_risk": "Low Risk",
                "moderate_risk": "Moderate Risk",
                "high_risk": "High Risk",
                "critical_risk": "Critical Risk"
            },
            "hi": {
                "app_title": "चिकित्सा रिपोर्ट सारांशकर्ता",
                "upload_report": "चिकित्सा रिपोर्ट अपलोड करें",
                "analyze": "रिपोर्ट का विश्लेषण करें",
                "summary": "सारांश",
                "abnormal_values": "असामान्य मान",
                "risk_assessment": "जोखिम मूल्यांकन",
                "health_insights": "स्वास्थ्य अंतर्दृष्टि",
                "chatbot": "प्रश्न पूछें",
                "export": "रिपोर्ट निर्यात करें",
                "language": "भाषा",
                "processing": "प्रसंस्करण...",
                "success": "सफलता!",
                "error": "त्रुटि",
                "no_file": "कृपया एक फ़ाइल अपलोड करें",
                "file_uploaded": "फ़ाइल सफलतापूर्वक अपलोड की गई",
                "analyzing": "आपकी रिपोर्ट का विश्लेषण किया जा रहा है...",
                "disclaimer": "यह केवल सूचनात्मक उद्देश्यों के लिए है। चिकित्सा सलाह के लिए स्वास्थ्य पेशेवर से परामर्श करें।",
                "patient_info": "रोगी की जानकारी",
                "test_results": "परीक्षण परिणाम",
                "recommendations": "सिफारिशें",
                "normal": "सामान्य",
                "borderline": "सीमा रेखा",
                "abnormal": "असामान्य",
                "critical": "गंभीर",
                "low_risk": "कम जोखिम",
                "moderate_risk": "मध्यम जोखिम",
                "high_risk": "उच्च जोखिम",
                "critical_risk": "गंभीर जोखिम"
            }
        }
        
        return ui_texts.get(language, ui_texts["en"]).get(key, key)
    
    def translate_medical_term(self, term: str, target_lang: str = "hi") -> str:
        """
        Translate medical term with special handling
        
        Args:
            term: Medical term
            target_lang: Target language
            
        Returns:
            Translated term
        """
        # Common medical terms dictionary
        medical_terms = {
            "en_to_hi": {
                "hemoglobin": "हीमोग्लोबिन",
                "glucose": "ग्लूकोज़",
                "cholesterol": "कोलेस्ट्रॉल",
                "blood pressure": "रक्तचाप",
                "diabetes": "मधुमेह",
                "hypertension": "उच्च रक्तचाप",
                "anemia": "रक्ताल्पता",
                "platelet": "प्लेटलेट",
                "white blood cell": "श्वेत रक्त कोशिका",
                "red blood cell": "लाल रक्त कोशिका"
            }
        }
        
        term_lower = term.lower()
        
        if target_lang == "hi" and term_lower in medical_terms["en_to_hi"]:
            return medical_terms["en_to_hi"][term_lower]
        
        # Fallback to general translation
        return self.translate(term, source_lang="en", target_lang=target_lang) or term
    
    def clear_cache(self):
        """Clear translation cache"""
        self.translation_cache.clear()
        logger.info("Translation cache cleared")
    
    def get_cache_size(self) -> int:
        """Get number of cached translations"""
        return len(self.translation_cache)

# Made with Bob
