'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Package, Search, Filter, AlertTriangle } from 'lucide-react';
import { useState } from 'react';

interface StoreAnalyticsModalProps {
    isOpen: boolean;
    onClose: () => void;
    store: { name: string; id: string } | null;
    inventory: any[];
    products: Record<string, string>;
}

export default function StoreAnalyticsModal({ isOpen, onClose, store, inventory, products }: StoreAnalyticsModalProps) {
    const [searchTerm, setSearchTerm] = useState('');
    const [filterStatus, setFilterStatus] = useState<string>('all');

    if (!store) return null;

    // Filter logic
    const filteredInventory = inventory.filter(item => {
        const productName = products[item.product_id] || item.product_id;
        const matchesSearch = productName.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.product_id.toLowerCase().includes(searchTerm.toLowerCase());

        // @ts-ignore
        const itemStatus = item.stock_status ?? item.availability_status ?? 'in_stock';
        const matchesFilter = filterStatus === 'all' || itemStatus === filterStatus ||
            (filterStatus === 'low_stock' && itemStatus === 'low_stock');

        return matchesSearch && matchesFilter;
    });

    // Summary stats
    const totalItems = inventory.length;
    // @ts-ignore
    const lowStockCount = inventory.filter(i => (i.stock_status ?? i.availability_status) === 'low_stock').length;
    // @ts-ignore
    const outOfStockCount = inventory.filter(i => (i.stock_status ?? i.availability_status) === 'out_of_stock').length;

    return (
        <AnimatePresence>
            {isOpen && (
                <div style={{ position: 'fixed', inset: 0, zIndex: 50, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        style={{ position: 'absolute', inset: 0, backgroundColor: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)' }}
                    />

                    {/* Modal */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ type: "spring", duration: 0.4 }}
                        style={{
                            position: 'relative',
                            backgroundColor: '#ffffff',
                            width: '100%',
                            maxWidth: '900px',
                            maxHeight: '85vh',
                            borderRadius: '16px',
                            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                            overflow: 'hidden',
                            display: 'flex',
                            flexDirection: 'column'
                        }}
                    >
                        {/* Header */}
                        <div style={{
                            padding: '20px 24px',
                            borderBottom: '1px solid #f1f5f9',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            backgroundColor: '#ffffff'
                        }}>
                            <div>
                                <h2 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a', margin: 0 }}>{store.name}</h2>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                                    <span style={{ fontSize: '11px', fontFamily: 'monospace', color: '#64748b', backgroundColor: '#f1f5f9', padding: '3px 8px', borderRadius: '4px' }}>{store.id}</span>
                                    <span style={{ fontSize: '13px', color: '#94a3b8' }}>•</span>
                                    <span style={{ fontSize: '13px', color: '#64748b' }}>Real-time Inventory Analytics</span>
                                </div>
                            </div>
                            <button
                                onClick={onClose}
                                style={{ padding: '8px', borderRadius: '8px', border: 'none', backgroundColor: 'transparent', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                className="hover:bg-gray-100 transition-colors"
                            >
                                <X style={{ width: '20px', height: '20px', color: '#64748b' }} />
                            </button>
                        </div>

                        {/* Stats Row */}
                        <div style={{ padding: '16px 24px', backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0', display: 'flex', gap: '16px' }}>
                            <div style={{ padding: '12px 16px', backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', flex: 1 }}>
                                <div style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>{totalItems}</div>
                                <div style={{ fontSize: '11px', fontWeight: 600, color: '#94a3b8', letterSpacing: '0.5px', marginTop: '2px' }}>TOTAL SKUS</div>
                            </div>
                            <div style={{ padding: '12px 16px', backgroundColor: '#fef2f2', borderRadius: '10px', border: '1px solid #fecaca', flex: 1 }}>
                                <div style={{ fontSize: '20px', fontWeight: 700, color: '#dc2626' }}>{lowStockCount}</div>
                                <div style={{ fontSize: '11px', fontWeight: 600, color: '#dc2626', letterSpacing: '0.5px', marginTop: '2px' }}>LOW STOCK</div>
                            </div>
                            <div style={{ padding: '12px 16px', backgroundColor: '#fefce8', borderRadius: '10px', border: '1px solid #fef08a', flex: 1 }}>
                                <div style={{ fontSize: '20px', fontWeight: 700, color: '#ca8a04' }}>{outOfStockCount}</div>
                                <div style={{ fontSize: '11px', fontWeight: 600, color: '#ca8a04', letterSpacing: '0.5px', marginTop: '2px' }}>OUT OF STOCK</div>
                            </div>
                        </div>

                        {/* Search and Filter */}
                        <div style={{ padding: '16px 24px', borderBottom: '1px solid #e2e8f0', display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <div style={{ flex: 1, position: 'relative' }}>
                                <Search style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', width: '16px', height: '16px', color: '#94a3b8' }} />
                                <input
                                    type="text"
                                    placeholder="Search by product name or ID..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    style={{
                                        width: '100%',
                                        padding: '10px 12px 10px 40px',
                                        fontSize: '13px',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '8px',
                                        outline: 'none',
                                        backgroundColor: '#ffffff'
                                    }}
                                    className="focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Filter style={{ width: '16px', height: '16px', color: '#64748b' }} />
                                <select
                                    value={filterStatus}
                                    onChange={(e) => setFilterStatus(e.target.value)}
                                    style={{
                                        padding: '10px 14px',
                                        fontSize: '13px',
                                        fontWeight: 500,
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '8px',
                                        backgroundColor: '#ffffff',
                                        color: '#475569',
                                        cursor: 'pointer',
                                        outline: 'none'
                                    }}
                                >
                                    <option value="all">All Status</option>
                                    <option value="low_stock">Low Stock</option>
                                    <option value="in_stock">In Stock</option>
                                    <option value="out_of_stock">Out of Stock</option>
                                </select>
                            </div>
                        </div>

                        {/* Table */}
                        <div style={{ flex: 1, overflowY: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead style={{ backgroundColor: '#f8fafc', position: 'sticky', top: 0, zIndex: 10 }}>
                                    <tr>
                                        <th style={{ padding: '14px 24px', textAlign: 'left', fontSize: '11px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', borderBottom: '1px solid #e2e8f0' }}>PRODUCT</th>
                                        <th style={{ padding: '14px 24px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', borderBottom: '1px solid #e2e8f0', width: '100px' }}>SIZE</th>
                                        <th style={{ padding: '14px 24px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', borderBottom: '1px solid #e2e8f0', width: '100px' }}>COLOR</th>
                                        <th style={{ padding: '14px 24px', textAlign: 'right', fontSize: '11px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', borderBottom: '1px solid #e2e8f0', width: '100px' }}>STOCK</th>
                                        <th style={{ padding: '14px 24px', textAlign: 'center', fontSize: '11px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', borderBottom: '1px solid #e2e8f0', width: '120px' }}>STATUS</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredInventory.length > 0 ? (
                                        filteredInventory.map((item, idx) => {
                                            const name = products[item.product_id] || item.product_id;

                                            // Parse variant info
                                            const size = item.size || (item.sku ? item.sku.split('#')[1] : '-');
                                            const color = item.color || (item.sku ? item.sku.split('#')[2] : '-');

                                            // Legacy fallbacks
                                            // @ts-ignore
                                            const currentStock = item.current_stock ?? item.quantity ?? 0;
                                            // @ts-ignore
                                            const status = item.stock_status ?? item.availability_status ?? 'in_stock';

                                            // Status styling
                                            const statusConfig: Record<string, { bg: string; color: string; label: string }> = {
                                                low_stock: { bg: '#fef2f2', color: '#dc2626', label: 'Low Stock' },
                                                out_of_stock: { bg: '#fefce8', color: '#ca8a04', label: 'Out of Stock' },
                                                in_stock: { bg: '#f0fdf4', color: '#16a34a', label: 'In Stock' }
                                            };
                                            const statusStyle = statusConfig[status] || { bg: '#f1f5f9', color: '#64748b', label: status };

                                            return (
                                                <motion.tr
                                                    key={`${item.product_id}-${idx}`}
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    transition={{ delay: Math.min(idx * 0.02, 0.5) }}
                                                    style={{ borderBottom: '1px solid #f1f5f9' }}
                                                    className="hover:bg-gray-50 transition-colors"
                                                >
                                                    <td style={{ padding: '16px 24px' }}>
                                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                            <div style={{
                                                                width: '36px',
                                                                height: '36px',
                                                                borderRadius: '8px',
                                                                backgroundColor: '#f1f5f9',
                                                                display: 'flex',
                                                                alignItems: 'center',
                                                                justifyContent: 'center',
                                                                flexShrink: 0
                                                            }}>
                                                                <Package style={{ width: '18px', height: '18px', color: '#94a3b8' }} />
                                                            </div>
                                                            <div>
                                                                <div style={{ fontSize: '14px', fontWeight: 600, color: '#0f172a' }}>{name}</div>
                                                                <div style={{ fontSize: '11px', fontFamily: 'monospace', color: '#94a3b8', marginTop: '2px' }}>{item.product_id}</div>
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td style={{ padding: '16px 24px', textAlign: 'center' }}>
                                                        <span style={{
                                                            fontSize: '12px',
                                                            fontWeight: 600,
                                                            color: '#475569',
                                                            backgroundColor: '#f1f5f9',
                                                            padding: '4px 10px',
                                                            borderRadius: '4px'
                                                        }}>
                                                            {String(size || '-')}
                                                        </span>
                                                    </td>
                                                    <td style={{ padding: '16px 24px', textAlign: 'center' }}>
                                                        <span style={{ fontSize: '13px', color: '#64748b' }}>{String(color || '-')}</span>
                                                    </td>
                                                    <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                                                        <span style={{
                                                            fontSize: '15px',
                                                            fontWeight: 700,
                                                            color: currentStock < 10 ? '#dc2626' : '#0f172a'
                                                        }}>
                                                            {currentStock}
                                                        </span>
                                                    </td>
                                                    <td style={{ padding: '16px 24px', textAlign: 'center' }}>
                                                        <span style={{
                                                            display: 'inline-flex',
                                                            alignItems: 'center',
                                                            gap: '4px',
                                                            padding: '5px 10px',
                                                            borderRadius: '6px',
                                                            fontSize: '11px',
                                                            fontWeight: 600,
                                                            backgroundColor: statusStyle.bg,
                                                            color: statusStyle.color
                                                        }}>
                                                            {status === 'low_stock' && <AlertTriangle style={{ width: '12px', height: '12px' }} />}
                                                            {statusStyle.label}
                                                        </span>
                                                    </td>
                                                </motion.tr>
                                            );
                                        })
                                    ) : (
                                        <tr>
                                            <td colSpan={5} style={{ padding: '48px 24px', textAlign: 'center' }}>
                                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', color: '#94a3b8' }}>
                                                    <Search style={{ width: '32px', height: '32px', opacity: 0.3, marginBottom: '12px' }} />
                                                    <p style={{ fontSize: '14px', fontWeight: 500, margin: 0 }}>No products found</p>
                                                    <p style={{ fontSize: '12px', marginTop: '4px' }}>Try adjusting your search or filters</p>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        {/* Footer */}
                        <div style={{
                            padding: '12px 24px',
                            borderTop: '1px solid #e2e8f0',
                            backgroundColor: '#f8fafc',
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            fontSize: '12px',
                            color: '#64748b'
                        }}>
                            <span>Showing {filteredInventory.length} of {totalItems} items</span>
                            <span>Last updated: {new Date().toLocaleTimeString()}</span>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
}
