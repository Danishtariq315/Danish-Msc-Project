import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.schemas.healthcare_schemas import (
    PatientIntakeOutput,
    MedicalKnowledgeOutput,
    TriageAssessmentOutput,
    ReferralRecommendationOutput
)

load_dotenv()

# LLM initialize
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.1
)

# ─────────────────────────────────────────
# AGENT 1: Patient Intake Agent
# ─────────────────────────────────────────
def patient_intake_agent(patient_data: dict, structured: bool = True) -> PatientIntakeOutput:
    """
    Collects and structures patient-reported symptoms.
    structured=True  → RQ2 structured prompt
    structured=False → RQ2 unstructured prompt
    """
    if structured:
        prompt = f"""You are a Patient Intake Agent. Extract and structure patient information.

Patient Data: {json.dumps(patient_data)}

You MUST respond with ONLY a valid JSON object. No explanation, no markdown, no extra text.
Required JSON format:
{{
    "patient_id": "string",
    "age": integer,
    "gender": "string",
    "chief_complaint": "string (main symptom)",
    "symptoms": ["list", "of", "symptoms"],
    "duration_days": integer,
    "severity_score": float between 0-10
}}"""
    else:
        prompt = f"""You are a Patient Intake Agent. 
Look at this patient data and collect their information: {json.dumps(patient_data)}
Respond in JSON format with patient details."""

    response = llm.invoke(prompt)
    
    # Clean response
    content = response.content.strip()
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()
    
    data = json.loads(content)
    return PatientIntakeOutput(**data)


# ─────────────────────────────────────────
# AGENT 2: Medical Knowledge Agent
# ─────────────────────────────────────────
def medical_knowledge_agent(intake: PatientIntakeOutput, structured: bool = True) -> MedicalKnowledgeOutput:
    """
    Retrieves clinical guidelines and differential diagnoses.
    """
    if structured:
        prompt = f"""You are a Medical Knowledge Agent. Retrieve clinical knowledge for this patient.

Patient: {intake.age}yo {intake.gender}
Chief Complaint: {intake.chief_complaint}
Symptoms: {', '.join(intake.symptoms)}
Duration: {intake.duration_days} days
Severity: {intake.severity_score}/10

You MUST respond with ONLY a valid JSON object. No explanation, no markdown.
Required JSON format:
{{
    "retrieved_guidelines": ["relevant clinical guideline 1", "guideline 2"],
    "possible_diagnoses": ["diagnosis 1", "diagnosis 2", "diagnosis 3"],
    "red_flag_symptoms": ["red flag 1 if any"],
    "recommended_tests": ["test 1", "test 2"]
}}"""
    else:
        prompt = f"""You are a Medical Knowledge Agent.
Patient has: {intake.chief_complaint}, symptoms: {', '.join(intake.symptoms)}.
What are the possible diagnoses and recommended tests? Respond in JSON."""

    response = llm.invoke(prompt)
    content = response.content.strip()
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()
    
    data = json.loads(content)
    return MedicalKnowledgeOutput(**data)


# ─────────────────────────────────────────
# AGENT 3: Triage Assessment Agent
# ─────────────────────────────────────────
def triage_assessment_agent(
    intake: PatientIntakeOutput,
    knowledge: MedicalKnowledgeOutput,
    structured: bool = True
) -> TriageAssessmentOutput:
    """
    Classifies urgency level based on intake + knowledge.
    """
    if structured:
        prompt = f"""You are a Triage Assessment Agent. Classify urgency for this patient.

Patient: {intake.age}yo {intake.gender}
Chief Complaint: {intake.chief_complaint}
Symptoms: {', '.join(intake.symptoms)}
Severity Score: {intake.severity_score}/10
Possible Diagnoses: {', '.join(knowledge.possible_diagnoses)}
Red Flags: {', '.join(knowledge.red_flag_symptoms)}

You MUST respond with ONLY a valid JSON object. No explanation, no markdown.
Required JSON format:
{{
    "urgency_level": "low" or "medium" or "high" or "critical",
    "confidence_score": float between 0-1,
    "primary_diagnosis": "most likely diagnosis",
    "clinical_reasoning": "brief reasoning for urgency level",
    "risk_factors": ["risk factor 1", "risk factor 2"]
}}"""
    else:
        prompt = f"""You are a Triage Assessment Agent.
Patient has {intake.chief_complaint} with severity {intake.severity_score}/10.
Possible diagnoses: {', '.join(knowledge.possible_diagnoses)}.
Classify urgency and respond in JSON."""

    response = llm.invoke(prompt)
    content = response.content.strip()
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()
    
    data = json.loads(content)
    return TriageAssessmentOutput(**data)


# ─────────────────────────────────────────
# AGENT 4: Referral Recommendation Agent
# ─────────────────────────────────────────
def referral_recommendation_agent(
    intake: PatientIntakeOutput,
    assessment: TriageAssessmentOutput,
    structured: bool = True
) -> ReferralRecommendationOutput:
    """
    Generates structured referral recommendation.
    """
    if structured:
        prompt = f"""You are a Referral Recommendation Agent. Generate clinical referral guidance.

Patient: {intake.age}yo {intake.gender}
Primary Diagnosis: {assessment.primary_diagnosis}
Urgency Level: {assessment.urgency_level}
Confidence: {assessment.confidence_score}
Clinical Reasoning: {assessment.clinical_reasoning}

You MUST respond with ONLY a valid JSON object. No explanation, no markdown.
Required JSON format:
{{
    "referral_required": true or false,
    "referral_type": "specialist type or null",
    "recommended_actions": ["action 1", "action 2"],
    "follow_up_days": integer,
    "advisory_note": "brief advisory note for clinician"
}}"""
    else:
        prompt = f"""You are a Referral Recommendation Agent.
Patient urgency is {assessment.urgency_level}, diagnosis: {assessment.primary_diagnosis}.
Should they be referred? Respond in JSON."""

    response = llm.invoke(prompt)
    content = response.content.strip()
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    content = content.strip()
    
    data = json.loads(content)
    return ReferralRecommendationOutput(**data)