'use client';

import Sidebar from '@/components/Sidebar';
import { useState } from 'react';

interface ClientLayoutProps {
    children: React.ReactNode;
    activeAgentsCount?: number;
}

export default function ClientLayout({ children, activeAgentsCount = 0 }: ClientLayoutProps) {
    return (
        <div className="flex h-screen bg-gray-50">
            <Sidebar activeAgentsCount={activeAgentsCount} isSystemOperational={true} />
            <main className="flex-1 overflow-hidden">
                {children}
            </main>
        </div>
    );
}
