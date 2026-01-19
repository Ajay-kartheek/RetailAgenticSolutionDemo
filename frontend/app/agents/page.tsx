'use client';

import { useState, useEffect } from 'react';
import {
    TrendingUp,
    BarChart3,
    Package,
    Truck,
    Tag,
    Palette,
    ChevronRight,
    ChevronDown,
    Clock,
    Sparkles,
    ArrowRight,
    Lightbulb,
    Target,
    AlertCircle,
    AlertTriangle,
    Loader2,
    Table2
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import { getAgentHistory, getStores, getDemandInsights } from '@/lib/api';
import type { Store, DemandInsight } from '@/lib/types';

// Agent configurations
const agentConfigs = [

    {
        id: 'demand_agent',
        name: 'Demand Agent',
        description: 'Retrieves and analyzes demand forecasts from ML models',
        icon: TrendingUp,
        color: 'text-blue-600',
        bg: 'bg-blue-100',
        hasDetailedView: true, // Flag for agents with detailed table views
    },
    {
        id: 'trend_agent',
        name: 'Trend Analyzer',
        description: 'Analyzes sales trends by comparing actual vs forecasted sales',
        icon: BarChart3,
        color: 'text-indigo-600',
        bg: 'bg-indigo-100',
    },
    {
        id: 'inventory_agent',
        name: 'Inventory Agent',
        description: 'Assesses current stock levels and identifies inventory issues',
        icon: Package,
        color: 'text-amber-600',
        bg: 'bg-amber-100',
    },
    {
        id: 'replenishment_agent',
        name: 'Replenishment Agent',
        description: 'Creates optimal replenishment plans via transfers or orders',
        icon: Truck,
        color: 'text-emerald-600',
        bg: 'bg-emerald-100',
    },
    {
        id: 'pricing_agent',
        name: 'Pricing Agent',
        description: 'Generates pricing and promotion recommendations',
        icon: Tag,
        color: 'text-orange-600',
        bg: 'bg-orange-100',
    },
    {
        id: 'campaign_agent',
        name: 'Campaign Agent',
        description: 'Creates marketing campaigns with AI-generated creatives',
        icon: Palette,
        color: 'text-pink-600',
        bg: 'bg-pink-100',
    },
];

interface AgentResult {
    agent_id: string;
    summary: string;
    insights: string[];
    recommendations: string[];
    metrics: Record<string, string | number>;
    timestamp?: string;
}

// Demand Table Component
function DemandDataTable({ selectedStore, onStoreChange }: { selectedStore: string, onStoreChange: (storeId: string) => void }) {
    const [stores, setStores] = useState<Store[]>([]);
    const [insights, setInsights] = useState<DemandInsight[]>([]);
    const [summary, setSummary] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStores = async () => {
            try {
                const storeData = await getStores();
                setStores(storeData);
            } catch (err) {
                console.error('Failed to fetch stores:', err);
            }
        };
        fetchStores();
    }, []);

    useEffect(() => {
        const fetchInsights = async () => {
            setLoading(true);
            try {
                const data = await getDemandInsights(selectedStore || undefined);
                setInsights(data.insights || []);
                setSummary(data.summary || null);
            } catch (err) {
                console.error('Failed to fetch demand insights:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchInsights();
    }, [selectedStore]);

    const getStockStatusBadge = (status: string) => {
        const styles: Record<string, string> = {
            in_stock: 'bg-green-100 text-green-700',
            low_stock: 'bg-yellow-100 text-yellow-700',
            out_of_stock: 'bg-red-100 text-red-700',
            overstocked: 'bg-blue-100 text-blue-700',
        };
        const labels: Record<string, string> = {
            in_stock: 'In Stock',
            low_stock: 'Low Stock',
            out_of_stock: 'Out of Stock',
            overstocked: 'Overstocked',
        };
        return (
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${styles[status] || styles.in_stock}`}>
                {labels[status] || status}
            </span>
        );
    };

    return (
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
            {/* Section Header with Store Selector */}
            <div className="flex items-center justify-between" style={{ marginBottom: '20px' }}>
                <div className="flex items-center gap-2">
                    <Table2 style={{ width: '18px', height: '18px', color: '#3b82f6' }} />
                    <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Demand Forecast Data</h3>
                </div>

                {/* Store Selector - Fixed dropdown */}
                <div className="relative">
                    <select
                        value={selectedStore}
                        onChange={(e) => onStoreChange(e.target.value)}
                        style={{
                            appearance: 'none',
                            backgroundColor: 'white',
                            border: '1px solid #e2e8f0',
                            borderRadius: '8px',
                            padding: '8px 36px 8px 12px',
                            fontSize: '13px',
                            fontWeight: 500,
                            color: '#374151',
                            cursor: 'pointer',
                            minWidth: '220px',
                        }}
                        className="focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                        <option value="">All Stores</option>
                        {stores.map((store) => (
                            <option key={store.store_id} value={store.store_id}>
                                {store.store_name || (store as any).name || store.city}
                            </option>
                        ))}
                    </select>
                    <ChevronDown style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', width: '16px', height: '16px', color: '#9ca3af', pointerEvents: 'none' }} />
                </div>
            </div>

            {/* Summary Stats - No stock-related stats for demand agent */}
            {summary && (
                <div className="flex gap-4 flex-wrap" style={{ marginBottom: '20px' }}>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#0369a1', marginBottom: '4px' }}>TOTAL ITEMS</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#0c4a6e' }}>{summary.total_items}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#15803d', marginBottom: '4px' }}>TOTAL DEMAND</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#14532d' }}>{summary.total_forecasted_demand?.toLocaleString()}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#faf5ff', border: '1px solid #e9d5ff', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#7e22ce', marginBottom: '4px' }}>AVG CONFIDENCE</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#581c87' }}>{(summary.average_confidence * 100).toFixed(0)}%</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#fef3c7', border: '1px solid #fde68a', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#b45309', marginBottom: '4px' }}>PERIOD</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#78350f' }}>{summary.period}</div>
                    </div>
                </div>
            )}

            {/* Data Table */}
            {loading ? (
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
                    <span className="ml-2 text-gray-500 text-sm">Loading demand data...</span>
                </div>
            ) : insights.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-gray-400">
                    <Package className="w-10 h-10 mb-3" />
                    <p className="text-sm">No demand forecasts available</p>
                    <p className="text-xs text-gray-400 mt-1">Run an analysis from the dashboard to generate forecasts</p>
                </div>
            ) : (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '10px', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Product</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Category</th>
                                {!selectedStore && (
                                    <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Store</th>
                                )}
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Forecasted Demand</th>
                                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Confidence</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Season</th>
                            </tr>
                        </thead>
                        <tbody>
                            {insights.slice(0, 20).map((insight, index) => (
                                <tr
                                    key={`${insight.store_id}-${insight.product_id}`}
                                    style={{
                                        borderBottom: index < insights.length - 1 ? '1px solid #f1f5f9' : 'none',
                                        transition: 'background-color 0.15s ease'
                                    }}
                                    className="hover:bg-gray-50"
                                >
                                    <td style={{ padding: '12px 16px' }}>
                                        <div>
                                            <p style={{ fontSize: '13px', fontWeight: 500, color: '#0f172a' }}>{insight.product_name}</p>
                                            <p style={{ fontSize: '11px', color: '#94a3b8' }}>{insight.product_id}</p>
                                        </div>
                                    </td>
                                    <td style={{ padding: '12px 16px', fontSize: '13px', color: '#475569' }}>{insight.category}</td>
                                    {!selectedStore && (
                                        <td style={{ padding: '12px 16px', fontSize: '13px', color: '#475569' }}>{insight.store_id}</td>
                                    )}
                                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                        <span style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{insight.forecasted_demand.toLocaleString()} <span style={{ color: '#94a3b8', fontWeight: 400 }}>units</span></span>
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                        <span style={{
                                            padding: '4px 10px',
                                            borderRadius: '9999px',
                                            fontSize: '12px',
                                            fontWeight: 500,
                                            backgroundColor: insight.confidence >= 0.9 ? '#dcfce7' : insight.confidence >= 0.7 ? '#fef9c3' : '#fee2e2',
                                            color: insight.confidence >= 0.9 ? '#166534' : insight.confidence >= 0.7 ? '#854d0e' : '#991b1b'
                                        }}>
                                            {(insight.confidence * 100).toFixed(0)}%
                                        </span>
                                    </td>
                                    <td style={{ padding: '12px 16px', fontSize: '13px', color: '#475569' }}>{insight.season}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {insights.length > 20 && (
                        <div style={{ padding: '12px 16px', textAlign: 'center', backgroundColor: '#f8fafc', borderTop: '1px solid #e2e8f0' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Showing 20 of {insights.length} items</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// Trend Data Table Component
interface TrendInsight {
    store_id: string;
    product_id: string;
    product_name: string;
    category: string;
    forecasted_demand: number;
    actual_sales: number;
    expected_sales: number;
    velocity_ratio: number;
    trend_status: 'in-trend' | 'average' | 'slow-moving' | 'no-trend';
    projected_total: number;
    surplus_deficit: number;
    season: string;
    days_elapsed: number;
    days_remaining: number;
}

interface TrendSummary {
    total_items: number;
    trending_count: number;
    slow_moving_count: number;
    average_velocity_ratio: number;
    period: string;
    days_elapsed: number;
}

function TrendDataTable({ selectedStore, onStoreChange }: { selectedStore: string, onStoreChange: (storeId: string) => void }) {
    const [stores, setStores] = useState<Store[]>([]);
    const [insights, setInsights] = useState<TrendInsight[]>([]);
    const [summary, setSummary] = useState<TrendSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStores = async () => {
            try {
                const data = await getStores();
                setStores((data as any).stores || data || []);
            } catch (err) {
                console.error('Error fetching stores:', err);
            }
        };
        fetchStores();
    }, []);

    useEffect(() => {
        const fetchTrendInsights = async () => {
            setLoading(true);
            try {
                const { getTrendInsights } = await import('@/lib/api');
                const data = await getTrendInsights(selectedStore || undefined);
                setInsights(data.insights || []);
                setSummary(data.summary || null);
            } catch (err) {
                console.error('Error fetching trend insights:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchTrendInsights();
    }, [selectedStore]);

    const getTrendBadge = (status: string) => {
        const styles: Record<string, { bg: string; color: string; label: string }> = {
            'in-trend': { bg: '#dcfce7', color: '#166534', label: 'Trending' },
            'average': { bg: '#dbeafe', color: '#1e40af', label: 'Average' },
            'slow-moving': { bg: '#fef3c7', color: '#92400e', label: 'Slow' },
            'no-trend': { bg: '#fee2e2', color: '#991b1b', label: 'None' },
        };
        const style = styles[status] || styles['average'];
        return (
            <span style={{ padding: '4px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600, backgroundColor: style.bg, color: style.color, whiteSpace: 'nowrap' }}>
                {style.label}
            </span>
        );
    };

    return (
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
            {/* Section Header with Store Selector */}
            <div className="flex items-center justify-between" style={{ marginBottom: '20px' }}>
                <div className="flex items-center gap-2">
                    <BarChart3 style={{ width: '18px', height: '18px', color: '#6366f1' }} />
                    <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Trend Analysis Data</h3>
                </div>

                {/* Store Selector */}
                <div className="relative">
                    <select
                        value={selectedStore}
                        onChange={(e) => onStoreChange(e.target.value)}
                        style={{
                            appearance: 'none',
                            backgroundColor: 'white',
                            border: '1px solid #e2e8f0',
                            borderRadius: '8px',
                            padding: '8px 36px 8px 12px',
                            fontSize: '13px',
                            fontWeight: 500,
                            color: '#374151',
                            cursor: 'pointer',
                            minWidth: '220px',
                        }}
                        className="focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                        <option value="">All Stores</option>
                        {stores.map((store) => (
                            <option key={store.store_id} value={store.store_id}>
                                {store.store_name || (store as any).name || store.city}
                            </option>
                        ))}
                    </select>
                    <ChevronDown style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', width: '16px', height: '16px', color: '#9ca3af', pointerEvents: 'none' }} />
                </div>
            </div>

            {/* Summary Stats */}
            {summary && (
                <div className="flex gap-4 flex-wrap" style={{ marginBottom: '20px' }}>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#15803d', marginBottom: '4px' }}>TRENDING</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#14532d' }}>{summary.trending_count}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#fef3c7', border: '1px solid #fde68a', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#b45309', marginBottom: '4px' }}>SLOW MOVING</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#78350f' }}>{summary.slow_moving_count}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#ede9fe', border: '1px solid #c4b5fd', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#6d28d9', marginBottom: '4px' }}>AVG VELOCITY</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#4c1d95' }}>{summary.average_velocity_ratio}x</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#0369a1', marginBottom: '4px' }}>PERIOD</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#0c4a6e' }}>{summary.period}</div>
                    </div>
                </div>
            )}

            {/* Data Table */}
            {loading ? (
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-indigo-500" />
                    <span className="ml-2 text-gray-500">Loading trend data...</span>
                </div>
            ) : insights.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    No trend data available for this selection.
                </div>
            ) : (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '10px', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Product</th>
                                {!selectedStore && (
                                    <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Store</th>
                                )}
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Actual Sales</th>
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Expected</th>
                                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Velocity</th>
                                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Status</th>
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Projected</th>
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Surplus/Deficit</th>
                            </tr>
                        </thead>
                        <tbody>
                            {insights.slice(0, 20).map((insight, idx) => (
                                <tr key={`${insight.product_id}-${insight.store_id}-${idx}`} style={{ borderBottom: idx < insights.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                                    <td style={{ padding: '12px 16px' }}>
                                        <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{insight.product_name}</div>
                                        <div style={{ fontSize: '11px', color: '#94a3b8' }}>{insight.category}</div>
                                    </td>
                                    {!selectedStore && (
                                        <td style={{ padding: '12px 16px', fontSize: '13px', color: '#475569' }}>{insight.store_id}</td>
                                    )}
                                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                        <span style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{insight.actual_sales} <span style={{ color: '#94a3b8', fontWeight: 400 }}>units</span></span>
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                        <span style={{ fontSize: '13px', color: '#64748b' }}>{insight.expected_sales}</span>
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                        <span style={{
                                            padding: '4px 10px',
                                            borderRadius: '9999px',
                                            fontSize: '12px',
                                            fontWeight: 600,
                                            backgroundColor: insight.velocity_ratio >= 1.5 ? '#dcfce7' : insight.velocity_ratio >= 0.8 ? '#dbeafe' : '#fef3c7',
                                            color: insight.velocity_ratio >= 1.5 ? '#166534' : insight.velocity_ratio >= 0.8 ? '#1e40af' : '#92400e'
                                        }}>
                                            {insight.velocity_ratio}x
                                        </span>
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                        {getTrendBadge(insight.trend_status)}
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                        <span style={{ fontSize: '13px', fontWeight: 500, color: '#0f172a' }}>{insight.projected_total}</span>
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                        <span style={{
                                            fontSize: '13px',
                                            fontWeight: 600,
                                            color: insight.surplus_deficit >= 0 ? '#16a34a' : '#dc2626'
                                        }}>
                                            {insight.surplus_deficit >= 0 ? '+' : ''}{insight.surplus_deficit}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {insights.length > 20 && (
                        <div style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid #e2e8f0', textAlign: 'center' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Showing 20 of {insights.length} items</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// Inventory Data Table Component
interface InventoryInsight {
    store_id: string;
    product_id: string;
    product_name: string;
    category: string;
    current_stock: number;
    forecasted_demand: number;
    stock_ratio: number;
    stock_status: 'understocked' | 'healthy' | 'overstocked';
    days_of_stock: number | null;
}

interface InventorySummary {
    total_items: number;
    understocked_count: number;
    overstocked_count: number;
    healthy_count: number;
    period: string;
    days_remaining: number;
}

function InventoryDataTable({ selectedStore, onStoreChange }: { selectedStore: string, onStoreChange: (storeId: string) => void }) {
    const [stores, setStores] = useState<Store[]>([]);
    const [insights, setInsights] = useState<InventoryInsight[]>([]);
    const [summary, setSummary] = useState<InventorySummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStores = async () => {
            try {
                const data = await getStores();
                setStores((data as any).stores || data || []);
            } catch (err) {
                console.error('Error fetching stores:', err);
            }
        };
        fetchStores();
    }, []);

    useEffect(() => {
        const fetchInventoryInsights = async () => {
            setLoading(true);
            try {
                const { getInventoryInsights } = await import('@/lib/api');
                const data = await getInventoryInsights(selectedStore || undefined);
                setInsights(data.insights || []);
                setSummary(data.summary || null);
            } catch (err) {
                console.error('Error fetching inventory insights:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchInventoryInsights();
    }, [selectedStore]);

    const getStatusBadge = (status: string) => {
        const styles: Record<string, { bg: string; color: string; label: string }> = {
            'understocked': { bg: '#fee2e2', color: '#991b1b', label: 'Understocked' },
            'healthy': { bg: '#dcfce7', color: '#166534', label: 'Healthy' },
            'overstocked': { bg: '#dbeafe', color: '#1e40af', label: 'Overstocked' },
        };
        const style = styles[status] || styles['healthy'];
        return (
            <span style={{ padding: '4px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600, backgroundColor: style.bg, color: style.color, whiteSpace: 'nowrap' }}>
                {style.label}
            </span>
        );
    };

    const getDaysOfStockStyle = (days: number | null) => {
        if (days === null) return { bg: '#f1f5f9', color: '#64748b' };
        if (days < 7) return { bg: '#fee2e2', color: '#991b1b' };
        if (days < 14) return { bg: '#fef3c7', color: '#92400e' };
        return { bg: '#dcfce7', color: '#166534' };
    };

    return (
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
            {/* Section Header with Store Selector */}
            <div className="flex items-center justify-between" style={{ marginBottom: '20px' }}>
                <div className="flex items-center gap-2">
                    <Package style={{ width: '18px', height: '18px', color: '#f59e0b' }} />
                    <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Stock Health Overview</h3>
                </div>

                {/* Store Selector */}
                <div className="relative">
                    <select
                        value={selectedStore}
                        onChange={(e) => onStoreChange(e.target.value)}
                        style={{
                            appearance: 'none',
                            backgroundColor: 'white',
                            border: '1px solid #e2e8f0',
                            borderRadius: '8px',
                            padding: '8px 36px 8px 12px',
                            fontSize: '13px',
                            fontWeight: 500,
                            color: '#374151',
                            cursor: 'pointer',
                            minWidth: '220px',
                        }}
                        className="focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500"
                    >
                        <option value="">All Stores</option>
                        {stores.map((store) => (
                            <option key={store.store_id} value={store.store_id}>
                                {store.store_name || (store as any).name || store.city}
                            </option>
                        ))}
                    </select>
                    <ChevronDown style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', width: '16px', height: '16px', color: '#9ca3af', pointerEvents: 'none' }} />
                </div>
            </div>

            {/* Summary Stats */}
            {summary && (
                <div className="flex gap-4 flex-wrap" style={{ marginBottom: '20px' }}>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#0369a1', marginBottom: '4px' }}>TOTAL ITEMS</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#0c4a6e' }}>{summary.total_items}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#fee2e2', border: '1px solid #fecaca', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#991b1b', marginBottom: '4px' }}>UNDERSTOCKED</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#7f1d1d' }}>{summary.understocked_count}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#dbeafe', border: '1px solid #bfdbfe', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#1e40af', marginBottom: '4px' }}>OVERSTOCKED</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#1e3a8a' }}>{summary.overstocked_count}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#dcfce7', border: '1px solid #bbf7d0', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#166534', marginBottom: '4px' }}>HEALTHY</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#14532d' }}>{summary.healthy_count}</div>
                    </div>
                </div>
            )}

            {/* Data Table */}
            {loading ? (
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-amber-500" />
                    <span className="ml-2 text-gray-500">Loading inventory data...</span>
                </div>
            ) : insights.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    No inventory data available for this selection.
                </div>
            ) : (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '10px', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Product</th>
                                {!selectedStore && (
                                    <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Store</th>
                                )}
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Current Stock</th>
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Demand</th>
                                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Stock Ratio</th>
                                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Status</th>
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Days of Stock</th>
                            </tr>
                        </thead>
                        <tbody>
                            {insights.slice(0, 20).map((insight, idx) => {
                                const daysStyle = getDaysOfStockStyle(insight.days_of_stock);
                                return (
                                    <tr key={`${insight.product_id}-${insight.store_id}-${idx}`} style={{ borderBottom: idx < insights.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                                        <td style={{ padding: '12px 16px' }}>
                                            <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{insight.product_name}</div>
                                            <div style={{ fontSize: '11px', color: '#94a3b8' }}>{insight.category}</div>
                                        </td>
                                        {!selectedStore && (
                                            <td style={{ padding: '12px 16px', fontSize: '13px', color: '#475569' }}>{insight.store_id}</td>
                                        )}
                                        <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                            <span style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{insight.current_stock} <span style={{ color: '#94a3b8', fontWeight: 400 }}>units</span></span>
                                        </td>
                                        <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                            <span style={{ fontSize: '13px', color: '#64748b' }}>{insight.forecasted_demand}</span>
                                        </td>
                                        <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                            <span style={{
                                                padding: '4px 10px',
                                                borderRadius: '9999px',
                                                fontSize: '12px',
                                                fontWeight: 600,
                                                backgroundColor: insight.stock_ratio < 0.5 ? '#fee2e2' : insight.stock_ratio > 1.5 ? '#dbeafe' : '#dcfce7',
                                                color: insight.stock_ratio < 0.5 ? '#991b1b' : insight.stock_ratio > 1.5 ? '#1e40af' : '#166534'
                                            }}>
                                                {insight.stock_ratio}x
                                            </span>
                                        </td>
                                        <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                            {getStatusBadge(insight.stock_status)}
                                        </td>
                                        <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                            <span style={{
                                                padding: '4px 10px',
                                                borderRadius: '9999px',
                                                fontSize: '12px',
                                                fontWeight: 500,
                                                backgroundColor: daysStyle.bg,
                                                color: daysStyle.color
                                            }}>
                                                {insight.days_of_stock !== null ? `${insight.days_of_stock} days` : '—'}
                                            </span>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                    {insights.length > 20 && (
                        <div style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid #e2e8f0', textAlign: 'center' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Showing 20 of {insights.length} items</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// Replenishment Data Table Component
interface ReplenishmentInsight {
    plan_id: string;
    product_id: string;
    product_name: string;
    category: string;
    target_store_id: string;
    required_quantity: number;
    action_type: string;
    source: string;
    urgency: 'critical' | 'high' | 'normal';
    total_cost: number;
    expected_completion_date: string | null;
    requires_approval: boolean;
    reasoning: string;
    risk: string;
}

interface ReplenishmentSummary {
    total_plans: number;
    critical_count: number;
    high_count: number;
    transfer_count: number;
    order_count: number;
    total_cost: number;
    period: string;
}

function ReplenishmentDataTable({ selectedStore, onStoreChange }: { selectedStore: string, onStoreChange: (storeId: string) => void }) {
    const [stores, setStores] = useState<Store[]>([]);
    const [insights, setInsights] = useState<ReplenishmentInsight[]>([]);
    const [summary, setSummary] = useState<ReplenishmentSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStores = async () => {
            try {
                const data = await getStores();
                setStores((data as any).stores || data || []);
            } catch (err) {
                console.error('Error fetching stores:', err);
            }
        };
        fetchStores();
    }, []);

    useEffect(() => {
        const fetchReplenishmentInsights = async () => {
            setLoading(true);
            try {
                const { getReplenishmentInsights } = await import('@/lib/api');
                const data = await getReplenishmentInsights(selectedStore || undefined);
                setInsights(data.insights || []);
                setSummary(data.summary || null);
            } catch (err) {
                console.error('Error fetching replenishment insights:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchReplenishmentInsights();
    }, [selectedStore]);

    const getUrgencyBadge = (urgency: string) => {
        const styles: Record<string, { bg: string; color: string; label: string }> = {
            'critical': { bg: '#fee2e2', color: '#991b1b', label: 'Critical' },
            'high': { bg: '#fef3c7', color: '#92400e', label: 'High' },
            'normal': { bg: '#dcfce7', color: '#166534', label: 'Normal' },
        };
        const style = styles[urgency] || styles['normal'];
        return (
            <span style={{ padding: '4px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600, backgroundColor: style.bg, color: style.color, whiteSpace: 'nowrap' }}>
                {style.label}
            </span>
        );
    };

    const getActionTypeBadge = (actionType: string) => {
        const styles: Record<string, { bg: string; color: string; label: string }> = {
            'inter_store_transfer': { bg: '#dbeafe', color: '#1e40af', label: 'Transfer' },
            'manufacturer_order': { bg: '#ede9fe', color: '#5b21b6', label: 'Order' },
            'combined': { bg: '#fce7f3', color: '#9d174d', label: 'Combined' },
            'manual_review': { bg: '#f1f5f9', color: '#475569', label: 'Manual' },
        };
        const style = styles[actionType] || styles['manual_review'];
        return (
            <span style={{ padding: '4px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600, backgroundColor: style.bg, color: style.color, whiteSpace: 'nowrap' }}>
                {style.label}
            </span>
        );
    };

    const formatDate = (dateStr: string | null) => {
        if (!dateStr) return '—';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    };

    return (
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
            {/* Section Header with Store Selector */}
            <div className="flex items-center justify-between" style={{ marginBottom: '20px' }}>
                <div className="flex items-center gap-2">
                    <Truck style={{ width: '18px', height: '18px', color: '#10b981' }} />
                    <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Replenishment Plans</h3>
                </div>

                {/* Store Selector */}
                <div className="relative">
                    <select
                        value={selectedStore}
                        onChange={(e) => onStoreChange(e.target.value)}
                        style={{
                            appearance: 'none',
                            backgroundColor: 'white',
                            border: '1px solid #e2e8f0',
                            borderRadius: '8px',
                            padding: '8px 36px 8px 12px',
                            fontSize: '13px',
                            fontWeight: 500,
                            color: '#374151',
                            cursor: 'pointer',
                            minWidth: '220px',
                        }}
                        className="focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
                    >
                        <option value="">All Stores</option>
                        {stores.map((store) => (
                            <option key={store.store_id} value={store.store_id}>
                                {store.store_name || (store as any).name || store.city}
                            </option>
                        ))}
                    </select>
                    <ChevronDown style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', width: '16px', height: '16px', color: '#9ca3af', pointerEvents: 'none' }} />
                </div>
            </div>

            {/* Summary Stats */}
            {summary && (
                <div className="flex gap-4 flex-wrap" style={{ marginBottom: '20px' }}>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#0369a1', marginBottom: '4px' }}>TOTAL PLANS</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#0c4a6e' }}>{summary.total_plans}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#fee2e2', border: '1px solid #fecaca', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#991b1b', marginBottom: '4px' }}>CRITICAL</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#7f1d1d' }}>{summary.critical_count}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#dbeafe', border: '1px solid #bfdbfe', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#1e40af', marginBottom: '4px' }}>TRANSFERS</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#1e3a8a' }}>{summary.transfer_count}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#dcfce7', border: '1px solid #bbf7d0', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#166534', marginBottom: '4px' }}>TOTAL COST</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#14532d' }}>₹{summary.total_cost.toLocaleString()}</div>
                    </div>
                </div>
            )}

            {/* Data Table */}
            {loading ? (
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-emerald-500" />
                    <span className="ml-2 text-gray-500">Loading replenishment plans...</span>
                </div>
            ) : insights.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    No replenishment plans available for this selection.
                </div>
            ) : (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '10px', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Product</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Target Store</th>
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Qty Needed</th>
                                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Action</th>
                                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Source</th>
                                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Urgency</th>
                                <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Cost</th>
                                <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>ETA</th>
                            </tr>
                        </thead>
                        <tbody>
                            {insights.slice(0, 20).map((insight, idx) => (
                                <tr key={`${insight.plan_id}-${idx}`} style={{ borderBottom: idx < insights.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                                    <td style={{ padding: '12px 16px' }}>
                                        <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{insight.product_name}</div>
                                        <div style={{ fontSize: '11px', color: '#94a3b8' }}>{insight.category}</div>
                                    </td>
                                    <td style={{ padding: '12px 16px', fontSize: '13px', color: '#475569' }}>{insight.target_store_id}</td>
                                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                        <span style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{insight.required_quantity} <span style={{ color: '#94a3b8', fontWeight: 400 }}>units</span></span>
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                        {getActionTypeBadge(insight.action_type)}
                                    </td>
                                    <td style={{ padding: '12px 16px', fontSize: '13px', color: '#475569' }}>{insight.source || '—'}</td>
                                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                        {getUrgencyBadge(insight.urgency)}
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>
                                        <span style={{ fontSize: '13px', fontWeight: 500, color: '#0f172a' }}>₹{insight.total_cost.toLocaleString()}</span>
                                    </td>
                                    <td style={{ padding: '12px 16px', textAlign: 'center' }}>
                                        <span style={{ fontSize: '12px', color: '#64748b' }}>{formatDate(insight.expected_completion_date)}</span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {insights.length > 20 && (
                        <div style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid #e2e8f0', textAlign: 'center' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Showing 20 of {insights.length} plans</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// Pricing Data Table Component
interface PricingInsight {
    product_id: string;
    product_name: string;
    category: string;
    store_id: string;
    current_price: number;
    recommended_price: number;
    price_change_percent: number;
    recommendation_type: 'discount' | 'price_increase' | 'bundle' | 'flash_sale' | 'hold';
    stock_status: string;
    trend_status: string;
    expected_revenue_impact_weekly: number;
    confidence: number;
    reasoning: string;
    valid_from: string;
    valid_until: string;
}

interface PricingSummary {
    total_recommendations: number;
    discount_count: number;
    increase_count: number;
    hold_count: number;
    total_weekly_impact: number;
    period: string;
}

function PricingDataTable({ selectedStore, onStoreChange }: { selectedStore: string, onStoreChange: (storeId: string) => void }) {
    const [stores, setStores] = useState<Store[]>([]);
    const [insights, setInsights] = useState<PricingInsight[]>([]);
    const [summary, setSummary] = useState<PricingSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStores = async () => {
            try {
                const data = await getStores();
                setStores((data as any).stores || data || []);
            } catch (err) {
                console.error('Error fetching stores:', err);
            }
        };
        fetchStores();
    }, []);

    useEffect(() => {
        const fetchPricingInsights = async () => {
            setLoading(true);
            try {
                const { getPricingInsights } = await import('@/lib/api');
                const data = await getPricingInsights(selectedStore || undefined);
                setInsights(data.insights || []);
                setSummary(data.summary || null);
            } catch (err) {
                console.error('Error fetching pricing insights:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchPricingInsights();
    }, [selectedStore]);

    const getRecommendationTypeBadge = (type: string) => {
        const styles: Record<string, { bg: string; color: string; label: string }> = {
            'discount': { bg: '#fee2e2', color: '#991b1b', label: 'Discount' },
            'price_increase': { bg: '#dcfce7', color: '#166534', label: 'Increase' },
            'bundle': { bg: '#ede9fe', color: '#5b21b6', label: 'Bundle' },
            'flash_sale': { bg: '#fef3c7', color: '#92400e', label: 'Flash Sale' },
            'hold': { bg: '#f1f5f9', color: '#475569', label: 'Hold' },
        };
        const style = styles[type] || styles['hold'];
        return (
            <span style={{ padding: '4px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600, backgroundColor: style.bg, color: style.color, whiteSpace: 'nowrap' }}>
                {style.label}
            </span>
        );
    };

    const getStockStatusBadge = (status: string) => {
        const styles: Record<string, { bg: string; color: string; label: string }> = {
            'in-stock': { bg: '#dcfce7', color: '#166534', label: 'In Stock' },
            'understocked': { bg: '#fee2e2', color: '#991b1b', label: 'Understocked' },
            'overstocked': { bg: '#dbeafe', color: '#1e40af', label: 'Overstocked' },
        };
        const style = styles[status] || styles['in-stock'];
        return (
            <span style={{ padding: '4px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600, backgroundColor: style.bg, color: style.color, whiteSpace: 'nowrap' }}>
                {style.label}
            </span>
        );
    };

    const getTrendStatusBadge = (status: string) => {
        const styles: Record<string, { bg: string; color: string; label: string }> = {
            'in-trend': { bg: '#dcfce7', color: '#166534', label: 'Trending' },
            'average': { bg: '#f1f5f9', color: '#475569', label: 'Average' },
            'slow-moving': { bg: '#fef3c7', color: '#92400e', label: 'Slow' },
            'no-trend': { bg: '#fee2e2', color: '#991b1b', label: 'No Trend' },
        };
        const style = styles[status] || styles['average'];
        return (
            <span style={{ padding: '4px 10px', borderRadius: '9999px', fontSize: '11px', fontWeight: 600, backgroundColor: style.bg, color: style.color, whiteSpace: 'nowrap' }}>
                {style.label}
            </span>
        );
    };

    return (
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
            {/* Section Header with Store Selector */}
            <div className="flex items-center justify-between" style={{ marginBottom: '20px' }}>
                <div className="flex items-center gap-2">
                    <Tag style={{ width: '18px', height: '18px', color: '#f97316' }} />
                    <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Pricing Recommendations</h3>
                </div>

                {/* Store Selector */}
                <div className="relative">
                    <select
                        value={selectedStore}
                        onChange={(e) => onStoreChange(e.target.value)}
                        style={{
                            appearance: 'none',
                            backgroundColor: 'white',
                            border: '1px solid #e2e8f0',
                            borderRadius: '8px',
                            padding: '8px 36px 8px 12px',
                            fontSize: '13px',
                            fontWeight: 500,
                            color: '#374151',
                            cursor: 'pointer',
                            minWidth: '220px',
                        }}
                        className="focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    >
                        <option value="">All Stores</option>
                        {stores.map((store) => (
                            <option key={store.store_id} value={store.store_id}>
                                {store.store_name || (store as any).name || store.city}
                            </option>
                        ))}
                    </select>
                    <ChevronDown style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', width: '16px', height: '16px', color: '#9ca3af', pointerEvents: 'none' }} />
                </div>
            </div>

            {/* Summary Stats */}
            {summary && (
                <div className="flex gap-4 flex-wrap" style={{ marginBottom: '20px' }}>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#fff7ed', border: '1px solid #fed7aa', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#c2410c', marginBottom: '4px' }}>TOTAL RECOMMENDATIONS</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#7c2d12' }}>{summary.total_recommendations}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#fee2e2', border: '1px solid #fecaca', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#991b1b', marginBottom: '4px' }}>DISCOUNTS</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#7f1d1d' }}>{summary.discount_count}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#dcfce7', border: '1px solid #bbf7d0', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#166534', marginBottom: '4px' }}>INCREASES</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#14532d' }}>{summary.increase_count}</div>
                    </div>
                    <div style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#ede9fe', border: '1px solid #c4b5fd', minWidth: '140px' }}>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: '#6d28d9', marginBottom: '4px' }}>WEEKLY IMPACT</div>
                        <div style={{ fontSize: '18px', fontWeight: 700, color: summary.total_weekly_impact >= 0 ? '#166534' : '#991b1b' }}>
                            {summary.total_weekly_impact >= 0 ? '+' : ''}₹{summary.total_weekly_impact.toLocaleString()}
                        </div>
                    </div>
                </div>
            )}

            {/* Data Table */}
            {loading ? (
                <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-6 h-6 animate-spin text-orange-500" />
                    <span className="ml-2 text-gray-500">Loading pricing data...</span>
                </div>
            ) : insights.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                    No pricing recommendations available for this selection.
                </div>
            ) : (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '10px', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Product</th>
                                {!selectedStore && (
                                    <th style={{ padding: '10px 12px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Store</th>
                                )}
                                <th style={{ padding: '10px 12px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Current</th>
                                <th style={{ padding: '10px 12px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>New Price</th>
                                <th style={{ padding: '10px 12px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Change</th>
                                <th style={{ padding: '10px 12px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Type</th>
                                <th style={{ padding: '10px 12px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Stock</th>
                                <th style={{ padding: '10px 12px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Trend</th>
                            </tr>
                        </thead>
                        <tbody>
                            {insights.slice(0, 20).map((insight, idx) => (
                                <tr key={`${insight.product_id}-${insight.store_id}-${idx}`} style={{ borderBottom: idx < insights.length - 1 ? '1px solid #f1f5f9' : 'none' }}>
                                    <td style={{ padding: '10px 12px' }}>
                                        <div style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>{insight.product_name}</div>
                                        <div style={{ fontSize: '11px', color: '#94a3b8' }}>{insight.category}</div>
                                    </td>
                                    {!selectedStore && (
                                        <td style={{ padding: '10px 12px', fontSize: '12px', color: '#475569' }}>{insight.store_id}</td>
                                    )}
                                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                                        <span style={{ fontSize: '12px', color: '#64748b' }}>₹{insight.current_price.toLocaleString()}</span>
                                    </td>
                                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                                        <span style={{ fontSize: '12px', fontWeight: 600, color: '#0f172a' }}>₹{insight.recommended_price.toLocaleString()}</span>
                                    </td>
                                    <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                                        <span style={{
                                            padding: '3px 8px',
                                            borderRadius: '9999px',
                                            fontSize: '11px',
                                            fontWeight: 600,
                                            backgroundColor: insight.price_change_percent < 0 ? '#fee2e2' : insight.price_change_percent > 0 ? '#dcfce7' : '#f1f5f9',
                                            color: insight.price_change_percent < 0 ? '#991b1b' : insight.price_change_percent > 0 ? '#166534' : '#475569'
                                        }}>
                                            {insight.price_change_percent > 0 ? '+' : ''}{insight.price_change_percent.toFixed(1)}%
                                        </span>
                                    </td>
                                    <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                                        {getRecommendationTypeBadge(insight.recommendation_type)}
                                    </td>
                                    <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                                        {getStockStatusBadge(insight.stock_status)}
                                    </td>
                                    <td style={{ padding: '10px 12px', textAlign: 'center' }}>
                                        {getTrendStatusBadge(insight.trend_status)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {insights.length > 20 && (
                        <div style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid #e2e8f0', textAlign: 'center' }}>
                            <span style={{ fontSize: '12px', color: '#64748b' }}>Showing 20 of {insights.length} recommendations</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default function AgentInsights() {
    const [selectedAgent, setSelectedAgent] = useState(agentConfigs[0]);
    const [history, setHistory] = useState<Record<string, AgentResult>>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedStore, setSelectedStore] = useState<string>('');

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                setLoading(true);
                const data = await getAgentHistory();
                setHistory(data);
                setError(null);
            } catch (err) {
                console.error('Failed to fetch agent history:', err);
                setError('Failed to load agent insights. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, []);

    const currentInsights = history[selectedAgent.id] || {
        agent_id: selectedAgent.id,
        summary: "No analysis data available yet.",
        insights: [],
        recommendations: [],
        metrics: {}
    };

    const Icon = selectedAgent.icon;

    // Format timestamp nicely
    const formattedTime = currentInsights.timestamp
        ? new Date(currentInsights.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : null;

    const timeAgo = currentInsights.timestamp
        ? (() => {
            const diff = new Date().getTime() - new Date(currentInsights.timestamp).getTime();
            const mins = Math.floor(diff / 60000);
            if (mins < 1) return 'Just now';
            if (mins < 60) return `${mins} min ago`;
            const hours = Math.floor(mins / 60);
            if (hours < 24) return `${hours} hours ago`;
            return 'Yesterday';
        })()
        : null;

    return (
        <div className="flex h-screen w-full bg-gray-100 font-sans overflow-hidden">
            <Sidebar />

            <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
                {/* Header */}
                <header style={{ height: '64px', padding: '0 32px' }} className="bg-white border-b border-gray-200 flex items-center justify-between shrink-0">
                    <div style={{ gap: '12px', fontSize: '14px' }} className="flex items-center">
                        <span style={{ fontWeight: 500, color: '#64748b' }}>Agent Network</span>
                        <ChevronRight style={{ width: '14px', height: '14px', color: '#94a3b8' }} />
                        <div style={{ gap: '10px' }} className="flex items-center">
                            <div style={{ width: '32px', height: '32px', borderRadius: '8px' }} className={`flex items-center justify-center ${selectedAgent.bg}`}>
                                <Icon style={{ width: '16px', height: '16px' }} className={selectedAgent.color} />
                            </div>
                            <h1 style={{ fontSize: '16px', fontWeight: 600 }} className="text-gray-900">{selectedAgent.name}</h1>
                        </div>
                    </div>

                    {formattedTime && (
                        <div className="flex items-center gap-2" style={{ fontSize: '12px', color: '#64748b' }}>
                            <Clock style={{ width: '14px', height: '14px' }} />
                            Last updated: {timeAgo}
                        </div>
                    )}
                </header>

                {/* Master Detail View */}
                <div style={{ padding: '24px', gap: '24px' }} className="flex-1 flex overflow-hidden">

                    {/* Agent List Sidebar */}
                    <div style={{ width: '260px' }} className="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col overflow-hidden">
                        <div style={{ padding: '16px 20px', borderBottom: '1px solid #f1f5f9' }}>
                            <h2 style={{ fontSize: '13px', fontWeight: 600, color: '#0f172a' }}>All Agents</h2>
                            <p style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>Click to view insights</p>
                        </div>
                        <div style={{ padding: '12px', flex: 1, overflowY: 'auto' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                {agentConfigs.map(agent => {
                                    const AgentIcon = agent.icon;
                                    const isSelected = selectedAgent.id === agent.id;
                                    const hasData = !!history[agent.id];

                                    return (
                                        <button
                                            key={agent.id}
                                            onClick={() => setSelectedAgent(agent)}
                                            style={{
                                                width: '100%',
                                                textAlign: 'left',
                                                padding: '10px 12px',
                                                borderRadius: '8px',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '10px',
                                                backgroundColor: isSelected ? '#f1f5f9' : 'transparent',
                                                border: 'none',
                                                cursor: 'pointer',
                                                transition: 'all 0.15s ease'
                                            }}
                                            className="hover:bg-gray-50"
                                        >
                                            <div style={{ width: '32px', height: '32px', borderRadius: '8px', flexShrink: 0 }} className={`flex items-center justify-center ${agent.bg}`}>
                                                <AgentIcon style={{ width: '16px', height: '16px' }} className={agent.color} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <span style={{ fontSize: '13px', fontWeight: isSelected ? 600 : 500, color: isSelected ? '#0f172a' : '#475569' }} className="truncate block">
                                                    {agent.name}
                                                </span>
                                            </div>
                                            {isSelected && <ChevronRight style={{ width: '14px', height: '14px', color: '#0f172a', marginLeft: 'auto' }} />}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    {/* Detail View */}
                    <div className="flex-1 overflow-y-auto bg-white rounded-xl border border-gray-200 shadow-sm relative">

                        {loading ? (
                            <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
                                <div className="flex flex-col items-center gap-3">
                                    <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                                    <p className="text-sm text-gray-500 font-medium">Loading insights...</p>
                                </div>
                            </div>
                        ) : error ? (
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="flex flex-col items-center gap-3 text-center p-8">
                                    <AlertCircle className="w-10 h-10 text-red-500" />
                                    <p className="text-sm text-gray-900 font-medium">{error}</p>
                                    <button
                                        onClick={() => window.location.reload()}
                                        className="px-4 py-2 bg-gray-900 text-white rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
                                    >
                                        Retry
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <>
                                {/* Agent Header */}
                                <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
                                    <div className="flex items-start gap-4">
                                        <div style={{ width: '56px', height: '56px', borderRadius: '14px' }} className={`flex items-center justify-center ${selectedAgent.bg}`}>
                                            <Icon style={{ width: '28px', height: '28px' }} className={selectedAgent.color} />
                                        </div>
                                        <div className="flex-1">
                                            <h2 style={{ fontSize: '22px', fontWeight: 600 }} className="text-gray-900">{selectedAgent.name}</h2>
                                            <p style={{ fontSize: '14px', color: '#64748b', marginTop: '6px' }}>{selectedAgent.description}</p>
                                        </div>
                                    </div>

                                    {/* Summary Box */}
                                    {currentInsights.summary && (
                                        <div style={{ marginTop: '24px', padding: '20px' }} className="bg-gray-50 rounded-xl border border-gray-100">
                                            <p className="text-sm text-gray-700 leading-relaxed">
                                                "{currentInsights.summary}"
                                            </p>
                                        </div>
                                    )}

                                    {/* Metrics Row - Hide for agents with custom data tables */}
                                    {!['demand_agent', 'trend_agent', 'inventory_agent', 'replenishment_agent', 'pricing_agent'].includes(selectedAgent.id) && currentInsights.metrics && Object.keys(currentInsights.metrics).length > 0 && (
                                        <div className="flex gap-4 mt-6 flex-wrap">
                                            {Object.entries(currentInsights.metrics).map(([label, value], i) => (
                                                <div key={i} style={{ padding: '12px 16px', borderRadius: '10px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', minWidth: '120px' }}>
                                                    <div style={{ fontSize: '10px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', marginBottom: '4px' }}>{label.toUpperCase()}</div>
                                                    <div style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>{value}</div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Demand Agent Data Table - Show at TOP for demand_agent */}
                                {selectedAgent.id === 'demand_agent' && (
                                    <DemandDataTable
                                        selectedStore={selectedStore}
                                        onStoreChange={setSelectedStore}
                                    />
                                )}

                                {/* Trend Analyzer Data Table - Show for trend_agent */}
                                {selectedAgent.id === 'trend_agent' && (
                                    <TrendDataTable
                                        selectedStore={selectedStore}
                                        onStoreChange={setSelectedStore}
                                    />
                                )}

                                {/* Inventory Agent Data Table - Show for inventory_agent */}
                                {selectedAgent.id === 'inventory_agent' && (
                                    <InventoryDataTable
                                        selectedStore={selectedStore}
                                        onStoreChange={setSelectedStore}
                                    />
                                )}

                                {/* Replenishment Agent Data Table - Show for replenishment_agent */}
                                {selectedAgent.id === 'replenishment_agent' && (
                                    <ReplenishmentDataTable
                                        selectedStore={selectedStore}
                                        onStoreChange={setSelectedStore}
                                    />
                                )}

                                {/* Pricing Agent Data Table - Show for pricing_agent */}
                                {selectedAgent.id === 'pricing_agent' && (
                                    <PricingDataTable
                                        selectedStore={selectedStore}
                                        onStoreChange={setSelectedStore}
                                    />
                                )}
                                {/* Insights Section */}
                                <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
                                    <div className="flex items-center gap-2" style={{ marginBottom: '16px' }}>
                                        <Lightbulb style={{ width: '18px', height: '18px', color: '#f59e0b' }} />
                                        <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Key Insights</h3>
                                    </div>

                                    {currentInsights.insights && currentInsights.insights.length > 0 ? (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                            {currentInsights.insights.map((insight, i) => (
                                                <div
                                                    key={i}
                                                    style={{ padding: '12px 14px', borderRadius: '8px', backgroundColor: '#fffbeb', border: '1px solid #fef3c7' }}
                                                    className="flex items-start gap-3"
                                                >
                                                    <Sparkles style={{ width: '14px', height: '14px', color: '#f59e0b', marginTop: '2px', flexShrink: 0 }} />
                                                    <p style={{ fontSize: '13px', color: '#78350f', lineHeight: 1.5 }}>{insight}</p>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500 italic">No specific insights available yet. Run a new analysis to generate insights.</p>
                                    )}
                                </div>

                                {/* Recommendations Section */}
                                <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
                                    <div className="flex items-center gap-2" style={{ marginBottom: '16px' }}>
                                        <Target style={{ width: '18px', height: '18px', color: '#3b82f6' }} />
                                        <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Recommendations</h3>
                                    </div>

                                    {currentInsights.recommendations && currentInsights.recommendations.length > 0 ? (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                            {currentInsights.recommendations.map((rec, i) => (
                                                <div
                                                    key={i}
                                                    style={{ padding: '12px 14px', borderRadius: '8px', backgroundColor: '#eff6ff', border: '1px solid #dbeafe' }}
                                                    className="flex items-start gap-3"
                                                >
                                                    <ArrowRight style={{ width: '14px', height: '14px', color: '#3b82f6', marginTop: '2px', flexShrink: 0 }} />
                                                    <p style={{ fontSize: '13px', color: '#1e3a8a', lineHeight: 1.5 }}>{rec}</p>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <p className="text-sm text-gray-500 italic">No recommendations available yet.</p>
                                    )}
                                </div>

                                {/* Placeholder - demand table moved to top */}
                            </>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
