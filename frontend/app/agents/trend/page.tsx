'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';

export default function DemandAgentPage() {
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
        className="flex items-start gap-4"
      >
        <div className="w-16 h-16 rounded-2xl bg-blue-500/20 flex items-center justify-center text-4xl">
          📊
        </div>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Demand Agent</h1>
          <p className="text-gray-600 mt-1">
            Retrieves and analyzes demand forecasts from ML models for accurate demand prediction
          </p>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Info Cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white border border-gray-300 rounded-2xl p-6"
        >
          <h3 className="font-semibold text-gray-900 mb-2">Data Source</h3>
          <p className="text-sm text-gray-600">
            Retrieves ML-generated demand forecasts from DynamoDB (mocked for demo)
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-white border border-gray-300 rounded-2xl p-6"
        >
          <h3 className="font-semibold text-gray-900 mb-2">Forecast Period</h3>
          <p className="text-sm text-gray-600">
            Generates predictions for Q1 2026 across all stores and products
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white border border-gray-300 rounded-2xl p-6"
        >
          <h3 className="font-semibold text-gray-900 mb-2">Output</h3>
          <p className="text-sm text-gray-600">
            Predicted demand quantities with confidence scores for downstream agents
          </p>
        </motion.div>
      </div>

      {/* Latest Forecasts Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="bg-white border border-gray-300 rounded-2xl p-6"
      >
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Latest Forecasts</h2>

        <div className="bg-gray-50 border border-gray-200 rounded-xl p-8 text-center">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-gray-600 mb-4">
            Run an analysis from the dashboard to see demand forecasts.
          </p>
          <Link
            href="/"
            className="inline-block px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-semibold rounded-xl hover:shadow-lg hover:scale-105 transition-all"
          >
            Go to Dashboard
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
