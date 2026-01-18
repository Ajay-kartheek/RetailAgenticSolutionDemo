'use client';

import { useState, useEffect } from 'react';
import {
  Play,
  Loader2,
  Brain,
  TrendingUp as TrendIcon,
  BarChart3,
  Package,
  Truck,
  Tag,
  Palette,
  Search,
  Bell,
  MapPin,
  ArrowUpRight
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import AgentActivityPanel from '@/components/AgentActivityPanel';
import { useAgentContext } from '@/context/AgentContext';
import { getStores, getInventoryStatusSummary, getStoreInventory, getStoreForecasts, getProducts } from '@/lib/api';
import { Store } from '@/lib/types';
import StoreAnalyticsModal from '@/components/StoreAnalyticsModal';

const agents = [
  { id: 'orchestrator', name: 'Orchestrator', icon: Brain, color: 'text-purple-600', bg: 'bg-purple-100' },
  { id: 'demand_agent', name: 'Demand Forecasting', icon: TrendIcon, color: 'text-blue-600', bg: 'bg-blue-100' },
  { id: 'trend_agent', name: 'Trend Watcher', icon: BarChart3, color: 'text-indigo-600', bg: 'bg-indigo-100' },
  { id: 'inventory_agent', name: 'Inventory Optimizer', icon: Package, color: 'text-amber-600', bg: 'bg-amber-100' },
  { id: 'replenishment_agent', name: 'Store Replenishment', icon: Truck, color: 'text-emerald-600', bg: 'bg-emerald-100' },
  { id: 'pricing_agent', name: 'Pricing & Promotion', icon: Tag, color: 'text-orange-600', bg: 'bg-orange-100' },
  { id: 'campaign_agent', name: 'Brand Campaign', icon: Palette, color: 'text-pink-600', bg: 'bg-pink-100' },
];

// Map stores to visual coordinates - adjusted to align with SVG outline
// The SVG goes from about x:10-98, y:5-98 so dots need to match
const STORE_COORDINATES: Record<string, { x: number; y: number }> = {
  'STORE_CHN': { x: 88, y: 12 },   // Chennai - top right (coast)
  'STORE_VLR': { x: 75, y: 18 },   // Vellore - upper right  
  'STORE_SLM': { x: 50, y: 35 },   // Salem - north central
  'STORE_ERD': { x: 35, y: 42 },   // Erode - west central  
  'STORE_TPR': { x: 28, y: 48 },   // Tiruppur - west (near CBE)
  'STORE_CBE': { x: 18, y: 52 },   // Coimbatore - far left (western border)
  'STORE_TCH': { x: 55, y: 55 },   // Trichy - central
  'STORE_TJV': { x: 68, y: 52 },   // Thanjavur - east central
  'STORE_MDU': { x: 45, y: 72 },   // Madurai - south central
  'STORE_NGL': { x: 30, y: 92 },   // Nagercoil - southern tip
};



const statusColors = {
  critical: 'bg-rose-500',
  high: 'bg-orange-500',
  medium: 'bg-blue-500',
  low: 'bg-emerald-500'
};

export default function Dashboard() {
  const [stores, setStores] = useState<any[]>([]);
  const [products, setProducts] = useState<Record<string, string>>({}); // Map: ID -> Name
  const [selectedStore, setSelectedStore] = useState<any>(null);
  const [isAnalyticsOpen, setIsAnalyticsOpen] = useState(false);
  const [fullInventory, setFullInventory] = useState<any[]>([]);
  const [storeDetails, setStoreDetails] = useState<{
    loading: boolean;
    stockHealth: { critical: number, low: number, good: number };
    alerts: { name: string, stock: number }[];
    topDemand: { name: string, forecast: number }[];
  }>({
    loading: false,
    stockHealth: { critical: 0, low: 0, good: 0 },
    alerts: [],
    topDemand: []
  });

  // Use global context
  const { isRunning, isExecuting, agentStatuses, activityMessages, startAnalysis } = useAgentContext();

  // Load initial store data and products
  useEffect(() => {
    const loadData = async () => {
      try {
        const [storesData, statusSummary, productsList] = await Promise.all([
          getStores(),
          getInventoryStatusSummary(),
          getProducts()
        ]);

        // Create product map
        const prodMap: Record<string, string> = {};
        productsList.forEach(p => prodMap[p.product_id] = p.name || p.product_name || p.product_id);
        setProducts(prodMap);

        // Map backend stores to UI format
        const mappedStores = storesData.map(s => {
          const coords = STORE_COORDINATES[s.store_id] || { x: 50, y: 50 };
          const statusCounts = statusSummary.by_store[s.store_id] || {};

          let status = 'low'; // default (green)
          if (statusCounts.understocked > 0) status = 'critical';
          else if (statusCounts.overstocked > 5) status = 'high';
          else if (statusCounts.in_stock > 0) status = 'medium'; // Normal

          return {
            id: s.store_id,
            name: s.store_name,
            status: status,
            x: coords.x,
            y: coords.y,
            // These will be fetched on click, placeholders for now
            stock: 0,
            demand: 0
          };
        });

        setStores(mappedStores);
        if (mappedStores.length > 0 && !selectedStore) {
          setSelectedStore(mappedStores[0]);
        }
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      }
    };

    loadData();
  }, []);

  // Fetch details when store selected
  useEffect(() => {
    if (!selectedStore) return;

    const fetchDetails = async () => {
      setStoreDetails(prev => ({ ...prev, loading: true }));
      try {
        const [inventory, forecasts] = await Promise.all([
          getStoreInventory(selectedStore.id),
          getStoreForecasts(selectedStore.id)
        ]);

        setFullInventory(inventory); // Save for modal

        // Analyze Inventory
        let critical = 0;
        let low = 0;
        let good = 0;
        const criticalItems: any[] = [];

        inventory.forEach(item => {
          // @ts-ignore - handle both new and legacy field names
          const status = item.stock_status ?? item.availability_status ?? 'in_stock';
          // @ts-ignore
          const stock = item.current_stock ?? item.quantity ?? 0;

          if (status === 'out_of_stock') {
            critical++;
            criticalItems.push({
              name: products[item.product_id] || item.product_id,
              stock: stock
            });
          } else if (status === 'low_stock' || stock < 10) {
            low++;
            if (criticalItems.length < 5) {
              criticalItems.push({
                name: products[item.product_id] || item.product_id,
                stock: stock
              });
            }
          } else {
            good++;
          }
        });

        // Analyze Forecasts (Top 3)
        // Fix: Use 'forecasted_demand' key based on seed.py
        const sortedForecasts = forecasts
          .sort((a, b) => b.forecasted_demand - a.forecasted_demand)
          .slice(0, 3)
          .map(f => ({
            name: products[f.product_id] || f.product_id,
            forecast: Math.round(Number(f.forecasted_demand) || 0)
          }));

        setStoreDetails({
          loading: false,
          stockHealth: { critical, low, good },
          alerts: criticalItems.slice(0, 3),
          topDemand: sortedForecasts
        });
      } catch (err) {
        console.error("Failed to fetch store details", err);
        setStoreDetails(prev => ({ ...prev, loading: false }));
      }
    };

    fetchDetails();
  }, [selectedStore, products]);

  // Derived state
  const activeCount = Object.values(agentStatuses).filter(s => s.status === 'running').length;

  const activeAgents = Object.values(agentStatuses)
    .filter(s => s.status === 'running')
    .map(s => s.id);

  // Map context messages to panel format
  const panelMessages = activityMessages.map(m => ({
    id: m.id,
    agent_name: m.agentId,
    type: (m.type === 'thinking' ? 'thinking' :
      m.type === 'error' ? 'error' :
        m.type === 'success' ? 'result' : 'communication') as any,
    message: m.message,
    thinking: m.type === 'thinking' ? m.message : undefined,
    timestamp: new Date(m.timestamp)
  })).reverse();

  const handleRun = async () => {
    await startAnalysis();
  };

  return (
    <div className="flex h-screen w-full bg-gray-100 font-sans overflow-hidden">
      <Sidebar activeAgentsCount={activeCount} />

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header style={{ height: '72px', padding: '0 32px' }} className="bg-white border-b border-gray-200 flex items-center justify-between shrink-0">
          <h1 style={{ fontSize: '20px', fontWeight: 600 }} className="text-gray-900">Executive Dashboard</h1>

          <div className="flex items-center" style={{ gap: '24px' }}>
            {/* Search */}
            <div className="relative">
              <Search style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)' }} className="w-4 h-4 text-gray-400" />
              <input
                style={{ paddingLeft: '40px', paddingRight: '16px', height: '40px', width: '280px', fontSize: '14px' }}
                className="bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Search..."
              />
            </div>

            {/* Notification */}
            <button style={{ padding: '10px', position: 'relative' }} className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
              <Bell className="w-5 h-5" />
              <span style={{ position: 'absolute', top: '6px', right: '6px', width: '8px', height: '8px' }} className="bg-rose-500 rounded-full"></span>
            </button>

            {/* User profile */}
            <div style={{ paddingLeft: '24px', gap: '12px' }} className="flex items-center border-l border-gray-200">
              <div className="text-right">
                <div style={{ fontSize: '14px', fontWeight: 500 }} className="text-gray-900">Admin User</div>
                <div style={{ fontSize: '12px' }} className="text-gray-500">Super Admin</div>
              </div>
              <div style={{ width: '36px', height: '36px', fontSize: '13px' }} className="rounded-full bg-gray-900 text-white flex items-center justify-center font-semibold">
                SK
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto" style={{ padding: '40px' }}>
          <div className="max-w-7xl mx-auto">

            {/* Stats Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4" style={{ gap: '24px', marginBottom: '48px' }}>
              {[
                { label: 'Active Agents', value: activeCount || '0', unit: 'Running', trend: '+2', color: 'text-blue-600', bg: 'bg-blue-50' },
                { label: 'Warning Signals', value: '4', unit: 'Critical', trend: '-1', color: 'text-rose-600', bg: 'bg-rose-50' },
                { label: 'Forecast Accuracy', value: '94.2%', unit: 'vs LME', trend: '+5.2%', color: 'text-emerald-600', bg: 'bg-emerald-50' },
                { label: 'Pending Decisions', value: '12', unit: 'Actions', trend: '+3', color: 'text-gray-900', bg: 'bg-gray-100' },
              ].map((stat, i) => (
                <div key={i} style={{ padding: '24px' }} className="bg-white rounded-xl border border-gray-200 shadow-sm">
                  <div style={{ marginBottom: '16px' }} className="flex items-center justify-between">
                    <span style={{ fontSize: '14px', fontWeight: 500 }} className="text-gray-500">{stat.label}</span>
                    <span style={{ fontSize: '12px', padding: '4px 10px' }} className={`inline-flex items-center font-semibold rounded-full ${stat.bg} ${stat.color}`}>
                      <ArrowUpRight style={{ width: '12px', height: '12px', marginRight: '4px' }} /> {stat.trend}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    <span style={{ fontSize: '28px', fontWeight: 700 }} className="text-gray-900">{stat.value}</span>
                    <span style={{ fontSize: '13px' }} className="text-gray-400">{stat.unit}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Map & Details Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3" style={{ gap: '24px', marginBottom: '48px' }}>

              {/* Map Card */}
              <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col">
                <div style={{ padding: '20px 24px', borderBottom: '1px solid #f1f5f9', flexShrink: 0 }} className="flex items-center justify-between">
                  <div>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a', margin: 0 }}>Network Status Map</h3>
                    <p style={{ fontSize: '13px', marginTop: '4px', color: '#64748b', margin: 0 }}>Real-time store monitoring</p>
                  </div>
                  <div style={{ padding: '6px 12px', gap: '8px', fontSize: '12px', display: 'flex', alignItems: 'center', backgroundColor: '#ecfdf5', borderRadius: '9999px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981' }} className="animate-pulse"></span>
                    <span style={{ color: '#059669', fontWeight: 600 }}>Live</span>
                  </div>
                </div>

                {/* Map Area - fills remaining space */}
                <div style={{
                  flex: 1,
                  minHeight: '400px',
                  position: 'relative',
                  backgroundColor: '#f0f9ff',
                  overflow: 'hidden'
                }}>
                  {/* Tamil Nadu Outline SVG */}
                  <svg
                    viewBox="0 0 100 100"
                    preserveAspectRatio="none"
                    style={{
                      position: 'absolute',
                      inset: 0,
                      width: '100%',
                      height: '100%',
                      opacity: 0.15
                    }}
                  >
                    {/* Simplified TN state outline path */}
                    <path
                      d="M95 5 L98 10 L96 18 L90 22 L85 28 L80 35 L75 40 L72 48 L75 55 L72 62 L68 68 L60 75 L50 82 L42 88 L35 95 L28 98 L22 95 L18 88 L15 78 L12 68 L10 55 L12 45 L15 38 L18 32 L25 25 L35 18 L48 12 L62 8 L78 5 Z"
                      fill="#3b82f6"
                      stroke="#2563eb"
                      strokeWidth="1"
                    />
                  </svg>

                  {/* City labels for context */}
                  <div style={{ position: 'absolute', left: '90%', top: '9%', fontSize: '8px', color: '#475569', fontWeight: 600, transform: 'translateX(-50%)' }}>Chennai</div>
                  <div style={{ position: 'absolute', left: '10%', top: '52%', fontSize: '8px', color: '#475569', fontWeight: 600 }}>Coimbatore</div>
                  <div style={{ position: 'absolute', left: '45%', top: '76%', fontSize: '8px', color: '#475569', fontWeight: 600, transform: 'translateX(-50%)' }}>Madurai</div>
                  <div style={{ position: 'absolute', left: '30%', top: '96%', fontSize: '8px', color: '#475569', fontWeight: 600, transform: 'translateX(-50%)' }}>Nagercoil</div>

                  {/* Store pins */}
                  {stores.map(store => (
                    <button
                      key={store.id}
                      onClick={() => setSelectedStore(store)}
                      className="absolute transform -translate-x-1/2 -translate-y-1/2 group z-10"
                      style={{ left: `${store.x}%`, top: `${store.y}%` }}
                    >
                      <div className={`w-5 h-5 rounded-full border-3 border-white shadow-xl transition-transform ${statusColors[store.status as keyof typeof statusColors]} ${selectedStore?.id === store.id ? 'scale-150 ring-4 ring-gray-300' : 'hover:scale-125'}`}></div>
                      <div className="opacity-0 group-hover:opacity-100 absolute bottom-full left-1/2 -translate-x-1/2 mb-3 px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-xl shadow-xl whitespace-nowrap">
                        {store.name}
                      </div>
                    </button>
                  ))}

                  {stores.length === 0 && (
                    <div className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">Loading map data...</div>
                  )}
                </div>
              </div>

              {/* Store Details Card */}
              <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex flex-col h-full">
                <div style={{ padding: '20px 24px', borderBottom: '1px solid #f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a', margin: 0 }}>Store Details</h3>
                </div>

                {selectedStore ? (
                  <div style={{ padding: '16px 20px', flex: 1, overflowY: 'auto' }}>
                    {/* Store Header */}
                    <div style={{ marginBottom: '16px' }}>
                      <h4 style={{ fontSize: '17px', fontWeight: 700, color: '#0f172a', margin: 0 }}>{selectedStore.name}</h4>
                      <p style={{ fontSize: '12px', color: '#64748b', marginTop: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <MapPin style={{ width: '12px', height: '12px' }} />
                        <span style={{ fontFamily: 'monospace', backgroundColor: '#f1f5f9', padding: '2px 6px', borderRadius: '4px', fontSize: '11px' }}>{selectedStore.id}</span>
                      </p>
                    </div>

                    {/* Stock Health Summary */}
                    <div style={{ marginBottom: '16px' }}>
                      <p style={{ fontSize: '10px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', marginBottom: '8px' }}>INVENTORY STATUS</p>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                        <div style={{ padding: '10px 8px', backgroundColor: '#fef2f2', borderRadius: '8px', textAlign: 'center', border: '1px solid #fecaca' }}>
                          <div style={{ fontSize: '18px', fontWeight: 700, color: '#dc2626' }}>{storeDetails.loading ? '-' : storeDetails.stockHealth.critical}</div>
                          <div style={{ fontSize: '9px', fontWeight: 600, color: '#ef4444', letterSpacing: '0.3px', marginTop: '2px' }}>OUT OF STOCK</div>
                        </div>
                        <div style={{ padding: '10px 8px', backgroundColor: '#fffbeb', borderRadius: '8px', textAlign: 'center', border: '1px solid #fef08a' }}>
                          <div style={{ fontSize: '18px', fontWeight: 700, color: '#ca8a04' }}>{storeDetails.loading ? '-' : storeDetails.stockHealth.low}</div>
                          <div style={{ fontSize: '9px', fontWeight: 600, color: '#ca8a04', letterSpacing: '0.3px', marginTop: '2px' }}>LOW STOCK</div>
                        </div>
                        <div style={{ padding: '10px 8px', backgroundColor: '#f0fdf4', borderRadius: '8px', textAlign: 'center', border: '1px solid #bbf7d0' }}>
                          <div style={{ fontSize: '18px', fontWeight: 700, color: '#16a34a' }}>{storeDetails.loading ? '-' : storeDetails.stockHealth.good}</div>
                          <div style={{ fontSize: '9px', fontWeight: 600, color: '#16a34a', letterSpacing: '0.3px', marginTop: '2px' }}>IN STOCK</div>
                        </div>
                      </div>
                    </div>

                    {/* Low Stock Alerts */}
                    <div style={{ padding: '12px', marginBottom: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <p style={{ fontSize: '11px', fontWeight: 600, color: '#475569', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <TrendIcon style={{ width: '12px', height: '12px', color: '#ef4444' }} />
                        Low Stock Alerts
                      </p>
                      {storeDetails.loading ? (
                        <div className="flex justify-center p-2"><Loader2 className="w-4 h-4 animate-spin text-gray-400" /></div>
                      ) : storeDetails.alerts.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {storeDetails.alerts.slice(0, 2).map((item, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <span style={{ fontSize: '12px', color: '#475569' }}>{item.name}</span>
                              <span style={{ fontSize: '11px', fontWeight: 700, color: '#dc2626', backgroundColor: '#fef2f2', padding: '2px 8px', borderRadius: '4px' }}>{item.stock} left</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic', textAlign: 'center', padding: '4px 0' }}>No critical items</p>
                      )}
                    </div>

                    {/* Top Demand */}
                    <div style={{ padding: '12px', marginBottom: '12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <p style={{ fontSize: '11px', fontWeight: 600, color: '#475569', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <BarChart3 style={{ width: '12px', height: '12px', color: '#3b82f6' }} />
                        High Demand Forecast
                      </p>
                      {storeDetails.loading ? (
                        <div className="flex justify-center p-2"><Loader2 className="w-4 h-4 animate-spin text-gray-400" /></div>
                      ) : storeDetails.topDemand.length > 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {storeDetails.topDemand.slice(0, 2).map((item, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <span style={{ fontSize: '12px', color: '#475569' }}>{item.name}</span>
                              <span style={{ fontSize: '11px', fontWeight: 700, color: '#2563eb', backgroundColor: '#eff6ff', padding: '2px 8px', borderRadius: '4px' }}>+{item.forecast}</span>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic', textAlign: 'center', padding: '4px 0' }}>No forecast data</p>
                      )}
                    </div>

                    {/* Action Button */}
                    <button
                      onClick={() => setIsAnalyticsOpen(true)}
                      style={{
                        width: '100%',
                        padding: '10px',
                        fontSize: '13px',
                        fontWeight: 600,
                        backgroundColor: '#0f172a',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '6px'
                      }}
                      className="hover:bg-gray-800 transition-colors"
                    >
                      View Full Analytics <ArrowUpRight style={{ width: '16px', height: '16px' }} />
                    </button>
                  </div>
                ) : (
                  <div style={{ padding: '48px 24px', textAlign: 'center', color: '#94a3b8', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
                    <MapPin style={{ width: '32px', height: '32px', opacity: 0.3, marginBottom: '12px' }} />
                    <p style={{ fontSize: '14px', fontWeight: 500 }}>Select a store from the map</p>
                    <p style={{ fontSize: '12px', marginTop: '4px' }}>Click on any pin to view details</p>
                  </div>
                )}
              </div>
            </div>

            {/* Agent Network */}
            <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
              <div style={{ padding: '20px 32px' }} className="border-b border-gray-100 flex items-center justify-between">
                <div>
                  <h3 style={{ fontSize: '18px', fontWeight: 600 }} className="text-gray-900">AI Agent Network</h3>
                  <p style={{ fontSize: '14px', marginTop: '4px' }} className="text-gray-500">{agents.length} agents available</p>
                </div>
                <button
                  onClick={handleRun}
                  disabled={isRunning}
                  style={{ padding: '10px 20px', fontSize: '14px', gap: '8px' }}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors flex items-center"
                >
                  {isRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  {isRunning ? 'Running...' : 'Run Analysis'}
                </button>
              </div>

              {/* Agent Cards Grid */}
              <div style={{ padding: '20px 32px' }}>
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7" style={{ gap: '10px' }}>
                  {agents.map(agent => {
                    const Icon = agent.icon;
                    const isActive = activeAgents.includes(agent.id);
                    return (
                      <div
                        key={agent.id}
                        style={{ padding: '14px 10px', minWidth: '100px' }}
                        className={`rounded-lg border transition-all ${isActive
                          ? 'border-purple-300 bg-purple-50 shadow-md'
                          : 'border-gray-200 bg-gray-50'
                          }`}
                      >
                        <div className="flex flex-col items-center text-center">
                          <div
                            style={{ width: '36px', height: '36px', marginBottom: '8px', position: 'relative' }}
                            className={`rounded-lg ${agent.bg} flex items-center justify-center flex-shrink-0`}
                          >
                            <Icon style={{ width: '18px', height: '18px' }} className={agent.color} />
                            {isActive && (
                              <div className="absolute inset-0 rounded-lg border-2 border-purple-400 animate-ping opacity-40" />
                            )}
                          </div>
                          {/* Fixed height name area for alignment */}
                          <div style={{ height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <h4 style={{ fontSize: '11px', fontWeight: 600, lineHeight: 1.2 }} className="text-gray-900">{agent.name}</h4>
                          </div>
                          <div style={{ gap: '4px', height: '14px' }} className="flex items-center">
                            {isActive ? (
                              <div className="flex gap-0.5">
                                {[0, 1, 2].map(i => (
                                  <div
                                    key={i}
                                    className="w-1 h-1 rounded-full bg-purple-500 animate-pulse"
                                    style={{ animationDelay: `${i * 200}ms` }}
                                  />
                                ))}
                              </div>
                            ) : (
                              <>
                                <span style={{ width: '5px', height: '5px' }} className="rounded-full bg-gray-300"></span>
                                <span style={{ fontSize: '9px' }} className="text-gray-400">Idle</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Agent Activity Panel - Live Feed */}
            <div style={{ marginTop: '20px' }}>
              <AgentActivityPanel
                messages={panelMessages}
                activeAgents={activeAgents}
                isRunning={isRunning || isExecuting}
              />
            </div>

          </div>
        </div>
      </main>

      {/* Analytics Modal */}
      <StoreAnalyticsModal
        isOpen={isAnalyticsOpen}
        onClose={() => setIsAnalyticsOpen(false)}
        store={selectedStore}
        inventory={fullInventory}
        products={products}
      />
    </div>
  );
}
