'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Brain,
    TrendingUp,
    BarChart3,
    Package,
    Truck,
    Tag,
    Palette,
    Sparkles,
    MessageSquare,
    ArrowRight,
    CheckCircle2,
    AlertCircle
} from 'lucide-react';
import { getRecentActivity } from '@/lib/api';

interface AgentMessage {
    id: string;
    agent_name: string;
    type: 'thinking' | 'communication' | 'result' | 'error';
    message: string;
    thinking?: string;
    timestamp: Date;
}

interface AgentActivityPanelProps {
    messages: AgentMessage[];
    activeAgents: string[];
    isRunning: boolean;
}

// Agent config with icons and colors
const agentConfig: Record<string, { icon: any; color: string; bgColor: string; name: string }> = {
    'orchestrator': { icon: Brain, color: '#8b5cf6', bgColor: '#ede9fe', name: 'Orchestrator' },
    'demand_agent': { icon: TrendingUp, color: '#3b82f6', bgColor: '#dbeafe', name: 'Demand Agent' },
    'trend_agent': { icon: BarChart3, color: '#6366f1', bgColor: '#e0e7ff', name: 'Trend Analyzer' },
    'inventory_agent': { icon: Package, color: '#f59e0b', bgColor: '#fef3c7', name: 'Inventory Agent' },
    'replenishment_agent': { icon: Truck, color: '#10b981', bgColor: '#d1fae5', name: 'Replenishment Agent' },
    'pricing_agent': { icon: Tag, color: '#f97316', bgColor: '#ffedd5', name: 'Pricing Agent' },
    'campaign_agent': { icon: Palette, color: '#ec4899', bgColor: '#fce7f3', name: 'Campaign Agent' },
};

// Thinking Animation Component
function ThinkingIndicator({ color }: { color: string }) {
    return (
        <div className="flex items-center gap-1">
            {[0, 1, 2].map((i) => (
                <motion.div
                    key={i}
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: color }}
                    animate={{
                        scale: [1, 1.3, 1],
                        opacity: [0.5, 1, 0.5],
                    }}
                    transition={{
                        duration: 1,
                        repeat: Infinity,
                        delay: i * 0.2,
                        ease: 'easeInOut',
                    }}
                />
            ))}
        </div>
    );
}

// Brain Wave Animation for Active Agent
// Each circle: starts invisible → fades in while expanding → fades out completely
// The cycle repeats, but since it starts AND ends at opacity 0, no visible flicker
function BrainWaveAnimation({ color }: { color: string }) {
    return (
        <div className="absolute inset-0 flex items-center justify-center">
            {[0, 1, 2].map((i) => (
                <motion.div
                    key={i}
                    className="absolute rounded-full"
                    style={{
                        border: `2px solid ${color}`,
                        width: '100%',
                        height: '100%',
                    }}
                    initial={{ scale: 1, opacity: 0 }}
                    animate={{
                        scale: [1, 1.3, 1.6],
                        opacity: [0, 0.4, 0],
                    }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        delay: i * 0.5,
                        ease: 'easeOut',
                    }}
                />
            ))}
        </div>
    );
}

// Agent Avatar Component
function AgentAvatar({ agentName, isActive }: { agentName: string; isActive: boolean }) {
    const config = agentConfig[agentName] || agentConfig['orchestrator'];
    const Icon = config.icon;

    return (
        <div className="relative" style={{ width: '44px', height: '44px' }}>
            {isActive && <BrainWaveAnimation color={config.color} />}
            <div
                className="relative z-10 w-full h-full rounded-xl flex items-center justify-center"
                style={{ backgroundColor: config.bgColor }}
            >
                <Icon style={{ width: '22px', height: '22px', color: config.color }} />
            </div>
        </div>
    );
}

