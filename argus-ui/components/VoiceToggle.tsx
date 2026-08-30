"use client";

import React, { useState } from 'react';
import { Mic } from 'lucide-react';
import dynamic from 'next/dynamic';

// Dynamic import to avoid SSR issues with speech APIs
const VoiceAssistant = dynamic(() => import('@/components/VoiceAssistant'), {
    ssr: false,
    loading: () => null
});

export default function VoiceToggle() {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <>
            {/* Floating Voice Button */}
            {!isOpen && (
                <button
                    onClick={() => setIsOpen(true)}
                    className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 shadow-lg shadow-cyan-500/30 flex items-center justify-center hover:scale-110 transition-transform duration-200 group"
                    title="Open ARGUS Voice Assistant"
                >
                    <Mic className="w-6 h-6 text-white" />
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse" />

                    {/* Tooltip */}
                    <span className="absolute right-16 bg-slate-800 text-white text-xs py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                        ARGUS Voice
                    </span>
                </button>
            )}

            {/* Voice Assistant Panel */}
            {isOpen && (
                <VoiceAssistant onClose={() => setIsOpen(false)} />
            )}
        </>
    );
}
