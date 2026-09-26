from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Agent 1 Output Schema
class PatientIntakeOutput(BaseModel):
    patient_id: str = Field(description="Unique patient identifier")
    age: int = Field(description="Patient age")
    gender: str = Field(description="Patient gender")
    chief_complaint: str = Field(description="Main symptom or reason for visit")
    symptoms: List[str] = Field(description="List of all reported symptoms")
    duration_days: int = Field(description="How long symptoms have been present")
    severity_score: float = Field(ge=0, le=10, description="Self-reported severity 0-10")

# Agent 2 Output Schema
class MedicalKnowledgeOutput(BaseModel):
    retrieved_guidelines: List[str] = Field(description="Relevant clinical guidelines")
    possible_diagnoses: List[str] = Field(description="Possible diagnoses based on symptoms")
    red_flag_symptoms: List[str] = Field(description="Warning symptoms that need immediate attention")
    recommended_tests: List[str] = Field(description="Suggested diagnostic tests")

# Agent 3 Output Schema
class TriageAssessmentOutput(BaseModel):
    urgency_level: UrgencyLevel = Field(description="Triage urgency classification")
    confidence_score: float = Field(ge=0, le=1, description="Confidence in assessment 0-1")
    primary_diagnosis: str = Field(description="Most likely diagnosis")
    clinical_reasoning: str = Field(description="Reasoning behind urgency level")
    risk_factors: List[str] = Field(description="Identified risk factors")

# Agent 4 Output Schema
class ReferralRecommendationOutput(BaseModel):
    referral_required: bool = Field(description="Whether referral is needed")
    referral_type: Optional[str] = Field(description="Type of specialist referral if needed")
    recommended_actions: List[str] = Field(description="Immediate actions to take")
    follow_up_days: int = Field(description="Days until follow-up required")
    advisory_note: str = Field(description="Final clinical advisory note")

# Final Pipeline Output
class HealthcarePipelineOutput(BaseModel):
    patient_intake: PatientIntakeOutput
    medical_knowledge: MedicalKnowledgeOutput
    triage_assessment: TriageAssessmentOutput
    referral_recommendation: ReferralRecommendationOutput
    total_steps: int
    processing_time_seconds: float