'use client';

import { useState, useEffect } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  TrendingUp,
  Clock,
  Filter,
  Search,
  MoreHorizontal,
  Loader2,
  Package,
  Truck,
  ArrowRight,
  ShoppingBag
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import { getDecisions, approveDecision, rejectDecision } from '@/lib/api';
import { useAgentContext } from '@/context/AgentContext';
import type { Decision } from '@/lib/types';

export default function DecisionsPage() {
  const [activeTab, setActiveTab] = useState('Pending');
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const { triggerExecution } = useAgentContext();

  useEffect(() => {
    fetchDecisions();
  }, []);

  const fetchDecisions = async () => {
    setLoading(true);
    try {
      const data = await getDecisions();
      setDecisions(data);
    } catch (error) {
      console.error('Failed to fetch decisions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: string) => {
    setProcessingId(id);
    try {
      // Find the decision to get details for the animation
      const decision = decisions.find(d => d.decision_id === id);
      const decisionType = decision?.decision_type || '';
      const productName = decision?.data?.product_name || decision?.title || 'product';

      // Trigger the execution animation
      const agentType = decisionType.includes('pricing') ? 'pricing' : 'replenishment';
      triggerExecution(agentType as 'pricing' | 'replenishment', {
        productName,
        action: decisionType.includes('pricing') ? 'Price updated' : 'Transfer initiated'
      });

      await approveDecision(id);
      // Update to executed since backend executes on approval
      setDecisions(prev => prev.map(d =>
        d.decision_id === id ? { ...d, status: 'executed' } : d
      ));
    } catch (error: any) {
      // If the decision was already approved/executed, just refresh the list
      if (error?.response?.status === 400) {
        console.log('Decision already processed, refreshing list...');
        fetchDecisions();
      } else {
        console.error('Failed to approve decision:', error);
      }
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (id: string) => {
    setProcessingId(id);
    try {
      await rejectDecision(id);
      setDecisions(prev => prev.map(d =>
        d.decision_id === id ? { ...d, status: 'rejected' } : d
      ));
    } catch (error) {
      console.error('Failed to reject decision:', error);
    } finally {
      setProcessingId(null);
    }
  };

  const [typeFilter, setTypeFilter] = useState<'all' | 'pricing' | 'replenishment'>('all');

  const filteredDecisions = decisions.filter(d => {
    // First filter by status
    let matchesStatus = false;
    if (activeTab === 'Approved') {
      matchesStatus = d.status === 'approved' || d.status === 'executed';
    } else if (activeTab === 'Pending') {
      matchesStatus = d.status === 'pending' || d.status === 'pending_approval';
    } else {
      matchesStatus = d.status.toLowerCase() === activeTab.toLowerCase();
    }

    // Then filter by type
    if (typeFilter === 'all') {
      return matchesStatus;
    } else if (typeFilter === 'pricing') {
      return matchesStatus && d.decision_type?.includes('pricing');
    } else if (typeFilter === 'replenishment') {
      return matchesStatus && d.decision_type?.includes('replenishment');
    }
    return matchesStatus;
  });

  return (
    <div className="flex h-screen w-full bg-gray-100 font-sans overflow-hidden">
      <Sidebar />

      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <header style={{ height: '64px', padding: '0 32px' }} className="bg-white border-b border-gray-200 flex items-center justify-between shrink-0">
          <div>
            <h1 style={{ fontSize: '18px', fontWeight: 600 }} className="text-gray-900">Decision Queue</h1>
            <p style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>
              {decisions.filter(d => d.status === 'pending').length} actions require approval
            </p>
          </div>

          {/* Tabs */}
          <div style={{ display: 'flex', gap: '4px', padding: '4px', borderRadius: '10px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
            {['Pending', 'Approved', 'Rejected'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '8px 16px',
                  fontSize: '12px',
                  fontWeight: 600,
                  borderRadius: '8px',
                  backgroundColor: activeTab === tab ? '#0f172a' : 'transparent',
                  color: activeTab === tab ? '#ffffff' : '#64748b',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {tab}
              </button>
            ))}
          </div>
        </header>

        {/* Content */}
        <div style={{ padding: '24px 32px' }} className="flex-1 overflow-y-auto">
          <div style={{ maxWidth: '900px', margin: '0 auto' }}>

            {/* Decision Type Filter Tabs */}
            <div style={{ marginBottom: '24px', display: 'flex', gap: '8px', backgroundColor: '#f8fafc', padding: '6px', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
              {[
                { key: 'all', label: 'All' },
                { key: 'pricing', label: 'Pricing' },
                { key: 'replenishment', label: 'Replenishment' }
              ].map((type) => {
                const count = decisions.filter(d => {
                  const matchesStatus = activeTab === 'Approved'
                    ? (d.status === 'approved' || d.status === 'executed')
                    : activeTab === 'Pending'
                      ? (d.status === 'pending' || d.status === 'pending_approval')
                      : d.status.toLowerCase() === activeTab.toLowerCase();
                  if (type.key === 'all') return matchesStatus;
                  if (type.key === 'pricing') return matchesStatus && d.decision_type?.includes('pricing');
                  if (type.key === 'replenishment') return matchesStatus && d.decision_type?.includes('replenishment');
                  return matchesStatus;
                }).length;

                return (
                  <button
                    key={type.key}
                    onClick={() => setTypeFilter(type.key as 'all' | 'pricing' | 'replenishment')}
                    style={{
                      flex: 1,
                      padding: '10px 16px',
                      fontSize: '13px',
                      fontWeight: 600,
                      borderRadius: '8px',
                      backgroundColor: typeFilter === type.key ? 'white' : 'transparent',
                      color: typeFilter === type.key ? '#0f172a' : '#64748b',
                      border: 'none',
                      boxShadow: typeFilter === type.key ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px'
                    }}
                  >
                    {type.label}
                    <span style={{
                      backgroundColor: typeFilter === type.key ? '#0f172a' : '#cbd5e1',
                      color: 'white',
                      padding: '2px 8px',
                      borderRadius: '10px',
                      fontSize: '11px',
                      fontWeight: 700,
                      minWidth: '24px',
                      textAlign: 'center'
                    }}>
                      {count}
                    </span>
                  </button>
                );
              })}
            </div>

            {loading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
              </div>
            ) : filteredDecisions.length === 0 ? (
              <div className="text-center py-12 text-gray-500 text-sm">
                No {activeTab.toLowerCase()} decisions found.
              </div>
            ) : (
              /* Decision Cards */
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {filteredDecisions.map((decision) => (
                  <div
                    key={decision.decision_id}
                    style={{ borderRadius: '12px', overflow: 'hidden' }}
                    className="bg-white border border-gray-200 shadow-sm hover:shadow-md transition-all"
                  >
                    {/* Card Header */}
                    <div style={{ padding: '20px 24px', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ display: 'flex', gap: '16px' }}>
                        {/* Icon */}
                        <div style={{
                          width: '40px',
                          height: '40px',
                          borderRadius: '10px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          backgroundColor: decision.priority === 'critical' ? '#fef2f2' : decision.priority === 'high' ? '#fffbeb' : '#eff6ff',
                          color: decision.priority === 'critical' ? '#dc2626' : decision.priority === 'high' ? '#d97706' : '#2563eb'
                        }}>
                          {decision.priority === 'critical' ? <AlertTriangle style={{ width: '20px', height: '20px' }} /> : <TrendingUp style={{ width: '20px', height: '20px' }} />}
                        </div>

                        {/* Title */}
                        <div>
                          <h3 style={{ fontSize: '15px', fontWeight: 600, marginBottom: '8px' }} className="text-gray-900">{decision.title}</h3>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span style={{ fontSize: '10px', fontFamily: 'monospace', color: '#64748b', backgroundColor: '#f1f5f9', padding: '4px 8px', borderRadius: '6px' }}>{decision.decision_id}</span>
                            <span style={{ fontSize: '12px', fontWeight: 500, color: '#64748b' }}>{decision.decision_type}</span>
                            {decision.priority === 'critical' && (
                              <span style={{ fontSize: '10px', fontWeight: 700, color: '#dc2626', backgroundColor: '#fef2f2', padding: '4px 10px', borderRadius: '999px' }}>CRITICAL</span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Cost / Confidence */}
                      <div className="text-right">
                        <div style={{ fontSize: '16px', fontWeight: 700 }} className="text-gray-900">
                          {decision.cost !== "0" ? `₹${Number(decision.cost).toLocaleString()}` : "No Cost"}
                        </div>
                        <div style={{ fontSize: '10px', fontWeight: 600, color: '#94a3b8', letterSpacing: '0.5px', marginTop: '2px' }}>EST. COST</div>
                      </div>
                    </div>

                    {/* Card Body */}
                    <div style={{ padding: '20px 24px' }}>
                      {/* Pricing Decision Details */}
                      {decision.decision_type?.includes('pricing') && decision.data && (
                        <div style={{
                          marginBottom: '20px',
                          padding: '16px 20px',
                          backgroundColor: '#fafbfc',
                          borderRadius: '12px',
                          border: '1px solid #e2e8f0'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                            <Package style={{ width: '16px', height: '16px', color: '#64748b' }} />
                            <span style={{ fontSize: '11px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px' }}>PRICING RECOMMENDATION</span>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '16px' }}>
                            {/* Current Price */}
                            <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                              <div style={{ fontSize: '10px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>CURRENT PRICE</div>
                              <div style={{ fontSize: '20px', fontWeight: 700, color: '#475569' }}>₹{decision.data.current_price || 0}</div>
                            </div>

                            {/* Arrow & Change */}
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                              <div style={{
                                fontSize: '12px',
                                fontWeight: 700,
                                color: (decision.data.price_change_percent || 0) < 0 ? '#dc2626' : '#16a34a',
                                backgroundColor: (decision.data.price_change_percent || 0) < 0 ? '#fef2f2' : '#f0fdf4',
                                padding: '4px 12px',
                                borderRadius: '20px'
                              }}>
                                {(decision.data.price_change_percent || 0) > 0 ? '+' : ''}{decision.data.price_change_percent || 0}%
                              </div>
                              <div style={{ fontSize: '20px', color: '#94a3b8', marginTop: '4px' }}>→</div>
                            </div>

                            {/* Recommended Price */}
                            <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#f0fdf4', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
                              <div style={{ fontSize: '10px', fontWeight: 600, color: '#16a34a', marginBottom: '4px' }}>RECOMMENDED</div>
                              <div style={{ fontSize: '20px', fontWeight: 700, color: '#16a34a' }}>₹{decision.data.recommended_price || decision.data.suggested_price || 0}</div>
                            </div>
                          </div>

                          {/* Reasoning */}
                          <div style={{ padding: '12px', backgroundColor: '#fffbeb', borderRadius: '8px', border: '1px solid #fef08a' }}>
                            <div style={{ fontSize: '11px', fontWeight: 600, color: '#ca8a04', marginBottom: '6px' }}>WHY THIS CHANGE?</div>
                            <p style={{ fontSize: '12px', color: '#92400e', lineHeight: 1.5, margin: 0 }}>
                              {decision.data.reasoning || decision.description || 'No reasoning provided'}
                            </p>
                          </div>

                          {/* Expected Impact */}
                          {decision.data.expected_revenue_impact_weekly && (
                            <div style={{ marginTop: '12px', display: 'flex', gap: '16px' }}>
                              <div style={{ flex: 1, padding: '10px 12px', backgroundColor: '#eff6ff', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
                                <div style={{ fontSize: '10px', fontWeight: 600, color: '#2563eb', marginBottom: '2px' }}>EXPECTED REVENUE IMPACT</div>
                                <div style={{ fontSize: '14px', fontWeight: 700, color: '#1d4ed8' }}>
                                  {decision.data.expected_revenue_impact_weekly > 0 ? '+' : ''}₹{decision.data.expected_revenue_impact_weekly.toLocaleString()}/week
                                </div>
                              </div>
                              {decision.data.valid_until && (
                                <div style={{ padding: '10px 12px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                                  <div style={{ fontSize: '10px', fontWeight: 600, color: '#64748b', marginBottom: '2px' }}>VALID UNTIL</div>
                                  <div style={{ fontSize: '14px', fontWeight: 600, color: '#475569' }}>{new Date(decision.data.valid_until).toLocaleDateString()}</div>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Replenishment Decision Details */}
                      {decision.decision_type?.includes('replenishment') && decision.data && (
                        <div style={{
                          marginBottom: '20px',
                          padding: '16px 20px',
                          backgroundColor: '#f0fdf4',
                          borderRadius: '12px',
                          border: '1px solid #bbf7d0'
                        }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                            <Truck style={{ width: '16px', height: '16px', color: '#16a34a' }} />
                            <span style={{ fontSize: '11px', fontWeight: 600, color: '#16a34a', letterSpacing: '0.5px' }}>
                              {decision.data.transfer_details ? 'INTER-STORE TRANSFER' : 'MANUFACTURER ORDER'}
                            </span>
                          </div>

                          {/* Transfer Details */}
                          {decision.data.transfer_details ? (
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '16px', alignItems: 'center', marginBottom: '16px' }}>
                              {/* Source Store */}
                              <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                                <div style={{ fontSize: '10px', fontWeight: 600, color: '#94a3b8', marginBottom: '4px' }}>FROM</div>
                                <div style={{ fontSize: '16px', fontWeight: 700, color: '#475569' }}>{decision.data.transfer_details.from_store_id}</div>
                                <div style={{ fontSize: '11px', color: '#94a3b8' }}>{decision.data.transfer_details.distance_km}km away</div>
                              </div>

                              {/* Arrow & Quantity */}
                              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                                <div style={{ fontSize: '18px', fontWeight: 700, color: '#16a34a' }}>{decision.data.transfer_details.quantity || decision.data.required_quantity} units</div>
                                <ArrowRight style={{ width: '24px', height: '24px', color: '#16a34a' }} />
                              </div>

                              {/* Target Store */}
                              <div style={{ textAlign: 'center', padding: '12px', backgroundColor: '#dcfce7', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
                                <div style={{ fontSize: '10px', fontWeight: 600, color: '#16a34a', marginBottom: '4px' }}>TO</div>
                                <div style={{ fontSize: '16px', fontWeight: 700, color: '#166534' }}>{decision.data.target_store_id}</div>
                                <div style={{ fontSize: '11px', color: '#16a34a' }}>Target Store</div>
                              </div>
                            </div>
                          ) : (
                            <div style={{ padding: '16px', backgroundColor: '#fffbeb', borderRadius: '8px', border: '1px solid #fef08a', marginBottom: '16px' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <ShoppingBag style={{ width: '16px', height: '16px', color: '#ca8a04' }} />
                                <span style={{ fontSize: '13px', fontWeight: 600, color: '#92400e' }}>
                                  Order {decision.data.required_quantity} units from manufacturer for {decision.data.target_store_id}
                                </span>
                              </div>
                              <p style={{ fontSize: '12px', color: '#a16207', marginTop: '8px' }}>
                                No donor store available. Manufacturer order required.
                              </p>
                            </div>
                          )}

                          {/* Product & Urgency Info */}
                          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                            <div style={{ padding: '8px 12px', backgroundColor: '#ffffff', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                              <span style={{ fontSize: '10px', fontWeight: 600, color: '#94a3b8' }}>PRODUCT: </span>
                              <span style={{ fontSize: '12px', fontWeight: 600, color: '#475569' }}>{decision.data.product_name || decision.data.product_id}</span>
                            </div>
                            {decision.data.urgency && (
                              <div style={{ padding: '8px 12px', backgroundColor: decision.data.urgency === 'critical' ? '#fef2f2' : '#fffbeb', borderRadius: '6px' }}>
                                <span style={{ fontSize: '11px', fontWeight: 700, color: decision.data.urgency === 'critical' ? '#dc2626' : '#d97706' }}>
                                  {decision.data.urgency.toUpperCase()} URGENCY
                                </span>
                              </div>
                            )}
                            {decision.data.expected_completion_date && (
                              <div style={{ padding: '8px 12px', backgroundColor: '#eff6ff', borderRadius: '6px', border: '1px solid #bfdbfe' }}>
                                <span style={{ fontSize: '10px', fontWeight: 600, color: '#2563eb' }}>ETA: </span>
                                <span style={{ fontSize: '12px', fontWeight: 600, color: '#1d4ed8' }}>
                                  {new Date(decision.data.expected_completion_date).toLocaleDateString()}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '24px' }}>
                        {/* Description - only show if not pricing or replenishment (already shown above) */}
                        <div>
                          {!decision.decision_type?.includes('pricing') && !decision.decision_type?.includes('replenishment') && (
                            <p style={{ fontSize: '13px', color: '#475569', lineHeight: 1.6, marginBottom: '16px' }}>{decision.description}</p>
                          )}
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                            {/* Tags - generated from type and agent */}
                            <span style={{ padding: '6px 10px', backgroundColor: '#f8fafc', color: '#475569', fontSize: '11px', fontWeight: 600, borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                              #{decision.agent_id}
                            </span>
                            {decision.tags?.map(tag => (
                              <span key={tag} style={{ padding: '6px 10px', backgroundColor: '#f8fafc', color: '#475569', fontSize: '11px', fontWeight: 600, borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                                #{tag}
                              </span>
                            ))}
                            {decision.expiry && (
                              <span style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#94a3b8' }}>
                                <Clock style={{ width: '12px', height: '12px' }} /> Expires in {decision.expiry}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Impact - only show for non-pricing decisions */}
                        {!decision.decision_type?.includes('pricing') && (
                          <div style={{ padding: '16px', backgroundColor: '#f8fafc', borderRadius: '10px', border: '1px solid #e2e8f0', minWidth: '180px', maxWidth: '300px' }}>
                            <h4 style={{ fontSize: '10px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', marginBottom: '12px' }}>IMPACT ANALYSIS</h4>
                            <p style={{ fontSize: '12px', color: '#475569', lineHeight: '1.4' }}>
                              {decision.impact || "No impact analysis available."}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Card Actions */}
                    {(activeTab === 'Pending') && (
                      <div style={{ padding: '16px 24px', backgroundColor: '#fafbfc', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                        <button
                          onClick={() => handleReject(decision.decision_id)}
                          disabled={processingId === decision.decision_id}
                          style={{ padding: '10px 20px', fontSize: '13px', fontWeight: 600, borderRadius: '8px', backgroundColor: 'transparent', color: '#475569', border: '1px solid #e2e8f0', cursor: 'pointer' }} className="hover:bg-white hover:border-gray-300 transition-colors disabled:opacity-50">
                          {processingId === decision.decision_id ? 'Processing...' : 'Reject'}
                        </button>
                        <button
                          onClick={() => handleApprove(decision.decision_id)}
                          disabled={processingId === decision.decision_id}
                          style={{ padding: '10px 20px', fontSize: '13px', fontWeight: 600, borderRadius: '8px', backgroundColor: '#0f172a', color: '#ffffff', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }} className="hover:bg-gray-800 transition-colors disabled:opacity-50">
                          {processingId === decision.decision_id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <CheckCircle2 style={{ width: '14px', height: '14px' }} />
                          )}
                          Approve Action
                        </button>
                      </div>
                    )}

                    {/* Approved/Executed Actions - Receive Stock (only for replenishment, not pricing) */}
                    {activeTab === 'Approved' && decision.status === 'executed' && decision.decision_type?.includes('replenishment') && decision.execution_result?.fulfillment_status !== 'received' && (
                      <div style={{ padding: '16px 24px', backgroundColor: '#fafbfc', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div className="flex items-center gap-2 text-sm text-blue-600 bg-blue-50 px-3 py-1.5 rounded-md font-medium">
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Stock In Transit
                        </div>

                        <button
                          onClick={async () => {
                            setProcessingId(decision.decision_id);
                            try {
                              // Call receive API (we need to import this or define inline)
                              // For now assumes receiveDecision exists or we use fetch
                              const res = await fetch(`http://localhost:8000/decisions/${decision.decision_id}/receive`, { method: 'POST' });
                              if (res.ok) {
                                const data = await res.json();
                                // Update local state
                                setDecisions(prev => prev.map(d =>
                                  d.decision_id === decision.decision_id
                                    ? { ...d, execution_result: { ...d.execution_result, fulfillment_status: 'received' } }
                                    : d
                                ));
                              }
                            } catch (e) {
                              console.error(e);
                            } finally {
                              setProcessingId(null);
                            }
                          }}
                          disabled={processingId === decision.decision_id}
                          className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700 disabled:opacity-50 flex items-center gap-2 transition-colors"
                        >
                          {processingId === decision.decision_id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Package className="w-4 h-4" />}
                          Receive Stock
                        </button>
                      </div>
                    )}

                    {/* Received State */}
                    {activeTab === 'Approved' && decision.execution_result?.fulfillment_status === 'received' && (
                      <div style={{ padding: '16px 24px', backgroundColor: '#f0fdf4', borderTop: '1px solid #bbf7d0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                        <span className="text-sm font-semibold text-green-700">Stock Received & Inventory Updated</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
