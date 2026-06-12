"""
Health Insights Generator Module
Generates personalized health insights and recommendations
"""

import logging
from typing import Dict, List, Any, Optional
from utils.grok_client import GrokClient
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class InsightsGenerator:
    """Generate personalized health insights"""
    
    def __init__(self):
        """Initialize insights generator"""
        self.grok_client = GrokClient()
        
    def generate_insights(
        self,
        report_summary: str,
        abnormal_values: List[Dict[str, Any]],
        patient_info: Dict[str, Any],
        risk_assessment: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive health insights
        
        Args:
            report_summary: Summary of medical report
            abnormal_values: List of abnormal test results
            patient_info: Patient information
            risk_assessment: Risk assessment results
            
        Returns:
            Dictionary containing health insights
        """
        try:
            logger.info("Generating health insights")
            
            # Get AI-generated insights
            ai_insights = self.grok_client.generate_health_insights(
                report_summary, abnormal_values
            )
            
            # Generate category-specific insights
            lifestyle_insights = self._generate_lifestyle_insights(abnormal_values)
            dietary_insights = self._generate_dietary_insights(abnormal_values)
            exercise_insights = self._generate_exercise_insights(abnormal_values, patient_info)
            monitoring_plan = self._generate_monitoring_plan(abnormal_values)
            preventive_measures = self._generate_preventive_measures(abnormal_values)
            
            return {
                "success": True,
                "ai_insights": ai_insights,
                "lifestyle_recommendations": lifestyle_insights,
                "dietary_recommendations": dietary_insights,
                "exercise_recommendations": exercise_insights,
                "monitoring_plan": monitoring_plan,
                "preventive_measures": preventive_measures,
                "priority_actions": self._prioritize_actions(abnormal_values)
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_lifestyle_insights(
        self,
        abnormal_values: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate lifestyle modification recommendations
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            List of lifestyle recommendations
        """
        recommendations = []
        test_names = [v.get('test_name', '').lower() for v in abnormal_values]
        
        # General recommendations
        recommendations.append("Maintain a consistent sleep schedule (7-8 hours per night)")
        recommendations.append("Practice stress management techniques (meditation, yoga)")
        recommendations.append("Stay hydrated (drink 8-10 glasses of water daily)")
        
        # Specific recommendations based on abnormal values
        if any('glucose' in name or 'sugar' in name or 'hba1c' in name for name in test_names):
            recommendations.append("Monitor blood sugar levels regularly")
            recommendations.append("Avoid skipping meals to maintain stable blood sugar")
            recommendations.append("Limit alcohol consumption")
        
        if any('cholesterol' in name or 'lipid' in name or 'triglyceride' in name for name in test_names):
            recommendations.append("Quit smoking if you smoke")
            recommendations.append("Limit alcohol intake")
            recommendations.append("Manage stress levels effectively")
        
        if any('blood pressure' in name or 'hypertension' in name for name in test_names):
            recommendations.append("Reduce sodium intake (less than 2,300mg per day)")
            recommendations.append("Limit caffeine consumption")
            recommendations.append("Practice relaxation techniques")
        
        if any('liver' in name or 'sgpt' in name or 'sgot' in name for name in test_names):
            recommendations.append("Avoid alcohol completely")
            recommendations.append("Avoid unnecessary medications")
            recommendations.append("Maintain healthy body weight")
        
        return recommendations[:8]
    
    def _generate_dietary_insights(
        self,
        abnormal_values: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate dietary recommendations
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            List of dietary recommendations
        """
        recommendations = []
        test_names = [v.get('test_name', '').lower() for v in abnormal_values]
        
        # General healthy eating
        recommendations.append("Eat a balanced diet with plenty of fruits and vegetables")
        recommendations.append("Choose whole grains over refined grains")
        recommendations.append("Include lean proteins in your diet")
        
        # Diabetes/Blood Sugar
        if any('glucose' in name or 'sugar' in name or 'hba1c' in name for name in test_names):
            recommendations.append("Limit refined sugars and carbohydrates")
            recommendations.append("Choose low glycemic index foods")
            recommendations.append("Include fiber-rich foods (oats, beans, vegetables)")
            recommendations.append("Eat smaller, frequent meals throughout the day")
        
        # Cholesterol/Lipids
        if any('cholesterol' in name or 'lipid' in name or 'triglyceride' in name for name in test_names):
            recommendations.append("Reduce saturated fats (red meat, butter, cheese)")
            recommendations.append("Avoid trans fats (processed foods, fried foods)")
            recommendations.append("Include omega-3 fatty acids (fish, walnuts, flaxseeds)")
            recommendations.append("Increase soluble fiber intake (oats, apples, beans)")
        
        # Kidney Function
        if any('creatinine' in name or 'urea' in name or 'kidney' in name for name in test_names):
            recommendations.append("Limit protein intake (consult with doctor)")
            recommendations.append("Reduce sodium intake")
            recommendations.append("Monitor potassium and phosphorus intake")
        
        # Anemia/Iron
        if any('hemoglobin' in name or 'anemia' in name or 'iron' in name for name in test_names):
            recommendations.append("Include iron-rich foods (spinach, red meat, lentils)")
            recommendations.append("Consume vitamin C to enhance iron absorption")
            recommendations.append("Consider iron supplements (consult doctor)")
        
        return recommendations[:10]
    
    def _generate_exercise_insights(
        self,
        abnormal_values: List[Dict[str, Any]],
        patient_info: Dict[str, Any]
    ) -> List[str]:
        """
        Generate exercise recommendations
        
        Args:
            abnormal_values: List of abnormal values
            patient_info: Patient information
            
        Returns:
            List of exercise recommendations
        """
        recommendations = []
        age = patient_info.get('age', 40)
        
        # General recommendations
        if age < 60:
            recommendations.append("Aim for 150 minutes of moderate aerobic activity per week")
            recommendations.append("Include strength training exercises 2-3 times per week")
        else:
            recommendations.append("Aim for 75-150 minutes of moderate activity per week")
            recommendations.append("Focus on balance and flexibility exercises")
        
        test_names = [v.get('test_name', '').lower() for v in abnormal_values]
        
        # Diabetes/Blood Sugar
        if any('glucose' in name or 'sugar' in name for name in test_names):
            recommendations.append("Exercise regularly to improve insulin sensitivity")
            recommendations.append("Try brisk walking for 30 minutes after meals")
            recommendations.append("Monitor blood sugar before and after exercise")
        
        # Cholesterol/Heart Health
        if any('cholesterol' in name or 'lipid' in name for name in test_names):
            recommendations.append("Include cardio exercises (walking, swimming, cycling)")
            recommendations.append("Gradually increase exercise intensity")
            recommendations.append("Aim for at least 30 minutes of activity most days")
        
        # General
        recommendations.append("Start slowly and gradually increase intensity")
        recommendations.append("Consult your doctor before starting new exercise programs")
        recommendations.append("Stay consistent with your exercise routine")
        
        return recommendations[:8]
    
    def _generate_monitoring_plan(
        self,
        abnormal_values: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Generate monitoring plan for abnormal values
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            List of monitoring recommendations
        """
        monitoring_plan = []
        test_names = [v.get('test_name', '').lower() for v in abnormal_values]
        
        # Diabetes monitoring
        if any('glucose' in name or 'hba1c' in name for name in test_names):
            monitoring_plan.append({
                "parameter": "Blood Glucose",
                "frequency": "Daily (fasting and post-meal)",
                "method": "Home glucose meter",
                "target": "Fasting: 70-100 mg/dL, Post-meal: <140 mg/dL"
            })
        
        # Blood Pressure
        if any('pressure' in name or 'hypertension' in name for name in test_names):
            monitoring_plan.append({
                "parameter": "Blood Pressure",
                "frequency": "Daily or as advised",
                "method": "Home BP monitor",
                "target": "<120/80 mmHg"
            })
        
        # Weight monitoring
        if any('cholesterol' in name or 'glucose' in name for name in test_names):
            monitoring_plan.append({
                "parameter": "Body Weight",
                "frequency": "Weekly",
                "method": "Home scale",
                "target": "Maintain healthy BMI (18.5-24.9)"
            })
        
        # General follow-up
        monitoring_plan.append({
            "parameter": "Follow-up Tests",
            "frequency": "As recommended by doctor (typically 3-6 months)",
            "method": "Laboratory tests",
            "target": "All values within normal range"
        })
        
        return monitoring_plan
    
    def _generate_preventive_measures(
        self,
        abnormal_values: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate preventive health measures
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            List of preventive measures
        """
        measures = []
        test_names = [v.get('test_name', '').lower() for v in abnormal_values]
        
        # General preventive care
        measures.append("Schedule regular health check-ups (annually or as advised)")
        measures.append("Keep track of your health metrics in a journal")
        measures.append("Stay informed about your health conditions")
        
        # Specific preventive measures
        if any('glucose' in name or 'hba1c' in name for name in test_names):
            measures.append("Get regular eye examinations (diabetic retinopathy screening)")
            measures.append("Have annual foot examinations")
            measures.append("Monitor for signs of neuropathy")
        
        if any('cholesterol' in name or 'lipid' in name for name in test_names):
            measures.append("Get regular cardiovascular assessments")
            measures.append("Monitor for chest pain or discomfort")
            measures.append("Consider cardiac stress tests as recommended")
        
        if any('kidney' in name or 'creatinine' in name for name in test_names):
            measures.append("Monitor kidney function regularly")
            measures.append("Stay well-hydrated")
            measures.append("Avoid nephrotoxic medications")
        
        measures.append("Maintain up-to-date vaccinations")
        measures.append("Practice good hygiene and infection prevention")
        
        return measures[:10]
    
    def _prioritize_actions(
        self,
        abnormal_values: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Prioritize actions based on severity
        
        Args:
            abnormal_values: List of abnormal values
            
        Returns:
            List of prioritized actions
        """
        actions = []
        
        # Critical actions
        critical_values = [v for v in abnormal_values if v.get('severity') == 'critical']
        if critical_values:
            actions.append({
                "priority": "URGENT",
                "action": "Seek immediate medical attention",
                "reason": f"{len(critical_values)} critical value(s) detected",
                "timeframe": "Within 24 hours"
            })
        
        # High priority actions
        abnormal_count = len([v for v in abnormal_values if v.get('severity') == 'abnormal'])
        if abnormal_count > 0:
            actions.append({
                "priority": "HIGH",
                "action": "Schedule doctor appointment",
                "reason": f"{abnormal_count} abnormal value(s) require medical consultation",
                "timeframe": "Within 1 week"
            })
        
        # Medium priority actions
        borderline_count = len([v for v in abnormal_values if v.get('severity') == 'borderline'])
        if borderline_count > 0:
            actions.append({
                "priority": "MEDIUM",
                "action": "Implement lifestyle changes",
                "reason": f"{borderline_count} borderline value(s) can be improved",
                "timeframe": "Start immediately"
            })
        
        # Ongoing actions
        actions.append({
            "priority": "ONGOING",
            "action": "Monitor health metrics regularly",
            "reason": "Track progress and prevent deterioration",
            "timeframe": "Continuous"
        })
        
        return actions

# Made with Bob
