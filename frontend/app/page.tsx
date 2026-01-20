'use client';

import { useState, useEffect } from 'react';
import {
  Loader2,
  TrendingUp as TrendIcon,
  BarChart3,
  Bell,
  MapPin,
  ArrowUpRight
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import { useAgentContext } from '@/context/AgentContext';
import { getStores, getInventoryStatusSummary, getStoreInventory, getStoreForecasts, getProducts, getDecisions } from '@/lib/api';
import { Store } from '@/lib/types';
import StoreAnalyticsModal from '@/components/StoreAnalyticsModal';

// Map stores to visual coordinates - positioned for the visible map area
// Coordinates are percentages within the container, centered on the map
const STORE_COORDINATES: Record<string, { x: number; y: number }> = {
  'STORE_CHN': { x: 68, y: 18 },   // Chennai - northeast coast
  'STORE_VLR': { x: 58, y: 24 },   // Vellore - north inland
  'STORE_SLM': { x: 48, y: 36 },   // Salem - north central
  'STORE_ERD': { x: 38, y: 42 },   // Erode - west central
  'STORE_TPR': { x: 33, y: 48 },   // Tiruppur - west
  'STORE_CBE': { x: 28, y: 52 },   // Coimbatore - far west
  'STORE_TCH': { x: 52, y: 54 },   // Trichy - central
  'STORE_TJV': { x: 62, y: 56 },   // Thanjavur - east central
  'STORE_MDU': { x: 46, y: 68 },   // Madurai - south central
  'STORE_NGL': { x: 40, y: 82 },   // Nagercoil - southern tip
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
  const [decisionsCount, setDecisionsCount] = useState<number>(0);
  const [pricingDecisionsCount, setPricingDecisionsCount] = useState<number>(0);
  const [storesAtRisk, setStoresAtRisk] = useState<number>(0);
  const [totalStores, setTotalStores] = useState<number>(0);
  const [stockOutRiskCount, setStockOutRiskCount] = useState<number>(0);
  const [replenishmentPending, setReplenishmentPending] = useState<number>(0);
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

  // Use global context (for active agents count in sidebar)
  const { agentStatuses } = useAgentContext();

  // Derived state for sidebar
  const activeCount = Object.values(agentStatuses).filter(s => s.status === 'running').length;

  // Load initial store data and products
  useEffect(() => {
    const loadData = async () => {
      try {
        const [storesData, statusSummary, productsList, allDecisionsData] = await Promise.all([
          getStores(),
          getInventoryStatusSummary(),
          getProducts(),
          getDecisions()
        ]);

        // Set total decisions count (both pricing and replenishment)
        setDecisionsCount(allDecisionsData?.length || 0);

        // Calculate Pricing Decisions count
        const pricingCount = allDecisionsData?.filter(
          (d: any) => d.decision_type?.includes('pricing')
        ).length || 0;
        setPricingDecisionsCount(pricingCount);

        // Calculate Stores at Risk (stores with understocked items)
        const storesWithIssues = Object.entries(statusSummary.by_store || {}).filter(
          ([_, counts]: [string, any]) => (counts.understocked || 0) > 0
        ).length;
        setStoresAtRisk(storesWithIssues);
        setTotalStores(storesData.length);

        // Calculate Stock-Out Risk SKUs (total understocked across all stores)
        const totalUnderstocked = Object.values(statusSummary.by_store || {}).reduce(
          (sum: number, counts: any) => sum + (counts.understocked || 0), 0
        );
        setStockOutRiskCount(totalUnderstocked as number);

        // Calculate Replenishment Actions Pending
        const pendingReplenishments = allDecisionsData?.filter(
          (d: any) => (d.status === 'pending' || d.status === 'pending_approval') &&
            d.decision_type?.includes('replenishment')
        ).length || 0;
        setReplenishmentPending(pendingReplenishments);

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

          // Create a display name if store_name is missing
          const storeNameMap: Record<string, string> = {
            'STORE_CHN': 'SK Brands - Chennai',
            'STORE_VLR': 'SK Brands - Vellore',
            'STORE_SLM': 'SK Brands - Salem',
            'STORE_ERD': 'SK Brands - Erode',
            'STORE_TPR': 'SK Brands - Tiruppur',
            'STORE_CBE': 'SK Brands - Coimbatore',
            'STORE_TCH': 'SK Brands - Trichy',
            'STORE_TJV': 'SK Brands - Thanjavur',
            'STORE_MDU': 'SK Brands - Madurai',
            'STORE_TUT': 'SK Brands - Thoothukudi',
            'STORE_NGL': 'SK Brands - Nagercoil',
          };
          const displayName = s.store_name || storeNameMap[s.store_id] || s.store_id;

          return {
            id: s.store_id,
            name: displayName,
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

  // Listen for postMessage from Folium map iframe when a marker is clicked
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data && event.data.type === 'storeSelected') {
        const storeId = event.data.storeId;
        const matchedStore = stores.find(s => s.id === storeId);
        if (matchedStore) {
          setSelectedStore(matchedStore);
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [stores]);

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

  return (
    <div className="flex h-screen w-full bg-gray-100 font-sans overflow-hidden">
      <Sidebar activeAgentsCount={activeCount} />

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header style={{ height: '72px', padding: '0 32px' }} className="bg-white border-b border-gray-200 flex items-center justify-between shrink-0">
          <h1 style={{ fontSize: '20px', fontWeight: 600 }} className="text-gray-900">Executive Dashboard</h1>

          <div className="flex items-center" style={{ gap: '24px' }}>
            {/* Notification */}
            <button style={{ padding: '10px', position: 'relative' }} className="text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg">
              <Bell className="w-5 h-5" />
              <span style={{ position: 'absolute', top: '6px', right: '6px', width: '8px', height: '8px' }} className="bg-rose-500 rounded-full"></span>
            </button>

            {/* User profile */}
            <div style={{ paddingLeft: '24px', gap: '12px' }} className="flex items-center border-l border-gray-200">
              <div style={{ fontSize: '14px', fontWeight: 600 }} className="text-gray-900">Admin User</div>
              <div style={{ width: '36px', height: '36px', fontSize: '13px' }} className="rounded-full bg-gray-900 text-white flex items-center justify-center font-semibold">
                SK
              </div>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto" style={{ padding: '40px' }}>
          <div className="w-full">

            {/* Stats Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4" style={{ gap: '24px', marginBottom: '48px' }}>
              {[
                { label: 'Pricing Recommendations', value: String(pricingDecisionsCount), unit: 'Suggestions', trend: pricingDecisionsCount > 0 ? `+${pricingDecisionsCount}` : '0', color: 'text-blue-600', bg: 'bg-blue-50' },
                { label: 'Stores at Risk', value: `${storesAtRisk} / ${totalStores}`, unit: 'Stores', trend: storesAtRisk > 0 ? `-${storesAtRisk}` : '0', color: 'text-rose-600', bg: 'bg-rose-50' },
                { label: 'Stock-Out Risk SKUs', value: String(stockOutRiskCount), unit: 'SKUs', trend: stockOutRiskCount > 0 ? `-${stockOutRiskCount}` : '0', color: 'text-amber-600', bg: 'bg-amber-50' },
                { label: 'Replenishment Pending', value: String(replenishmentPending), unit: 'Actions', trend: replenishmentPending > 0 ? `${replenishmentPending}` : '0', color: 'text-emerald-600', bg: 'bg-emerald-50' },
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

                {/* Map Area - Interactive Folium Map */}
                <div style={{
                  flex: 1,
                  minHeight: '400px',
                  position: 'relative',
                }}>
                  <iframe
                    src="/tamilnadu-stores-map.html"
                    style={{
                      width: '100%',
                      height: '100%',
                      border: 'none',
                      borderRadius: '0 0 12px 12px',
                    }}
                    title="Tamil Nadu Store Map"
                  />
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
