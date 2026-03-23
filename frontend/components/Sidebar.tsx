'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Brain,
  ClipboardCheck,
  TrendingUp,
  ChevronLeft,
  ChevronRight,
  Zap,
  Database,
  Loader2,
  CheckCircle2,
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Agent Network', href: '/agents', icon: Brain },
  { name: 'Decisions', href: '/decisions', icon: ClipboardCheck },
  { name: 'Campaigns & Trends', href: '/trends', icon: TrendingUp },
];

interface SidebarProps {
  activeAgentsCount?: number;
  isSystemOperational?: boolean;
}

export default function Sidebar({
  activeAgentsCount = 0,
  isSystemOperational = true
}: SidebarProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedStatus, setSeedStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const pathname = usePathname();

  const handleSeedDemo = async () => {
    if (isSeeding) return;
    setIsSeeding(true);
    setSeedStatus('idle');
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${API_URL}/demo/seed`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: 4 }),
      });
      if (!res.ok) throw new Error('Seed failed');
      setSeedStatus('success');
      setTimeout(() => setSeedStatus('idle'), 3000);
    } catch (err) {
      console.error('Seed error:', err);
      setSeedStatus('error');
      setTimeout(() => setSeedStatus('idle'), 3000);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <motion.aside
      initial={false}
      animate={{ width: isCollapsed ? 72 : 240 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      style={{
        backgroundColor: '#0f172a',
        borderRight: '1px solid #1e293b'
      }}
      className="h-screen flex flex-col relative z-30 shrink-0"
    >
      {/* Logo Section */}
      <div style={{ height: '64px', padding: '0 20px' }} className="flex items-center shrink-0">
        <div style={{ gap: '12px' }} className="flex items-center overflow-hidden">
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              overflow: 'hidden'
            }}
            className="flex items-center justify-center shrink-0"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo.png" alt="Logo" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
          <AnimatePresence mode="wait">
            {!isCollapsed && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.15 }}
                className="flex flex-col justify-center"
              >
                <h1 style={{ fontSize: '15px', fontWeight: 600, color: '#ffffff', lineHeight: 1.2 }}>SK Retail AI</h1>
                <span style={{ fontSize: '10px', fontWeight: 600, color: '#64748b', letterSpacing: '0.5px', marginTop: '2px' }}>COMMAND CENTER</span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ padding: '16px 12px', flex: 1 }} className="overflow-y-auto">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const isActive = pathname === item.href ||
              (item.href !== '/' && pathname.startsWith(item.href));
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '10px 12px',
                  borderRadius: '8px',
                  backgroundColor: isActive ? 'rgba(255,255,255,0.1)' : 'transparent',
                  color: isActive ? '#ffffff' : '#94a3b8',
                  textDecoration: 'none',
                  transition: 'all 0.15s ease'
                }}
                className="hover:bg-white/5"
              >
                <Icon
                  style={{
                    width: '18px',
                    height: '18px',
                    color: isActive ? '#60a5fa' : '#64748b',
                    flexShrink: 0
                  }}
                />
                <AnimatePresence mode="wait">
                  {!isCollapsed && (
                    <motion.span
                      initial={{ opacity: 0, x: -5 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -5 }}
                      transition={{ duration: 0.15 }}
                      style={{ fontSize: '13px', fontWeight: isActive ? 500 : 400 }}
                    >
                      {item.name}
                    </motion.span>
                  )}
                </AnimatePresence>
              </Link>
            );
          })}
        </div>
      </nav>

      {/* Seed Demo Data Button */}
      <div style={{ padding: '0 16px 8px' }} className="shrink-0">
        <button
          onClick={handleSeedDemo}
          disabled={isSeeding}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: isCollapsed ? 'center' : 'flex-start',
            gap: '10px',
            padding: isCollapsed ? '10px' : '10px 12px',
            borderRadius: '8px',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            background: seedStatus === 'success'
              ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1))'
              : seedStatus === 'error'
                ? 'linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1))'
                : 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1))',
            color: seedStatus === 'success' ? '#34d399' : seedStatus === 'error' ? '#f87171' : '#a5b4fc',
            cursor: isSeeding ? 'wait' : 'pointer',
            transition: 'all 0.2s ease',
            fontSize: '13px',
            fontWeight: 500,
            opacity: isSeeding ? 0.7 : 1,
          }}
          className="hover:opacity-90"
          title="Load Scenario 4: Comprehensive Retail Analysis"
        >
          {isSeeding ? (
            <Loader2 size={16} className="animate-spin" style={{ flexShrink: 0 }} />
          ) : seedStatus === 'success' ? (
            <CheckCircle2 size={16} style={{ flexShrink: 0 }} />
          ) : (
            <Database size={16} style={{ flexShrink: 0 }} />
          )}
          <AnimatePresence mode="wait">
            {!isCollapsed && (
              <motion.span
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -5 }}
                transition={{ duration: 0.15 }}
                style={{ whiteSpace: 'nowrap' }}
              >
                {isSeeding ? 'Seeding...' : seedStatus === 'success' ? 'Data Loaded!' : seedStatus === 'error' ? 'Seed Failed' : 'Seed Demo Data'}
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>

      {/* Footer Status */}
      <div style={{ padding: '16px' }} className="shrink-0">
        <div
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.5)',
            borderRadius: '10px',
            padding: '12px',
            border: '1px solid rgba(51, 65, 85, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }} className="overflow-hidden">
            <div className="relative shrink-0">
              <div
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: activeAgentsCount > 0 ? '#10b981' : '#475569'
                }}
              />
              {activeAgentsCount > 0 && (
                <div
                  style={{
                    position: 'absolute',
                    inset: 0,
                    borderRadius: '50%',
                    backgroundColor: '#10b981',
                    opacity: 0.75
                  }}
                  className="animate-ping"
                />
              )}
            </div>

            <AnimatePresence mode="wait">
              {!isCollapsed && (
                <motion.div
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  className="overflow-hidden"
                >
                  <span style={{ fontSize: '12px', fontWeight: 500, color: '#cbd5e1', whiteSpace: 'nowrap' }}>
                    {activeAgentsCount > 0 ? `${activeAgentsCount} Agent${activeAgentsCount > 1 ? 's' : ''} Active` : 'Standby'}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            style={{
              padding: '4px',
              color: '#64748b',
              background: 'none',
              border: 'none',
              cursor: 'pointer'
            }}
            className="hover:text-white transition-colors"
          >
            {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
        </div>
      </div>
    </motion.aside>
  );
}
