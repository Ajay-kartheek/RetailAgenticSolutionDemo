'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    TrendingUp,
    Megaphone,
    Sparkles,
    Loader2,
    Image as ImageIcon,
    Plus,
    ArrowUpRight,
    Download,
    Package,
    Target,
    Zap
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import { generateCampaignImage } from '@/lib/api';
import { useAgentContext } from '@/context/AgentContext';
import { useDataContext } from '@/context/DataContext';
import { Product } from '@/lib/types';

// --- Types ---

interface Trend {
    store_product_id: string;
    analysis_date: string;
    trend_name: string;
    confidence_score: number;
    impact_score: number;
    affected_products: string[];
    description: string;
    action_item?: string;
}

interface CampaignSuggestion {
    campaign_id: string;
    type: string;
    reason: string;
    products: string[];
    expected_impact: string;
    suggested_action: string;
}

// --- Components ---

function TrendsView({ trends, isLoading, onRunAnalysis }: { trends: Trend[], isLoading: boolean, onRunAnalysis: () => void }) {
    if (isLoading) {
        return (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 0' }}>
                <Loader2 style={{ width: '32px', height: '32px', color: '#3b82f6' }} className="animate-spin" />
                <p style={{ color: '#64748b', marginTop: '16px', fontSize: '14px' }}>Analyzing market trends...</p>
            </div>
        );
    }

    if (trends.length === 0) {
        return (
            <div style={{
                textAlign: 'center',
                padding: '60px 40px',
                backgroundColor: '#ffffff',
                borderRadius: '16px',
                border: '2px dashed #e2e8f0'
            }}>
                <div style={{
                    width: '64px',
                    height: '64px',
                    backgroundColor: '#f1f5f9',
                    borderRadius: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 16px'
                }}>
                    <TrendingUp style={{ width: '28px', height: '28px', color: '#94a3b8' }} />
                </div>
                <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#1e293b', marginBottom: '8px' }}>No active trends detected</h3>
                <p style={{ fontSize: '14px', color: '#64748b', marginBottom: '24px', maxWidth: '360px', margin: '0 auto 24px' }}>
                    The Trend Agent hasn't identified any significant market shifts yet.
                </p>
                <button
                    onClick={onRunAnalysis}
                    style={{
                        padding: '10px 20px',
                        backgroundColor: '#3b82f6',
                        color: '#ffffff',
                        fontWeight: 600,
                        fontSize: '13px',
                        borderRadius: '10px',
                        border: 'none',
                        cursor: 'pointer'
                    }}>
                    Run Analysis Now
                </button>
            </div>
        );
    }

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '20px' }}>
            {trends.map((trend, idx) => (
                <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    style={{
                        backgroundColor: '#ffffff',
                        borderRadius: '16px',
                        border: '1px solid #e2e8f0',
                        overflow: 'hidden',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                    }}
                >
                    <div style={{ padding: '24px' }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '16px' }}>
                            <div style={{ padding: '10px', backgroundColor: '#eff6ff', borderRadius: '12px' }}>
                                <TrendingUp style={{ width: '20px', height: '20px', color: '#3b82f6' }} />
                            </div>
                            <span style={{
                                padding: '4px 10px',
                                fontSize: '11px',
                                fontWeight: 700,
                                borderRadius: '20px',
                                backgroundColor: trend.confidence_score > 0.8 ? '#dcfce7' : '#fef9c3',
                                color: trend.confidence_score > 0.8 ? '#16a34a' : '#ca8a04'
                            }}>
                                {Math.round(trend.confidence_score * 100)}% Confidence
                            </span>
                        </div>

                        <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#1e293b', marginBottom: '8px' }}>{trend.trend_name}</h3>
                        <p style={{ fontSize: '13px', color: '#64748b', lineHeight: 1.6, marginBottom: '16px' }}>{trend.description}</p>

                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                            <div style={{
                                padding: '6px 12px',
                                backgroundColor: '#f1f5f9',
                                borderRadius: '8px',
                                fontSize: '12px',
                                fontWeight: 600,
                                color: '#475569'
                            }}>
                                Impact: {trend.impact_score}
                            </div>
                            <div style={{
                                padding: '6px 12px',
                                backgroundColor: '#f1f5f9',
                                borderRadius: '8px',
                                fontSize: '12px',
                                fontWeight: 600,
                                color: '#475569'
                            }}>
                                {trend.affected_products.length} Products
                            </div>
                        </div>

                        {trend.action_item && (
                            <div style={{
                                padding: '12px',
                                backgroundColor: '#fffbeb',
                                borderRadius: '10px',
                                border: '1px solid #fef3c7',
                                fontSize: '12px',
                                color: '#92400e'
                            }}>
                                <strong>Recommended:</strong> {trend.action_item}
                            </div>
                        )}
                    </div>
                </motion.div>
            ))}
        </div>
    );
}

