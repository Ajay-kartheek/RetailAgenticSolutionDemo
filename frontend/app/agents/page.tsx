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
    Clock,
    Sparkles,
    ArrowRight,
    Lightbulb,
    Target,
    AlertCircle,
    Loader2
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import { getAgentHistory } from '@/lib/api';

// Agent configurations
const agentConfigs = [

    {
        id: 'demand_agent',
        name: 'Demand Agent',
        description: 'Retrieves and analyzes demand forecasts from ML models',
        icon: TrendingUp,
        color: 'text-blue-600',
        bg: 'bg-blue-100',
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

export default function AgentInsights() {
    const [selectedAgent, setSelectedAgent] = useState(agentConfigs[0]);
    const [history, setHistory] = useState<Record<string, AgentResult>>({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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
                                        <div style={{ marginTop: '40px', marginBottom: '40px', padding: '32px' }} className="bg-gray-50 rounded-xl border border-gray-100 shadow-sm">
                                            <p className="text-base text-gray-700 leading-relaxed font-medium">
                                                "{currentInsights.summary}"
                                            </p>
                                        </div>
                                    )}

                                    {/* Metrics Row */}
                                    {currentInsights.metrics && Object.keys(currentInsights.metrics).length > 0 && (
                                        <div className="flex gap-6 mt-10 flex-wrap">
                                            {Object.entries(currentInsights.metrics).map(([label, value], i) => (
                                                <div key={i} style={{ padding: '16px 20px', borderRadius: '12px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', minWidth: '140px' }}>
                                                    <div style={{ fontSize: '11px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', marginBottom: '6px' }}>{label.toUpperCase()}</div>
                                                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>{value}</div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                {/* Insights Section */}
                                <div style={{ padding: '24px 32px', borderBottom: '1px solid #f1f5f9' }}>
                                    <div className="flex items-center gap-2" style={{ marginBottom: '32px' }}>
                                        <Lightbulb style={{ width: '18px', height: '18px', color: '#f59e0b' }} />
                                        <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Key Insights</h3>
                                    </div>

                                    {currentInsights.insights && currentInsights.insights.length > 0 ? (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                            {currentInsights.insights.map((insight, i) => (
                                                <div
                                                    key={i}
                                                    style={{ padding: '14px 16px', borderRadius: '10px', backgroundColor: '#fffbeb', border: '1px solid #fef3c7' }}
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
                                <div style={{ padding: '24px 32px' }}>
                                    <div className="flex items-center gap-2" style={{ marginBottom: '32px' }}>
                                        <Target style={{ width: '18px', height: '18px', color: '#3b82f6' }} />
                                        <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">Recommendations</h3>
                                    </div>

                                    {currentInsights.recommendations && currentInsights.recommendations.length > 0 ? (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                            {currentInsights.recommendations.map((rec, i) => (
                                                <div
                                                    key={i}
                                                    style={{ padding: '14px 16px', borderRadius: '10px', backgroundColor: '#eff6ff', border: '1px solid #dbeafe' }}
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
                            </>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
