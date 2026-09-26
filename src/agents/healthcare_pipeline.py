import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.agents.healthcare_agents import (
    patient_intake_agent,
    medical_knowledge_agent,
    triage_assessment_agent,
    referral_recommendation_agent
)
from src.schemas.healthcare_schemas import (
    PatientIntakeOutput,
    MedicalKnowledgeOutput,
    TriageAssessmentOutput,
    ReferralRecommendationOutput,
    HealthcarePipelineOutput
)

class HealthcareState(TypedDict):
    patient_data: dict
    structured: bool
    orchestration: str
    intake: PatientIntakeOutput | None
    knowledge: MedicalKnowledgeOutput | None
    assessment: TriageAssessmentOutput | None
    referral: ReferralRecommendationOutput | None
    steps: int
    errors: list
    start_time: float


def run_intake(state: HealthcareState) -> HealthcareState:
    print("  → [Agent 1] Patient Intake Agent running...")
    try:
        result = patient_intake_agent(state["patient_data"], structured=state["structured"])
        state["intake"] = result
        state["steps"] += 1
        print(f"    ✓ Intake complete — {result.chief_complaint}")
    except Exception as e:
        state["errors"].append(f"Intake Agent Error: {str(e)}")
        print(f"    ✗ Intake failed: {e}")
    return state


def run_knowledge(state: HealthcareState) -> HealthcareState:
    print("  → [Agent 2] Medical Knowledge Agent running...")
    if state["intake"] is None:
        state["errors"].append("Knowledge Agent skipped — no intake data")
        return state
    try:
        result = medical_knowledge_agent(state["intake"], structured=state["structured"])
        state["knowledge"] = result
        state["steps"] += 1
        print(f"    ✓ Knowledge complete — {len(result.possible_diagnoses)} diagnoses found")
    except Exception as e:
        state["errors"].append(f"Knowledge Agent Error: {str(e)}")
        print(f"    ✗ Knowledge failed: {e}")
    return state


def run_assessment(state: HealthcareState) -> HealthcareState:
    print("  → [Agent 3] Triage Assessment Agent running...")
    if state["intake"] is None or state["knowledge"] is None:
        state["errors"].append("Assessment Agent skipped — missing upstream data")
        return state
    try:
        result = triage_assessment_agent(state["intake"], state["knowledge"], structured=state["structured"])
        state["assessment"] = result
        state["steps"] += 1
        print(f"    ✓ Assessment complete — Urgency: {result.urgency_level}")
    except Exception as e:
        state["errors"].append(f"Assessment Agent Error: {str(e)}")
        print(f"    ✗ Assessment failed: {e}")
    return state


def run_referral(state: HealthcareState) -> HealthcareState:
    print("  → [Agent 4] Referral Recommendation Agent running...")
    if state["intake"] is None or state["assessment"] is None:
        state["errors"].append("Referral Agent skipped — missing upstream data")
        return state
    try:
        result = referral_recommendation_agent(state["intake"], state["assessment"], structured=state["structured"])
        state["referral"] = result
        state["steps"] += 1
        print(f"    ✓ Referral complete — Referral: {result.referral_required}")
    except Exception as e:
        state["errors"].append(f"Referral Agent Error: {str(e)}")
        print(f"    ✗ Referral failed: {e}")
    return state


def build_hierarchical_graph():
    graph = StateGraph(HealthcareState)
    graph.add_node("intake", run_intake)
    graph.add_node("knowledge", run_knowledge)
    graph.add_node("assessment", run_assessment)
    graph.add_node("referral", run_referral)
    graph.set_entry_point("intake")
    graph.add_edge("intake", "knowledge")
    graph.add_edge("knowledge", "assessment")
    graph.add_edge("assessment", "referral")
    graph.add_edge("referral", END)
    return graph.compile()


def build_flat_graph():
    graph = StateGraph(HealthcareState)
    graph.add_node("intake", run_intake)
    graph.add_node("knowledge", run_knowledge)
    graph.add_node("assessment", run_assessment)
    graph.add_node("referral", run_referral)
    graph.set_entry_point("intake")
    graph.add_edge("intake", "knowledge")
    graph.add_edge("knowledge", "assessment")
    graph.add_edge("assessment", "referral")
    graph.add_edge("referral", END)
    return graph.compile()


def run_healthcare_pipeline(
    patient_data: dict,
    orchestration: str = "hierarchical",
    structured: bool = True
) -> HealthcarePipelineOutput:

    print(f"\n{'='*55}")
    print(f"  HEALTHCARE TRIAGE PIPELINE")
    print(f"  Orchestration: {orchestration.upper()}")
    print(f"  Prompt Mode:   {'STRUCTURED' if structured else 'UNSTRUCTURED'}")
    print(f"{'='*55}")

    initial_state = HealthcareState(
        patient_data=patient_data,
        structured=structured,
        orchestration=orchestration,
        intake=None,
        knowledge=None,
        assessment=None,
        referral=None,
        steps=0,
        errors=[],
        start_time=time.time()
    )

    if orchestration == "hierarchical":
        app = build_hierarchical_graph()
    else:
        app = build_flat_graph()

    final_state = app.invoke(initial_state)
    elapsed = time.time() - final_state["start_time"]

    print(f"\n{'='*55}")
    print(f"  Pipeline Complete")
    print(f"  Steps taken : {final_state['steps']}")
    print(f"  Time taken  : {elapsed:.2f}s")
    if final_state["errors"]:
        print(f"  Errors      : {final_state['errors']}")
    print(f"{'='*55}\n")

    # ── Failure check ──
    failed_agents = []
    if final_state["intake"]     is None: failed_agents.append("Patient Intake Agent")
    if final_state["knowledge"]  is None: failed_agents.append("Medical Knowledge Agent")
    if final_state["assessment"] is None: failed_agents.append("Triage Assessment Agent")
    if final_state["referral"]   is None: failed_agents.append("Referral Agent")

    if failed_agents:
        raise ValueError(
            f"Pipeline incomplete. Failed agents: {', '.join(failed_agents)}. "
            f"Errors: {final_state['errors']}"
        )

    return HealthcarePipelineOutput(
        patient_intake=final_state["intake"],
        medical_knowledge=final_state["knowledge"],
        triage_assessment=final_state["assessment"],
        referral_recommendation=final_state["referral"],
        total_steps=final_state["steps"],
        processing_time_seconds=round(elapsed, 2)
    )