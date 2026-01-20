'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, TrendingUp, Package, AlertTriangle, ChevronDown, Loader2, BarChart3 } from 'lucide-react';
import { useDataContext } from '@/context/DataContext';
import type { Store, DemandInsight } from '@/lib/types';

export default function DemandAgentPage() {
  const [stores, setStores] = useState<Store[]>([]);
  const [selectedStore, setSelectedStore] = useState<string>('');
  const [insights, setInsights] = useState<DemandInsight[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const { fetchStores, fetchDemandInsights } = useDataContext();

  // Fetch stores on mount (cached)
  useEffect(() => {
    const loadStores = async () => {
      try {
        const storeData = await fetchStores();
        setStores(storeData);
      } catch (err) {
        console.error('Failed to fetch stores:', err);
      }
    };
    loadStores();
  }, [fetchStores]);

  // Fetch insights when store selection changes (cached by storeId)
  useEffect(() => {
    const loadInsights = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchDemandInsights(selectedStore || undefined);
        setInsights(data.insights || []);
        setSummary(data.summary || null);
      } catch (err) {
        console.error('Failed to fetch demand insights:', err);
        setError('Failed to load demand insights. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    loadInsights();
  }, [selectedStore, fetchDemandInsights]);

  const getStockStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      in_stock: 'bg-green-100 text-green-700 border-green-200',
      low_stock: 'bg-yellow-100 text-yellow-700 border-yellow-200',
      out_of_stock: 'bg-red-100 text-red-700 border-red-200',
      overstocked: 'bg-blue-100 text-blue-700 border-blue-200',
    };
    const labels: Record<string, string> = {
      in_stock: 'In Stock',
      low_stock: 'Low Stock',
      out_of_stock: 'Out of Stock',
      overstocked: 'Overstocked',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${styles[status] || styles.in_stock}`}>
        {labels[status] || status}
      </span>
    );
  };

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.9) return 'bg-green-100 text-green-700';
    if (confidence >= 0.7) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  return (
    <div className="space-y-6">
      {/* Back Link */}
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-blue-600 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between"
      >
        <div className="flex items-start gap-4">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
            <TrendingUp className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Demand Agent</h1>
            <p className="text-gray-600 mt-1">
              Analyzes ML demand forecasts and provides actionable insights
            </p>
          </div>
        </div>

        {/* Store Selector */}
        <div className="relative">
          <select
            value={selectedStore}
            onChange={(e) => setSelectedStore(e.target.value)}
            className="appearance-none bg-white border border-gray-300 rounded-xl px-4 py-3 pr-10 text-sm font-medium text-gray-700 shadow-sm hover:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 cursor-pointer min-w-[200px]"
          >
            <option value="">All Stores</option>
            {stores.map((store) => (
              <option key={store.store_id} value={store.store_id}>
                {store.store_name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
        </div>
      </motion.div>

      {/* Summary Cards */}
      {summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4"
        >
          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <Package className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Items</p>
                <p className="text-xl font-bold text-gray-900">{summary.total_items}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Total Demand</p>
                <p className="text-xl font-bold text-gray-900">{summary.total_forecasted_demand?.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Avg Confidence</p>
                <p className="text-xl font-bold text-gray-900">{(summary.average_confidence * 100).toFixed(0)}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
                <AlertTriangle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-500">Low Stock Items</p>
                <p className="text-xl font-bold text-gray-900">{summary.low_stock_items}</p>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Data Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden"
      >
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900">Demand Forecast Analysis</h2>
          <p className="text-sm text-gray-500 mt-1">
            {selectedStore
              ? `Showing forecasts for ${stores.find(s => s.store_id === selectedStore)?.store_name || selectedStore}`
              : 'Showing forecasts for all stores'
            }
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            <span className="ml-3 text-gray-600">Loading demand insights...</span>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-16 text-red-600">
            <AlertTriangle className="w-6 h-6 mr-2" />
            {error}
          </div>
        ) : insights.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-gray-500">
            <Package className="w-12 h-12 mb-4 text-gray-300" />
            <p>No demand forecasts available</p>
            <p className="text-sm text-gray-400 mt-1">Run an analysis from the dashboard to generate forecasts</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Product</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Category</th>
                  {!selectedStore && (
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Store</th>
                  )}
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Forecasted Demand</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Current Stock</th>
                  <th className="px-6 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Stock Status</th>
                  <th className="px-6 py-3 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Confidence</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Season</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {insights.map((insight, index) => (
                  <motion.tr
                    key={`${insight.store_id}-${insight.product_id}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.02 }}
                    className="hover:bg-gray-50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{insight.product_name}</p>
                        <p className="text-xs text-gray-500">{insight.product_id}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{insight.category}</td>
                    {!selectedStore && (
                      <td className="px-6 py-4 text-sm text-gray-600">{insight.store_id}</td>
                    )}
                    <td className="px-6 py-4 text-right">
                      <span className="font-semibold text-gray-900">{insight.forecasted_demand.toLocaleString()}</span>
                      <span className="text-xs text-gray-500 ml-1">units</span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className={`font-medium ${insight.current_stock < insight.forecasted_demand * 0.3 ? 'text-red-600' : 'text-gray-900'}`}>
                        {insight.current_stock.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      {getStockStatusBadge(insight.stock_status)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceBadge(insight.confidence)}`}>
                        {(insight.confidence * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{insight.season}</td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
}
