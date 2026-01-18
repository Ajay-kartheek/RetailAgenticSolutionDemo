'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity } from 'lucide-react';
import { createSSEConnection } from '@/lib/api';
import type { SSEEvent } from '@/lib/types';

interface Message {
  id: string;
  text: string;
  timestamp: Date;
  type: 'progress' | 'start' | 'complete' | 'error';
}

interface ProgressStreamProps {
  isActive: boolean;
  onComplete?: (result: any) => void;
  onError?: (error: Error) => void;
  onProgress?: (message: string) => void;
}

export default function ProgressStream({ isActive, onComplete, onError, onProgress }: ProgressStreamProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const cleanupRef = useRef<(() => void) | null>(null);
  const hasStartedRef = useRef(false);

  useEffect(() => {
    if (isActive && !hasStartedRef.current) {
      hasStartedRef.current = true;
      setIsConnected(true);
      setMessages([]);

      createSSEConnection(
        { include_campaigns: true },
        (event: SSEEvent) => {
          handleSSEEvent(event);
        },
        (error: Error) => {
          console.error('SSE Error:', error);
          setIsConnected(false);
          hasStartedRef.current = false;
          if (onError) {
            onError(error);
          }
        }
      ).then((cleanup) => {
        cleanupRef.current = cleanup;
      });

      return () => {
        if (cleanupRef.current) {
          cleanupRef.current();
        }
        setIsConnected(false);
        hasStartedRef.current = false;
      };
    } else if (!isActive && hasStartedRef.current) {
      // Reset when isActive becomes false
      hasStartedRef.current = false;
    }
  }, [isActive]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSSEEvent = (event: SSEEvent) => {
    const newMessage: Message = {
      id: `${Date.now()}-${Math.random()}`,
      text: '',
      timestamp: new Date(),
      type: event.type === 'progress' || event.type === 'start' || event.type === 'complete' || event.type === 'error'
        ? event.type
        : 'progress',
    };

    switch (event.type) {
      case 'start':
        newMessage.text = `Analysis started (Run ID: ${event.run_id})`;
        break;
      case 'progress':
        // Show thinking if available, otherwise show message
        const displayText = event.thinking
          ? `💭 ${event.thinking}`
          : event.message || 'Processing...';
        newMessage.text = displayText;

        // Notify parent component of progress
        if (onProgress && event.message) {
          onProgress(event.message);
        }
        break;
      case 'complete':
        newMessage.text = 'Analysis completed successfully';
        if (onComplete && event.result) {
          onComplete(event.result);
        }
        setIsConnected(false);
        hasStartedRef.current = false;
        break;
      case 'error':
        newMessage.text = `Error: ${event.error}`;
        setIsConnected(false);
        hasStartedRef.current = false;
        break;
      case 'heartbeat':
        return;
    }

    setMessages((prev) => [...prev, newMessage]);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const messageStyles = {
    progress: 'bg-blue-50 border-l-blue-500',
    start: 'bg-green-50 border-l-green-500',
    complete: 'bg-green-50 border-l-green-600',
    error: 'bg-red-50 border-l-red-500',
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-sm">
      <div className="bg-gray-50 px-5 py-4 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Activity className="w-5 h-5 text-gray-700" />
          <h3 className="text-base font-bold text-gray-900">Live Activity</h3>
        </div>
        {isConnected && (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            <span className="text-xs font-semibold text-red-600 uppercase tracking-wide">Live</span>
          </div>
        )}
      </div>

      <div className="h-[calc(100vh-400px)] min-h-[500px] max-h-[700px] overflow-y-auto p-5 space-y-3">
        {messages.length === 0 && (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <Activity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-sm text-gray-500">No activity yet</p>
              <p className="text-xs text-gray-400 mt-1">Click "Analyze SK Brands" to start</p>
            </div>
          </div>
        )}

        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.02 }}
              className={`
                ${messageStyles[message.type]}
                border-l-4 rounded-lg p-4
              `}
            >
              <div className="text-xs text-gray-500 font-mono mb-1.5">
                {formatTime(message.timestamp)}
              </div>
              <div className="text-sm text-gray-900 font-medium">{message.text}</div>
            </motion.div>
          ))}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
