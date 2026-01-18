'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Activity,
    Brain,
    TrendingUp,
    BarChart3,
    Package,
    Truck,
    Tag,
    Palette,
    ArrowRight,
    Wrench,
    MessageSquare,
} from 'lucide-react';
import { createSSEConnection } from '@/lib/api';
import type { SSEEvent } from '@/lib/types';
import type { AgentData, AgentStatusType } from './AgentCardPanel';

interface Message {
    id: string;
    agentId: string;
    agentName: string;
    type: 'thinking' | 'communication' | 'tool_call' | 'result' | 'error';
    content: string;
    timestamp: Date;
}

interface LiveActivityPanelProps {
    isActive: boolean;
    onComplete?: (result: any) => void;
    onError?: (error: Error) => void;
    onAgentUpdate?: (agentId: string, status: AgentStatusType, thinking?: string, message?: string) => void;
}

const agentIcons: Record<string, React.ComponentType<{ className?: string }>> = {
    orchestrator: Brain,
    Orchestrator: Brain,
    demand_agent: TrendingUp,
    demand: TrendingUp,
    trend_agent: BarChart3,
    trend: BarChart3,
    inventory_agent: Package,
    inventory: Package,
    replenishment_agent: Truck,
    replenishment: Truck,
    pricing_agent: Tag,
    pricing: Tag,
    campaign_agent: Palette,
    campaign: Palette,
};

const agentColors: Record<string, string> = {
    orchestrator: 'border-l-purple-500 bg-purple-50',
    Orchestrator: 'border-l-purple-500 bg-purple-50',
    demand_agent: 'border-l-blue-500 bg-blue-50',
    demand: 'border-l-blue-500 bg-blue-50',
    trend_agent: 'border-l-indigo-500 bg-indigo-50',
    trend: 'border-l-indigo-500 bg-indigo-50',
    inventory_agent: 'border-l-amber-500 bg-amber-50',
    inventory: 'border-l-amber-500 bg-amber-50',
    replenishment_agent: 'border-l-green-500 bg-green-50',
    replenishment: 'border-l-green-500 bg-green-50',
    pricing_agent: 'border-l-orange-500 bg-orange-50',
    pricing: 'border-l-orange-500 bg-orange-50',
    campaign_agent: 'border-l-pink-500 bg-pink-50',
    campaign: 'border-l-pink-500 bg-pink-50',
};

function formatTime(date: Date): string {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
    });
}

function getAgentDisplayName(agentName: string): string {
    const names: Record<string, string> = {
        orchestrator: 'Orchestrator',
        Orchestrator: 'Orchestrator',
        demand_agent: 'Demand Agent',
        demand: 'Demand Agent',
        trend_agent: 'Trend Agent',
        trend: 'Trend Agent',
        inventory_agent: 'Inventory Agent',
        inventory: 'Inventory Agent',
        replenishment_agent: 'Replenishment Agent',
        replenishment: 'Replenishment Agent',
        pricing_agent: 'Pricing Agent',
        pricing: 'Pricing Agent',
        campaign_agent: 'Campaign Agent',
        campaign: 'Campaign Agent',
    };
    return names[agentName] || agentName;
}

function getAgentId(agentName: string): string {
    const ids: Record<string, string> = {
        orchestrator: 'orchestrator',
        Orchestrator: 'orchestrator',
        demand_agent: 'demand',
        demand: 'demand',
        trend_agent: 'trend',
        trend: 'trend',
        inventory_agent: 'inventory',
        inventory: 'inventory',
        replenishment_agent: 'replenishment',
        replenishment: 'replenishment',
        pricing_agent: 'pricing',
        pricing: 'pricing',
        campaign_agent: 'campaign',
        campaign: 'campaign',
    };
    return ids[agentName] || agentName;
}

function MessageIcon({ type }: { type: Message['type'] }) {
    switch (type) {
        case 'thinking':
            return <Brain className="w-3.5 h-3.5" />;
        case 'communication':
            return <ArrowRight className="w-3.5 h-3.5" />;
        case 'tool_call':
            return <Wrench className="w-3.5 h-3.5" />;
        case 'result':
            return <MessageSquare className="w-3.5 h-3.5" />;
        default:
            return <Activity className="w-3.5 h-3.5" />;
    }
}

