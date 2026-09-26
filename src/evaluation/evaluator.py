import time
import json
import random
from datetime import datetime
from src.agents.healthcare_pipeline import run_healthcare_pipeline
from src.agents.supply_chain_pipeline import run_supply_chain_pipeline

# ─────────────────────────────────────────
# Sample Test Cases
# ─────────────────────────────────────────

HEALTHCARE_CASES = [
    {
        "patient_id": "P001", "age": 55, "gender": "male",
        "complaint": "severe chest pain radiating to left arm",
        "symptoms": ["chest pain", "left arm pain", "sweating", "nausea"],
        "duration_days": 1, "severity": 9
    },
    {
        "patient_id": "P002", "age": 32, "gender": "female",
        "complaint": "mild headache and fatigue",
        "symptoms": ["headache", "fatigue", "mild fever"],
        "duration_days": 3, "severity": 4
    },
    {
        "patient_id": "P003", "age": 68, "gender": "male",
        "complaint": "sudden difficulty speaking and facial drooping",
        "symptoms": ["slurred speech", "facial drooping", "arm weakness", "confusion"],
        "duration_days": 1, "severity": 10
    },
    {
        "patient_id": "P004", "age": 25, "gender": "female",
        "complaint": "stomach pain and vomiting",
        "symptoms": ["abdominal pain", "vomiting", "diarrhea", "mild fever"],
        "duration_days": 2, "severity": 5
    },
    {
        "patient_id": "P005", "age": 45, "gender": "male",
        "complaint": "shortness of breath and wheezing",
        "symptoms": ["shortness of breath", "wheezing", "chest tightness", "cough"],
        "duration_days": 2, "severity": 7
    },
]

SUPPLY_CHAIN_CASES = [
    {
        "product_id": "SKU-001", "product_name": "Dell Laptop",
        "current_stock": 45, "monthly_sales_avg": 120,
        "reorder_point": 80, "unit_cost": 850.00,
        "suppliers": ["Dell Direct", "TechWholesale", "Global IT"]
    },
    {
        "product_id": "SKU-002", "product_name": "Office Chair",
        "current_stock": 200, "monthly_sales_avg": 50,
        "reorder_point": 60, "unit_cost": 150.00,
        "suppliers": ["FurniturePlus", "OfficePro", "DirectSupply"]
    },
    {
        "product_id": "SKU-003", "product_name": "Surgical Masks",
        "current_stock": 500, "monthly_sales_avg": 1000,
        "reorder_point": 800, "unit_cost": 0.50,
        "suppliers": ["MedSupply Co", "HealthFirst", "SafeGuard Ltd"]
    },
    {
        "product_id": "SKU-004", "product_name": "Printer Paper",
        "current_stock": 1200, "monthly_sales_avg": 300,
        "reorder_point": 400, "unit_cost": 25.00,
        "suppliers": ["PaperDirect", "OfficeWorld", "BulkSupply"]
    },
    {
        "product_id": "SKU-005", "product_name": "Hand Sanitizer",
        "current_stock": 80, "monthly_sales_avg": 200,
        "reorder_point": 150, "unit_cost": 3.50,
        "suppliers": ["CleanCo", "HygieneFirst", "MedPlus"]
    },
]


# ─────────────────────────────────────────
# Single Run Evaluator
# ─────────────────────────────────────────

def evaluate_single_run(domain: str, case: dict, orchestration: str, structured: bool) -> dict:
    """Run one case and return metrics."""
    
    result = {
        "domain": domain,
        "case_id": case.get("patient_id") or case.get("product_id"),
        "orchestration": orchestration,
        "structured": structured,
        "success": False,
        "steps": 0,
        "latency": 0.0,
        "error": None
    }

    try:
        start = time.time()

        if domain == "healthcare":
            output = run_healthcare_pipeline(case, orchestration, structured)
            result["steps"] = output.total_steps
            result["latency"] = output.processing_time_seconds
            result["urgency"] = output.triage_assessment.urgency_level.value if output.triage_assessment else None
            result["success"] = all([
                output.patient_intake,
                output.medical_knowledge,
                output.triage_assessment,
                output.referral_recommendation
            ])

        elif domain == "supply_chain":
            output = run_supply_chain_pipeline(case, orchestration, structured)
            result["steps"] = output.total_steps
            result["latency"] = output.processing_time_seconds
            result["order_required"] = output.procurement_recommendation.order_required if output.procurement_recommendation else None
            result["success"] = all([
                output.inventory_analysis,
                output.demand_forecast,
                output.supplier_evaluation,
                output.procurement_recommendation
            ])

    except Exception as e:
        result["error"] = str(e)
        result["latency"] = round(time.time() - start, 2)

    return result


# ─────────────────────────────────────────
# Full Evaluation Runner
# ─────────────────────────────────────────

def run_full_evaluation(n_cases: int = 5):
    """
    Run complete evaluation across all configurations.
    RQ1: hierarchical vs flat
    RQ2: structured vs unstructured
    """

    print("\n" + "="*60)
    print("  FULL EVALUATION FRAMEWORK")
    print(f"  Cases per config: {n_cases}")
    print(f"  Started: {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)

    configs = [
        ("hierarchical", True,  "RQ1+RQ2 Proposed System"),
        ("hierarchical", False, "RQ2 Unstructured Baseline"),
        ("flat",         True,  "RQ1 Flat Comparison"),
        ("flat",         False, "RQ1+RQ2 Flat+Unstructured"),
    ]

    all_results = []

    for orchestration, structured, label in configs:
        print(f"\n--- Config: {label} ---")

        hc_cases  = HEALTHCARE_CASES[:n_cases]
        sc_cases  = SUPPLY_CHAIN_CASES[:n_cases]

        for case in hc_cases:
            r = evaluate_single_run("healthcare", case, orchestration, structured)
            all_results.append(r)

        for case in sc_cases:
            r = evaluate_single_run("supply_chain", case, orchestration, structured)
            all_results.append(r)

    # ─── Calculate Summary Metrics ───
    print("\n" + "="*60)
    print("  RESULTS SUMMARY")
    print("="*60)

    summary = {}

    for orchestration, structured, label in configs:
        key = label
        runs = [r for r in all_results
                if r["orchestration"] == orchestration
                and r["structured"] == structured]

        if not runs:
            continue

        total       = len(runs)
        successful  = sum(1 for r in runs if r["success"])
        tcr         = round((successful / total) * 100, 1)
        avg_steps   = round(sum(r["steps"] for r in runs) / total, 1)
        avg_latency = round(sum(r["latency"] for r in runs) / total, 2)
        errors      = sum(1 for r in runs if r["error"])

        summary[key] = {
            "total_runs"    : total,
            "successful"    : successful,
            "tcr_percent"   : tcr,
            "avg_steps"     : avg_steps,
            "avg_latency_s" : avg_latency,
            "error_count"   : errors,
        }

        print(f"\n  [{label}]")
        print(f"    TCR          : {tcr}%  ({successful}/{total} tasks)")
        print(f"    Avg Steps    : {avg_steps}")
        print(f"    Avg Latency  : {avg_latency}s")
        print(f"    Errors       : {errors}")

    # ─── Save Results ───
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"logs/evaluation_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump({
            "summary" : summary,
            "details" : all_results,
            "metadata": {
                "timestamp" : timestamp,
                "n_cases"   : n_cases,
                "total_runs": len(all_results)
            }
        }, f, indent=2)

    print(f"\n  Results saved → {filename}")
    print("="*60)

    return summary, all_results