// Single Activity Message
function ActivityMessage({ message, isLatest }: { message: AgentMessage; isLatest: boolean }) {
    const config = agentConfig[message.agent_name] || agentConfig['orchestrator'];

    return (
        <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            className="flex"
            style={{ marginBottom: '20px', gap: '14px' }}
        >
            {/* Agent Avatar */}
            <div className="flex-shrink-0">
                <AgentAvatar agentName={message.agent_name} isActive={isLatest && message.type === 'thinking'} />
            </div>

            {/* Message Content */}
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                    <span style={{ fontSize: '13px', fontWeight: 600, color: config.color }}>
                        {config.name}
                    </span>
                    <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                        {message.timestamp.toLocaleTimeString()}
                    </span>
                    {message.type === 'thinking' && isLatest && (
                        <div className="flex items-center gap-1 px-2 py-0.5 rounded-full" style={{ backgroundColor: config.bgColor }}>
                            <Sparkles style={{ width: '10px', height: '10px', color: config.color }} />
                            <span style={{ fontSize: '10px', fontWeight: 600, color: config.color }}>THINKING</span>
                        </div>
                    )}
                    {message.type === 'result' && (
                        <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-50">
                            <CheckCircle2 style={{ width: '10px', height: '10px', color: '#10b981' }} />
                            <span style={{ fontSize: '10px', fontWeight: 600, color: '#10b981' }}>COMPLETE</span>
                        </div>
                    )}
                    {message.type === 'error' && (
                        <div className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-red-50">
                            <AlertCircle style={{ width: '10px', height: '10px', color: '#ef4444' }} />
                            <span style={{ fontSize: '10px', fontWeight: 600, color: '#ef4444' }}>ERROR</span>
                        </div>
                    )}
                </div>

                {/* Message Box */}
                <div
                    className="rounded-xl"
                    style={{
                        padding: '12px 16px',
                        backgroundColor: isLatest ? '#f8fafc' : '#ffffff',
                        border: '1px solid #e2e8f0',
                    }}
                >
                    <p style={{ fontSize: '13px', color: '#334155', lineHeight: 1.5 }}>
                        {message.message}
                    </p>

                    {/* Thinking text with typewriter effect */}
                    {message.thinking && (
                        <div
                            className="mt-2 pt-2"
                            style={{ borderTop: '1px dashed #e2e8f0' }}
                        >
                            <div className="flex items-start gap-2">
                                <MessageSquare style={{ width: '12px', height: '12px', color: '#94a3b8', marginTop: '3px' }} />
                                <p style={{ fontSize: '12px', color: '#64748b', fontStyle: 'italic', lineHeight: 1.5 }}>
                                    "{message.thinking}"
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Show thinking indicator for active agents */}
                    {message.type === 'thinking' && isLatest && (
                        <div className="mt-2 flex items-center gap-2">
                            <ThinkingIndicator color={config.color} />
                            <span style={{ fontSize: '11px', color: '#94a3b8' }}>Processing...</span>
                        </div>
                    )}
                </div>
            </div>
        </motion.div>
    );
}

export default function AgentActivityPanel({ messages, activeAgents, isRunning }: AgentActivityPanelProps) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const [executionHistory, setExecutionHistory] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState<'live' | 'history'>('live');

    // Fetch execution history from API
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const activities = await getRecentActivity(10);
                if (activities && activities.length > 0) {
                    setExecutionHistory(activities);
                }
            } catch (e) {
                // Silently fail - API might not be available yet
                console.log('Activity API not available yet');
            }
        };
        fetchHistory();
        // Refresh every 10 seconds for more real-time feel
        const interval = setInterval(fetchHistory, 10000);
        return () => clearInterval(interval);
    }, []);

    // Auto-scroll to latest message
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, executionHistory]);

    // Convert execution history to display format with workflow context
    const historyMessages = executionHistory.map((item, idx) => ({
        id: item.activity_id,
        agent_name: item.agent_id,
        type: 'result' as const,
        message: item.description,
        timestamp: new Date(item.timestamp),
        details: item.details,
        // Add workflow context for display
        workflow: [
            { agent: 'orchestrator', action: 'Received approved decision', done: true },
            { agent: item.agent_id, action: item.description, done: true }
        ]
    }));

    // Which messages to show based on tab
    const displayMessages = activeTab === 'live' ? messages : historyMessages;

    return (
        <div
            className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col"
            style={{ height: '500px' }}
        >
            {/* Header with Tabs */}
            <div className="border-b border-gray-100">
                <div
                    className="flex items-center justify-between"
                    style={{ padding: '12px 20px' }}
                >
                    <div className="flex items-center gap-3">
                        <div className="relative">
                            <Brain style={{ width: '20px', height: '20px', color: '#8b5cf6' }} />
                            {(isRunning || executionHistory.length > 0) && (
                                <motion.div
                                    className="absolute -top-1 -right-1 w-2 h-2 rounded-full"
                                    style={{ backgroundColor: isRunning ? '#10b981' : '#8b5cf6' }}
                                    animate={{ scale: isRunning ? [1, 1.3, 1] : 1 }}
                                    transition={{ duration: 1, repeat: isRunning ? Infinity : 0 }}
                                />
                            )}
                        </div>
                        <h3 style={{ fontSize: '15px', fontWeight: 600 }} className="text-gray-900">
                            Agent Activity
                        </h3>
                    </div>

                    {isRunning && (
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 rounded-full">
                            <ThinkingIndicator color="#10b981" />
                            <span style={{ fontSize: '11px', fontWeight: 600, color: '#10b981' }}>Live</span>
                        </div>
                    )}
                </div>

                {/* Tab Bar */}
                <div style={{ padding: '0 20px', display: 'flex', gap: '4px' }}>
                    <button
                        onClick={() => setActiveTab('live')}
                        style={{
                            padding: '8px 16px',
                            fontSize: '12px',
                            fontWeight: 600,
                            borderRadius: '8px 8px 0 0',
                            border: 'none',
                            cursor: 'pointer',
                            backgroundColor: activeTab === 'live' ? '#f8fafc' : 'transparent',
                            color: activeTab === 'live' ? '#0f172a' : '#64748b',
                            borderBottom: activeTab === 'live' ? '2px solid #8b5cf6' : '2px solid transparent'
                        }}
                    >
                        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <Sparkles style={{ width: '12px', height: '12px' }} />
                            Live Feed
                            {messages.length > 0 && (
                                <span style={{
                                    backgroundColor: '#8b5cf6',
                                    color: '#fff',
                                    padding: '2px 6px',
                                    borderRadius: '10px',
                                    fontSize: '10px'
                                }}>
                                    {messages.length}
                                </span>
                            )}
                        </span>
                    </button>
                    <button
                        onClick={() => setActiveTab('history')}
                        style={{
                            padding: '8px 16px',
                            fontSize: '12px',
                            fontWeight: 600,
                            borderRadius: '8px 8px 0 0',
                            border: 'none',
                            cursor: 'pointer',
                            backgroundColor: activeTab === 'history' ? '#f8fafc' : 'transparent',
                            color: activeTab === 'history' ? '#0f172a' : '#64748b',
                            borderBottom: activeTab === 'history' ? '2px solid #10b981' : '2px solid transparent'
                        }}
                    >
                        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <CheckCircle2 style={{ width: '12px', height: '12px' }} />
                            Execution Log
                            {executionHistory.length > 0 && (
                                <span style={{
                                    backgroundColor: '#10b981',
                                    color: '#fff',
                                    padding: '2px 6px',
                                    borderRadius: '10px',
                                    fontSize: '10px'
                                }}>
                                    {executionHistory.length}
                                </span>
                            )}
                        </span>
                    </button>
                </div>
            </div>

            {/* Activity Feed */}
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto"
                style={{ padding: '20px', backgroundColor: '#f8fafc' }}
            >
                {displayMessages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center">
                        <div
                            className="w-16 h-16 rounded-2xl bg-white flex items-center justify-center mb-4 border border-gray-200"
                        >
                            {activeTab === 'live' ? (
                                <Sparkles style={{ width: '28px', height: '28px', color: '#cbd5e1' }} />
                            ) : (
                                <CheckCircle2 style={{ width: '28px', height: '28px', color: '#cbd5e1' }} />
                            )}
                        </div>
                        <p style={{ fontSize: '14px', fontWeight: 500, color: '#64748b' }}>
                            {activeTab === 'live' ? 'No live activity' : 'No execution history'}
                        </p>
                        <p style={{ fontSize: '12px', color: '#94a3b8', marginTop: '4px' }}>
                            {activeTab === 'live'
                                ? 'Run agent analysis to see live updates'
                                : 'Approve decisions to see agent actions'}
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {/* Show workflow header for execution log */}
                        {activeTab === 'history' && (
                            <div className="flex items-center gap-2 mb-4 pb-2 border-b border-gray-200">
                                <div className="flex items-center gap-1 text-xs text-gray-500">
                                    <Brain style={{ width: '12px', height: '12px', color: '#8b5cf6' }} />
                                    <span>Orchestrator</span>
                                    <ArrowRight style={{ width: '10px', height: '10px' }} />
                                    <Tag style={{ width: '12px', height: '12px', color: '#f97316' }} />
                                    <span>Agent Execution</span>
                                </div>
                            </div>
                        )}
                        <AnimatePresence>
                            {displayMessages.map((msg: AgentMessage, index: number) => (
                                <ActivityMessage
                                    key={msg.id}
                                    message={msg}
                                    isLatest={index === displayMessages.length - 1}
                                />
                            ))}
                        </AnimatePresence>
                    </div>
                )}
            </div>

            {/* Active Agents Footer */}
            {activeAgents.length > 0 && (
                <div
                    className="border-t border-gray-100"
                    style={{ padding: '12px 20px' }}
                >
                    <div className="flex items-center gap-2">
                        <span style={{ fontSize: '11px', color: '#64748b' }}>Active:</span>
                        <div className="flex items-center gap-1">
                            {activeAgents.map((agent) => {
                                const config = agentConfig[agent] || agentConfig['Orchestrator'];
                                const Icon = config.icon;
                                return (
                                    <div
                                        key={agent}
                                        className="flex items-center gap-1 px-2 py-1 rounded-full"
                                        style={{ backgroundColor: config.bgColor }}
                                    >
                                        <Icon style={{ width: '12px', height: '12px', color: config.color }} />
                                        <span style={{ fontSize: '10px', fontWeight: 500, color: config.color }}>
                                            {config.name.split(' ')[0]}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
