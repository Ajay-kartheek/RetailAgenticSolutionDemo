"""
Pydantic models for all data structures in the Retail Agentic AI platform.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================


class StoreType(str, Enum):
    """Type of retail store."""
    FLAGSHIP = "flagship"
    STANDARD = "standard"


class Season(str, Enum):
    """Product seasons."""
    SUMMER = "Summer"
    WINTER = "Winter"
    MONSOON = "Monsoon"
    ALL_SEASON = "All-Season"


class Gender(str, Enum):
    """Target gender for products."""
    MALE = "Male"
    FEMALE = "Female"
    UNISEX = "Unisex"


class AvailabilityStatus(str, Enum):
    """Inventory availability status."""
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"


class TrendStatus(str, Enum):
    """Product trend classification."""
    IN_TREND = "in-trend"
    AVERAGE = "average"
    SLOW_MOVING = "slow-moving"
    NO_TREND = "no-trend"


class StockStatus(str, Enum):
    """Inventory stock status classification."""
    UNDERSTOCKED = "understocked"
    IN_STOCK = "in-stock"
    OVERSTOCKED = "overstocked"


class DecisionType(str, Enum):
    """Types of decisions made by agents."""
    REPLENISHMENT = "replenishment"
    TRANSFER = "transfer"
    PRICING = "pricing"
    PROMOTION = "promotion"
    MARKDOWN = "markdown"
    CAMPAIGN = "campaign"


class DecisionStatus(str, Enum):
    """Status of a decision."""
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_EXECUTED = "auto_executed"
    EXPIRED = "expired"


class ActionType(str, Enum):
    """Type of replenishment action."""
    INTER_STORE_TRANSFER = "inter_store_transfer"
    MANUFACTURER_ORDER = "manufacturer_order"
    COMBINED = "combined"


# ============================================================================
# Core Models
# ============================================================================


class Store(BaseModel):
    """Retail store information."""
    store_id: str = Field(..., description="Unique store identifier (e.g., STORE_CHN)")
    store_name: str = Field(..., description="Display name of the store")
    city: str = Field(..., description="City where store is located")
    region: str = Field(default="Tamil Nadu", description="State/Region")
    latitude: float = Field(..., description="Store latitude")
    longitude: float = Field(..., description="Store longitude")
    capacity: int = Field(..., description="Maximum inventory capacity")
    store_type: StoreType = Field(..., description="Type of store")
    manager_name: str | None = Field(default=None, description="Store manager name")
    contact_phone: str | None = Field(default=None, description="Contact phone number")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class Product(BaseModel):
    """Product catalog item."""
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product display name")
    category: str = Field(..., description="Product category (e.g., Shirts, Trousers)")
    sub_category: str = Field(..., description="Sub-category (e.g., Formal, Casual)")
    gender: Gender = Field(..., description="Target gender")
    seasons: list[Season] = Field(..., description="Applicable seasons")
    occasions: list[str] = Field(..., description="Suitable occasions")
    base_price: Decimal = Field(..., description="Base selling price (MRP)")
    cost_price: Decimal = Field(..., description="Cost price")
    sizes: list[str] = Field(..., description="Available sizes")
    colors: list[str] = Field(..., description="Available colors")
    brand: str = Field(default="SK Brands", description="Brand name")
    material: str | None = Field(default=None, description="Primary material")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    @property
    def margin_percent(self) -> float:
        """Calculate profit margin percentage."""
        if self.cost_price > 0:
            return float((self.base_price - self.cost_price) / self.base_price * 100)
        return 0.0


class InventoryItem(BaseModel):
    """Inventory record for a specific product variant at a store."""
    store_id: str = Field(..., description="Store identifier")
    product_id: str = Field(..., description="Product identifier")
    size: str = Field(..., description="Size variant")
    color: str = Field(..., description="Color variant")
    quantity: int = Field(..., ge=0, description="Current quantity in stock")
    availability_status: AvailabilityStatus = Field(..., description="Stock availability status")
    reorder_level: int = Field(default=20, description="Minimum stock level before reorder")
    last_restock_date: date | None = Field(default=None, description="Last restock date")
    location_in_store: str | None = Field(default=None, description="Shelf/rack location")
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True

    @property
    def sku(self) -> str:
        """Generate SKU from components."""
        return f"{self.product_id}_{self.size}_{self.color}"


class SalesRecord(BaseModel):
    """Daily sales record for a product at a store."""
    store_id: str = Field(..., description="Store identifier")
    product_id: str = Field(..., description="Product identifier")
    sale_date: date = Field(..., description="Date of sale")
    quantity_sold: int = Field(..., ge=0, description="Units sold")
    revenue: Decimal = Field(..., description="Total revenue")
    discount_amount: Decimal = Field(default=Decimal("0"), description="Discount applied")
    channel: str = Field(default="store", description="Sales channel (store/online)")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DemandForecast(BaseModel):
    """Demand forecast from ML model (mocked for demo)."""
    product_id: str = Field(..., description="Product identifier")
    store_id: str = Field(..., description="Store identifier")
    forecast_period: str = Field(..., description="Period identifier (e.g., 2026-Q1)")
    season: Season = Field(..., description="Season for forecast")
    period_start: date = Field(..., description="Forecast period start date")
    period_end: date = Field(..., description="Forecast period end date")
    forecasted_demand: int = Field(..., ge=0, description="Predicted demand units")
    confidence: float = Field(..., ge=0, le=1, description="Forecast confidence score")
    forecast_model: str = Field(default="mock_sagemaker_v1", description="Model used")
    factors: dict[str, Any] = Field(default_factory=dict, description="Contributing factors")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class StoreTransfer(BaseModel):
    """Transfer route information between stores."""
    from_store_id: str = Field(..., description="Source store identifier")
    to_store_id: str = Field(..., description="Destination store identifier")
    distance_km: float = Field(..., description="Distance in kilometers")
    travel_time_hours: float = Field(..., description="Estimated travel time in hours")
    transfer_cost_per_unit: Decimal = Field(..., description="Cost per unit to transfer")
    route_type: str = Field(default="road", description="Transport mode (road/rail)")
    is_active: bool = Field(default=True, description="Whether route is available")


class ManufacturerLeadTime(BaseModel):
    """Lead time information for ordering from manufacturer."""
    product_id: str = Field(..., description="Product identifier")
    manufacturer_id: str = Field(..., description="Manufacturer identifier")
    manufacturer_name: str = Field(..., description="Manufacturer name")
    lead_time_days: int = Field(..., description="Days to fulfill order")
    minimum_order_qty: int = Field(..., description="Minimum order quantity")
    cost_per_unit: Decimal = Field(..., description="Cost per unit from manufacturer")
    reliability_score: float = Field(..., ge=0, le=1, description="Manufacturer reliability")
    location: str | None = Field(default=None, description="Manufacturer location")


# ============================================================================
# Agent Output Models
# ============================================================================


class TrendAnalysis(BaseModel):
    """Output from Trend Analyser Agent."""
    store_id: str = Field(..., description="Store identifier")
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name for display")
    analysis_date: date = Field(default_factory=date.today)
    forecast_period: str = Field(..., description="Forecast period analyzed")
    forecasted_demand: int = Field(..., description="Original forecasted demand")
    actual_sales_to_date: int = Field(..., description="Actual units sold so far")
    days_elapsed: int = Field(..., description="Days into the forecast period")
    days_remaining: int = Field(..., description="Days remaining in period")
    current_velocity_percent: float = Field(..., description="Actual sales as % of forecast")
    expected_velocity_percent: float = Field(..., description="Expected sales % at this point")
    velocity_ratio: float = Field(..., description="Actual/Expected velocity ratio")
    trend_status: TrendStatus = Field(..., description="Trend classification")
    trend_confidence: float = Field(..., ge=0, le=1, description="Confidence in classification")
    projected_total_sales: int = Field(..., description="Projected sales by period end")
    demand_surplus_deficit: int = Field(..., description="Projected surplus(+) or deficit(-)")
    reasoning: str = Field(..., description="Explanation for the trend classification")

    class Config:
        use_enum_values = True


class InventoryStatusAnalysis(BaseModel):
    """Output from Inventory Agent."""
    store_id: str = Field(..., description="Store identifier")
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    current_stock: int = Field(..., description="Current total stock across variants")
    forecasted_demand: int = Field(..., description="Demand for remaining period")
    days_of_stock_remaining: float = Field(..., description="Days until stockout at current rate")
    stock_to_demand_ratio: float = Field(..., description="Stock / Remaining Demand ratio")
    stock_status: StockStatus = Field(..., description="Stock classification")
    trend_status: TrendStatus = Field(..., description="Associated trend status")
    urgency_score: float = Field(..., ge=0, le=1, description="Urgency for action (1=critical)")
    action_required: bool = Field(..., description="Whether action is needed")
    recommended_action: str | None = Field(default=None, description="Suggested action")
    reasoning: str = Field(..., description="Explanation for the status")

    class Config:
        use_enum_values = True


class ReplenishmentPlan(BaseModel):
    """Output from Replenishment Agent."""
    plan_id: str = Field(..., description="Unique plan identifier")
    target_store_id: str = Field(..., description="Store needing replenishment")
    product_id: str = Field(..., description="Product to replenish")
    product_name: str = Field(..., description="Product name")
    current_stock: int = Field(..., description="Current stock at target")
    required_quantity: int = Field(..., description="Total quantity needed")
    action_type: ActionType = Field(..., description="Type of replenishment action")

    # Transfer details (if applicable)
    transfer_from_store_id: str | None = Field(default=None)
    transfer_quantity: int | None = Field(default=None)
    transfer_cost: Decimal | None = Field(default=None)
    transfer_time_hours: float | None = Field(default=None)

    # Manufacturer order details (if applicable)
    manufacturer_order_quantity: int | None = Field(default=None)
    manufacturer_order_cost: Decimal | None = Field(default=None)
    manufacturer_lead_time_days: int | None = Field(default=None)

    total_cost: Decimal = Field(..., description="Total cost of replenishment")
    expected_completion_date: date = Field(..., description="When stock will be available")
    confidence: float = Field(..., ge=0, le=1, description="Plan confidence score")
    risk_if_not_executed: str = Field(..., description="Risk description if plan not approved")
    reasoning: str = Field(..., description="Explanation for the plan")
    requires_approval: bool = Field(default=True, description="Whether HITL approval needed")

    class Config:
        use_enum_values = True


class PricingRecommendation(BaseModel):
    """Output from Pricing & Promotion Agent."""
    store_id: str = Field(..., description="Store identifier")
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    current_price: Decimal = Field(..., description="Current selling price")
    recommended_price: Decimal = Field(..., description="Recommended price")
    price_change_percent: float = Field(..., description="Price change percentage")
    recommendation_type: str = Field(..., description="Type: increase/decrease/hold/promotion")
    promotion_details: str | None = Field(default=None, description="Promotion specifics if any")
    expected_revenue_impact: Decimal = Field(..., description="Expected revenue change")
    expected_margin_impact: Decimal = Field(..., description="Expected margin change")
    stock_status: StockStatus = Field(..., description="Current stock status")
    trend_status: TrendStatus = Field(..., description="Current trend status")
    confidence: float = Field(..., ge=0, le=1, description="Recommendation confidence")
    valid_from: date = Field(..., description="Recommended start date")
    valid_until: date = Field(..., description="Recommended end date")
    reasoning: str = Field(..., description="Explanation for recommendation")
    requires_approval: bool = Field(default=True, description="Whether HITL approval needed")

    class Config:
        use_enum_values = True


class CampaignCreative(BaseModel):
    """Output from Brand Campaign Agent."""
    campaign_id: str = Field(..., description="Unique campaign identifier")
    campaign_name: str = Field(..., description="Campaign name")
    product_ids: list[str] = Field(..., description="Products featured in campaign")
    store_ids: list[str] = Field(..., description="Target stores")
    campaign_type: str = Field(..., description="Type: banner/social/email/whatsapp")
    promotion_linked: str | None = Field(default=None, description="Linked promotion if any")
    prompt_used: str = Field(..., description="Prompt used for image generation")
    image_url: str | None = Field(default=None, description="Generated image URL (S3)")
    image_base64: str | None = Field(default=None, description="Base64 encoded image")
    headline: str = Field(..., description="Campaign headline text")
    description: str = Field(..., description="Campaign description")
    call_to_action: str = Field(..., description="CTA text")
    expected_reach: int | None = Field(default=None, description="Expected audience reach")
    expected_uplift_percent: float | None = Field(default=None, description="Expected sales uplift")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Decision & Audit Models
# ============================================================================


class Decision(BaseModel):
    """Decision record for audit trail and HITL."""
    decision_id: str = Field(..., description="Unique decision identifier")
    decision_type: DecisionType = Field(..., description="Type of decision")
    agent_id: str = Field(..., description="Agent that made the recommendation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Context
    store_id: str | None = Field(default=None, description="Related store")
    product_id: str | None = Field(default=None, description="Related product")

    # Recommendation details
    recommendation_summary: str = Field(..., description="Brief summary of recommendation")
    recommendation_details: dict[str, Any] = Field(..., description="Full recommendation data")
    confidence: float = Field(..., ge=0, le=1, description="Agent confidence score")

    # Impact estimates
    estimated_cost: Decimal | None = Field(default=None, description="Estimated cost")
    estimated_revenue_impact: Decimal | None = Field(default=None, description="Revenue impact")
    risk_assessment: str | None = Field(default=None, description="Risk if not executed")

    # Status tracking
    status: DecisionStatus = Field(default=DecisionStatus.PENDING_APPROVAL)
    requires_approval: bool = Field(default=True, description="Whether HITL needed")
    approved_by: str | None = Field(default=None, description="User who approved")
    approved_at: datetime | None = Field(default=None, description="Approval timestamp")
    rejection_reason: str | None = Field(default=None, description="Reason if rejected")

    # Execution
    executed_at: datetime | None = Field(default=None, description="Execution timestamp")
    execution_result: dict[str, Any] | None = Field(default=None, description="Execution outcome")

    # Explainability
    reasoning: str = Field(..., description="Agent's reasoning for this decision")
    input_signals: dict[str, Any] = Field(default_factory=dict, description="Input data used")
    trade_offs_considered: list[str] = Field(default_factory=list, description="Trade-offs")

    class Config:
        use_enum_values = True


# ============================================================================
# API Request/Response Models
# ============================================================================


class OrchestratorRunRequest(BaseModel):
    """Request to trigger orchestrator run."""
    store_ids: list[str] | None = Field(default=None, description="Specific stores to analyze")
    product_ids: list[str] | None = Field(default=None, description="Specific products to analyze")
    include_campaigns: bool = Field(default=False, description="Whether to generate campaigns")
    auto_approve_low_risk: bool = Field(default=False, description="Auto-approve low risk decisions")


class OrchestratorRunResponse(BaseModel):
    """Response from orchestrator run."""
    run_id: str = Field(..., description="Unique run identifier")
    status: str = Field(..., description="Run status")
    started_at: datetime = Field(..., description="Run start time")
    completed_at: datetime | None = Field(default=None, description="Run completion time")
    agents_executed: list[str] = Field(default_factory=list, description="Agents that ran")
    decisions_generated: int = Field(default=0, description="Number of decisions created")
    decisions_pending_approval: int = Field(default=0, description="Decisions awaiting HITL")
    summary: str = Field(..., description="Run summary")


class AgentThinkingUpdate(BaseModel):
    """Real-time update from agent thinking process."""
    run_id: str = Field(..., description="Run identifier")
    agent_id: str = Field(..., description="Agent sending update")
    agent_name: str = Field(..., description="Agent display name")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    update_type: str = Field(..., description="Type: thinking/tool_call/result/error")
    message: str = Field(..., description="Update message")
    data: dict[str, Any] | None = Field(default=None, description="Additional data")
