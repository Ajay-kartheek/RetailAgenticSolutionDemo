'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    TrendingUp,
    Megaphone,
    Calendar,
    ArrowRight,
    Sparkles,
    Loader2,
    Image as ImageIcon,
    BarChart3,
    Tag,
    ShoppingBag,
    Plus
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import { getTrends, getCampaignSuggestions, generateCampaignImage, getProducts } from '@/lib/api';
import { useAgentContext } from '@/context/AgentContext';
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

function TrendsView({ trends, isLoading }: { trends: Trend[], isLoading: boolean }) {
    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
                <p className="text-slate-500">Analyzing market trends...</p>
            </div>
        );
    }

    if (trends.length === 0) {
        return (
            <div className="text-center py-20 bg-white rounded-xl border border-dashed border-slate-300">
                <TrendingUp className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-900">No active trends detected</h3>
                <p className="text-slate-500 mt-2">The Trend Agent hasn't identified any significant market shifts yet.</p>
                <button className="mt-6 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors">
                    Run Analysis Now
                </button>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {trends.map((trend, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden hover:shadow-md transition-shadow"
                    >
                        <div className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="p-2 bg-blue-50 rounded-lg">
                                    <TrendingUp className="w-5 h-5 text-blue-600" />
                                </div>
                                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${trend.confidence_score > 0.8 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                                    }`}>
                                    {Math.round(trend.confidence_score * 100)}% Confidence
                                </span>
                            </div>

                            <h3 className="text-lg font-bold text-slate-900 mb-2">{trend.trend_name}</h3>
                            <p className="text-sm text-slate-600 mb-4 line-clamp-3">{trend.description}</p>

                            <div className="flex items-center gap-2 mb-4">
                                <div className="flex -space-x-2">
                                    {trend.affected_products.slice(0, 3).map((prod, i) => (
                                        <div key={i} className="w-6 h-6 rounded-full bg-slate-200 border-2 border-white flex items-center justify-center text-[10px] font-bold text-slate-600">
                                            {prod.substring(0, 1)}
                                        </div>
                                    ))}
                                </div>
                                <span className="text-xs text-slate-500">
                                    Affects {trend.affected_products.length} products
                                </span>
                            </div>

                            {trend.action_item && (
                                <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-100 text-xs text-slate-700">
                                    <strong>Recommended:</strong> {trend.action_item}
                                </div>
                            )}
                        </div>
                        <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-between items-center">
                            <span className="text-xs font-mono text-slate-400">IMPACT SCORE: {trend.impact_score}</span>
                            <button className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1">
                                View Details <ArrowRight className="w-3 h-3" />
                            </button>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}

function CampaignsView({
    suggestions,
    isLoading,
    onCreateClick
}: {
    suggestions: CampaignSuggestion[],
    isLoading: boolean,
    onCreateClick: () => void
}) {
    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-8 h-8 text-purple-500 animate-spin mb-4" />
                <p className="text-slate-500">Identifying campaign opportunities...</p>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            <div className="flex justify-between items-center bg-purple-50 p-6 rounded-2xl border border-purple-100">
                <div>
                    <h2 className="text-xl font-bold text-purple-900 mb-2">Campaign Manager</h2>
                    <p className="text-purple-700 text-sm max-w-xl">
                        Launch AI-driven marketing campaigns. Generate professional creatives instantly with Amazon Titan Image Generator.
                    </p>
                </div>
                <button
                    onClick={onCreateClick}
                    className="flex items-center gap-2 px-5 py-3 bg-purple-600 text-white rounded-xl font-semibold shadow-lg shadow-purple-200 hover:bg-purple-700 transition-all hover:scale-105 active:scale-95"
                >
                    <Plus className="w-5 h-5" />
                    Create New Campaign
                </button>
            </div>

            <div>
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 px-1">AI Recommendations</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {suggestions.length > 0 ? suggestions.map((campaign, idx) => (
                        <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <Megaphone className="w-24 h-24 text-purple-600 transform rotate-12" />
                            </div>

                            <div className="relative z-10">
                                <div className="flex items-center gap-3 mb-3">
                                    <span className="px-3 py-1 bg-purple-100 text-purple-700 text-xs font-bold rounded-full uppercase">
                                        {campaign.type}
                                    </span>
                                    <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full flex items-center gap-1">
                                        <TrendingUp className="w-3 h-3" /> {campaign.expected_impact}
                                    </span>
                                </div>

                                <h4 className="text-lg font-bold text-slate-900 mb-2">{campaign.suggested_action}</h4>
                                <p className="text-sm text-slate-600 mb-6">{campaign.reason}</p>

                                <div className="flex items-center gap-3">
                                    <button
                                        onClick={onCreateClick}
                                        className="flex-1 py-2 px-4 bg-white border border-slate-300 text-slate-700 text-sm font-semibold rounded-lg hover:bg-slate-50 transition-colors"
                                    >
                                        Edit Details
                                    </button>
                                    <button
                                        onClick={onCreateClick}
                                        className="flex-1 py-2 px-4 bg-purple-600 text-white text-sm font-semibold rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
                                    >
                                        <Sparkles className="w-4 h-4" />
                                        Generate Assets
                                    </button>
                                </div>
                            </div>
                        </div>
                    )) : (
                        <div className="col-span-2 text-center py-12 border border-dashed border-slate-300 rounded-xl">
                            <p className="text-slate-500">No specific campaign recommendations at this time.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function CreateCampaignModal({
    isOpen,
    onClose,
    products
}: {
    isOpen: boolean,
    onClose: () => void,
    products: Product[]
}) {
    const { addMessage, updateAgentStatus } = useAgentContext();
    const [step, setStep] = useState(1);
    const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
    const [campaignType, setCampaignType] = useState('promotional');
    const [prompt, setPrompt] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);

    const handleGenerate = async () => {
        if (selectedProducts.length === 0) return;

        setIsGenerating(true);
        // Clean previous image
        setGeneratedImage(null);

        // 1. Notify Orchestrator
        updateAgentStatus('orchestrator', 'running', 'Delegating creative task...');
        addMessage('orchestrator', 'Received request for campaign creative. Assigning to Campaign Agent...', 'thinking');

        await new Promise(r => setTimeout(r, 800));

        // 2. Campaign Agent "Thinking"
        updateAgentStatus('orchestrator', 'idle');
        updateAgentStatus('campaign_agent', 'running', 'Generating image with Amazon Titan...');
        addMessage('campaign_agent', `Generating ${campaignType} campaign image for ${selectedProducts.length} products...`, 'thinking');

        try {
            // 3. Call API
            const result = await generateCampaignImage({
                product_id: selectedProducts[0], // Use first product for demo
                campaign_type: campaignType,
                promotion_text: prompt
            });

            setGeneratedImage(result.image_base64);

            // 4. Success Message
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
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden shadow-2xl flex flex-col">
                <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                    <div>
                        <h2 className="text-xl font-bold text-slate-900">Create Campaign</h2>
                        <p className="text-sm text-slate-500">Design your campaign and generate creatives</p>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full transition-colors">
                        <span className="sr-only">Close</span>
                        <svg className="w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-6">
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
                        {/* Left: Configuration */}
                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Campaign Type</label>
                                <select
                                    value={campaignType}
                                    onChange={(e) => setCampaignType(e.target.value)}
                                    className="w-full p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-shadow"
                                >
                                    <option value="promotional">Promotional Sale</option>
                                    <option value="seasonal">Seasonal / Holiday</option>
                                    <option value="new_arrival">New Arrival Launch</option>
                                    <option value="clearance">Clearance Event</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Select Primary Product</label>
                                <select
                                    className="w-full p-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-shadow"
                                    onChange={(e) => {
                                        if (e.target.value) setSelectedProducts([e.target.value]);
                                    }}
                                >
                                    <option value="">Select a product...</option>
                                    {products.map(p => (
                                        <option key={p.product_id} value={p.product_id}>{p.name} ({p.category})</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Creative Prompt (Optional)</label>
                                <textarea
                                    value={prompt}
                                    onChange={(e) => setPrompt(e.target.value)}
                                    placeholder="E.g., Summer vibe, beach background, minimalistic..."
                                    className="w-full p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-shadow h-24 resize-none"
                                />
                                <p className="text-xs text-slate-500 mt-1">If left blank, the agent will generate one based on the product and trends.</p>
                            </div>

                            <button
                                onClick={handleGenerate}
                                disabled={isGenerating || selectedProducts.length === 0}
                                className={`w-full py-3 px-4 rounded-xl font-bold text-white shadow-md transition-all
                                    ${isGenerating || selectedProducts.length === 0
                                        ? 'bg-slate-300 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 hover:scale-[1.02]'
                                    }`}
                            >
                                {isGenerating ? (
                                    <span className="flex items-center justify-center gap-2">
                                        <Loader2 className="w-5 h-5 animate-spin" /> Generating Assets...
                                    </span>
                                ) : (
                                    <span className="flex items-center justify-center gap-2">
                                        <Sparkles className="w-5 h-5" /> Generate Campaign Creative
                                    </span>
                                )}
                            </button>
                        </div>

                        {/* Right: Preview */}
                        <div className="bg-slate-100 rounded-xl border border-slate-200 flex flex-col items-center justify-center min-h-[400px] relative overflow-hidden group">
                            {generatedImage ? (
                                <>
                                    <img
                                        src={`data:image/jpeg;base64,${generatedImage}`}
                                        alt="Generated Campaign"
                                        className="w-full h-full object-cover"
                                    />
                                    <div className="absolute inset-x-0 bottom-0 p-4 bg-gradient-to-t from-black/70 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button className="w-full py-2 bg-white text-slate-900 font-bold rounded-lg hover:bg-slate-50">
                                            Use This Creative
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <div className="text-center p-8">
                                    <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm">
                                        <ImageIcon className="w-8 h-8 text-slate-300" />
                                    </div>
                                    <h3 className="text-slate-900 font-semibold mb-1">No Creative Generated</h3>
                                    <p className="text-slate-500 text-sm max-w-[200px] mx-auto">
                                        Select a product and campaign type to generate AI-powered marketing assets.
                                    </p>
                                    <div className="mt-6 flex items-center justify-center gap-2 text-xs text-slate-400">
                                        <Sparkles className="w-3 h-3" /> Powered by Amazon Titan
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
    const [activeTab, setActiveTab] = useState<'trends' | 'campaigns'>('trends');
    const [trends, setTrends] = useState<Trend[]>([]);
    const [campaignSuggestions, setCampaignSuggestions] = useState<CampaignSuggestion[]>([]);
    const [products, setProducts] = useState<Product[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        const loadData = async () => {
            setIsLoading(true);
            try {
                const [trendsData, campaignsData, productsData] = await Promise.all([
                    getTrends(),
                    getCampaignSuggestions(),
                    getProducts()
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
    }, []);

    return (
        <div className="flex h-screen w-full bg-slate-50 text-slate-900 font-sans overflow-hidden">
            <Sidebar />

            <main className="flex-1 flex flex-col min-w-0 bg-slate-50 relative overflow-hidden">
                {/* Header */}
                <header className="h-16 bg-white border-b border-slate-200 flex items-center px-6 sticky top-0 z-20 shrink-0 justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-600">
                            <TrendingUp size={18} />
                        </div>
                        <h1 className="text-lg font-semibold text-slate-900">Trends & Campaigns</h1>
                    </div>

                    <div className="flex p-1 bg-slate-100 rounded-lg border border-slate-200">
                        <button
                            onClick={() => setActiveTab('trends')}
                            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === 'trends'
                                ? 'bg-white text-slate-900 shadow-sm border border-slate-200/50'
                                : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            Market Trends
                        </button>
                        <button
                            onClick={() => setActiveTab('campaigns')}
                            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-all ${activeTab === 'campaigns'
                                ? 'bg-white text-purple-700 shadow-sm border border-purple-100'
                                : 'text-slate-500 hover:text-slate-700'
                                }`}
                        >
                            Campaigns
                        </button>
                    </div>
                </header>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-8">
                    <div className="max-w-7xl mx-auto">
                        <AnimatePresence mode="wait">
                            {activeTab === 'trends' ? (
                                <motion.div
                                    key="trends"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    <div className="mb-6">
                                        <h2 className="text-2xl font-bold text-slate-900">Active Market Trends</h2>
                                        <p className="text-slate-500 mt-1">Real-time analysis of demand signals and market shifts.</p>
                                    </div>
                                    <TrendsView trends={trends} isLoading={isLoading} />
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="campaigns"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: -20 }}
                                    transition={{ duration: 0.2 }}
                                >
                                    <div className="mb-6">
                                        <h2 className="text-2xl font-bold text-slate-900">Campaign Management</h2>
                                        <p className="text-slate-500 mt-1">Create and manage marketing campaigns driven by trend insights.</p>
                                    </div>
                                    <CampaignsView
                                        suggestions={campaignSuggestions}
                                        isLoading={isLoading}
                                        onCreateClick={() => setIsModalOpen(true)}
                                    />
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>

                <CreateCampaignModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    products={products}
                />
            </main>
        </div>
    );
}
