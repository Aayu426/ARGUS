"use client";

import { useState, useEffect } from 'react';
import { Settings, Trash2, FileDown, RefreshCcw, Shield, AlertTriangle, CheckCircle, Lock, Hash, Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export default function SystemConfig() {
    const [caseId, setCaseId] = useState<string | null>(null);
    const [evidenceCount, setEvidenceCount] = useState(0);
    const [showConfirmClear, setShowConfirmClear] = useState(false);
    const [isClearing, setIsClearing] = useState(false);
    const [isExporting, setIsExporting] = useState(false);
    const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

    // Integrity State
    const [chainStatus, setChainStatus] = useState<any>(null);
    const [ledgerEntries, setLedgerEntries] = useState<any[]>([]);
    const [isVerifying, setIsVerifying] = useState(false);

    useEffect(() => {
        const savedCaseId = localStorage.getItem('argus_case_id');
        if (savedCaseId) {
            setCaseId(savedCaseId);
            fetchEvidenceCount(savedCaseId);
        }
        // Fetch integrity status on load
        fetchIntegrityStatus();
        fetchLedger();
    }, []);

    const fetchEvidenceCount = async (id: string) => {
        try {
            const res = await fetch(`http://localhost:8000/api/evidence/${id}`);
            const data = await res.json();
            setEvidenceCount(data.files?.length || 0);
        } catch (e) {
            console.error("Failed to fetch evidence count:", e);
        }
    };

    const fetchIntegrityStatus = async () => {
        setIsVerifying(true);
        try {
            const res = await fetch('http://localhost:8000/api/integrity/verify');
            const data = await res.json();
            setChainStatus(data);
        } catch (e) {
            setChainStatus({ status: 'ERROR', error: 'Failed to connect' });
        }
        setIsVerifying(false);
    };

    const fetchLedger = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/integrity/ledger');
            const data = await res.json();
            setLedgerEntries(data.entries || []);
        } catch (e) {
            console.error("Failed to fetch ledger:", e);
        }
    };

    const handleResetCase = () => {
        localStorage.removeItem('argus_case_id');
        setCaseId(null);
        setEvidenceCount(0);
        setMessage({ text: 'Case ID reset. A new case will be created on next Evidence Vault visit.', type: 'success' });
    };

    const handleClearEvidence = async () => {
        if (!caseId) return;
        setIsClearing(true);
        try {
            const res = await fetch(`http://localhost:8000/api/evidence/${caseId}/clear`, { method: 'DELETE' });
            if (res.ok) {
                setEvidenceCount(0);
                setMessage({ text: 'All evidence has been purged from the vault.', type: 'success' });
            } else {
                setMessage({ text: 'Failed to clear evidence.', type: 'error' });
            }
        } catch (e) {
            setMessage({ text: 'Error clearing evidence.', type: 'error' });
        }
        setIsClearing(false);
        setShowConfirmClear(false);
    };

    const handleExportReport = async () => {
        if (!caseId) {
            setMessage({ text: 'No active case to export.', type: 'error' });
            return;
        }
        setIsExporting(true);
        try {
            const res = await fetch(`http://localhost:8000/api/report/${caseId}`);
            const data = await res.json();
            if (data.report_path) {
                window.open(`http://localhost:8000/api/report/${caseId}/download`, '_blank');
                setMessage({ text: `Report generated: ${data.report_path}`, type: 'success' });
            }
        } catch (e) {
            setMessage({ text: 'Failed to generate report.', type: 'error' });
        }
        setIsExporting(false);
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-white flex items-center">
                    <Settings className="mr-2 text-primary" />
                    System Configuration
                </h1>
                <span className="text-xs font-mono text-sky-500 bg-sky-500/10 px-2 py-1 rounded border border-sky-500/20">
                    ADMIN PANEL
                </span>
            </div>

            {message && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-4 rounded-lg border flex items-center space-x-3 ${message.type === 'success'
                        ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400'
                        : 'bg-red-500/10 border-red-500/20 text-red-400'
                        }`}
                >
                    {message.type === 'success' ? <CheckCircle className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
                    <span>{message.text}</span>
                    <button onClick={() => setMessage(null)} className="ml-auto text-xs opacity-50 hover:opacity-100">×</button>
                </motion.div>
            )}

            {/* Integrity Verification Section */}
            <div className="glass-panel rounded-xl overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/50">
                    <h3 className="font-semibold text-white flex items-center">
                        <Lock className="h-4 w-4 mr-2 text-emerald-500" />
                        Chain of Custody Integrity
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">Cryptographic verification of forensic ledger</p>
                </div>

                <div className="p-6 space-y-4">
                    {/* Status Display */}
                    <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <div className="flex items-center space-x-4">
                            <div className={`h-12 w-12 rounded-full flex items-center justify-center ${chainStatus?.status === 'VERIFIED'
                                    ? 'bg-emerald-500/20 text-emerald-500'
                                    : chainStatus?.status === 'COMPROMISED'
                                        ? 'bg-red-500/20 text-red-500'
                                        : 'bg-slate-700 text-slate-400'
                                }`}>
                                {chainStatus?.status === 'VERIFIED' ? <CheckCircle className="h-6 w-6" /> :
                                    chainStatus?.status === 'COMPROMISED' ? <AlertTriangle className="h-6 w-6" /> :
                                        <Hash className="h-6 w-6" />}
                            </div>
                            <div>
                                <div className="text-lg font-bold text-white">
                                    {chainStatus?.status || 'UNKNOWN'}
                                </div>
                                <div className="text-xs text-slate-500">
                                    {chainStatus?.total_blocks || 0} blocks in ledger
                                </div>
                            </div>
                        </div>
                        <button
                            onClick={fetchIntegrityStatus}
                            disabled={isVerifying}
                            className="flex items-center space-x-2 px-4 py-2 bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-500/30 rounded text-sm text-emerald-400 transition-colors"
                        >
                            <RefreshCcw className={`h-4 w-4 ${isVerifying ? 'animate-spin' : ''}`} />
                            <span>{isVerifying ? 'Verifying...' : 'Re-Verify'}</span>
                        </button>
                    </div>

                    {/* Hash Algorithms */}
                    <div className="grid grid-cols-3 gap-3">
                        <div className="p-3 bg-slate-800/30 rounded-lg border border-slate-700/50 text-center">
                            <div className="text-xs text-slate-500 mb-1">Algorithm 1</div>
                            <div className="text-sm font-mono text-primary">SHA3-512</div>
                        </div>
                        <div className="p-3 bg-slate-800/30 rounded-lg border border-slate-700/50 text-center">
                            <div className="text-xs text-slate-500 mb-1">Algorithm 2</div>
                            <div className="text-sm font-mono text-primary">SHA-256</div>
                        </div>
                        <div className="p-3 bg-slate-800/30 rounded-lg border border-slate-700/50 text-center">
                            <div className="text-xs text-slate-500 mb-1">Algorithm 3</div>
                            <div className="text-sm font-mono text-primary">BLAKE3</div>
                        </div>
                    </div>

                    {/* Recent Ledger Entries */}
                    {ledgerEntries.length > 0 && (
                        <div className="mt-4">
                            <div className="text-xs text-slate-500 mb-2 flex items-center">
                                <Activity className="h-3 w-3 mr-1" />
                                Recent Chain Entries
                            </div>
                            <div className="max-h-40 overflow-y-auto space-y-1 scrollbar-thin scrollbar-thumb-slate-700">
                                {ledgerEntries.slice(-5).reverse().map((entry, idx) => (
                                    <div key={idx} className="flex items-center justify-between text-xs p-2 bg-slate-900/50 rounded">
                                        <span className="text-slate-400 font-mono">{entry.block_id}</span>
                                        <span className="text-primary">{entry.action}</span>
                                        <span className="text-slate-500">{entry.actor}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Case Management Section */}
            <div className="glass-panel rounded-xl overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/50">
                    <h3 className="font-semibold text-white flex items-center">
                        <Shield className="h-4 w-4 mr-2 text-primary" />
                        Case Management
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">Manage your active forensic case and evidence</p>
                </div>

                <div className="p-6 space-y-6">
                    <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <div>
                            <div className="text-sm font-medium text-white">Active Case ID</div>
                            <div className="text-xs text-slate-500 mt-1">Current forensic case identifier</div>
                        </div>
                        <div className="flex items-center space-x-3">
                            <code className="px-3 py-1.5 bg-slate-900 rounded text-primary font-mono text-sm border border-slate-700">
                                {caseId ? caseId.substring(0, 8) + '...' : 'No Active Case'}
                            </code>
                            <button
                                onClick={handleResetCase}
                                className="flex items-center space-x-2 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded text-sm text-white transition-colors"
                            >
                                <RefreshCcw className="h-4 w-4" />
                                <span>Reset</span>
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <div>
                            <div className="text-sm font-medium text-white">Evidence in Vault</div>
                            <div className="text-xs text-slate-500 mt-1">Total artifacts secured with SHA3-512</div>
                        </div>
                        <div className="text-2xl font-bold text-emerald-500 font-mono">
                            {evidenceCount}
                        </div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-red-500/5 rounded-lg border border-red-500/20">
                        <div>
                            <div className="text-sm font-medium text-white">Clear All Evidence</div>
                            <div className="text-xs text-slate-500 mt-1">Permanently delete all files from the vault</div>
                        </div>
                        {!showConfirmClear ? (
                            <button
                                onClick={() => setShowConfirmClear(true)}
                                disabled={evidenceCount === 0}
                                className="flex items-center space-x-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 rounded text-sm text-red-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Trash2 className="h-4 w-4" />
                                <span>Purge Vault</span>
                            </button>
                        ) : (
                            <div className="flex items-center space-x-2">
                                <span className="text-xs text-red-400">Are you sure?</span>
                                <button
                                    onClick={handleClearEvidence}
                                    disabled={isClearing}
                                    className="px-3 py-1.5 bg-red-500 hover:bg-red-600 rounded text-sm text-white transition-colors"
                                >
                                    {isClearing ? 'Clearing...' : 'Yes, Delete All'}
                                </button>
                                <button
                                    onClick={() => setShowConfirmClear(false)}
                                    className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded text-sm text-white transition-colors"
                                >
                                    Cancel
                                </button>
                            </div>
                        )}
                    </div>

                    <div className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <div>
                            <div className="text-sm font-medium text-white">Export Case Report</div>
                            <div className="text-xs text-slate-500 mt-1">Generate court-admissible PDF documentation</div>
                        </div>
                        <button
                            onClick={handleExportReport}
                            disabled={!caseId || isExporting}
                            className="flex items-center space-x-2 px-4 py-2 bg-primary/20 hover:bg-primary/30 border border-primary/30 rounded text-sm text-primary transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <FileDown className="h-4 w-4" />
                            <span>{isExporting ? 'Generating...' : 'Download PDF'}</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* System Info */}
            <div className="glass-panel rounded-xl overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-800 bg-slate-900/50">
                    <h3 className="font-semibold text-white">System Information</h3>
                </div>
                <div className="p-6 grid grid-cols-2 gap-4 text-sm">
                    <div className="flex justify-between p-3 bg-slate-800/30 rounded">
                        <span className="text-slate-500">Version</span>
                        <span className="text-white font-mono">2.0.0-ELITE</span>
                    </div>
                    <div className="flex justify-between p-3 bg-slate-800/30 rounded">
                        <span className="text-slate-500">Backend</span>
                        <span className="text-emerald-500 font-mono">ONLINE</span>
                    </div>
                    <div className="flex justify-between p-3 bg-slate-800/30 rounded">
                        <span className="text-slate-500">Compliance</span>
                        <span className="text-white font-mono">NIST-800-53</span>
                    </div>
                    <div className="flex justify-between p-3 bg-slate-800/30 rounded">
                        <span className="text-slate-500">Hashing</span>
                        <span className="text-white font-mono">SHA3 + BLAKE3</span>
                    </div>
                </div>
            </div>
        </div>
    );
}

