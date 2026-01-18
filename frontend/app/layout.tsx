import type { Metadata } from 'next';
import '@/styles/globals.css';

import { AgentProvider } from '@/context/AgentContext';

export const metadata: Metadata = {
  title: 'SK Brands Retail AI',
  description: 'Intelligent retail operations powered by AI agents',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased">
        <AgentProvider>
          {children}
        </AgentProvider>
      </body>
    </html>
  );
}
