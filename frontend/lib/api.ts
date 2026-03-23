import axios from 'axios';
import type {
  Store,
  Product,
  InventoryItem,
  Decision,
  OrchestratorResult,
  SSEEvent,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Stores
export const getStores = async (): Promise<Store[]> => {
  const { data } = await api.get('/stores');
  return data.stores;
};

export const getStore = async (storeId: string): Promise<Store> => {
  const { data } = await api.get(`/stores/${storeId}`);
  return data;
};

export const getStoreInventory = async (storeId: string): Promise<InventoryItem[]> => {
  const { data } = await api.get(`/stores/${storeId}/inventory`);
  return data.inventory;
};

export const getStoreForecasts = async (storeId: string): Promise<any[]> => {
  const { data } = await api.get(`/stores/${storeId}/forecasts`);
  return data.forecasts;
};

// Products
export const getProducts = async (): Promise<Product[]> => {
  const { data } = await api.get('/products');
  return data.products;
};

export const getProduct = async (productId: string): Promise<Product> => {
  const { data } = await api.get(`/products/${productId}`);
  return data;
};

// Inventory
export const getInventoryAlerts = async () => {
  const { data } = await api.get('/inventory/alerts');
  return data;
};

export const getInventoryStatusSummary = async () => {
  const { data } = await api.get('/inventory/status-summary');
  return data;
};

// Decisions
export const getDecisions = async (): Promise<Decision[]> => {
  const { data } = await api.get('/decisions');
  return data.decisions;
};

export const getPendingDecisions = async (): Promise<Decision[]> => {
  const { data } = await api.get('/decisions/pending');
  return data.decisions;
};

export const approveDecision = async (decisionId: string, notes?: string) => {
  const { data } = await api.post(`/decisions/${decisionId}/approve`, { notes });
  return data;
};

export const rejectDecision = async (decisionId: string, notes?: string) => {
  const { data } = await api.post(`/decisions/${decisionId}/reject`, { notes });
  return data;
};

// Agent Activity
export const getRecentActivity = async (limit: number = 10) => {
  try {
    const { data } = await api.get(`/activity/recent?limit=${limit}`);
    return data.activities || [];
  } catch (e) {
    console.error('Failed to fetch activity:', e);
    return [];
  }
};

// Orchestrator
export const runOrchestrator = async (params?: {
  forecast_period?: string;
  store_ids?: string[];
  product_ids?: string[];
  include_campaigns?: boolean;
}): Promise<OrchestratorResult> => {
  const { data } = await api.post('/orchestrator/run', params || {});
  return data.result;
};

// SSE Streaming with fetch API (supports POST)
export const createSSEConnection = async (
  params: {
    forecast_period?: string;
    store_ids?: string[];
    product_ids?: string[];
    include_campaigns?: boolean;
  },
  onEvent: (event: SSEEvent) => void,
  onError: (error: Error) => void
): Promise<(() => void)> => {
  const controller = new AbortController();

  try {
    const response = await fetch(`${API_BASE_URL}/orchestrator/run/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(params),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is null');
    }

    // Read the stream
    const readStream = async () => {
      let buffer = '';
      try {
        while (true) {
          const { done, value } = await reader.read();

          if (done) {
            break;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');

          // Keep the last (potentially incomplete) line in the buffer
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                onEvent(data as SSEEvent);
              } catch (e) {
                // If parsing fails, this might be a partial chunk - skip silently
              }
            }
          }
        }
      } catch (error) {
        if (error instanceof Error && error.name !== 'AbortError') {
          console.error('Stream reading error:', error);
          onError(error);
        }
      }
    };

    readStream();

  } catch (error) {
    console.error('SSE connection error:', error);
    onError(error instanceof Error ? error : new Error('SSE connection failed'));
  }

  // Return cleanup function
  return () => {
    controller.abort();
  };
};

// Trends
export const getTrends = async () => {
  const { data } = await api.get('/trends/');
  return data.trends;
};

// Campaigns
export const getCampaignSuggestions = async () => {
  const { data } = await api.get('/campaigns/suggestions');
  return data.suggestions;
};

export const generateCampaignImage = async (params: {
  product_id: string;
  campaign_type: string;
  promotion_text?: string;
}) => {
  const { data } = await api.post('/campaigns/generate-image', params);
  return data;
};

// Agents
export const getAgentHistory = async () => {
  const { data } = await api.get('/agents/history');
  return data.history;
};

export const getAgentStatus = async () => {
  const { data } = await api.get('/agents/status');
  return data;
};

// Demand Insights
export const getDemandInsights = async (storeId?: string, period: string = '2026-Q1') => {
  const params = new URLSearchParams();
  if (storeId) params.append('store_id', storeId);
  params.append('period', period);
  const { data } = await api.get(`/agents/demand/insights?${params.toString()}`);
  return data;
};

// Trend Insights
export const getTrendInsights = async (storeId?: string, period: string = '2026-Q1') => {
  const params = new URLSearchParams();
  if (storeId) params.append('store_id', storeId);
  params.append('period', period);
  const { data } = await api.get(`/agents/trend/insights?${params.toString()}`);
  return data;
};

// Inventory Insights
export const getInventoryInsights = async (storeId?: string, period: string = '2026-Q1') => {
  const params = new URLSearchParams();
  if (storeId) params.append('store_id', storeId);
  params.append('period', period);
  const { data } = await api.get(`/agents/inventory/insights?${params.toString()}`);
  return data;
};

// Replenishment Insights
export const getReplenishmentInsights = async (storeId?: string, period: string = '2026-Q1') => {
  const params = new URLSearchParams();
  if (storeId) params.append('store_id', storeId);
  params.append('period', period);
  const { data } = await api.get(`/agents/replenishment/insights?${params.toString()}`);
  return data;
};

// Pricing Insights
export const getPricingInsights = async (storeId?: string, period: string = '2026-Q1') => {
  const params = new URLSearchParams();
  if (storeId) params.append('store_id', storeId);
  params.append('period', period);
  const { data } = await api.get(`/agents/pricing/insights?${params.toString()}`);
  return data;
};

export default api;


