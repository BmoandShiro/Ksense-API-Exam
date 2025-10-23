#!/usr/bin/env python3
"""
Healthcare API Assessment - Patient Risk Scoring System
Implements risk scoring for patients based on blood pressure, temperature, and age.
"""

import requests
import json
import time
import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Patient:
    """Patient data structure"""
    patient_id: str
    name: str
    age: Optional[int]
    gender: str
    blood_pressure: Optional[str]
    temperature: Optional[float]
    visit_date: str
    diagnosis: str
    medications: str


@dataclass
class RiskScores:
    """Risk scores for a patient"""
    blood_pressure_score: int
    temperature_score: int
    age_score: int
    total_score: int


class HealthcareAPIClient:
    """Client for interacting with the Healthcare API"""
    
    def __init__(self, api_key: str, base_url: str = "https://assessment.ksensetech.com/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/json"
        })
    
    def fetch_patients(self, page: int = 1, limit: int = 5, max_retries: int = 3) -> Dict:
        """Fetch patients with retry logic for handling API failures"""
        url = f"{self.base_url}/patients"
        params = {"page": page, "limit": limit}
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limiting - wait and retry
                    wait_time = 2 ** attempt
                    print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                elif response.status_code in [500, 503]:
                    # Server error - wait and retry
                    wait_time = 1 + attempt
                    print(f"Server error {response.status_code}. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                wait_time = 1 + attempt
                print(f"Request failed: {e}. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        raise Exception(f"Failed to fetch patients after {max_retries} attempts")
    
    def fetch_all_patients(self) -> List[Patient]:
        """Fetch all patients across all pages"""
        all_patients = []
        page = 1
        
        while True:
            try:
                response = self.fetch_patients(page=page, limit=20)  # Use max limit
                patients_data = response.get("data", [])
                
                if not patients_data:
                    break
                
                for patient_data in patients_data:
                    patient = Patient(
                        patient_id=patient_data.get("patient_id", ""),
                        name=patient_data.get("name", ""),
                        age=self._parse_age(patient_data.get("age")),
                        gender=patient_data.get("gender", ""),
                        blood_pressure=patient_data.get("blood_pressure"),
                        temperature=self._parse_temperature(patient_data.get("temperature")),
                        visit_date=patient_data.get("visit_date", ""),
                        diagnosis=patient_data.get("diagnosis", ""),
                        medications=patient_data.get("medications", "")
                    )
                    all_patients.append(patient)
                
                # Check if there are more pages
                pagination = response.get("pagination", {})
                if not pagination.get("hasNext", False):
                    break
                
                page += 1
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                break
        
        return all_patients
    
    def submit_assessment(self, high_risk_patients: List[str], fever_patients: List[str], 
                         data_quality_issues: List[str]) -> Dict:
        """Submit assessment results"""
        url = f"{self.base_url}/submit-assessment"
        payload = {
            "high_risk_patients": high_risk_patients,
            "fever_patients": fever_patients,
            "data_quality_issues": data_quality_issues
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def _parse_age(self, age_value) -> Optional[int]:
        """Parse age value, handling various formats"""
        if age_value is None or age_value == "":
            return None
        
        try:
            # Try to convert to int
            if isinstance(age_value, (int, float)):
                return int(age_value)
            
            # Try to extract number from string
            if isinstance(age_value, str):
                # Remove non-numeric characters except decimal point
                cleaned = re.sub(r'[^\d.]', '', str(age_value))
                if cleaned:
                    return int(float(cleaned))
            
            return None
        except (ValueError, TypeError):
            return None
    
    def _parse_temperature(self, temp_value) -> Optional[float]:
        """Parse temperature value, handling various formats"""
        if temp_value is None or temp_value == "":
            return None
        
        try:
            # Try to convert to float
            if isinstance(temp_value, (int, float)):
                return float(temp_value)
            
            # Try to extract number from string
            if isinstance(temp_value, str):
                # Remove non-numeric characters except decimal point
                cleaned = re.sub(r'[^\d.]', '', str(temp_value))
                if cleaned:
                    return float(cleaned)
            
            return None
        except (ValueError, TypeError):
            return None


class RiskScorer:
    """Calculates risk scores for patients"""
    
    @staticmethod
    def calculate_blood_pressure_score(blood_pressure: Optional[str]) -> int:
        """Calculate blood pressure risk score (0-3 points)"""
        if not blood_pressure or blood_pressure.strip() == "":
            return 0
        
        try:
            # Parse blood pressure format "systolic/diastolic"
            parts = blood_pressure.strip().split('/')
            if len(parts) != 2:
                return 0
            
            systolic_str, diastolic_str = parts
            
            # Check for missing values
            if not systolic_str.strip() or not diastolic_str.strip():
                return 0
            
            # Extract numeric values
            systolic = float(re.sub(r'[^\d.]', '', systolic_str))
            diastolic = float(re.sub(r'[^\d.]', '', diastolic_str))
            
            # Determine risk categories
            systolic_stage = RiskScorer._get_systolic_stage(systolic)
            diastolic_stage = RiskScorer._get_diastolic_stage(diastolic)
            
            # Use the higher risk stage
            return max(systolic_stage, diastolic_stage)
            
        except (ValueError, TypeError, IndexError):
            return 0
    
    @staticmethod
    def _get_systolic_stage(systolic: float) -> int:
        """Get systolic blood pressure stage"""
        if systolic < 120:
            return 0  # Normal
        elif systolic <= 129:
            return 1  # Elevated
        elif systolic <= 139:
            return 2  # Stage 1
        else:
            return 3  # Stage 2
    
    @staticmethod
    def _get_diastolic_stage(diastolic: float) -> int:
        """Get diastolic blood pressure stage"""
        if diastolic < 80:
            return 0  # Normal
        elif diastolic <= 89:
            return 2  # Stage 1
        else:
            return 3  # Stage 2
    
    @staticmethod
    def calculate_temperature_score(temperature: Optional[float]) -> int:
        """Calculate temperature risk score (0-2 points)"""
        if temperature is None:
            return 0
        
        try:
            temp = float(temperature)
            if temp <= 99.5:
                return 0  # Normal
            elif temp <= 100.9:
                return 1  # Low Fever
            else:
                return 2  # High Fever
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def calculate_age_score(age: Optional[int]) -> int:
        """Calculate age risk score (0-2 points)"""
        if age is None:
            return 0
        
        try:
            age_int = int(age)
            if age_int < 40:
                return 0  # Under 40
            elif age_int <= 65:
                return 1  # 40-65
            else:
                return 2  # Over 65
        except (ValueError, TypeError):
            return 0
    
    @staticmethod
    def calculate_total_risk_score(patient: Patient) -> RiskScores:
        """Calculate total risk score for a patient"""
        bp_score = RiskScorer.calculate_blood_pressure_score(patient.blood_pressure)
        temp_score = RiskScorer.calculate_temperature_score(patient.temperature)
        age_score = RiskScorer.calculate_age_score(patient.age)
        
        total_score = bp_score + temp_score + age_score
        
        return RiskScores(
            blood_pressure_score=bp_score,
            temperature_score=temp_score,
            age_score=age_score,
            total_score=total_score
        )


class PatientAnalyzer:
    """Analyzes patients and categorizes them based on risk criteria"""
    
    def __init__(self, api_client: HealthcareAPIClient):
        self.api_client = api_client
        self.scorer = RiskScorer()
    
    def analyze_patients(self) -> Tuple[List[str], List[str], List[str]]:
        """Analyze all patients and return categorized lists"""
        print("Fetching all patients...")
        patients = self.api_client.fetch_all_patients()
        print(f"Fetched {len(patients)} patients")
        
        high_risk_patients = []
        fever_patients = []
        data_quality_issues = []
        
        for patient in patients:
            # Calculate risk scores
            risk_scores = self.scorer.calculate_total_risk_score(patient)
            
            # Check for high risk (total score >= 4)
            if risk_scores.total_score >= 4:
                high_risk_patients.append(patient.patient_id)
            
            # Check for fever (temperature >= 99.6)
            if patient.temperature is not None and patient.temperature >= 99.6:
                fever_patients.append(patient.patient_id)
            
            # Check for data quality issues - be more specific
            has_data_issues = False
            
            # Check blood pressure - only flag if truly invalid/missing
            if not patient.blood_pressure or patient.blood_pressure.strip() == "":
                has_data_issues = True
            else:
                # Check for invalid formats like "150/" or "/90" or non-numeric
                bp_parts = patient.blood_pressure.strip().split('/')
                if len(bp_parts) != 2:
                    has_data_issues = True
                else:
                    systolic_str, diastolic_str = bp_parts
                    if not systolic_str.strip() or not diastolic_str.strip():
                        has_data_issues = True
                    else:
                        # Check if they're numeric
                        try:
                            float(re.sub(r'[^\d.]', '', systolic_str))
                            float(re.sub(r'[^\d.]', '', diastolic_str))
                        except (ValueError, TypeError):
                            has_data_issues = True
            
            # Check temperature - only flag if truly invalid/missing
            if patient.temperature is None:
                has_data_issues = True
            else:
                # Check if temperature is a valid number
                try:
                    temp_val = float(patient.temperature)
                    if temp_val < 90 or temp_val > 110:  # Reasonable temperature range
                        has_data_issues = True
                except (ValueError, TypeError):
                    has_data_issues = True
            
            # Check age - only flag if truly invalid/missing
            if patient.age is None:
                has_data_issues = True
            else:
                # Check if age is a reasonable number
                try:
                    age_val = int(patient.age)
                    if age_val < 0 or age_val > 150:  # Reasonable age range
                        has_data_issues = True
                except (ValueError, TypeError):
                    has_data_issues = True
            
            if has_data_issues:
                data_quality_issues.append(patient.patient_id)
        
        return high_risk_patients, fever_patients, data_quality_issues
    
    def print_analysis_summary(self, high_risk: List[str], fever: List[str], data_quality: List[str]):
        """Print summary of analysis results"""
        print(f"\n=== ANALYSIS SUMMARY ===")
        print(f"High-risk patients (score >= 4): {len(high_risk)}")
        print(f"Fever patients (temp >= 99.6°F): {len(fever)}")
        print(f"Data quality issues: {len(data_quality)}")
        
        print(f"\nHigh-risk patients: {high_risk}")
        print(f"Fever patients: {fever}")
        print(f"Data quality issues: {data_quality}")


def main():
    """Main function to run the patient risk scoring system"""
    # API configuration
    API_KEY = "ak_50fccb76cde25bea1ce85de688325144b6c91e945e51f827"
    
    # Initialize API client
    api_client = HealthcareAPIClient(API_KEY)
    
    # Initialize analyzer
    analyzer = PatientAnalyzer(api_client)
    
    try:
        # Analyze patients
        high_risk_patients, fever_patients, data_quality_issues = analyzer.analyze_patients()
        
        # Print summary
        analyzer.print_analysis_summary(high_risk_patients, fever_patients, data_quality_issues)
        
        # Submit assessment
        print(f"\nSubmitting assessment...")
        result = api_client.submit_assessment(
            high_risk_patients=high_risk_patients,
            fever_patients=fever_patients,
            data_quality_issues=data_quality_issues
        )
        
        print(f"\n=== SUBMISSION RESULT ===")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()