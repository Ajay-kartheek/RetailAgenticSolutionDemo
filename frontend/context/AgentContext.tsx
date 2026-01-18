'use client';

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { runOrchestrator, createSSEConnection } from '@/lib/api';
import type { SSEEvent, AgentStatus } from '@/lib/types';

interface AgentState {
    id: string;
    status: AgentStatus;
    message?: string;
}

interface ActivityMessage {
    id: string;
    agentId: string; // e.g., 'Orchestrator', 'Demand Agent'
    message: string;
    timestamp: Date;
    type: 'info' | 'success' | 'warning' | 'error' | 'thinking';
}

interface AgentContextType {
    isRunning: boolean;
    isExecuting: boolean;
    agentStatuses: Record<string, AgentState>;
    activityMessages: ActivityMessage[];
    startAnalysis: () => Promise<void>;
    stopAnalysis: () => void;
    triggerExecution: (agentType: 'pricing' | 'replenishment', details: { productName?: string; action?: string }) => Promise<void>;
    addMessage: (agentId: string, message: string, type: ActivityMessage['type']) => void;
    updateAgentStatus: (agentId: string, status: AgentStatus, message?: string) => void;
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export const AgentProvider = ({ children }: { children: ReactNode }) => {
    const [isRunning, setIsRunning] = useState(false);
    const [isExecuting, setIsExecuting] = useState(false);
    const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentState>>({
        orchestrator: { id: 'orchestrator', status: 'idle' },
        demand_agent: { id: 'demand_agent', status: 'idle' },
        trend_agent: { id: 'trend_agent', status: 'idle' },
        inventory_agent: { id: 'inventory_agent', status: 'idle' },
        replenishment_agent: { id: 'replenishment_agent', status: 'idle' },
        pricing_agent: { id: 'pricing_agent', status: 'idle' },
        campaign_agent: { id: 'campaign_agent', status: 'idle' },
    });

    const [activityMessages, setActivityMessages] = useState<ActivityMessage[]>([]);
    const [abortController, setAbortController] = useState<(() => void) | null>(null);

    const addMessage = useCallback((agentId: string, message: string, type: ActivityMessage['type'] = 'info') => {
        setActivityMessages(prev => [
            {
                id: Math.random().toString(36).substring(7),
                agentId,
                message,
                timestamp: new Date(),
                type
            },
            ...prev
        ].slice(0, 50)); // Keep last 50 messages
    }, []);

    const updateAgentStatus = useCallback((agentId: string, status: AgentStatus, message?: string) => {
        setAgentStatuses(prev => ({
            ...prev,
            [agentId]: {
                ...prev[agentId],
                id: agentId,
                status,
                message
            }
        }));
    }, []);

    // Handle incoming SSE events
    const handleSSEEvent = useCallback((event: SSEEvent) => {
        const { type, agent_name, status, message, thinking } = event;

        // Handle completion
        if (type === 'complete') {
            setIsRunning(false);
            addMessage('System', 'Analysis completed successfully', 'success');
            updateAgentStatus('orchestrator', 'completed', 'Orchestration complete');
            return;
        }

        // Handle errors
        if (type === 'error') {
            setIsRunning(false);
            const errorMessage = event.error || 'Unknown error occurred';
            addMessage('System', `Analysis failed: ${errorMessage}`, 'error');
            updateAgentStatus('orchestrator', 'error', errorMessage);
            return;
        }

        if (type === 'heartbeat' || type === 'start') return;

        const safeAgentName = agent_name || 'System';

        // Map agent name to ID (lowercase, underscores)
        const agentId = safeAgentName.toLowerCase().replace(/ /g, '_');

        // Update status
        if (status === 'running' || status === 'completed' || status === 'error') {
            updateAgentStatus(agentId, status, message);
        }

        // Add activity log
        if (thinking) {
            addMessage(safeAgentName, thinking, 'thinking');
        } else if (message) {
            const msgType = status === 'error' ? 'error' : status === 'completed' ? 'success' : 'info';
            addMessage(safeAgentName, message, msgType);
        }
    }, [addMessage, updateAgentStatus]);

    const startAnalysis = async () => {
        if (isRunning) return;

        setIsRunning(true);
        setActivityMessages([]); // Clear previous logs

        // Reset statuses
        setAgentStatuses(prev => {
            const reset = { ...prev };
            Object.keys(reset).forEach(key => {
                reset[key] = { ...reset[key], status: 'idle', message: undefined };
            });
            return reset;
        });

        addMessage('System', 'Initializing agent orchestration...', 'info');

        // Start SSE connection
        try {
            const stopSSE = await createSSEConnection(
                { forecast_period: '2026-Q1' },
                handleSSEEvent,
                (error) => {
                    console.error('SSE Error:', error);
                    addMessage('System', `Connection error: ${error.message}`, 'error');
                    setIsRunning(false);
                }
            );

            setAbortController(() => stopSSE);

        } catch (error) {
            console.error('Failed to start analysis:', error);
            addMessage('System', 'Failed to start analysis', 'error');
            setIsRunning(false);
        }
    };

    const stopAnalysis = useCallback(() => {
        if (abortController) {
            abortController();
            setAbortController(null);
        }
        setIsRunning(false);
        addMessage('System', 'Analysis stopped by user', 'warning');
    }, [abortController, addMessage]);

    // Trigger execution animation when a decision is approved
    const triggerExecution = useCallback(async (
        agentType: 'pricing' | 'replenishment',
        details: { productName?: string; action?: string }
    ) => {
        setIsExecuting(true);

        const agentId = agentType === 'pricing' ? 'pricing_agent' : 'replenishment_agent';
        const agentDisplayName = agentType === 'pricing' ? 'Pricing Agent' : 'Replenishment Agent';

        // Show orchestrator receiving the decision
        updateAgentStatus('orchestrator', 'running', 'Processing approved decision...');
        addMessage('orchestrator', `Received approved decision. Delegating to ${agentDisplayName}...`, 'thinking');

        // Simulate orchestrator thinking
        await new Promise(resolve => setTimeout(resolve, 800));

        // Activate the specialist agent
        updateAgentStatus('orchestrator', 'idle');
        updateAgentStatus(agentId, 'running', 'Executing decision...');

        if (agentType === 'pricing') {
            addMessage(agentId, `Updating price for ${details.productName || 'product'}...`, 'thinking');
        } else {
            addMessage(agentId, `Processing stock transfer for ${details.productName || 'product'}...`, 'thinking');
        }

        // Simulate agent execution
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Complete
        updateAgentStatus(agentId, 'completed', 'Execution complete');
        addMessage(agentId, `${details.action || 'Decision executed'} successfully! ✓`, 'success');

        // Reset after a moment
        await new Promise(resolve => setTimeout(resolve, 1000));
        updateAgentStatus(agentId, 'idle');
        setIsExecuting(false);
    }, [addMessage, updateAgentStatus]);

    return (
        <AgentContext.Provider value={{
            isRunning,
            isExecuting,
            agentStatuses,
            activityMessages,
            startAnalysis,
            stopAnalysis,
            triggerExecution,
            addMessage,
            updateAgentStatus
        }}>
            {children}
        </AgentContext.Provider>
    );
};

export const useAgentContext = () => {
    const context = useContext(AgentContext);
    if (context === undefined) {
        throw new Error('useAgentContext must be used within an AgentProvider');
    }
    return context;
};
