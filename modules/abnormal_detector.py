"""
Abnormal Value Detector Module
Identifies and classifies abnormal test values
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class AbnormalDetector:
    """Detect and classify abnormal medical test values"""
    
    def __init__(self):
        """Initialize abnormal detector"""
        self.normal_ranges = self._load_normal_ranges()
        
    def _load_normal_ranges(self) -> Dict[str, Any]:
        """
        Load normal ranges from JSON file
        
        Returns:
            Dictionary of normal ranges
        """
        try:
            ranges_file = Path("assets/medical_ranges.json")
            if ranges_file.exists():
                with open(ranges_file, 'r') as f:
                    return json.load(f)
            else:
                logger.warning("Normal ranges file not found, using defaults")
                return {}
        except Exception as e:
            logger.error(f"Error loading normal ranges: {str(e)}")
            return {}
    
    def detect_abnormal_values(
        self,
        test_values: List[Dict[str, Any]],
        gender: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect abnormal values in test results
        
        Args:
            test_values: List of test results with name, value, unit
            gender: Patient gender for gender-specific ranges
            
        Returns:
            List of abnormal values with severity classification
        """
        abnormal_values = []
        
        for test in test_values:
            test_name = test.get('test_name', '').lower().strip()
            value = test.get('value')
            unit = test.get('unit', '').lower().strip()
            
            if value is None:
                continue
            
            # Find matching normal range
            normal_range = self._find_normal_range(test_name, gender)
            
            if normal_range:
                # Check if value is abnormal
                is_abnormal, severity, deviation = self._check_abnormality(
                    value, normal_range, gender
                )
                
                if is_abnormal:
                    abnormal_values.append({
                        'test_name': test.get('test_name'),
                        'value': value,
                        'unit': test.get('unit', ''),
                        'normal_range': self._format_normal_range(normal_range, gender),
                        'severity': severity,
                        'deviation_percent': deviation,
                        'status': self._get_status_description(severity),
                        'color': self._get_severity_color(severity)
                    })
        
        # Sort by severity (critical first)
        severity_order = {'critical': 0, 'abnormal': 1, 'borderline': 2}
        abnormal_values.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        logger.info(f"Detected {len(abnormal_values)} abnormal values")
        return abnormal_values
    
    def _find_normal_range(
        self,
        test_name: str,
        gender: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find normal range for a test
        
        Args:
            test_name: Name of the test
            gender: Patient gender
            
        Returns:
            Normal range dictionary or None
        """
        # Search through all categories
        for category, tests in self.normal_ranges.items():
            for test_key, range_data in tests.items():
                # Check if test name matches
                if test_key in test_name or test_name in test_key:
                    return range_data
                
                # Check common aliases
                aliases = self._get_test_aliases(test_key)
                if any(alias in test_name for alias in aliases):
                    return range_data
        
        return None
    
    def _get_test_aliases(self, test_key: str) -> List[str]:
        """
        Get common aliases for a test
        
        Args:
            test_key: Test key from normal ranges
            
        Returns:
            List of aliases
        """
        aliases_map = {
            'hemoglobin': ['hb', 'hgb'],
            'wbc': ['white blood cell', 'leukocyte'],
            'rbc': ['red blood cell', 'erythrocyte'],
            'platelets': ['platelet count', 'plt'],
            'glucose_fasting': ['fasting glucose', 'fbs', 'fpg'],
            'glucose_random': ['random glucose', 'rbs'],
            'cholesterol_total': ['total cholesterol', 'chol'],
            'sgpt': ['alt', 'alanine aminotransferase'],
            'sgot': ['ast', 'aspartate aminotransferase'],
            'creatinine': ['creat', 'cr'],
            'tsh': ['thyroid stimulating hormone'],
            'hba1c': ['glycated hemoglobin', 'a1c']
        }
        
        return aliases_map.get(test_key, [])
    
    def _check_abnormality(
        self,
        value: float,
        normal_range: Dict[str, Any],
        gender: Optional[str] = None
    ) -> tuple:
        """
        Check if value is abnormal and classify severity
        
        Args:
            value: Test value
            normal_range: Normal range dictionary
            gender: Patient gender
            
        Returns:
            Tuple of (is_abnormal, severity, deviation_percent)
        """
        # Handle gender-specific ranges
        if gender and gender.lower() in ['male', 'female']:
            gender_key = gender.lower()
            if gender_key in normal_range:
                normal_range = normal_range[gender_key]
        
        min_val = normal_range.get('min')
        max_val = normal_range.get('max')
        
        # Calculate deviation
        if min_val is not None and max_val is not None:
            # Value should be within range
            if value < min_val:
                deviation = ((min_val - value) / min_val) * 100
                severity = self._classify_severity(deviation)
                return True, severity, round(deviation, 2)
            elif value > max_val:
                deviation = ((value - max_val) / max_val) * 100
                severity = self._classify_severity(deviation)
                return True, severity, round(deviation, 2)
            else:
                return False, 'normal', 0.0
                
        elif min_val is not None:
            # Only minimum threshold
            if value < min_val:
                deviation = ((min_val - value) / min_val) * 100
                severity = self._classify_severity(deviation)
                return True, severity, round(deviation, 2)
            else:
                return False, 'normal', 0.0
                
        elif max_val is not None:
            # Only maximum threshold
            if value > max_val:
                deviation = ((value - max_val) / max_val) * 100
                severity = self._classify_severity(deviation)
                return True, severity, round(deviation, 2)
            else:
                return False, 'normal', 0.0
        
        return False, 'normal', 0.0
    
    def _classify_severity(self, deviation_percent: float) -> str:
        """
        Classify severity based on deviation percentage
        
        Args:
            deviation_percent: Percentage deviation from normal
            
        Returns:
            Severity level: 'borderline', 'abnormal', or 'critical'
        """
        if deviation_percent > 30:
            return 'critical'
        elif deviation_percent > 10:
            return 'abnormal'
        else:
            return 'borderline'
    
    def _format_normal_range(
        self,
        normal_range: Dict[str, Any],
        gender: Optional[str] = None
    ) -> str:
        """
        Format normal range as string
        
        Args:
            normal_range: Normal range dictionary
            gender: Patient gender
            
        Returns:
            Formatted range string
        """
        # Handle gender-specific ranges
        if gender and gender.lower() in ['male', 'female']:
            gender_key = gender.lower()
            if gender_key in normal_range:
                normal_range = normal_range[gender_key]
        
        min_val = normal_range.get('min')
        max_val = normal_range.get('max')
        unit = normal_range.get('unit', '')
        
        if min_val is not None and max_val is not None:
            return f"{min_val}-{max_val} {unit}"
        elif min_val is not None:
            return f"≥ {min_val} {unit}"
        elif max_val is not None:
            return f"≤ {max_val} {unit}"
        else:
            return "N/A"
    
    def _get_status_description(self, severity: str) -> str:
        """
        Get human-readable status description
        
        Args:
            severity: Severity level
            
        Returns:
            Status description
        """
        descriptions = {
            'normal': 'Within normal range',
            'borderline': 'Slightly outside normal range',
            'abnormal': 'Significantly outside normal range',
            'critical': 'Critically outside normal range - requires immediate attention'
        }
        return descriptions.get(severity, 'Unknown')
    
    def _get_severity_color(self, severity: str) -> str:
        """
        Get color code for severity level
        
        Args:
            severity: Severity level
            
        Returns:
            Hex color code
        """
        colors = {
            'normal': '#43A047',      # Green
            'borderline': '#FFA726',  # Orange
            'abnormal': '#FF7043',    # Deep Orange
            'critical': '#E53935'     # Red
        }
        return colors.get(severity, '#757575')
    
    def get_abnormal_count_by_severity(
        self,
        abnormal_values: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Count abnormal values by severity
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            Dictionary with counts by severity
        """
        counts = {
            'critical': 0,
            'abnormal': 0,
            'borderline': 0
        }
        
        for value in abnormal_values:
            severity = value.get('severity', 'abnormal')
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def get_abnormal_by_category(
        self,
        abnormal_values: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group abnormal values by category
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            Dictionary of abnormal values grouped by category
        """
        categories = {
            'Blood Tests': [],
            'Lipid Profile': [],
            'Liver Function': [],
            'Kidney Function': [],
            'Thyroid Function': [],
            'Diabetes Markers': [],
            'Other': []
        }
        
        category_keywords = {
            'Blood Tests': ['hemoglobin', 'hb', 'wbc', 'rbc', 'platelet'],
            'Lipid Profile': ['cholesterol', 'hdl', 'ldl', 'triglyceride'],
            'Liver Function': ['sgpt', 'sgot', 'alt', 'ast', 'bilirubin', 'alp'],
            'Kidney Function': ['creatinine', 'urea', 'bun', 'uric acid'],
            'Thyroid Function': ['tsh', 't3', 't4', 'thyroid'],
            'Diabetes Markers': ['glucose', 'hba1c', 'sugar']
        }
        
        for value in abnormal_values:
            test_name_lower = value.get('test_name', '').lower()
            categorized = False
            
            for category, keywords in category_keywords.items():
                if any(keyword in test_name_lower for keyword in keywords):
                    categories[category].append(value)
                    categorized = True
                    break
            
            if not categorized:
                categories['Other'].append(value)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

# Made with Bob