function CampaignsView({
    suggestions,
    isLoading,
    onCreateClick,
    onSuggestionsUpdate
}: {
    suggestions: CampaignSuggestion[],
    isLoading: boolean,
    onCreateClick: (context?: { campaignType?: string, products?: string[], title?: string }) => void,
    onSuggestionsUpdate: (suggestions: CampaignSuggestion[]) => void
}) {
    const { addMessage, updateAgentStatus } = useAgentContext();
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisMessages, setAnalysisMessages] = useState<string[]>([]);

    const handleGetRecommendations = async () => {
        setIsAnalyzing(true);
        setAnalysisMessages([]);

        updateAgentStatus('orchestrator', 'running', 'Starting campaign analysis...');
        addMessage('orchestrator', 'Received campaign analysis request...', 'thinking');

        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/campaigns/analyze/stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!response.body) throw new Error('No response body');

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                const lines = text.split('\n').filter(line => line.startsWith('data: '));

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line.replace('data: ', ''));

                        if (data.type === 'progress') {
                            const agentId = data.agent_name === 'Orchestrator' ? 'orchestrator' : 'campaign_agent';
                            updateAgentStatus(agentId, data.status || 'running', data.message);
                            addMessage(agentId, data.message, data.thinking ? 'thinking' : 'info');
                            setAnalysisMessages(prev => [...prev, data.message]);
                        }

                        if (data.type === 'complete' && data.suggestions) {
                            // Transform to match CampaignSuggestion interface
                            const transformedSuggestions = data.suggestions.map((s: any, idx: number) => ({
                                campaign_id: `AI_${Date.now()}_${idx}`,
                                type: s.campaign_type || s.type || 'promotional',
                                reason: s.description || s.reason || '',
                                products: s.target_products || [],
                                expected_impact: s.expected_impact || 'medium',
                                suggested_action: s.title || s.suggested_action || 'Run Campaign'
                            }));
                            onSuggestionsUpdate(transformedSuggestions);

                            updateAgentStatus('campaign_agent', 'completed', 'Analysis complete!');
                            addMessage('campaign_agent', `Generated ${transformedSuggestions.length} AI campaign recommendations! ✓`, 'success');

                            setTimeout(() => {
                                updateAgentStatus('orchestrator', 'idle');
                                updateAgentStatus('campaign_agent', 'idle');
                            }, 3000);
                        }

                        if (data.type === 'error') {
                            addMessage('campaign_agent', `Error: ${data.error}`, 'error');
                        }
                    } catch (e) { }
                }
            }
        } catch (error) {
            console.error('Campaign analysis error:', error);
            addMessage('orchestrator', 'Campaign analysis failed. Please try again.', 'error');
        } finally {
            setIsAnalyzing(false);
        }
    };

    if (isLoading && !isAnalyzing) {
        return (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 0' }}>
                <Loader2 style={{ width: '32px', height: '32px', color: '#a855f7' }} className="animate-spin" />
                <p style={{ color: '#64748b', marginTop: '16px', fontSize: '14px' }}>Loading...</p>
            </div>
        );
    }

    return (
        <div>
            {/* Campaign Manager Header */}
            <div style={{
                padding: '24px',
                backgroundColor: '#faf5ff',
                borderRadius: '16px',
                border: '1px solid #e9d5ff',
                marginBottom: '24px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div>
                    <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#581c87', marginBottom: '4px' }}>Campaign Manager</h2>
                    <p style={{ fontSize: '13px', color: '#7e22ce' }}>
                        AI-powered campaign recommendations with real-time agent analysis.
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button
                        onClick={handleGetRecommendations}
                        disabled={isAnalyzing}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '12px 20px',
                            backgroundColor: isAnalyzing ? '#e9d5ff' : '#ffffff',
                            color: isAnalyzing ? '#9333ea' : '#7c3aed',
                            fontWeight: 600,
                            fontSize: '13px',
                            borderRadius: '10px',
                            border: '1px solid #c4b5fd',
                            cursor: isAnalyzing ? 'wait' : 'pointer'
                        }}
                    >
                        {isAnalyzing ? (
                            <><Loader2 style={{ width: '16px', height: '16px' }} className="animate-spin" /> Analyzing...</>
                        ) : (
                            <><Sparkles style={{ width: '16px', height: '16px' }} /> Get AI Recommendations</>
                        )}
                    </button>
                    <button
                        onClick={() => onCreateClick()}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '12px 20px',
                            backgroundColor: '#9333ea',
                            color: '#ffffff',
                            fontWeight: 600,
                            fontSize: '13px',
                            borderRadius: '10px',
                            border: 'none',
                            cursor: 'pointer',
                            boxShadow: '0 4px 12px rgba(147, 51, 234, 0.3)'
                        }}
                    >
                        <Plus style={{ width: '16px', height: '16px' }} />
                        Create New Campaign
                    </button>
                </div>
            </div>

            {/* Analysis Progress */}
            {isAnalyzing && analysisMessages.length > 0 && (
                <div style={{
                    padding: '16px',
                    backgroundColor: '#f8fafc',
                    borderRadius: '12px',
                    border: '1px solid #e2e8f0',
                    marginBottom: '24px'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: 700, color: '#64748b', marginBottom: '8px' }}>ANALYSIS PROGRESS</div>
                    {analysisMessages.map((msg, i) => (
                        <div key={i} style={{ fontSize: '13px', color: '#475569', padding: '4px 0' }}>
                            → {msg}
                        </div>
                    ))}
                </div>
            )}

            {/* AI Recommendations */}
            <h3 style={{ fontSize: '11px', fontWeight: 700, color: '#94a3b8', letterSpacing: '0.5px', marginBottom: '16px' }}>AI RECOMMENDATIONS</h3>

            {suggestions.length > 0 ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '20px' }}>
                    {suggestions.map((campaign, idx) => (
                        <div key={idx} style={{
                            backgroundColor: '#ffffff',
                            padding: '24px',
                            borderRadius: '16px',
                            border: '1px solid #e2e8f0',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                                <span style={{
                                    padding: '4px 10px',
                                    backgroundColor: '#f3e8ff',
                                    color: '#7c3aed',
                                    fontSize: '11px',
                                    fontWeight: 700,
                                    borderRadius: '20px'
                                }}>
                                    {campaign.type}
                                </span>
                                <span style={{
                                    padding: '4px 10px',
                                    backgroundColor: campaign.expected_impact === 'high' ? '#dcfce7' : '#fef3c7',
                                    color: campaign.expected_impact === 'high' ? '#16a34a' : '#ca8a04',
                                    fontSize: '11px',
                                    fontWeight: 700,
                                    borderRadius: '20px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '4px'
                                }}>
                                    <ArrowUpRight style={{ width: '12px', height: '12px' }} />
                                    {campaign.expected_impact} impact
                                </span>
                            </div>

                            <h4 style={{ fontSize: '15px', fontWeight: 700, color: '#1e293b', marginBottom: '8px' }}>{campaign.suggested_action}</h4>
                            <p style={{ fontSize: '13px', color: '#64748b', lineHeight: 1.6, marginBottom: '20px' }}>{campaign.reason}</p>

                            <div style={{ display: 'flex', gap: '10px' }}>
                                <button
                                    onClick={() => onCreateClick({
                                        campaignType: campaign.type,
                                        products: campaign.products,
                                        title: campaign.suggested_action
                                    })}
                                    style={{
                                        flex: 1,
                                        padding: '10px 16px',
                                        backgroundColor: '#9333ea',
                                        border: 'none',
                                        color: '#ffffff',
                                        fontSize: '12px',
                                        fontWeight: 600,
                                        borderRadius: '10px',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '6px'
                                    }}
                                >
                                    <Sparkles style={{ width: '14px', height: '14px' }} />
                                    Generate Assets
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div style={{
                    textAlign: 'center',
                    padding: '48px',
                    border: '2px dashed #e2e8f0',
                    borderRadius: '16px'
                }}>
                    <Sparkles style={{ width: '32px', height: '32px', color: '#a855f7', margin: '0 auto 16px' }} />
                    <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#1e293b', marginBottom: '8px' }}>No recommendations yet</h3>
                    <p style={{ color: '#64748b', fontSize: '14px', marginBottom: '20px' }}>
                        Click "Get AI Recommendations" to analyze your data and generate campaign ideas.
                    </p>
                </div>
            )}
        </div>
    );
}

function CreateCampaignModal({
    isOpen,
    onClose,
    products,
    context
}: {
    isOpen: boolean,
    onClose: () => void,
    products: Product[],
    context?: {
        campaignType?: string,
        products?: string[],
        title?: string
    }
}) {
    const { addMessage, updateAgentStatus } = useAgentContext();
    const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
    const [campaignType, setCampaignType] = useState('promotional');
    const [prompt, setPrompt] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);

    // Reset and pre-fill when modal opens or context changes
    useEffect(() => {
        if (isOpen) {
            // Clear previous state
            setGeneratedImage(null);
            setIsGenerating(false);

            // Pre-fill from context if provided
            if (context?.campaignType) {
                setCampaignType(context.campaignType);
            } else {
                setCampaignType('promotional');
            }

            if (context?.products && context.products.length > 0) {
                // Try to find matching product by name/category
                const matched = products.find(p =>
                    context.products?.some(cp =>
                        (p.name || p.product_name || '').toLowerCase().includes(cp.toLowerCase()) ||
                        p.category.toLowerCase().includes(cp.toLowerCase())
                    )
                );
                if (matched) {
                    setSelectedProducts([matched.product_id]);
                } else {
                    setSelectedProducts([]);
                }
            } else {
                setSelectedProducts([]);
            }

            if (context?.title) {
                setPrompt(context.title);
            } else {
                setPrompt('');
            }
        }
    }, [isOpen, context, products]);

    const handleGenerate = async () => {
        if (selectedProducts.length === 0) return;

        setIsGenerating(true);
        setGeneratedImage(null);

        updateAgentStatus('orchestrator', 'running', 'Delegating creative task...');
        addMessage('orchestrator', 'Received request for campaign creative. Assigning to Campaign Agent...', 'thinking');

        await new Promise(r => setTimeout(r, 800));

        updateAgentStatus('orchestrator', 'idle');
        updateAgentStatus('campaign_agent', 'running', 'Generating image with Amazon Titan...');
        addMessage('campaign_agent', `Generating ${campaignType} campaign image...`, 'thinking');

        try {
            const result = await generateCampaignImage({
                product_id: selectedProducts[0],
                campaign_type: campaignType,
                promotion_text: prompt
            });

            setGeneratedImage(result.image_base64);

            updateAgentStatus('campaign_agent', 'completed', 'Image generated successfully');
            addMessage('campaign_agent', 'Campaign creative generated successfully! ✓', 'success');

            setTimeout(() => updateAgentStatus('campaign_agent', 'idle'), 3000);

        } catch (error) {
            console.error(error);
            updateAgentStatus('campaign_agent', 'idle');
            addMessage('campaign_agent', 'Failed to generate image. Please try again.', 'error');
        } finally {
            setIsGenerating(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed',
            inset: 0,
            zIndex: 50,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '16px',
            backgroundColor: 'rgba(0, 0, 0, 0.6)',
            backdropFilter: 'blur(4px)'
        }}>
            <div style={{
                backgroundColor: '#ffffff',
                borderRadius: '20px',
                width: '100%',
                maxWidth: '900px',
                maxHeight: '90vh',
                overflow: 'hidden',
                boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
                display: 'flex',
                flexDirection: 'column'
            }}>
                {/* Modal Header */}
                <div style={{
                    padding: '20px 24px',
                    borderBottom: '1px solid #e2e8f0',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    backgroundColor: '#f8fafc'
                }}>
                    <div>
                        <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#1e293b' }}>Create Campaign</h2>
                        <p style={{ fontSize: '13px', color: '#64748b' }}>Design your campaign and generate creatives</p>
                    </div>
                    <button onClick={onClose} style={{
                        padding: '8px',
                        backgroundColor: 'transparent',
                        border: 'none',
                        cursor: 'pointer',
                        borderRadius: '8px'
                    }}>
                        <svg style={{ width: '20px', height: '20px', color: '#64748b' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Modal Body */}
                <div style={{ flex: '1', overflowY: 'auto', padding: '24px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                        {/* Left: Configuration */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div>
                                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#475569', marginBottom: '8px' }}>Campaign Type</label>
                                <select
                                    value={campaignType}
                                    onChange={(e) => setCampaignType(e.target.value)}
                                    style={{
                                        width: '100%',
                                        padding: '10px 12px',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '10px',
                                        fontSize: '14px',
                                        outline: 'none'
                                    }}
                                >
                                    <option value="promotional">Promotional Sale</option>
                                    <option value="seasonal">Seasonal / Holiday</option>
                                    <option value="new_arrival">New Arrival Launch</option>
                                    <option value="clearance">Clearance Event</option>
                                </select>
                            </div>

                            <div>
                                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#475569', marginBottom: '8px' }}>Select Primary Product</label>
                                <select
                                    style={{
                                        width: '100%',
                                        padding: '10px 12px',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '10px',
                                        fontSize: '14px',
                                        outline: 'none'
                                    }}
                                    onChange={(e) => {
                                        if (e.target.value) setSelectedProducts([e.target.value]);
                                    }}
                                >
                                    <option value="">Select a product...</option>
                                    {products.map(p => (
                                        <option key={p.product_id} value={p.product_id}>
                                            {p.name || p.product_name || 'Unknown'} ({p.category})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#475569', marginBottom: '8px' }}>Creative Prompt (Optional)</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="E.g., Summer vibe, beach background, minimalistic..."
                                    style={{
                                        width: '100%',
                                        padding: '12px',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '10px',
                                        fontSize: '14px',
                                        outline: 'none',
                                        height: '100px',
                                        resize: 'none'
                                    }}
                                />
                            </div>

                            <button
                                onClick={handleGenerate}
                                disabled={isGenerating || selectedProducts.length === 0}
                                style={{
                                    width: '100%',
                                    padding: '14px',
                                    borderRadius: '12px',
                                    fontWeight: 700,
                                    color: '#ffffff',
                                    border: 'none',
                                    cursor: isGenerating || selectedProducts.length === 0 ? 'not-allowed' : 'pointer',
                                    background: isGenerating || selectedProducts.length === 0 ? '#cbd5e1' : 'linear-gradient(135deg, #9333ea 0%, #6366f1 100%)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px'
                                }}
                            >
                                {isGenerating ? (
                                    <>
                                        <Loader2 style={{ width: '18px', height: '18px' }} className="animate-spin" /> Generating...
                                    </>
                                ) : (
                                    <>
                                        <Sparkles style={{ width: '18px', height: '18px' }} /> Generate Creative
                                    </>
                                )}
                            </button>
                        </div>

                        {/* Right: Preview */}
                        <div style={{
                            backgroundColor: '#f1f5f9',
                            borderRadius: '16px',
                            border: '1px solid #e2e8f0',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            minHeight: '360px',
                            position: 'relative',
                            overflow: 'hidden'
                        }}>
                            {generatedImage ? (
                                <>
                                    <img
                                        src={`data:image/jpeg;base64,${generatedImage}`}
                                        alt="Generated Campaign"
                                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                                    />
                                    <div style={{
                                        position: 'absolute',
                                        bottom: '16px',
                                        right: '16px',
                                        display: 'flex',
                                        gap: '8px'
                                    }}>
                                        <button
                                            onClick={() => {
                                                const link = document.createElement('a');
                                                link.href = `data:image/png;base64,${generatedImage}`;
                                                link.download = `campaign_${campaignType}_${Date.now()}.png`;
                                                link.click();
                                            }}
                                            style={{
                                                padding: '10px 16px',
                                                backgroundColor: '#ffffff',
                                                border: 'none',
                                                borderRadius: '10px',
                                                fontWeight: 600,
                                                fontSize: '12px',
                                                color: '#1e293b',
                                                cursor: 'pointer',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                                boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                                            }}
                                        >
                                            <Download style={{ width: '14px', height: '14px' }} />
                                            Download
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <div style={{ textAlign: 'center', padding: '32px' }}>
                                    <div style={{
                                        width: '64px',
                                        height: '64px',
                                        backgroundColor: '#ffffff',
                                        borderRadius: '50%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        margin: '0 auto 16px',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.08)'
                                    }}>
                                        <ImageIcon style={{ width: '28px', height: '28px', color: '#94a3b8' }} />
                                    </div>
                                    <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#1e293b', marginBottom: '4px' }}>No Creative Generated</h3>
                                    <p style={{ fontSize: '13px', color: '#64748b', maxWidth: '200px', margin: '0 auto' }}>
                                        Select a product and campaign type to generate assets.
                                    </p>
                                    <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px', fontSize: '11px', color: '#94a3b8' }}>
                                        <Sparkles style={{ width: '12px', height: '12px' }} /> Powered by Amazon Titan
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function TrendsPage() {
    const { startAnalysis } = useAgentContext();
    const [activeTab, setActiveTab] = useState<'trends' | 'campaigns'>('campaigns');

    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalContext, setModalContext] = useState<{
        campaignType?: string,
        products?: string[],
        title?: string
    } | undefined>(undefined);

    const {
        trends: cachedTrends,
        campaignSuggestions: cachedCampaigns,
        products: cachedProducts,
        fetchTrends,
        fetchCampaignSuggestions,
        fetchProducts
    } = useDataContext() as any;

    const [trends, setTrends] = useState<Trend[]>(cachedTrends || []);
    const [campaignSuggestions, setCampaignSuggestions] = useState<CampaignSuggestion[]>(cachedCampaigns || []);
    const [products, setProducts] = useState<Product[]>(cachedProducts || []);

    // Only show loading if we don't have cached data for the main views
    const hasCache = cachedTrends?.length > 0 || cachedCampaigns?.length > 0;
    const [isLoading, setIsLoading] = useState(!hasCache);

    useEffect(() => {
        // If we have cache, ensuring loading is false immediately
        if (hasCache) {
            setIsLoading(false);
            setTrends(cachedTrends || []);
            setCampaignSuggestions(cachedCampaigns || []);
            setProducts(cachedProducts || []);
        }

        const loadData = async () => {
            // Only set loading true if we really have no data
            if (!hasCache) setIsLoading(true);
            try {
                const [trendsData, campaignsData, productsData] = await Promise.all([
                    fetchTrends(),
                    fetchCampaignSuggestions(),
                    fetchProducts()
                ]);
                setTrends(trendsData || []);
                setCampaignSuggestions(campaignsData || []);
                setProducts(productsData || []);
            } catch (error) {
                console.error("Failed to load page data:", error);
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, [fetchTrends, fetchCampaignSuggestions, fetchProducts, hasCache, cachedTrends, cachedCampaigns, cachedProducts]);

    return (
        <div className="flex h-screen w-full bg-gray-100 font-sans overflow-hidden">
            <Sidebar />

            <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
                {/* Header */}
                <header style={{ height: '64px', padding: '0 32px' }} className="bg-white border-b border-gray-200 flex items-center justify-between shrink-0">
                    <div>
                        <h1 style={{ fontSize: '18px', fontWeight: 600 }} className="text-gray-900">Trends & Campaigns</h1>
                        <p style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
                            Market insights and AI-powered marketing
                        </p>
                    </div>

                    {/* Tabs */}
                    <div style={{ display: 'flex', gap: '4px', padding: '4px', borderRadius: '10px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
                        {[
                            { key: 'campaigns', label: 'Campaigns', icon: Megaphone },
                            { key: 'trends', label: 'Market Trends', icon: TrendingUp }
                        ].map((tab) => (
                            <button
                                key={tab.key}
                                onClick={() => setActiveTab(tab.key as 'trends' | 'campaigns')}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px',
                                    padding: '8px 16px',
                                    fontSize: '12px',
                                    fontWeight: 600,
                                    borderRadius: '8px',
                                    backgroundColor: activeTab === tab.key ? '#0f172a' : 'transparent',
                                    color: activeTab === tab.key ? '#ffffff' : '#64748b',
                                    border: 'none',
                                    cursor: 'pointer',
                                    transition: 'all 0.15s ease'
                                }}
                            >
                                <tab.icon style={{ width: '14px', height: '14px' }} />
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </header>

                {/* Content */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
                    <AnimatePresence mode="wait">
                        {activeTab === 'trends' ? (
                            <motion.div
                                key="trends"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.2 }}
                            >
                                <TrendsView trends={trends} isLoading={isLoading} onRunAnalysis={startAnalysis} />
                            </motion.div>
                        ) : (
                            <motion.div
                                key="campaigns"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                                transition={{ duration: 0.2 }}
                            >
                                <CampaignsView
                                    suggestions={campaignSuggestions}
                                    isLoading={isLoading}
                                    onCreateClick={(ctx) => {
                                        setModalContext(ctx);
                                        setIsModalOpen(true);
                                    }}
                                    onSuggestionsUpdate={setCampaignSuggestions}
                                />
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                <CreateCampaignModal
                    isOpen={isModalOpen}
                    onClose={() => {
                        setIsModalOpen(false);
                        setModalContext(undefined);
                    }}
                    products={products}
                    context={modalContext}
                />
            </main>
        </div>
    );
}
