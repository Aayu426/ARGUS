"use client";

import { useState, useEffect } from 'react';
import { Upload, File, CheckCircle, Clock, Shield, Trash } from 'lucide-react';
import { motion } from 'framer-motion';
import { ArgusAPI } from '@/lib/api';

export default function EvidenceVault() {
    const [dragActive, setDragActive] = useState(false);
    const [files, setFiles] = useState<any[]>([]);
    const [caseId, setCaseId] = useState<string | null>(null);

    // Initialize Case on Load (With Persistence)
    useEffect(() => {
        async function initCase() {
            // Check localStorage
            const savedCaseId = localStorage.getItem('argus_case_id');
            if (savedCaseId) {
                setCaseId(savedCaseId);
                console.log("Restored Case:", savedCaseId);
                fetchFiles(savedCaseId);
            } else {
                const res = await ArgusAPI.createCase();
                if (res && res.case_id) {
                    setCaseId(res.case_id);
                    localStorage.setItem('argus_case_id', res.case_id);
                    console.log("New Case:", res.case_id);
                }
            }
        }
        initCase();
    }, []);

    const fetchFiles = async (id: string) => {
        try {
            const res = await fetch(`http://localhost:8000/api/evidence/${id}`);
            const data = await res.json();
            if (data.files) {
                setFiles(data.files);
            }
        } catch (e) {
            console.error("Failed to fetch evidence:", e);
        }
    };

    const handleDelete = async (filename: string) => {
        if (!caseId) return;
        try {
            await fetch(`http://localhost:8000/api/evidence/${caseId}/${filename}`, { method: 'DELETE' });
            // Remove from UI
            setFiles(prev => prev.filter(f => f.name !== filename));
        } catch (e) {
            console.error("Delete failed:", e);
        }
    };

    const handleDrag = (e: any) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = async (e: any) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            // Handle multiple files
            Array.from(e.dataTransfer.files).forEach((file: any) => handleFileUpload(file));
        }
    };

    const handleFileUpload = async (file: File) => {
        const newFileObj = {
            name: file.name,
            size: (file.size / 1024).toFixed(2) + " KB",
            type: file.name.split('.').pop()?.toUpperCase() || "UNKNOWN",
            status: "Uploading...",
            progress: 10
        };

        setFiles(prev => [newFileObj, ...prev]);

        if (caseId) {
            try {
                // Real Upload
                const res = await ArgusAPI.uploadEvidence(caseId, file);
                if (res && res.status === "uploaded") {
                    setFiles(prev => prev.map(f => f.name === file.name ? { ...f, status: "Secured (SHA3)", progress: 100 } : f));
                } else {
                    setFiles(prev => prev.map(f => f.name === file.name ? { ...f, status: "Failed", progress: 0 } : f));
                }
            } catch (err) {
                console.error(err);
                setFiles(prev => prev.map(f => f.name === file.name ? { ...f, status: "Error", progress: 0 } : f));
            }
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-white flex items-center">
                    <Shield className="mr-2 text-primary" />
                    Evidence Vault
                </h1>
                <span className="text-xs font-mono text-emerald-500 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20">
                    CHAIN OF CUSTODY: ACTIVE {caseId ? `(${caseId.substring(0, 6)}...)` : ''}
                </span>
            </div>

            {/* Upload Zone */}
            <div
                className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all duration-300 cursor-pointer ${dragActive ? 'border-primary bg-primary/5' : 'border-slate-700 hover:border-slate-500'}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input')?.click()}
            >
                <input
                    id="file-input"
                    type="file"
                    multiple
                    className="hidden"
                    onChange={(e) => {
                        if (e.target.files && e.target.files.length > 0) {
                            Array.from(e.target.files).forEach((file: any) => handleFileUpload(file));
                        }
                    }}
                    accept="image/*,.pdf,.txt,.doc,.docx,.zip"
                />
                <div className="flex flex-col items-center pointer-events-none">
                    <div className="h-16 w-16 bg-slate-800 rounded-full flex items-center justify-center mb-4 text-primary shadow-lg shadow-black/50">
                        <Upload className="h-8 w-8" />
                    </div>
                    <h3 className="text-xl font-medium text-white">Drag & Drop Evidence Artifacts</h3>
                    <p className="text-slate-400 mt-2">Supports Images, Documents, and Archives. <span className="text-primary">Multi-file supported.</span></p>
                    <button
                        className="mt-4 px-6 py-2 bg-primary/20 border border-primary text-primary rounded-lg hover:bg-primary/30 transition-colors pointer-events-auto"
                        onClick={(e) => {
                            e.stopPropagation();
                            document.getElementById('file-input')?.click();
                        }}
                    >
                        Browse Files
                    </button>
                    <p className="text-xs text-slate-500 mt-4 font-mono">ALL UPLOADS ARE AUTOMATICALLY HASHED (SHA3-512)</p>
                </div>
            </div>

            {/* File List */}
            <div className="glass-panel rounded-xl overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
                    <h3 className="font-semibold text-white">Secure Artifacts</h3>
                    <span className="text-xs text-slate-500">{files.length} ITEMS</span>
                </div>

                <div className="divide-y divide-slate-800">
                    {files.length === 0 ? (
                        <div className="p-8 text-center text-slate-500 text-sm">No evidence ingested yet.</div>
                    ) : (
                        files.map((file, idx) => (
                            <motion.div
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                key={idx}
                                className="p-4 flex items-center justify-between hover:bg-slate-800/30 transition-colors"
                            >
                                <div className="flex items-center space-x-4">
                                    <div className="h-10 w-10 rounded bg-slate-800 flex items-center justify-center text-slate-400">
                                        <File className="h-5 w-5" />
                                    </div>
                                    <div>
                                        <div className="text-white font-medium text-sm">{file.name}</div>
                                        <div className="text-xs text-slate-500 flex items-center space-x-2">
                                            <span>{file.size}</span>
                                            <span>•</span>
                                            <span>{file.type}</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center space-x-6">
                                    <div className="text-right">
                                        <div className={`text-xs font-bold ${file.progress === 100 ? 'text-emerald-500' : 'text-primary'}`}>
                                            {file.status}
                                        </div>
                                        <div className="w-24 h-1 bg-slate-800 rounded-full mt-1 overflow-hidden">
                                            <div className={`h-full transition-all duration-500 ${file.progress === 100 ? 'bg-emerald-500' : 'bg-primary'}`} style={{ width: `${file.progress}%` }}></div>
                                        </div>
                                    </div>

                                    {file.progress === 100 && (
                                        <button
                                            onClick={() => handleDelete(file.name)}
                                            className="text-xs border border-red-500/20 text-red-400 hover:bg-red-500/10 px-2 py-1 rounded transition-colors"
                                            title="Delete Evidence"
                                        >
                                            <Trash className="h-4 w-4" />
                                        </button>
                                    )}
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
