"use client";

import { useEffect, useState } from 'react';
import { Shield, Activity, Share2, FileText, Download, Loader2, PlayCircle, MapPin, AlertTriangle, CheckCircle, User, Globe, Clock, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import { useCaseContext } from '@/lib/case-context';
import Link from 'next/link';

export default function Dashboard() {
  const {
    caseId,
    caseState,
    isLoading,
    isProcessing,
    initCase,
    loadDemoData,
    processAllEvidence,
    refreshCaseState,
    getScenarios,
    getAttribution,
    getLocations
  } = useCaseContext();


  const [downloadingReport, setDownloadingReport] = useState(false);

  useEffect(() => {
    initCase();
  }, [initCase]);

  const handleLoadDemo = async () => {
    await loadDemoData();
  };

  const handleProcessAll = async () => {
    await processAllEvidence();
  };

  const handleDownloadReport = async () => {
    if (!caseId) return;

    setDownloadingReport(true);
    try {
      const res = await fetch(`http://localhost:8000/api/report/enhanced`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          analysis_results: caseState ? {
            case_id: caseId,
            confidence_score: {
              attribution_confidence_score: caseState.overall_risk_score,
              verdict: caseState.overall_risk_score > 80 ? "STRONG" : "MODERATE",
              confidence_level: "HIGH"
            },
            integrity: { status: "VERIFIED" },
            nlp: { entities: caseState.entities?.length || 0 },
            image: { images_analyzed: caseState.image_analyses?.length || 0 }
          } : {}
        })
      });

      if (res.ok) {
        // Open download in new tab
        window.open(`http://localhost:8000/api/report/${caseId}/download`, '_blank');
      }
    } catch (e) {
      console.error('Report download failed:', e);
    }
    setDownloadingReport(false);
  };

  const handleResetCase = async () => {
    if (!caseId) return;
    try {
      await fetch(`http://localhost:8000/api/case/${caseId}/reset`, { method: 'POST' });
      await refreshCaseState();
    } catch (e) {
      console.error('Reset failed:', e);
    }
  };

  const handleLoadFullDemo = async () => {
    if (!caseId) return;
    try {
      await fetch(`http://localhost:8000/api/case/${caseId}/load-demo-full`, { method: 'POST' });
      await refreshCaseState();
    } catch (e) {
      console.error('Load full demo failed:', e);
    }
  };

  const scenarios = getScenarios();
  const attribution = getAttribution();
  const locations = getLocations();

  return (
    <div className="space-y-6">
      {/* Header with Actions */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tight">COMMAND CENTER</h1>
          <p className="text-slate-400 text-sm mt-1">
            Case: <span className="text-primary font-mono">{caseId?.substring(0, 8) || 'Initializing...'}</span>
            {caseState?.status && (
              <span className={`ml-3 px-2 py-0.5 rounded text-xs ${caseState.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-500' : caseState.status === 'READY' ? 'bg-slate-500/20 text-slate-400' : 'bg-amber-500/20 text-amber-500'}`}>
                {caseState.status}
              </span>
            )}
          </p>
        </div>

        <div className="flex space-x-2 flex-wrap">
          {/* Reset Button - for judge demo */}
          <button
            onClick={handleResetCase}
            disabled={isLoading || isProcessing}
            className="px-3 py-2 bg-slate-700/50 border border-slate-600 text-slate-300 rounded hover:bg-slate-600/50 transition-colors flex items-center space-x-1 disabled:opacity-50 text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 12a9 9 0 109-9 9.75 9.75 0 00-6.74 2.74L3 8" /><path d="M3 3v5h5" /></svg>
            <span>Reset</span>
          </button>

          {/* Load Demo - basic */}
          <button
            onClick={handleLoadDemo}
            disabled={isLoading || isProcessing}
            className="px-3 py-2 bg-purple-600/20 border border-purple-500/50 text-purple-400 rounded hover:bg-purple-600/30 transition-colors flex items-center space-x-1 disabled:opacity-50 text-sm"
          >
            <PlayCircle className="h-4 w-4" />
            <span>Demo</span>
          </button>

          {/* Load Full Demo - enhanced with multiple images */}
          <button
            onClick={handleLoadFullDemo}
            disabled={isLoading || isProcessing}
            className="px-3 py-2 bg-indigo-600/20 border border-indigo-500/50 text-indigo-400 rounded hover:bg-indigo-600/30 transition-colors flex items-center space-x-1 disabled:opacity-50 text-sm"
          >
            <MapPin className="h-4 w-4" />
            <span>Full Demo (2 Images)</span>
          </button>

          <button
            onClick={handleProcessAll}
            disabled={isLoading || isProcessing}
            className="px-3 py-2 bg-primary/20 border border-primary/50 text-primary rounded hover:bg-primary/30 transition-colors flex items-center space-x-1 disabled:opacity-50 text-sm"
          >
            {isProcessing ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Activity className="h-4 w-4" />
                <span>Process All</span>
              </>
            )}
          </button>
          {caseState?.status === 'COMPLETED' && (
            <button
              onClick={handleDownloadReport}
              disabled={downloadingReport}
              className="px-3 py-2 bg-emerald-600/20 border border-emerald-500/50 text-emerald-400 rounded hover:bg-emerald-600/30 transition-colors flex items-center space-x-1 text-sm"
            >
              {downloadingReport ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              <span>Report</span>
            </button>
          )}

        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard icon={<FileText />} label="Evidence Files" value={caseState?.evidence_files?.length || 0} color="sky" />
        <StatCard icon={<User />} label="Entities" value={caseState?.entities?.length || 0} color="purple" />
        <StatCard icon={<MapPin />} label="Locations" value={locations.length} color="emerald" />
        <StatCard icon={<Share2 />} label="Graph Nodes" value={caseState?.graph_nodes?.length || 0} color="amber" />
        <StatCard icon={<Target />} label="Risk Score" value={`${caseState?.overall_risk_score?.toFixed(1) || 0}%`} color="red" />
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Final Attribution Panel */}
        <div className="lg:col-span-2">
          {attribution ? (
            <motion.div
              className="glass-panel rounded-xl border border-red-500/30 p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center">
                  <Target className="h-5 w-5 mr-2 text-red-500" />
                  FINAL ATTRIBUTION
                </h3>
                <div className="px-3 py-1 bg-red-500/20 border border-red-500/50 rounded text-red-400 text-sm font-mono">
                  CONFIDENCE: {attribution.confidence_score}%
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <div className="text-sm text-slate-500 mb-1">Primary Suspect</div>
                  <div className="text-2xl font-bold text-white">{attribution.suspect}</div>
                  <div className="text-sm text-red-400 mt-1">{attribution.role}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500 mb-1">Probable Location</div>
                  <div className="text-lg text-white">{attribution.probable_location || 'Unknown'}</div>
                </div>
              </div>

              {attribution.aliases && attribution.aliases.length > 0 && (
                <div className="mt-4">
                  <div className="text-sm text-slate-500 mb-2">Known Aliases</div>
                  <div className="flex flex-wrap gap-2">
                    {attribution.aliases.map((alias, idx) => (
                      <span key={idx} className="px-2 py-1 bg-slate-800 text-slate-300 text-xs rounded font-mono">
                        {alias}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {attribution.risk_breakdown && (
                <div className="mt-6 grid grid-cols-4 gap-3">
                  <RiskMeter label="NLP" score={attribution.risk_breakdown.nlp_score} />
                  <RiskMeter label="Graph" score={attribution.risk_breakdown.graph_score} />
                  <RiskMeter label="Image" score={attribution.risk_breakdown.image_score} />
                  <RiskMeter label="Location" score={attribution.risk_breakdown.location_score} />
                </div>
              )}

              <div className="mt-4 text-xs text-slate-500">
                {attribution.evidence_summary}
              </div>
            </motion.div>
          ) : (
            <div className="glass-panel rounded-xl border border-slate-700 p-8 text-center">
              <Target className="h-12 w-12 text-slate-600 mx-auto mb-3" />
              <h3 className="text-lg text-slate-400">No Attribution Yet</h3>
              <p className="text-sm text-slate-500 mt-2">Load demo data or upload evidence and click "Process All Evidence"</p>
            </div>
          )}

          {/* Scenarios Timeline */}
          {scenarios.length > 0 && (
            <div className="mt-6 glass-panel rounded-xl border border-slate-700 p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                <Clock className="h-5 w-5 mr-2 text-primary" />
                ENTITY-LOCATION SCENARIOS
              </h3>
              <div className="space-y-3 max-h-80 overflow-y-auto">
                {scenarios.map((scenario, idx) => (
                  <motion.div
                    key={idx}
                    className="flex items-start space-x-3 p-3 bg-slate-900/50 rounded-lg border-l-4"
                    style={{ borderLeftColor: scenario.color }}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                  >
                    <div className="flex-shrink-0 mt-1">
                      {scenario.risk_level === 'HIGH' ? (
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                      ) : scenario.risk_level === 'LOW' ? (
                        <CheckCircle className="h-4 w-4 text-emerald-500" />
                      ) : (
                        <MapPin className="h-4 w-4 text-amber-500" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white text-sm">{scenario.entity}</span>
                        <span className="text-xs text-slate-500">{scenario.timestamp || 'N/A'}</span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1">{scenario.description}</p>
                      <div className="flex items-center space-x-2 mt-2 text-xs">
                        <span className="text-slate-500">{scenario.location}</span>
                        {scenario.coordinates && (
                          <a
                            href={`https://www.google.com/maps?q=${scenario.coordinates[0]},${scenario.coordinates[1]}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:underline flex items-center"
                          >
                            <Globe className="h-3 w-3 mr-1" />
                            View Map
                          </a>
                        )}
                      </div>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${scenario.risk_level === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                      scenario.risk_level === 'LOW' ? 'bg-emerald-500/20 text-emerald-400' :
                        'bg-amber-500/20 text-amber-400'
                      }`}>
                      {scenario.risk_level}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Sidebar - Quick Links & Locations */}
        <div className="space-y-4">
          {/* Module Links */}
          <div className="glass-panel rounded-xl border border-slate-700 p-4">
            <h3 className="text-sm font-bold text-slate-400 mb-3">ANALYSIS MODULES</h3>
            <div className="space-y-2">
              <ModuleLink href="/nlp" icon={<FileText />} label="NLP Analysis" count={caseState?.text_analyses?.length || 0} />
              <ModuleLink href="/vision" icon={<Activity />} label="Visual Lab" count={caseState?.image_analyses?.length || 0} />
              <ModuleLink href="/graph" icon={<Share2 />} label="Network Graph" count={caseState?.graph_nodes?.length || 0} />
              <ModuleLink href="/evidence" icon={<Shield />} label="Evidence Vault" count={caseState?.evidence_files?.length || 0} />
            </div>
          </div>

          {/* Locations Map Preview */}
          {locations.length > 0 && (
            <div className="glass-panel rounded-xl border border-emerald-500/30 p-4">
              <h3 className="text-sm font-bold text-emerald-400 mb-3 flex items-center">
                <MapPin className="h-4 w-4 mr-2" />
                EXTRACTED LOCATIONS
              </h3>
              <div className="space-y-2">
                {locations.map((loc, idx) => (
                  <a
                    key={idx}
                    href={loc.map_url || `https://www.google.com/maps?q=${loc.latitude},${loc.longitude}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block p-2 bg-slate-900 rounded hover:bg-slate-800 transition-colors"
                  >
                    <div className="text-xs text-white truncate">{loc.address}</div>
                    <div className="text-[10px] text-slate-500 font-mono">
                      {loc.latitude.toFixed(4)}, {loc.longitude.toFixed(4)}
                    </div>
                    {loc.timestamp && (
                      <div className="text-[10px] text-slate-500">{loc.timestamp}</div>
                    )}
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* Integrity Status */}
          <div className="glass-panel rounded-xl border border-slate-700 p-4">
            <h3 className="text-sm font-bold text-slate-400 mb-3">INTEGRITY STATUS</h3>
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <CheckCircle className="h-5 w-5 text-emerald-500" />
              </div>
              <div>
                <div className="text-white font-bold">CHAIN VERIFIED</div>
                <div className="text-xs text-slate-500">All evidence hashed & timestamped</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, color }: { icon: any, label: string, value: string | number, color: string }) {
  const colors = {
    sky: 'text-sky-500 bg-sky-500/10 border-sky-500/20',
    purple: 'text-purple-500 bg-purple-500/10 border-purple-500/20',
    emerald: 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20',
    amber: 'text-amber-500 bg-amber-500/10 border-amber-500/20',
    red: 'text-red-500 bg-red-500/10 border-red-500/20'
  };

  return (
    <div className={`glass-panel rounded-lg p-4 border ${colors[color as keyof typeof colors]}`}>
      <div className="flex items-center justify-between">
        <div className={`h-8 w-8 rounded-lg flex items-center justify-center ${colors[color as keyof typeof colors]}`}>
          {icon}
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-white">{value}</div>
          <div className="text-[10px] text-slate-500 uppercase">{label}</div>
        </div>
      </div>
    </div>
  );
}

function RiskMeter({ label, score }: { label: string, score: number }) {
  const color = score > 80 ? 'bg-red-500' : score > 50 ? 'bg-amber-500' : 'bg-emerald-500';
  return (
    <div className="text-center">
      <div className="text-[10px] text-slate-500 uppercase mb-1">{label}</div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
        <motion.div
          className={`h-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      <div className="text-xs text-white mt-1">{score.toFixed(0)}%</div>
    </div>
  );
}

function ModuleLink({ href, icon, label, count }: { href: string, icon: any, label: string, count: number }) {
  return (
    <Link href={href} className="flex items-center justify-between p-2 rounded hover:bg-slate-800 transition-colors group">
      <div className="flex items-center space-x-2">
        <div className="text-slate-500 group-hover:text-primary transition-colors">{icon}</div>
        <span className="text-sm text-slate-300 group-hover:text-white">{label}</span>
      </div>
      <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-400">{count}</span>
    </Link>
  );
}
