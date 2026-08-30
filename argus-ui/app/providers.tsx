"use client";

import { CaseProvider } from '@/lib/case-context';
import VoiceToggle from '@/components/VoiceToggle';

export function Providers({ children }: { children: React.ReactNode }) {
    return (
        <CaseProvider>
            {children}
            <VoiceToggle />
        </CaseProvider>
    );
}
