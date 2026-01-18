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
  Settings,
  ChevronLeft,
  ChevronRight,
  Zap,
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
}

const navItems: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Agent Insights', href: '/agents', icon: Brain },
  { name: 'Decisions', href: '/decisions', icon: ClipboardCheck },
  { name: 'Trends & Campaigns', href: '/trends', icon: TrendingUp },
  { name: 'Settings', href: '/settings', icon: Settings },
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
  const pathname = usePathname();

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
              backgroundColor: '#3b82f6'
            }}
            className="flex items-center justify-center shrink-0 text-white"
          >
            <Zap style={{ width: '20px', height: '20px' }} className="fill-current" />
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
