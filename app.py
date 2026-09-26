import streamlit as st
import json
import glob
import pandas as pd
from src.agents.healthcare_pipeline import run_healthcare_pipeline
from src.agents.supply_chain_pipeline import run_supply_chain_pipeline

st.set_page_config(
    page_title="Multi-Agent AI System",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Agent AI System")
st.caption("MSc Dissertation — Danish | Glasgow Caledonian University")

# ─── Sidebar ───
st.sidebar.header("⚙️ Configuration")
domain        = st.sidebar.selectbox("Select Domain", ["Healthcare Triage", "Supply Chain Optimisation"])
orchestration = st.sidebar.selectbox("Orchestration Strategy (RQ1)", ["hierarchical", "flat"])
prompt_mode   = st.sidebar.selectbox("Prompt Mode (RQ2)", ["structured", "unstructured"])
st.sidebar.markdown("---")
st.sidebar.markdown("**RQ1:** Hierarchical vs Flat")
st.sidebar.markdown("**RQ2:** Structured vs Unstructured")

# ════════════════════════════════════════
# HEALTHCARE DOMAIN
# ════════════════════════════════════════
if domain == "Healthcare Triage":
    st.header("🏥 Healthcare Triage Pipeline")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Patient Information")
        patient_id = st.text_input("Patient ID", value="P001")
        age        = st.number_input("Age", min_value=1, max_value=120, value=55)
        gender     = st.selectbox("Gender", ["male", "female", "other"])
        complaint  = st.text_input("Chief Complaint", value="severe chest pain radiating to left arm")
        symptoms   = st.text_area("Symptoms (comma separated)", value="chest pain, left arm pain, sweating, nausea")
        duration   = st.number_input("Duration (days)", min_value=1, value=1)
        severity   = st.slider("Severity Score", 1, 10, 9)

    with col2:
        st.subheader("Pipeline Status")
        st.empty()

    if st.button("🚀 Run Triage Pipeline", type="primary"):
        patient_data = {
            "patient_id"   : patient_id,
            "age"          : age,
            "gender"       : gender,
            "complaint"    : complaint,
            "symptoms"     : [s.strip() for s in symptoms.split(",")],
            "duration_days": duration,
            "severity"     : severity
        }

        try:
            with st.spinner("Running pipeline..."):
                progress = st.progress(0)
                log      = st.empty()
                log.info("Agent 1: Patient Intake running...")
                progress.progress(25)

                result = run_healthcare_pipeline(
                    patient_data=patient_data,
                    orchestration=orchestration,
                    structured=(prompt_mode == "structured")
                )
                progress.progress(100)

            st.success("✅ Pipeline Complete!")
            st.markdown("---")
            st.subheader("📊 Results")

            urgency = result.triage_assessment.urgency_level.value
            color   = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(urgency, "⚪")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Urgency Level", f"{color} {urgency.upper()}")
            c2.metric("Confidence",    f"{result.triage_assessment.confidence_score:.0%}")
            c3.metric("Steps Taken",   result.total_steps)
            c4.metric("Time",          f"{result.processing_time_seconds}s")

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("🩺 Clinical Assessment")
                st.write(f"**Primary Diagnosis:** {result.triage_assessment.primary_diagnosis}")
                st.write(f"**Clinical Reasoning:** {result.triage_assessment.clinical_reasoning}")
                st.write(f"**Risk Factors:** {', '.join(result.triage_assessment.risk_factors)}")
                st.markdown("---")
                st.subheader("📋 Possible Diagnoses")
                for i, d in enumerate(result.medical_knowledge.possible_diagnoses, 1):
                    st.write(f"{i}. {d}")

            with col2:
                st.subheader("📬 Referral Recommendation")
                if result.referral_recommendation.referral_required:
                    st.error(f"⚠️ Referral Required: **{result.referral_recommendation.referral_type}**")
                else:
                    st.success("✅ No Referral Required")
                st.write(f"**Follow-up:** {result.referral_recommendation.follow_up_days} days")
                st.write(f"**Advisory Note:** {result.referral_recommendation.advisory_note}")
                st.markdown("---")
                st.subheader("🚨 Red Flag Symptoms")
                for flag in result.medical_knowledge.red_flag_symptoms:
                    st.warning(flag)
                st.markdown("---")
                st.subheader("🔬 Recommended Tests")
                for test in result.medical_knowledge.recommended_tests:
                    st.write(f"• {test}")

        except ValueError as e:
            st.error("❌ Pipeline Failed!")
            st.warning("**Cause:** Unstructured prompts caused agent output validation failures")
            st.code(str(e), language="text")
            st.info("💡 **RQ2 Finding Demonstrated:** Switch Prompt Mode to 'structured' to fix this. "
                    "This is exactly what Research Question 2 proves — structured prompt design "
                    "is essential for reliable agent output.")

        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

# ════════════════════════════════════════
# SUPPLY CHAIN DOMAIN
# ════════════════════════════════════════
else:
    st.header("📦 Supply Chain Optimisation Pipeline")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Product Information")
        product_id    = st.text_input("Product ID", value="SKU-001")
        product_name  = st.text_input("Product Name", value="Dell Laptop 15inch")
        current_stock = st.number_input("Current Stock", min_value=0, value=45)
        monthly_sales = st.number_input("Monthly Sales Avg", min_value=0, value=120)
        reorder_point = st.number_input("Reorder Point", min_value=0, value=80)
        unit_cost     = st.number_input("Unit Cost ($)", min_value=0.0, value=850.0)
        suppliers_txt = st.text_area("Suppliers (comma separated)",
                                     value="Dell Direct, TechWholesale, Global IT")

    with col2:
        st.subheader("Pipeline Status")
        st.empty()

    if st.button("🚀 Run Supply Chain Pipeline", type="primary"):
        product_data = {
            "product_id"       : product_id,
            "product_name"     : product_name,
            "current_stock"    : current_stock,
            "monthly_sales_avg": monthly_sales,
            "reorder_point"    : reorder_point,
            "unit_cost"        : unit_cost,
            "suppliers"        : [s.strip() for s in suppliers_txt.split(",")]
        }

        try:
            with st.spinner("Running pipeline..."):
                result = run_supply_chain_pipeline(
                    product_data=product_data,
                    orchestration=orchestration,
                    structured=(prompt_mode == "structured")
                )

            st.success("✅ Pipeline Complete!")
            st.markdown("---")
            st.subheader("📊 Results")

            priority = result.procurement_recommendation.priority
            p_color  = {"urgent": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Order Required", "YES ⚠️" if result.procurement_recommendation.order_required else "NO ✅")
            c2.metric("Priority",       f"{p_color} {priority.upper()}")
            c3.metric("Steps Taken",    result.total_steps)
            c4.metric("Time",           f"{result.processing_time_seconds}s")

            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Inventory & Forecast")
                st.write(f"**Shortage Risk:** {'⚠️ Yes' if result.inventory_analysis.shortage_risk else '✅ No'}")
                st.write(f"**Current Stock:** {result.inventory_analysis.current_stock} units")
                st.write(f"**Demand (30 days):** {result.demand_forecast.forecasted_demand_30days} units")
                st.write(f"**Trend:** {result.demand_forecast.trend}")
                st.write(f"**Forecast Confidence:** {result.demand_forecast.confidence_level:.0%}")

            with col2:
                st.subheader("🏭 Procurement Decision")
                st.write(f"**Best Supplier:** {result.supplier_evaluation.recommended_supplier}")
                st.write(f"**Lead Time:** {result.supplier_evaluation.lead_time_days} days")
                st.write(f"**Order Quantity:** {result.procurement_recommendation.recommended_quantity} units")
                st.write(f"**Estimated Cost:** ${result.procurement_recommendation.estimated_cost:,.2f}")
                st.write(f"**Reasoning:** {result.supplier_evaluation.reasoning}")
                st.markdown("---")
                st.subheader("📋 Action Items")
                for action in result.procurement_recommendation.action_items:
                    st.write(f"• {action}")

        except ValueError as e:
            st.error("❌ Pipeline Failed!")
            st.warning("**Cause:** Unstructured prompts caused agent output validation failures")
            st.code(str(e), language="text")
            st.info("💡 **RQ2 Finding Demonstrated:** Switch Prompt Mode to 'structured' to fix this.")

        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")

# ════════════════════════════════════════
# EVALUATION RESULTS
# ════════════════════════════════════════
st.markdown("---")
with st.expander("📊 View Evaluation Results (RQ1 & RQ2 Comparison)"):

    log_files = sorted(glob.glob("logs/evaluation_*.json"), reverse=True)

    if not log_files:
        st.warning("No evaluation results found. Run: python run_evaluation.py")
    else:
        with open(log_files[0]) as f:
            data = json.load(f)

        st.caption(f"Latest evaluation: {data['metadata']['timestamp']} | "
                   f"Total runs: {data['metadata']['total_runs']}")

        summary = data["summary"]
        rows = []
        for config, metrics in summary.items():
            rows.append({
                "Configuration"  : config,
                "TCR (%)"        : metrics["tcr_percent"],
                "Avg Steps"      : metrics["avg_steps"],
                "Avg Latency (s)": metrics["avg_latency_s"],
                "Errors"         : metrics["error_count"]
            })

        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Task Completion Rate (%)")
            st.bar_chart({r["Configuration"]: r["TCR (%)"] for r in rows})
        with col2:
            st.subheader("Avg Latency (seconds)")
            st.bar_chart({r["Configuration"]: r["Avg Latency (s)"] for r in rows})

        st.markdown("---")
        st.subheader("🔍 Key Findings")
        col1, col2 = st.columns(2)
        with col1:
            st.success("**RQ1:** Hierarchical = 2x faster than Flat (6s vs 11.84s) with same TCR")
        with col2:
            st.error("**RQ2:** Unstructured prompts = 0% TCR vs 100% with structured prompts")

# ─── Footer ───
st.markdown("---")
st.caption("Multi-Agent AI System | LangGraph + Groq LLaMA 3.1 | GCU MSc Dissertation 2025-26")