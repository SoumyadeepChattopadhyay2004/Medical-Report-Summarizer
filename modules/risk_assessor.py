"""
Risk Assessment Module with Explainable AI
Evaluates health risks based on test results
"""

import logging
from typing import Dict, List, Any, Optional
from utils.grok_client import GrokClient
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class RiskAssessor:
    """Assess health risks with explainable AI"""
    
    def __init__(self):
        """Initialize risk assessor"""
        self.grok_client = GrokClient()
        self.risk_weights = Config.SEVERITY_WEIGHTS
        self.risk_levels = Config.RISK_LEVELS
        
    def assess_risk(
        self,
        abnormal_values: List[Dict[str, Any]],
        patient_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment
        
        Args:
            abnormal_values: List of abnormal test results
            patient_info: Patient demographic information
            
        Returns:
            Dictionary containing risk assessment results
        """
        try:
            logger.info("Performing risk assessment")
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(abnormal_values)
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Get AI-powered risk explanation
            ai_assessment = self.grok_client.assess_health_risk(
                abnormal_values, patient_info
            )
            
            # Analyze risk factors
            risk_factors = self._analyze_risk_factors(abnormal_values)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                risk_level, abnormal_values
            )
            
            return {
                "success": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_color": self._get_risk_color(risk_level),
                "risk_factors": risk_factors,
                "ai_assessment": ai_assessment.get("assessment", "") if ai_assessment else "",
                "recommendations": recommendations,
                "abnormal_count": len(abnormal_values),
                "explanation": self._generate_explanation(risk_score, risk_factors)
            }
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_risk_score(self, abnormal_values: List[Dict[str, Any]]) -> float:
        """
        Calculate numerical risk score (0-100)
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            Risk score
        """
        if not abnormal_values:
            return 0.0
        
        total_score = 0.0
        
        for value in abnormal_values:
            severity = value.get('severity', 'abnormal')
            weight = self.risk_weights.get(severity, 0.2)
            
            # Factor in deviation percentage
            deviation = value.get('deviation_percent', 10)
            deviation_factor = min(deviation / 100, 1.0)  # Cap at 1.0
            
            # Calculate contribution
            contribution = weight * (1 + deviation_factor)
            total_score += contribution
        
        # Normalize to 0-100 scale
        # Assume 5 critical abnormalities = 100 score
        normalized_score = min((total_score / 2.0) * 100, 100)
        
        return round(normalized_score, 2)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """
        Determine risk level from score
        
        Args:
            risk_score: Numerical risk score
            
        Returns:
            Risk level: 'low', 'moderate', 'high', or 'critical'
        """
        for level, (min_score, max_score) in self.risk_levels.items():
            if min_score <= risk_score < max_score:
                return level
        
        return 'critical' if risk_score >= 85 else 'low'
    
    def _analyze_risk_factors(
        self,
        abnormal_values: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze individual risk factors
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            List of risk factors with contributions
        """
        risk_factors = []
        
        for value in abnormal_values:
            severity = value.get('severity', 'abnormal')
            weight = self.risk_weights.get(severity, 0.2)
            
            # Calculate contribution percentage
            contribution = (weight / sum(self.risk_weights.values())) * 100
            
            risk_factors.append({
                'test_name': value.get('test_name'),
                'value': value.get('value'),
                'unit': value.get('unit'),
                'severity': severity,
                'contribution_percent': round(contribution, 2),
                'concern_level': self._get_concern_description(severity)
            })
        
        # Sort by contribution
        risk_factors.sort(key=lambda x: x['contribution_percent'], reverse=True)
        
        return risk_factors
    
    def _get_concern_description(self, severity: str) -> str:
        """
        Get concern level description
        
        Args:
            severity: Severity level
            
        Returns:
            Concern description
        """
        descriptions = {
            'critical': 'Immediate medical attention required',
            'abnormal': 'Requires medical consultation',
            'borderline': 'Monitor and lifestyle changes recommended',
            'normal': 'No immediate concern'
        }
        return descriptions.get(severity, 'Unknown')
    
    def _generate_recommendations(
        self,
        risk_level: str,
        abnormal_values: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate risk-based recommendations
        
        Args:
            risk_level: Overall risk level
            abnormal_values: List of abnormal values
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # General recommendations based on risk level
        if risk_level == 'critical':
            recommendations.append("⚠️ Seek immediate medical attention")
            recommendations.append("Contact your healthcare provider urgently")
            recommendations.append("Do not delay medical consultation")
        elif risk_level == 'high':
            recommendations.append("Schedule an appointment with your doctor soon")
            recommendations.append("Discuss these results with a healthcare professional")
            recommendations.append("Follow prescribed treatment plans carefully")
        elif risk_level == 'moderate':
            recommendations.append("Consult with your healthcare provider")
            recommendations.append("Consider lifestyle modifications")
            recommendations.append("Monitor your health regularly")
        else:
            recommendations.append("Maintain healthy lifestyle habits")
            recommendations.append("Continue regular health check-ups")
            recommendations.append("Stay informed about your health")
        
        # Specific recommendations based on abnormal values
        test_names = [v.get('test_name', '').lower() for v in abnormal_values]
        
        if any('glucose' in name or 'hba1c' in name for name in test_names):
            recommendations.append("Monitor blood sugar levels regularly")
            recommendations.append("Follow a balanced diet low in refined sugars")
        
        if any('cholesterol' in name or 'lipid' in name for name in test_names):
            recommendations.append("Adopt a heart-healthy diet")
            recommendations.append("Increase physical activity")
            recommendations.append("Limit saturated fats and trans fats")
        
        if any('blood pressure' in name or 'hypertension' in name for name in test_names):
            recommendations.append("Reduce sodium intake")
            recommendations.append("Manage stress levels")
            recommendations.append("Monitor blood pressure regularly")
        
        return recommendations[:8]  # Limit to 8 recommendations
    
    def _generate_explanation(
        self,
        risk_score: float,
        risk_factors: List[Dict[str, Any]]
    ) -> str:
        """
        Generate human-readable explanation of risk assessment
        
        Args:
            risk_score: Risk score
            risk_factors: List of risk factors
            
        Returns:
            Explanation text
        """
        risk_level = self._determine_risk_level(risk_score)
        
        explanation = f"Your overall health risk score is {risk_score:.1f} out of 100, "
        explanation += f"which indicates a {risk_level} risk level. "
        
        if risk_factors:
            top_factors = risk_factors[:3]
            explanation += "The main contributing factors are: "
            factor_names = [f"{f['test_name']}" for f in top_factors]
            explanation += ", ".join(factor_names) + ". "
        
        explanation += self._get_risk_level_description(risk_level)
        
        return explanation
    
    def _get_risk_level_description(self, risk_level: str) -> str:
        """
        Get detailed description of risk level
        
        Args:
            risk_level: Risk level
            
        Returns:
            Description text
        """
        descriptions = {
            'low': "This suggests your test results are mostly within acceptable ranges. Continue maintaining healthy habits.",
            'moderate': "Some test results require attention. Lifestyle modifications and medical consultation are recommended.",
            'high': "Multiple test results are concerning. Medical consultation is strongly recommended to address these issues.",
            'critical': "Several test results are critically abnormal. Immediate medical attention is required."
        }
        return descriptions.get(risk_level, "")
    
    def _get_risk_color(self, risk_level: str) -> str:
        """
        Get color code for risk level
        
        Args:
            risk_level: Risk level
            
        Returns:
            Hex color code
        """
        colors = {
            'low': '#43A047',      # Green
            'moderate': '#FFA726', # Orange
            'high': '#FF7043',     # Deep Orange
            'critical': '#E53935'  # Red
        }
        return colors.get(risk_level, '#757575')
    
    def get_risk_trend(
        self,
        current_assessment: Dict[str, Any],
        previous_assessment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compare current risk with previous assessment
        
        Args:
            current_assessment: Current risk assessment
            previous_assessment: Previous risk assessment (if available)
            
        Returns:
            Trend analysis
        """
        if not previous_assessment:
            return {
                "trend": "no_data",
                "message": "No previous data available for comparison"
            }
        
        current_score = current_assessment.get('risk_score', 0)
        previous_score = previous_assessment.get('risk_score', 0)
        
        difference = current_score - previous_score
        
        if abs(difference) < 5:
            trend = "stable"
            message = "Your risk level remains stable"
        elif difference > 0:
            trend = "increasing"
            message = f"Your risk has increased by {abs(difference):.1f} points"
        else:
            trend = "decreasing"
            message = f"Your risk has decreased by {abs(difference):.1f} points"
        
        return {
            "trend": trend,
            "difference": difference,
            "message": message,
            "current_score": current_score,
            "previous_score": previous_score
        }

# Made with Bob
