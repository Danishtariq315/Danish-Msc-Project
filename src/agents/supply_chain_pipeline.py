import time
from typing import TypedDict
from langgraph.graph import StateGraph, END
from src.agents.supply_chain_agents import (
    inventory_analysis_agent,
    demand_forecast_agent,
    supplier_evaluation_agent,
    procurement_recommendation_agent
)
from src.schemas.supply_chain_schemas import (
    InventoryAnalysisOutput,
    DemandForecastOutput,
    SupplierEvaluationOutput,
    ProcurementRecommendationOutput,
    SupplyChainPipelineOutput
)

class SupplyChainState(TypedDict):
    product_data: dict
    structured: bool
    orchestration: str
    inventory: InventoryAnalysisOutput | None
    forecast: DemandForecastOutput | None
    supplier: SupplierEvaluationOutput | None
    procurement: ProcurementRecommendationOutput | None
    steps: int
    errors: list
    start_time: float


def run_inventory(state: SupplyChainState) -> SupplyChainState:
    print("  → [Agent 1] Inventory Analysis Agent running...")
    try:
        result = inventory_analysis_agent(state["product_data"], state["structured"])
        state["inventory"] = result
        state["steps"] += 1
        print(f"    ✓ Inventory complete — Shortage risk: {result.shortage_risk}")
    except Exception as e:
        state["errors"].append(f"Inventory Agent Error: {str(e)}")
        print(f"    ✗ Failed: {e}")
    return state


def run_forecast(state: SupplyChainState) -> SupplyChainState:
    print("  → [Agent 2] Demand Forecasting Agent running...")
    if state["inventory"] is None:
        state["errors"].append("Forecast skipped — no inventory data")
        return state
    try:
        result = demand_forecast_agent(state["inventory"], state["product_data"], state["structured"])
        state["forecast"] = result
        state["steps"] += 1
        print(f"    ✓ Forecast complete — {result.forecasted_demand_30days} units, trend: {result.trend}")
    except Exception as e:
        state["errors"].append(f"Forecast Agent Error: {str(e)}")
        print(f"    ✗ Failed: {e}")
    return state


def run_supplier(state: SupplyChainState) -> SupplyChainState:
    print("  → [Agent 3] Supplier Evaluation Agent running...")
    if state["forecast"] is None:
        state["errors"].append("Supplier eval skipped — no forecast data")
        return state
    try:
        result = supplier_evaluation_agent(state["forecast"], state["product_data"], state["structured"])
        state["supplier"] = result
        state["steps"] += 1
        print(f"    ✓ Supplier complete — Recommended: {result.recommended_supplier}")
    except Exception as e:
        state["errors"].append(f"Supplier Agent Error: {str(e)}")
        print(f"    ✗ Failed: {e}")
    return state


def run_procurement(state: SupplyChainState) -> SupplyChainState:
    print("  → [Agent 4] Procurement Recommendation Agent running...")
    if state["inventory"] is None or state["supplier"] is None:
        state["errors"].append("Procurement skipped — missing upstream data")
        return state
    try:
        result = procurement_recommendation_agent(
            state["inventory"], state["forecast"],
            state["supplier"], state["structured"]
        )
        state["procurement"] = result
        state["steps"] += 1
        print(f"    ✓ Procurement complete — Order: {result.order_required}, Priority: {result.priority}")
    except Exception as e:
        state["errors"].append(f"Procurement Agent Error: {str(e)}")
        print(f"    ✗ Failed: {e}")
    return state


def build_sc_graph():
    graph = StateGraph(SupplyChainState)
    graph.add_node("inventory",   run_inventory)
    graph.add_node("forecast",    run_forecast)
    graph.add_node("supplier",    run_supplier)
    graph.add_node("procurement", run_procurement)
    graph.set_entry_point("inventory")
    graph.add_edge("inventory",   "forecast")
    graph.add_edge("forecast",    "supplier")
    graph.add_edge("supplier",    "procurement")
    graph.add_edge("procurement", END)
    return graph.compile()


def run_supply_chain_pipeline(
    product_data: dict,
    orchestration: str = "hierarchical",
    structured: bool = True
) -> SupplyChainPipelineOutput:

    print(f"\n{'='*55}")
    print(f"  SUPPLY CHAIN PIPELINE")
    print(f"  Orchestration: {orchestration.upper()}")
    print(f"  Prompt Mode:   {'STRUCTURED' if structured else 'UNSTRUCTURED'}")
    print(f"{'='*55}")

    initial_state = SupplyChainState(
        product_data=product_data,
        structured=structured,
        orchestration=orchestration,
        inventory=None,
        forecast=None,
        supplier=None,
        procurement=None,
        steps=0,
        errors=[],
        start_time=time.time()
    )

    app = build_sc_graph()
    final_state = app.invoke(initial_state)
    elapsed = time.time() - final_state["start_time"]

    print(f"\n{'='*55}")
    print(f"  Pipeline Complete")
    print(f"  Steps  : {final_state['steps']}")
    print(f"  Time   : {elapsed:.2f}s")
    if final_state["errors"]:
        print(f"  Errors : {final_state['errors']}")
    print(f"{'='*55}\n")

    # ── Failure check ──
    failed_agents = []
    if final_state["inventory"]   is None: failed_agents.append("Inventory Analysis Agent")
    if final_state["forecast"]    is None: failed_agents.append("Demand Forecasting Agent")
    if final_state["supplier"]    is None: failed_agents.append("Supplier Evaluation Agent")
    if final_state["procurement"] is None: failed_agents.append("Procurement Agent")

    if failed_agents:
        raise ValueError(
            f"Pipeline incomplete. Failed agents: {', '.join(failed_agents)}. "
            f"Errors: {final_state['errors']}"
        )

    return SupplyChainPipelineOutput(
        inventory_analysis=final_state["inventory"],
        demand_forecast=final_state["forecast"],
        supplier_evaluation=final_state["supplier"],
        procurement_recommendation=final_state["procurement"],
        total_steps=final_state["steps"],
        processing_time_seconds=round(elapsed, 2)
    )