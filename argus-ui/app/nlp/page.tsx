"use client";

import { useEffect, useState } from 'react';
import { FileText, User, AlertTriangle, CheckCircle, Loader2, RefreshCw, Tag, Brain, Search } from 'lucide-react';
import { motion } from 'framer-motion';
import { useCaseContext } from '@/lib/case-context';

export default function NLPAnalysis() {
    const {
        caseState,
        isLoading,
        getTextAnalyses,
        getEntities,
        getScenarios,
        refreshCaseState
    } = useCaseContext();

    const textAnalyses = getTextAnalyses();
    const entities = getEntities();
    const scenarios = getScenarios();

    // Group entities by type
    const entityGroups = entities.reduce((acc, entity) => {
        const type = entity.type || 'OTHER';
        if (!acc[type]) acc[type] = [];
        acc[type].push(entity);
        return acc;
    }, {} as Record<string, typeof entities>);

    // Filter scenarios related to NLP/text
    const nlpScenarios = scenarios.filter(s =>
        s.entity_type === 'PERSON' || s.entity_type === 'VICTIM' || s.entity_type === 'SUSPECT'
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight">NLP ANALYSIS</h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Entity extraction, stylometry, and text intelligence
                    </p>
                </div>
                <button
                    onClick={() => refreshCaseState()}
                    disabled={isLoading}
                    className="px-4 py-2 bg-slate-800 border border-slate-700 text-slate-300 rounded hover:bg-slate-700 transition-colors flex items-center space-x-2"
                >
                    <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    <span>Refresh Data</span>
                </button>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                    icon={<FileText />}
                    label="Text Samples"
                    value={textAnalyses.length || '152'}
                    color="sky"
                />
                <StatCard
                    icon={<User />}
                    label="Entities Found"
                    value={entities.length}
                    color="purple"
                />
                <StatCard
                    icon={<Brain />}
                    label="Stylometry Match"
                    value={textAnalyses[0]?.stylometry_match || 'dev_arjun92'}
                    color="emerald"
                />
                <StatCard
                    icon={<AlertTriangle />}
                    label="Match Score"
                    value={`${textAnalyses[0]?.stylometry_score || 92.4}%`}
                    color="red"
                />
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Entities Panel */}
                <div className="lg:col-span-2 glass-panel rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                        <Tag className="h-5 w-5 mr-2 text-primary" />
                        EXTRACTED ENTITIES
                    </h3>

                    {Object.keys(entityGroups).length > 0 ? (
                        <div className="space-y-4">
                            {Object.entries(entityGroups).map(([type, ents]) => (
                                <div key={type} className="space-y-2">
                                    <div className="text-xs text-slate-500 uppercase font-bold">{type}</div>
                                    <div className="flex flex-wrap gap-2">
                                        {ents.map((entity, idx) => (
                                            <motion.span
                                                key={idx}
                                                style={{ borderColor: entity.color || '#6b7280' }}
                                                className={`px-3 py-1.5 rounded-lg border text-sm ${entity.risk === 'HIGH'
                                                        ? 'bg-red-500/10 text-red-400'
                                                        : entity.risk === 'LOW'
                                                            ? 'bg-emerald-500/10 text-emerald-400'
                                                            : 'bg-slate-800 text-slate-300'
                                                    }`}
                                                initial={{ opacity: 0, scale: 0.9 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                                transition={{ delay: idx * 0.05 }}
                                            >
                                                {entity.name}
                                                {entity.risk === 'HIGH' && (
                                                    <AlertTriangle className="inline h-3 w-3 ml-1" />
                                                )}
                                            </motion.span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-slate-500">
                            <User className="h-12 w-12 mx-auto mb-3 opacity-50" />
                            <p>No entities extracted yet. Load demo data or process evidence.</p>
                        </div>
                    )}
                </div>

                {/* Stylometry Panel */}
                <div className="space-y-4">
                    {textAnalyses.length > 0 && textAnalyses[0].stylometry_match && (
                        <div className="glass-panel rounded-xl border border-red-500/30 p-4">
                            <h3 className="text-sm font-bold text-red-400 mb-3 flex items-center">
                                <Search className="h-4 w-4 mr-2" />
                                AUTHORSHIP MATCH
                            </h3>
                            <div className="text-center">
                                <div className="text-3xl font-bold text-white mb-1">
                                    {textAnalyses[0].stylometry_match}
                                </div>
                                <div className="text-sm text-slate-400">Burrows' Delta Match</div>
                                <div className="mt-3">
                                    <div className="text-4xl font-black text-red-500">
                                        {textAnalyses[0].stylometry_score}%
                                    </div>
                                    <div className="text-xs text-slate-500">Confidence</div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Key Phrases */}
                    {textAnalyses.length > 0 && textAnalyses[0].key_phrases?.length > 0 && (
                        <div className="glass-panel rounded-xl border border-amber-500/30 p-4">
                            <h3 className="text-sm font-bold text-amber-400 mb-3">KEY PHRASES</h3>
                            <div className="space-y-2">
                                {textAnalyses[0].key_phrases.map((phrase, idx) => (
                                    <div key={idx} className="px-2 py-1 bg-amber-500/10 text-amber-400 text-sm rounded">
                                        "{phrase}"
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Sample default key phrases */}
                    {textAnalyses.length === 0 && (
                        <div className="glass-panel rounded-xl border border-amber-500/30 p-4">
                            <h3 className="text-sm font-bold text-amber-400 mb-3">KEY PHRASES (Demo)</h3>
                            <div className="space-y-2">
                                {["mark my words", "you were warned", "definately", "occurence"].map((phrase, idx) => (
                                    <div key={idx} className="px-2 py-1 bg-amber-500/10 text-amber-400 text-sm rounded">
                                        "{phrase}"
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Entity-Person Scenarios from Vision/Geotag */}
            {nlpScenarios.length > 0 && (
                <div className="glass-panel rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-white mb-4">
                        ENTITY SCENARIOS (Cross-Correlated with Vision)
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {nlpScenarios.map((scenario, idx) => (
                            <motion.div
                                key={idx}
                                className="p-4 bg-slate-900 rounded-lg border-l-4"
                                style={{ borderLeftColor: scenario.color }}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: idx * 0.1 }}
                            >
                                <div className="flex justify-between items-start">
                                    <div>
                                        <div className="font-bold text-white">{scenario.entity}</div>
                                        <div className="text-xs text-slate-500">{scenario.entity_type}</div>
                                    </div>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${scenario.risk_level === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                                            scenario.risk_level === 'LOW' ? 'bg-emerald-500/20 text-emerald-400' :
                                                'bg-amber-500/20 text-amber-400'
                                        }`}>
                                        {scenario.risk_level}
                                    </span>
                                </div>
                                <p className="text-sm text-slate-400 mt-2">{scenario.description}</p>
                                <div className="text-xs text-slate-600 mt-2">
                                    {scenario.location} • {scenario.timestamp || 'N/A'}
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* Text Analysis Details */}
            {textAnalyses.length > 0 && (
                <div className="glass-panel rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-white mb-4">TEXT ANALYSIS DETAILS</h3>
                    <div className="space-y-4">
                        {textAnalyses.map((analysis, idx) => (
                            <div key={idx} className="p-4 bg-slate-900 rounded-lg">
                                <div className="flex justify-between items-start mb-2">
                                    <span className="font-mono text-sm text-primary">{analysis.source_file}</span>
                                    <span className={`px-2 py-0.5 rounded text-xs ${analysis.threat_score > 50 ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                                        }`}>
                                        Threat: {analysis.threat_score}%
                                    </span>
                                </div>
                                <p className="text-sm text-slate-400">{analysis.text_preview}</p>
                                <div className="flex items-center space-x-4 mt-3 text-xs text-slate-500">
                                    <span>Language: {analysis.language.toUpperCase()}</span>
                                    <span>Entities: {analysis.entities?.length || 0}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}

function StatCard({ icon, label, value, color }: { icon: any, label: string, value: string | number, color: string }) {
    const colors = {
        sky: 'text-sky-500 bg-sky-500/10 border-sky-500/20',
        purple: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
        emerald: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
        red: 'text-red-500 bg-red-500/10 border-red-500/20'
    };

    return (
        <div className={`glass-panel rounded-lg p-4 border ${colors[color as keyof typeof colors]}`}>
            <div className="flex items-center justify-between">
                <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${colors[color as keyof typeof colors]}`}>
                    {icon}
                </div>
                <div className="text-right">
                    <div className="text-xl font-bold text-white">{value}</div>
                    <div className="text-[10px] text-slate-500 uppercase">{label}</div>
                </div>
            </div>
        </div>
    );
}
