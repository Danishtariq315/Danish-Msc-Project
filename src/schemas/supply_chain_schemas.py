from pydantic import BaseModel, Field
from typing import List, Optional

# Agent 1 Output Schema
class InventoryAnalysisOutput(BaseModel):
    product_id: str = Field(description="Product identifier")
    current_stock: int = Field(description="Current inventory level")
    reorder_point: int = Field(description="Level at which reorder is needed")
    shortage_risk: bool = Field(description="Whether shortage risk exists")
    surplus_items: List[str] = Field(description="Items with excess stock")
    flagged_items: List[str] = Field(description="Items needing immediate attention")

# Agent 2 Output Schema
class DemandForecastOutput(BaseModel):
    product_id: str = Field(description="Product identifier")
    forecasted_demand_30days: int = Field(description="Expected demand next 30 days")
    seasonal_factor: float = Field(description="Seasonal adjustment factor")
    trend: str = Field(description="Demand trend: increasing/stable/decreasing")
    confidence_level: float = Field(ge=0, le=1, description="Forecast confidence")

# Agent 3 Output Schema
class SupplierEvaluationOutput(BaseModel):
    evaluated_suppliers: List[str] = Field(description="List of evaluated suppliers")
    recommended_supplier: str = Field(description="Top recommended supplier")
    cost_score: float = Field(ge=0, le=10, description="Cost competitiveness score")
    reliability_score: float = Field(ge=0, le=10, description="Supplier reliability score")
    lead_time_days: int = Field(description="Expected delivery lead time")
    reasoning: str = Field(description="Reasoning for supplier selection")

# Agent 4 Output Schema
class ProcurementRecommendationOutput(BaseModel):
    order_required: bool = Field(description="Whether purchase order is needed")
    recommended_quantity: int = Field(description="Quantity to order")
    estimated_cost: float = Field(description="Estimated total cost")
    priority: str = Field(description="Order priority: low/medium/high/urgent")
    action_items: List[str] = Field(description="Steps to execute procurement")
    cost_benefit_summary: str = Field(description="Brief cost-benefit rationale")

# Final Pipeline Output
class SupplyChainPipelineOutput(BaseModel):
    inventory_analysis: InventoryAnalysisOutput
    demand_forecast: DemandForecastOutput
    supplier_evaluation: SupplierEvaluationOutput
    procurement_recommendation: ProcurementRecommendationOutput
    total_steps: int
    processing_time_seconds: float