function ActivityMessage({ message }: { message: Message }) {
    const Icon = agentIcons[message.agentId] || Brain;
    const colorClass = agentColors[message.agentId] || 'border-l-gray-500 bg-gray-50';

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`border-l-4 rounded-r-lg p-3 ${colorClass}`}
        >
            <div className="flex items-start gap-3">
                <div className="shrink-0 mt-0.5">
                    <Icon className="w-4 h-4 text-gray-600" />
                </div>
                <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm text-gray-900">
                            {getAgentDisplayName(message.agentName)}
                        </span>
                        <span className="text-xs text-gray-400 font-mono">
                            {formatTime(message.timestamp)}
                        </span>
                    </div>
                    <div className="flex items-start gap-1.5">
                        <MessageIcon type={message.type} />
                        <p className="text-sm text-gray-700">{message.content}</p>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}

export default function LiveActivityPanel({
    isActive,
    onComplete,
    onError,
    onAgentUpdate,
}: LiveActivityPanelProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const cleanupRef = useRef<(() => void) | null>(null);
    const hasStartedRef = useRef(false);

    useEffect(() => {
        if (isActive && !hasStartedRef.current) {
            hasStartedRef.current = true;
            setIsConnected(true);
            setMessages([]);

            createSSEConnection(
                { include_campaigns: false },
                (event: SSEEvent) => {
                    handleSSEEvent(event);
                },
                (error: Error) => {
                    console.error('SSE Error:', error);
                    setIsConnected(false);
                    hasStartedRef.current = false;
                    onError?.(error);
                }
            ).then((cleanup) => {
                cleanupRef.current = cleanup;
            });

            return () => {
                if (cleanupRef.current) {
                    cleanupRef.current();
                }
                setIsConnected(false);
                hasStartedRef.current = false;
            };
        } else if (!isActive && hasStartedRef.current) {
            hasStartedRef.current = false;
        }
    }, [isActive]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSSEEvent = (event: SSEEvent) => {
        switch (event.type) {
            case 'start':
                addMessage('orchestrator', 'Orchestrator', 'communication', `Analysis started - Run ID: ${event.run_id}`);
                onAgentUpdate?.('orchestrator', 'processing', 'Initializing analysis workflow');
                break;

            case 'progress':
                const agentName = (event as any).agent_name || 'orchestrator';
                const agentId = getAgentId(agentName);
                const thinking = (event as any).thinking;
                const message = (event as any).message || 'Processing...';
                const communication = (event as any).communication;

                // Determine message type
                let messageType: Message['type'] = 'result';
                let content = message;

                if (thinking) {
                    messageType = 'thinking';
                    content = thinking;
                } else if (communication) {
                    messageType = 'communication';
                    content = communication;
                }

                addMessage(agentId, agentName, messageType, content);

                // Update agent status
                const status = (event as any).status || 'processing';
                if (status === 'completed') {
                    onAgentUpdate?.(agentId, 'completed', undefined, content);
                } else if (status === 'running') {
                    onAgentUpdate?.(agentId, 'processing', thinking, message);
                }
                break;

            case 'complete':
                addMessage('orchestrator', 'Orchestrator', 'result', 'Analysis completed successfully');
                setIsConnected(false);
                hasStartedRef.current = false;
                onAgentUpdate?.('orchestrator', 'completed', undefined, 'Workflow completed');
                onComplete?.(event.result);
                break;

            case 'error':
                addMessage('orchestrator', 'Orchestrator', 'error', `Error: ${event.error}`);
                setIsConnected(false);
                hasStartedRef.current = false;
                onAgentUpdate?.('orchestrator', 'error');
                break;

            case 'heartbeat':
                // Ignore heartbeats
                break;
        }
    };

    const addMessage = (
        agentId: string,
        agentName: string,
        type: Message['type'],
        content: string
    ) => {
        const newMessage: Message = {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            agentId,
            agentName,
            type,
            content,
            timestamp: new Date(),
        };
        setMessages(prev => [...prev, newMessage]);
    };

    return (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm h-full flex flex-col">
            {/* Header */}
            <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-gray-700" />
                    <h3 className="text-sm font-bold text-gray-900">Live Activity</h3>
                </div>
                {isConnected && (
                    <div className="flex items-center gap-1.5">
                        <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                        <span className="text-xs font-semibold text-red-600 uppercase tracking-wide">Live</span>
                    </div>
                )}
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0">
                {messages.length === 0 ? (
                    <div className="h-full flex items-center justify-center">
                        <div className="text-center py-12">
                            <Activity className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                            <p className="text-sm text-gray-500">No activity yet</p>
                            <p className="text-xs text-gray-400 mt-1">Start an analysis to see agent activity</p>
                        </div>
                    </div>
                ) : (
                    <AnimatePresence mode="popLayout">
                        {messages.map((message) => (
                            <ActivityMessage key={message.id} message={message} />
                        ))}
                    </AnimatePresence>
                )}
                <div ref={messagesEndRef} />
            </div>
        </div>
    );
}
