import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.schemas.supply_chain_schemas import (
    InventoryAnalysisOutput,
    DemandForecastOutput,
    SupplierEvaluationOutput,
    ProcurementRecommendationOutput
)

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.1
)

def clean_json(content: str) -> dict:
    content = content.strip()
    if "```" in content:
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    return json.loads(content.strip())


# ─────────────────────────────────────────
# AGENT 1: Inventory Analysis Agent
# ─────────────────────────────────────────
def inventory_analysis_agent(product_data: dict, structured: bool = True) -> InventoryAnalysisOutput:
    if structured:
        prompt = f"""You are an Inventory Analysis Agent. Analyze stock levels.

Product Data: {json.dumps(product_data)}

You MUST respond with ONLY a valid JSON object. No explanation, no markdown.
Required JSON format:
{{
    "product_id": "string",
    "current_stock": integer,
    "reorder_point": integer,
    "shortage_risk": true or false,
    "surplus_items": ["item1 if any"],
    "flagged_items": ["items needing attention"]
}}"""
    else:
        prompt = f"""You are an Inventory Analysis Agent.
Look at this product data: {json.dumps(product_data)}
Analyze the inventory and respond in JSON."""

    response = llm.invoke(prompt)
    data = clean_json(response.content)
    return InventoryAnalysisOutput(**data)


# ─────────────────────────────────────────
# AGENT 2: Demand Forecasting Agent
# ─────────────────────────────────────────
def demand_forecast_agent(inventory: InventoryAnalysisOutput, product_data: dict, structured: bool = True) -> DemandForecastOutput:
    if structured:
        prompt = f"""You are a Demand Forecasting Agent. Predict future demand.

Product ID: {inventory.product_id}
Current Stock: {inventory.current_stock}
Shortage Risk: {inventory.shortage_risk}
Historical Data: {json.dumps(product_data)}

You MUST respond with ONLY a valid JSON object. No explanation, no markdown.
Required JSON format:
{{
    "product_id": "string",
    "forecasted_demand_30days": integer,
    "seasonal_factor": float between 0.5-2.0,
    "trend": "increasing" or "stable" or "decreasing",
    "confidence_level": float between 0-1
}}"""
    else:
        prompt = f"""You are a Demand Forecasting Agent.
Product {inventory.product_id} has {inventory.current_stock} units in stock.
Forecast demand for next 30 days and respond in JSON."""

    response = llm.invoke(prompt)
    data = clean_json(response.content)
    return DemandForecastOutput(**data)


# ─────────────────────────────────────────
# AGENT 3: Supplier Evaluation Agent
# ─────────────────────────────────────────
def supplier_evaluation_agent(forecast: DemandForecastOutput, product_data: dict, structured: bool = True) -> SupplierEvaluationOutput:
    if structured:
        prompt = f"""You are a Supplier Evaluation Agent. Score and rank suppliers.

Product ID: {forecast.product_id}
Forecasted Demand (30 days): {forecast.forecasted_demand_30days}
Trend: {forecast.trend}
Available Suppliers: {json.dumps(product_data.get('suppliers', ['Supplier A', 'Supplier B', 'Supplier C']))}

You MUST respond with ONLY a valid JSON object. No explanation, no markdown.
Required JSON format:
{{
    "evaluated_suppliers": ["Supplier A", "Supplier B"],
    "recommended_supplier": "best supplier name",
    "cost_score": float between 0-10,
    "reliability_score": float between 0-10,
    "lead_time_days": integer,
    "reasoning": "brief reason for selection"
}}"""
    else:
        prompt = f"""You are a Supplier Evaluation Agent.
We need {forecast.forecasted_demand_30days} units of product {forecast.product_id}.
Evaluate suppliers and respond in JSON."""

    response = llm.invoke(prompt)
    data = clean_json(response.content)
    return SupplierEvaluationOutput(**data)


# ─────────────────────────────────────────
# AGENT 4: Procurement Recommendation Agent
# ─────────────────────────────────────────
def procurement_recommendation_agent(
    inventory: InventoryAnalysisOutput,
    forecast: DemandForecastOutput,
    supplier: SupplierEvaluationOutput,
    structured: bool = True
) -> ProcurementRecommendationOutput:
    if structured:
        prompt = f"""You are a Procurement Recommendation Agent. Generate purchase order recommendation.

Product ID: {inventory.product_id}
Current Stock: {inventory.current_stock}
Forecasted Demand: {forecast.forecasted_demand_30days} units
Shortage Risk: {inventory.shortage_risk}
Recommended Supplier: {supplier.recommended_supplier}
Lead Time: {supplier.lead_time_days} days
Cost Score: {supplier.cost_score}/10

IMPORTANT: Respond with ONLY a valid JSON object. No text outside JSON. No comments inside JSON.
Required JSON format:
{{
    "order_required": true,
    "recommended_quantity": 500,
    "estimated_cost": 42500.00,
    "priority": "high",
    "action_items": ["Contact supplier", "Issue PO"],
    "cost_benefit_summary": "brief summary here"
}}"""
    else:
        prompt = f"""You are a Procurement Recommendation Agent.
Current stock is {inventory.current_stock}, demand forecast is {forecast.forecasted_demand_30days}.
Should we order? Respond in JSON."""

    # Retry logic — 3 attempts
    for attempt in range(3):
        try:
            response = llm.invoke(prompt)
            data = clean_json(response.content)
            return ProcurementRecommendationOutput(**data)
        except Exception as e:
            if attempt == 2:
                raise e
            print(f"    ⚠ Retry {attempt + 1}/3 — {str(e)[:50]}")