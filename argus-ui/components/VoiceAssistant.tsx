"use client";

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Loader2, Send } from 'lucide-react';
import { useCaseContext } from '@/lib/case-context';

interface VoiceAssistantProps {
    onClose?: () => void;
}

export default function VoiceAssistant({ onClose }: VoiceAssistantProps) {
    const { caseId } = useCaseContext();

    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [response, setResponse] = useState('');
    const [textInput, setTextInput] = useState('');
    const [error, setError] = useState<string | null>(null);

    const recognitionRef = useRef<any>(null);
    const synthRef = useRef<SpeechSynthesisUtterance | null>(null);

    // Initialize speech recognition
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-US';

                recognition.onresult = (event: any) => {
                    const current = event.resultIndex;
                    const transcriptText = event.results[current][0].transcript;
                    setTranscript(transcriptText);

                    if (event.results[current].isFinal) {
                        handleQuery(transcriptText);
                    }
                };

                recognition.onerror = (event: any) => {
                    console.error('Speech recognition error:', event.error);
                    setError(`Voice error: ${event.error}`);
                    setIsListening(false);
                };

                recognition.onend = () => {
                    setIsListening(false);
                };

                recognitionRef.current = recognition;
            } else {
                setError('Speech recognition not supported in this browser. Please use Chrome.');
            }
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.abort();
            }
            window.speechSynthesis?.cancel();
        };
    }, []);

    // Handle voice query
    const handleQuery = useCallback(async (query: string) => {
        if (!query.trim()) return;

        setIsProcessing(true);
        setResponse('');
        setError(null);

        try {
            const res = await fetch('http://localhost:8000/api/voice/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    case_id: caseId || 'demo'
                })
            });

            if (!res.ok) {
                throw new Error('Failed to get response');
            }

            const data = await res.json();
            const responseText = data.response;

            setResponse(responseText);
            speakResponse(responseText);

        } catch (e) {
            console.error('Query error:', e);
            setError('Failed to process query. Please try again.');
            setResponse('');
        } finally {
            setIsProcessing(false);
        }
    }, [caseId]);

    // Play online TTS (Google Translate Hack)
    const playOnlineTTS = (text: string, lang: string) => {
        // Simple chunking to avoid 200 char limit
        const chunkText = (str: string, size: number) => {
            const chunks = [];
            let i = 0;
            while (i < str.length) {
                let end = i + size;
                if (end < str.length) {
                    // Try to break at a period or space
                    const p = str.lastIndexOf('.', end);
                    const s = str.lastIndexOf(' ', end);
                    if (p > i) end = p + 1;
                    else if (s > i) end = s + 1;
                }
                chunks.push(str.slice(i, end));
                i = end;
            }
            return chunks;
        };

        const chunks = chunkText(text, 180);
        let currentChunk = 0;

        const playNextChunk = () => {
            if (currentChunk >= chunks.length) {
                setIsSpeaking(false);
                return;
            }

            const chunk = chunks[currentChunk];
            // 'tl' is target language
            // 'ta' for Tamil, 'hi' for Hindi
            const shortLang = lang.split('-')[0];
            // Use 'gtx' client and add specific params to avoid 404s
            const url = `https://translate.google.com/translate_tts?ie=UTF-8&q=${encodeURIComponent(chunk)}&tl=${shortLang}&client=gtx`;
            const audio = new Audio(url);

            audio.onended = () => {
                currentChunk++;
                playNextChunk();
            };

            audio.onerror = (e) => {
                console.error("Online TTS Error:", e);
                // Don't kill the whole process, maybe just skip or stop
                setIsSpeaking(false);
            };

            audio.play().catch(e => {
                console.error("Audio Playback Error:", e);
                setIsSpeaking(false);
            });
        };

        setIsSpeaking(true);
        playNextChunk();
    };

    // Speak the response
    const speakResponse = (text: string) => {
        if (!text || typeof window === 'undefined') return;

        window.speechSynthesis.cancel();

        // Detect Language
        const isHindi = /[\u0900-\u097F]/.test(text);
        const isTamil = /[\u0B80-\u0BFF]/.test(text);

        let targetLang = 'en-US';
        if (isHindi) targetLang = 'hi-IN';
        if (isTamil) targetLang = 'ta-IN';

        // Try to find a good voice
        let voices = window.speechSynthesis.getVoices();

        // Retry getting voices if empty
        if (voices.length === 0) {
            window.speechSynthesis.onvoiceschanged = () => {
                voices = window.speechSynthesis.getVoices();
            };
        }

        // Helper to normalize locale code
        const normalize = (l: string) => l.replace('_', '-').toLowerCase();
        const targetNormalized = normalize(targetLang);

        // 1. Exact match with "Google" or "Microsoft" (High quality)
        let preferredVoice = voices.find(v =>
            normalize(v.lang) === targetNormalized &&
            (v.name.includes('Google') || v.name.includes('Microsoft'))
        );

        // 2. Any match for the specific language
        if (!preferredVoice) {
            preferredVoice = voices.find(v => normalize(v.lang) === targetNormalized);
        }

        // 3. Match just the language code
        if (!preferredVoice) {
            const shortLang = targetNormalized.split('-')[0];
            preferredVoice = voices.find(v => normalize(v.lang).startsWith(shortLang));
        }

        // 4. Default English Fallback
        if (!preferredVoice && targetLang === 'en-US') {
            preferredVoice = voices.find(v =>
                v.name.includes('Google') ||
                v.name.includes('Microsoft') ||
                v.name.includes('Samantha') ||
                v.lang.startsWith('en')
            );
        }

        // === FALLBACK TO ONLINE TTS IF NATIVE VOICE MISSING FOR HINDI/TAMIL ===
        if (!preferredVoice && (isHindi || isTamil)) {
            console.warn(`No native voice found for ${targetLang}. Using Online Fallback.`);
            playOnlineTTS(text, targetLang);
            return;
        }

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        utterance.lang = targetLang;

        if (preferredVoice) {
            console.log(`Using voice: ${preferredVoice.name} (${preferredVoice.lang}) for ${targetLang}`);
            utterance.voice = preferredVoice;
        } else {
            console.warn(`No voice found for ${targetLang}. Using default.`);
        }

        utterance.onstart = () => setIsSpeaking(true);
        utterance.onend = () => setIsSpeaking(false);
        utterance.onerror = (e) => {
            console.error("TTS Error:", e);
            // Fallback to online if native fails unexpectedly
            if (isHindi || isTamil) {
                console.log("Recovering from native TTS error with Online TTS...");
                playOnlineTTS(text, targetLang);
            } else {
                setIsSpeaking(false);
            }
        };

        synthRef.current = utterance;
        window.speechSynthesis.speak(utterance);
    };

    // Toggle listening
    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
            setIsListening(false);
        } else {
            setTranscript('');
            setError(null);
            recognitionRef.current?.start();
            setIsListening(true);
        }
    };

    // Stop speaking
    const stopSpeaking = () => {
        window.speechSynthesis?.cancel();
        setIsSpeaking(false);
    };

    // Handle text input submit
    const handleTextSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (textInput.trim()) {
            setTranscript(textInput);
            handleQuery(textInput);
            setTextInput('');
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            {/* Main Voice Panel */}
            <div className="bg-slate-900/95 backdrop-blur-xl border border-cyan-500/30 rounded-2xl shadow-2xl shadow-cyan-500/10 w-[380px] overflow-hidden">
                {/* Header */}
                <div className="bg-gradient-to-r from-cyan-600/20 to-purple-600/20 border-b border-cyan-500/20 px-4 py-3">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            <div className={`w-3 h-3 rounded-full ${isSpeaking || isListening ? 'bg-cyan-400 animate-pulse' : 'bg-slate-500'}`} />
                            <span className="text-cyan-400 font-bold tracking-wide">ARGUS VOICE</span>
                        </div>
                        {onClose && (
                            <button onClick={onClose} className="text-slate-400 hover:text-white text-xl">&times;</button>
                        )}
                    </div>
                </div>

                {/* Status */}
                <div className="px-4 py-3 border-b border-slate-800">
                    <div className="text-xs text-slate-500 mb-1">STATUS</div>
                    <div className="text-sm text-slate-300">
                        {isListening && <span className="text-cyan-400">🎤 Listening...</span>}
                        {isProcessing && <span className="text-amber-400">⏳ Processing...</span>}
                        {isSpeaking && <span className="text-green-400">🔊 Speaking...</span>}
                        {!isListening && !isProcessing && !isSpeaking && <span className="text-slate-500">Ready for command</span>}
                    </div>
                </div>

                {/* Transcript */}
                {transcript && (
                    <div className="px-4 py-2 border-b border-slate-800">
                        <div className="text-xs text-slate-500 mb-1">YOU SAID</div>
                        <div className="text-sm text-white">{transcript}</div>
                    </div>
                )}

                {/* Response */}
                {response && (
                    <div className="px-4 py-3 border-b border-slate-800 max-h-48 overflow-y-auto">
                        <div className="text-xs text-slate-500 mb-1">ARGUS RESPONSE</div>
                        <div className="text-sm text-cyan-100 leading-relaxed">{response}</div>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="px-4 py-2 bg-red-500/10 border-b border-red-500/30">
                        <div className="text-sm text-red-400">{error}</div>
                    </div>
                )}

                {/* Text Input */}
                <form onSubmit={handleTextSubmit} className="px-4 py-3 border-b border-slate-800">
                    <div className="flex space-x-2">
                        <input
                            type="text"
                            value={textInput}
                            onChange={(e) => setTextInput(e.target.value)}
                            placeholder="Or type your question..."
                            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
                            disabled={isProcessing}
                        />
                        <button
                            type="submit"
                            disabled={isProcessing || !textInput.trim()}
                            className="bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 disabled:opacity-50 rounded-lg px-3 py-2 transition-colors"
                        >
                            <Send className="h-4 w-4 text-white" />
                        </button>
                    </div>
                </form>

                {/* Controls */}
                <div className="px-4 py-4 flex items-center justify-center space-x-4">
                    {/* Main Mic Button */}
                    <button
                        onClick={toggleListening}
                        disabled={isProcessing}
                        className={`relative w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${isListening
                            ? 'bg-red-500 hover:bg-red-400 shadow-lg shadow-red-500/50'
                            : 'bg-cyan-600 hover:bg-cyan-500 shadow-lg shadow-cyan-500/30'
                            } disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                        {isProcessing ? (
                            <Loader2 className="w-7 h-7 text-white animate-spin" />
                        ) : isListening ? (
                            <MicOff className="w-7 h-7 text-white" />
                        ) : (
                            <Mic className="w-7 h-7 text-white" />
                        )}

                        {isListening && (
                            <span className="absolute inset-0 rounded-full animate-ping bg-red-400 opacity-30" />
                        )}
                    </button>

                    {/* Stop Speaking Button */}
                    {isSpeaking && (
                        <button
                            onClick={stopSpeaking}
                            className="w-12 h-12 rounded-full bg-slate-700 hover:bg-slate-600 flex items-center justify-center transition-colors"
                        >
                            <VolumeX className="w-5 h-5 text-white" />
                        </button>
                    )}
                </div>

                {/* Hint */}
                <div className="px-4 pb-3 text-center">
                    <p className="text-xs text-slate-600">
                        {isListening ? 'Speak now...' : 'Click mic or type to ask ARGUS'}
                    </p>
                </div>
            </div>
        </div>
    );
}
