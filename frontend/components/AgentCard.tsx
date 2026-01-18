'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import type { AgentInfo } from '@/lib/types';

interface AgentCardProps {
  agent: AgentInfo;
  index: number;
}

const statusStyles = {
  idle: {
    border: 'border-gray-300',
    bg: 'bg-white',
    badge: 'bg-gray-500/20 text-gray-600',
  },
  running: {
    border: 'border-blue-400',
    bg: 'bg-gradient-to-br from-blue-50 to-white',
    badge: 'bg-blue-500/20 text-blue-600',
  },
  completed: {
    border: 'border-green-400',
    bg: 'bg-gradient-to-br from-green-50 to-white',
    badge: 'bg-green-500/20 text-green-600',
  },
  error: {
    border: 'border-red-400',
    bg: 'bg-gradient-to-br from-red-50 to-white',
    badge: 'bg-red-500/20 text-red-600',
  },
};

export default function AgentCard({ agent, index }: AgentCardProps) {
  const styles = statusStyles[agent.status];

  return (
    <Link href={`/agents/${agent.id}`}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0, scale: agent.status === 'running' ? 1.02 : 1 }}
        transition={{
          delay: index * 0.05,
          type: 'spring',
          stiffness: 400,
          damping: 10,
        }}
        className={`
          ${styles.bg} ${styles.border}
          border rounded-2xl p-6
          hover:shadow-lg hover:-translate-y-1
          transition-all duration-200
          cursor-pointer
          relative overflow-hidden
        `}
      >
        {/* Glow effect for running state */}
        {agent.status === 'running' && (
          <div className="absolute inset-0 bg-blue-400/10 animate-pulse pointer-events-none" />
        )}

        <div className="flex gap-4 relative z-10">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
            style={{ backgroundColor: agent.color + '20' }}
          >
            {agent.icon}
          </div>

          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">{agent.description}</p>

            <div className="mt-3">
              <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${styles.badge}`}>
                {agent.status === 'running' && (
                  <span className="w-2 h-2 bg-current rounded-full animate-pulse" />
                )}
                {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
              </span>
            </div>

            {agent.status === 'running' && agent.progress > 0 && (
              <div className="mt-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-gray-700">Progress</span>
                  <span className="text-xs font-semibold text-blue-600">{agent.progress}%</span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-600"
                    initial={{ width: 0 }}
                    animate={{ width: `${agent.progress}%` }}
                    transition={{ type: 'spring', stiffness: 100 }}
                  />
                </div>
              </div>
            )}

            {agent.status === 'completed' && (
              <div className="mt-3 flex items-center gap-2 text-green-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-sm font-medium">Complete</span>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
