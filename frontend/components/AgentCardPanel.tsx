'use client';

import { motion } from 'framer-motion';
import {
    Brain,
    TrendingUp,
    BarChart3,
    Package,
    Truck,
    Tag,
    Palette,
    CheckCircle2,
    AlertCircle,
    ChevronRight,
} from 'lucide-react';

export type AgentStatusType = 'idle' | 'processing' | 'active' | 'completed' | 'error';

export interface AgentData {
    id: string;
    name: string;
    description: string;
    status: AgentStatusType;
    lastMessage?: string;
    thinking?: string;
}

interface AgentCardPanelProps {
    agents: AgentData[];
    selectedAgentId?: string;
    onSelectAgent?: (agentId: string) => void;
}

const agentIcons: Record<string, React.ComponentType<{ className?: string }>> = {
    orchestrator: Brain,
    demand: TrendingUp,
    trend: BarChart3,
    inventory: Package,
    replenishment: Truck,
    pricing: Tag,
    campaign: Palette,
};

const agentColors: Record<string, { bg: string; border: string; text: string }> = {
    orchestrator: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-600' },
    demand: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-600' },
    trend: { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-600' },
    inventory: { bg: 'bg-amber-50', border: 'border-amber-200', text: 'text-amber-600' },
    replenishment: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-600' },
    pricing: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-600' },
    campaign: { bg: 'bg-pink-50', border: 'border-pink-200', text: 'text-pink-600' },
};

function StatusBadge({ status }: { status: AgentStatusType }) {
    const config = {
        idle: { label: 'Idle', dotClass: 'bg-gray-400', textClass: 'text-gray-600' },
        processing: { label: 'Processing', dotClass: 'bg-blue-500 animate-pulse', textClass: 'text-blue-600' },
        active: { label: 'Active', dotClass: 'bg-green-500', textClass: 'text-green-600' },
        completed: { label: 'Completed', dotClass: 'bg-green-500', textClass: 'text-green-600' },
        error: { label: 'Error', dotClass: 'bg-red-500', textClass: 'text-red-600' },
    };

    const { label, dotClass, textClass } = config[status];

    return (
        <div className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${dotClass}`} />
            <span className={`text-xs font-medium ${textClass}`}>{label}</span>
        </div>
    );
}

function ThinkingIndicator() {
    return (
        <div className="flex items-center gap-1 text-blue-600">
            <div className="flex gap-0.5">
                <motion.div
                    className="w-1.5 h-1.5 bg-blue-500 rounded-full"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                    className="w-1.5 h-1.5 bg-blue-500 rounded-full"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                />
                <motion.div
                    className="w-1.5 h-1.5 bg-blue-500 rounded-full"
                    animate={{ opacity: [0.3, 1, 0.3] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                />
            </div>
        </div>
    );
}

function AgentCard({
    agent,
    isSelected,
    onClick
}: {
    agent: AgentData;
    isSelected: boolean;
    onClick: () => void;
}) {
    const Icon = agentIcons[agent.id] || Brain;
    const colors = agentColors[agent.id] || agentColors.orchestrator;
    const isProcessing = agent.status === 'processing';
    const isActive = agent.status === 'active';

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.99 }}
            onClick={onClick}
            className={`
        relative bg-white rounded-xl border-2 p-4 cursor-pointer transition-all duration-300
        ${isSelected ? 'border-blue-500 shadow-lg shadow-blue-500/10' : 'border-gray-100 hover:border-gray-200'}
        ${isProcessing ? 'agent-thinking' : ''}
        ${isActive ? 'agent-active' : ''}
      `}
        >
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg ${colors.bg} ${colors.border} border flex items-center justify-center`}>
                        {isProcessing ? (
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                            >
                                <Icon className={`w-5 h-5 ${colors.text}`} />
                            </motion.div>
                        ) : agent.status === 'completed' ? (
                            <CheckCircle2 className="w-5 h-5 text-green-600" />
                        ) : agent.status === 'error' ? (
                            <AlertCircle className="w-5 h-5 text-red-600" />
                        ) : (
                            <Icon className={`w-5 h-5 ${colors.text}`} />
                        )}
                    </div>
                    <div>
                        <h3 className="font-semibold text-gray-900 text-sm">{agent.name}</h3>
                        <StatusBadge status={agent.status} />
                    </div>
                </div>
                <ChevronRight className={`w-4 h-4 text-gray-400 transition-transform ${isSelected ? 'rotate-90' : ''}`} />
            </div>

            {/* Description */}
            <p className="text-xs text-gray-500 mb-2 line-clamp-2">{agent.description}</p>

            {/* Thinking/Message */}
            {isProcessing && agent.thinking && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-3 pt-3 border-t border-gray-100"
                >
                    <div className="flex items-center gap-2 mb-1">
                        <ThinkingIndicator />
                        <span className="text-xs font-medium text-blue-600">Thinking</span>
                    </div>
                    <p className="text-xs text-gray-600 italic line-clamp-2">{agent.thinking}</p>
                </motion.div>
            )}

            {/* Last Message for completed */}
            {agent.status === 'completed' && agent.lastMessage && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-3 pt-3 border-t border-gray-100"
                >
                    <p className="text-xs text-gray-600 line-clamp-2">{agent.lastMessage}</p>
                </motion.div>
            )}
        </motion.div>
    );
}

export default function AgentCardPanel({
    agents,
    selectedAgentId,
    onSelectAgent
}: AgentCardPanelProps) {
    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900">AI Agents</h2>
                <div className="text-xs text-gray-500">
                    {agents.filter(a => a.status === 'processing' || a.status === 'active').length} active
                </div>
            </div>

            <div className="space-y-2">
                {agents.map((agent, index) => (
                    <motion.div
                        key={agent.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                    >
                        <AgentCard
                            agent={agent}
                            isSelected={selectedAgentId === agent.id}
                            onClick={() => onSelectAgent?.(agent.id)}
                        />
                    </motion.div>
                ))}
            </div>
        </div>
    );
}

// Default agents configuration
export const defaultAgents: AgentData[] = [
    {
        id: 'orchestrator',
        name: 'Orchestrator',
        description: 'Coordinates all agents and manages the analysis workflow',
        status: 'idle',
    },
    {
        id: 'demand',
        name: 'Demand Forecasting',
        description: 'Analyzes ML demand predictions for all stores and products',
        status: 'idle',
    },
    {
        id: 'trend',
        name: 'Trend Watcher',
        description: 'Compares actual sales vs forecasts to identify trending products',
        status: 'idle',
    },
    {
        id: 'inventory',
        name: 'Inventory Optimizer',
        description: 'Categorizes stock levels and identifies critical items',
        status: 'idle',
    },
    {
        id: 'replenishment',
        name: 'Store Replenishment',
        description: 'Creates optimal transfer and manufacturer order plans',
        status: 'idle',
    },
    {
        id: 'pricing',
        name: 'Pricing & Promotion',
        description: 'Generates dynamic pricing and promotion recommendations',
        status: 'idle',
    },
    {
        id: 'campaign',
        name: 'Brand Campaign',
        description: 'Creates marketing campaigns with AI-generated content',
        status: 'idle',
    },
];
