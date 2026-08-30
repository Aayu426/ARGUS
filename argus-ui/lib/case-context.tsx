"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

// Types matching backend UnifiedCaseState
export interface Entity {
    name: string;
    type: string;
    source: string;
    risk: string;
    color?: string;
}

export interface Location {
    address: string;
    latitude: number;
    longitude: number;
    timestamp?: string;
    source_file: string;
    map_url: string;
}

export interface Scenario {
    entity: string;
    entity_type: string;
    location: string;
    coordinates?: [number, number];
    timestamp?: string;
    description: string;
    risk_level: string;
    color: string;
    evidence_source: string;
}

export interface ImageAnalysis {
    file_name: string;
    file_path: string;
    gan_probability: number;
    ela_risk: string;
    is_authentic: boolean;
    geotag?: Location;
    device_info: Record<string, string>;
    warnings: string[];
}

export interface TextAnalysis {
    source_file: string;
    text_preview: string;
    language: string;
    entities: { name: string; type: string }[];
    threat_score: number;
    key_phrases: string[];
    stylometry_match?: string;
    stylometry_score: number;
}

export interface GraphNode {
    id: string;
    label: string;
    type: string;
    risk: string;
}

export interface GraphEdge {
    from: string;
    to: string;
    type: string;
    weight: number;
}

export interface FinalAttribution {
    suspect: string;
    aliases: string[];
    probable_location: string;
    role: string;
    confidence_score: number;
    evidence_summary: string;
    risk_breakdown: {
        nlp_score: number;
        graph_score: number;
        image_score: number;
        location_score: number;
    };
}

export interface CaseState {
    case_id: string;
    status: string;
    entities: Entity[];
    locations: Location[];
    scenarios: Scenario[];
    image_analyses: ImageAnalysis[];
    text_analyses: TextAnalysis[];
    graph_nodes: GraphNode[];
    graph_edges: GraphEdge[];
    graph_metrics: any;
    final_attribution?: FinalAttribution;
    overall_risk_score: number;
    evidence_files?: string[];  // List of evidence file names
}


interface CaseContextType {
    caseId: string | null;
    caseState: CaseState | null;
    isLoading: boolean;
    isProcessing: boolean;
    error: string | null;

    // Actions
    initCase: () => Promise<string | null>;
    loadDemoData: () => Promise<boolean>;
    processAllEvidence: () => Promise<boolean>;
    refreshCaseState: () => Promise<void>;

    // Getters for specific data
    getEntities: () => Entity[];
    getScenarios: () => Scenario[];
    getLocations: () => Location[];
    getImageAnalyses: () => ImageAnalysis[];
    getTextAnalyses: () => TextAnalysis[];
    getGraphData: () => { nodes: GraphNode[], edges: GraphEdge[], metrics: any };
    getAttribution: () => FinalAttribution | undefined;
}

const API_BASE = "http://localhost:8000/api";

const CaseContext = createContext<CaseContextType | undefined>(undefined);

export function CaseProvider({ children }: { children: ReactNode }) {
    const [caseId, setCaseId] = useState<string | null>(null);
    const [caseState, setCaseState] = useState<CaseState | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Initialize or restore case
    const initCase = useCallback(async (): Promise<string | null> => {
        setIsLoading(true);
        setError(null);

        try {
            // Check localStorage first
            const savedCaseId = localStorage.getItem('argus_case_id');
            if (savedCaseId) {
                setCaseId(savedCaseId);

                // Try to load existing state
                const stateRes = await fetch(`${API_BASE}/case/${savedCaseId}/state`);
                if (stateRes.ok) {
                    const state = await stateRes.json();
                    setCaseState(state);
                }

                setIsLoading(false);
                return savedCaseId;
            }

            // Create new case
            const res = await fetch(`${API_BASE}/case/new`, { method: "POST" });
            const data = await res.json();

            if (data.case_id) {
                setCaseId(data.case_id);
                localStorage.setItem('argus_case_id', data.case_id);
                setIsLoading(false);
                return data.case_id;
            }
        } catch (e) {
            console.error("Init case error:", e);
            setError("Failed to initialize case");
        }

        setIsLoading(false);
        return null;
    }, []);

    // Load demo data
    const loadDemoData = useCallback(async (): Promise<boolean> => {
        if (!caseId) {
            const newId = await initCase();
            if (!newId) return false;
        }

        const id = caseId || localStorage.getItem('argus_case_id');
        if (!id) return false;

        setIsLoading(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE}/case/${id}/load-demo`, { method: "POST" });

            if (res.ok) {
                // Refresh state after loading demo
                await refreshCaseState();
                return true;
            }
        } catch (e) {
            console.error("Load demo error:", e);
            setError("Failed to load demo data");
        }

        setIsLoading(false);
        return false;
    }, [caseId, initCase]);

    // Process all evidence
    const processAllEvidence = useCallback(async (): Promise<boolean> => {
        const id = caseId || localStorage.getItem('argus_case_id');
        if (!id) return false;

        setIsProcessing(true);
        setError(null);

        try {
            const res = await fetch(`${API_BASE}/case/${id}/process-all`, { method: "POST" });

            if (res.ok) {
                // Refresh state after processing
                await refreshCaseState();
                setIsProcessing(false);
                return true;
            }
        } catch (e) {
            console.error("Process error:", e);
            setError("Failed to process evidence");
        }

        setIsProcessing(false);
        return false;
    }, [caseId]);

    // Refresh case state from backend
    const refreshCaseState = useCallback(async (): Promise<void> => {
        const id = caseId || localStorage.getItem('argus_case_id');
        if (!id) return;

        setIsLoading(true);

        try {
            const res = await fetch(`${API_BASE}/case/${id}/state`);
            if (res.ok) {
                const state = await res.json();
                setCaseState(state);
            }
        } catch (e) {
            console.error("Refresh error:", e);
        }

        setIsLoading(false);
    }, [caseId]);

    // Getters
    const getEntities = useCallback(() => caseState?.entities || [], [caseState]);
    const getScenarios = useCallback(() => caseState?.scenarios || [], [caseState]);
    const getLocations = useCallback(() => caseState?.locations || [], [caseState]);
    const getImageAnalyses = useCallback(() => caseState?.image_analyses || [], [caseState]);
    const getTextAnalyses = useCallback(() => caseState?.text_analyses || [], [caseState]);
    const getGraphData = useCallback(() => ({
        nodes: caseState?.graph_nodes || [],
        edges: caseState?.graph_edges || [],
        metrics: caseState?.graph_metrics || {}
    }), [caseState]);
    const getAttribution = useCallback(() => caseState?.final_attribution, [caseState]);

    return (
        <CaseContext.Provider value={{
            caseId,
            caseState,
            isLoading,
            isProcessing,
            error,
            initCase,
            loadDemoData,
            processAllEvidence,
            refreshCaseState,
            getEntities,
            getScenarios,
            getLocations,
            getImageAnalyses,
            getTextAnalyses,
            getGraphData,
            getAttribution
        }}>
            {children}
        </CaseContext.Provider>
    );
}

export function useCaseContext() {
    const context = useContext(CaseContext);
    if (context === undefined) {
        throw new Error('useCaseContext must be used within a CaseProvider');
    }
    return context;
}
