// TypeScript types matching backend models

export type AgentStatus = 'idle' | 'running' | 'completed' | 'error';

export type TrendStatus = 'in-trend' | 'average' | 'slow-moving' | 'no-trend';

export type StockStatus = 'out_of_stock' | 'low_stock' | 'in_stock';

export type DecisionStatus = 'pending' | 'approved' | 'rejected' | 'executed';

export type DecisionType = 'replenishment' | 'transfer' | 'pricing' | 'promotion' | 'markdown' | 'campaign';

export interface Store {
  store_id: string;
  store_name: string;
  city: string;
  region: string;
  latitude: number;
  longitude: number;
  capacity: number;
  store_type: string;
}

export interface Product {
  product_id: string;
  name?: string;
  product_name?: string;
  category: string;
  brand?: string;
  base_price?: number;
  color?: string;
  size?: string;
}

export interface InventoryItem {
  store_id: string;
  product_id: string;
  current_stock: number;
  reorder_point: number;
  max_stock?: number;
  stock_status: StockStatus;
  last_updated: string;
  size?: string;
  color?: string;
}

export interface DemandForecast {
  store_id: string;
  product_id: string;
  period: string;
  predicted_demand: number;
  confidence: number;
}

export interface TrendAnalysis {
  product_id: string;
  store_id: string;
  trend_status: TrendStatus;
  velocity_ratio: number;
  actual_sales: number;
  expected_sales: number;
  analysis_period_days: number;
}

export interface ReplenishmentPlan {
  store_id: string;
  product_id: string;
  shortage: number;
  recommended_action: string;
  donor_stores?: Array<{
    store_id: string;
    available_stock: number;
    transfer_quantity: number;
  }>;
  manufacturer_order?: {
    quantity: number;
    lead_time_days: number;
  };
}

export interface PricingRecommendation {
  product_id: string;
  store_id: string;
  current_price: number;
  recommended_action: string;
  recommended_price?: number;
  discount_percentage?: number;
  markdown_percentage?: number;
  reasoning: string;
}

export interface CampaignCreative {
  product_id: string;
  campaign_type: string;
  image_base64: string;
  prompt_used: string;
  created_at: string;
}

export interface Decision {
  decision_id: string;
  decision_type: string; // Broadened from DecisionType enum as backend generates dynamic strings
  status: DecisionStatus;

  // Core fields
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'normal' | 'low';
  cost: string;
  impact: string;
  agent_id: string;
  data: any; // Raw plan content

  // Metadata
  timestamp: string;
  created_at?: string; // Legacy support
  approved_at?: string;
  rejected_at?: string;
  executed_at?: string;

  // Optional UI fields
  tags?: string[];
  expiry?: string;
  confidence?: number;

  // Legacy fields (optional)
  store_id?: string;
  product_id?: string;
  details?: any;
  execution_result?: {
    status?: string;
    fulfillment_status?: string;
    timestamp?: string;
    message?: string;
    [key: string]: any;
  };
}

export interface OrchestratorResult {
  run_id: string;
  status: string;
  demand_forecasts: DemandForecast[];
  trend_analyses: TrendAnalysis[];
  inventory_analyses: InventoryItem[];
  replenishment_plans: ReplenishmentPlan[];
  pricing_recommendations: PricingRecommendation[];
  campaigns?: CampaignCreative[];
  executive_summary?: string;
  summary: {
    total_stores: number;
    total_products: number;
    understocked_items: number;
    overstocked_items: number;
    trending_products: number;
    slow_moving_products: number;
  };
}

export interface SSEEvent {
  type: 'start' | 'progress' | 'heartbeat' | 'complete' | 'error';
  run_id?: string;
  message?: string;
  result?: OrchestratorResult;
  error?: string;
  // Enhanced fields for agent updates
  agent_name?: string;
  status?: 'running' | 'completed' | 'error';
  thinking?: string;
  communication?: string;
  data?: any;
}

export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  status: AgentStatus;
  progress: number;
}
