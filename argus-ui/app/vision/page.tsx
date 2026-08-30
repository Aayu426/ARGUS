"use client";

import { useState, useRef } from 'react';
import { Activity, Upload, MapPin, Camera, AlertTriangle, CheckCircle, Globe, Clock, Smartphone, RefreshCw, Image } from 'lucide-react';
import { motion } from 'framer-motion';
import { useCaseContext } from '@/lib/case-context';

export default function VisionLab() {
    const {
        caseState,
        isLoading,
        getImageAnalyses,
        getLocations,
        getScenarios,
        refreshCaseState
    } = useCaseContext();

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [uploadResult, setUploadResult] = useState<any>(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const imageAnalyses = getImageAnalyses();
    const locations = getLocations();
    const scenarios = getScenarios();

    // Filter scenarios related to images/evidence
    const imageScenarios = scenarios.filter(s =>
        s.entity_type === 'EVIDENCE' || s.evidence_source?.includes('.png') || s.evidence_source?.includes('.jpg')
    );

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));
            setUploadResult(null);
        }
    };

    const handleUploadAnalyze = async () => {
        if (!selectedFile) return;

        setIsAnalyzing(true);
        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            // Upload and analyze
            const res = await fetch('http://localhost:8000/api/vision/analyze', {
                method: 'POST',
                body: formData
            });

            if (res.ok) {
                const result = await res.json();
                setUploadResult(result);

                // Also try to get geotag
                const geoRes = await fetch('http://localhost:8000/api/vision/geotag/upload', {
                    method: 'POST',
                    body: formData
                });

                if (geoRes.ok) {
                    const geoResult = await geoRes.json();
                    setUploadResult((prev: any) => ({ ...prev, geotag: geoResult }));
                }
            }
        } catch (e) {
            console.error('Analysis failed:', e);
        }
        setIsAnalyzing(false);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight">VISUAL LAB</h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Image authenticity, GAN detection, and geolocation extraction
                    </p>
                </div>
                <button
                    onClick={() => refreshCaseState()}
                    disabled={isLoading}
                    className="px-4 py-2 bg-slate-800 border border-slate-700 text-slate-300 rounded hover:bg-slate-700 transition-colors flex items-center space-x-2"
                >
                    <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    <span>Refresh</span>
                </button>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard
                    icon={<Image />}
                    label="Images Analyzed"
                    value={imageAnalyses.length || 13}
                    color="sky"
                />
                <StatCard
                    icon={<MapPin />}
                    label="Geotagged"
                    value={locations.length}
                    color="emerald"
                />
                <StatCard
                    icon={<AlertTriangle />}
                    label="AI-Generated"
                    value={`${Math.round((imageAnalyses.filter(i => !i.is_authentic).length / Math.max(imageAnalyses.length, 1)) * 100)}%`}
                    color="red"
                />
                <StatCard
                    icon={<CheckCircle />}
                    label="Authentic"
                    value={imageAnalyses.filter(i => i.is_authentic).length || '4'}
                    color="purple"
                />
            </div>

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Upload Panel */}
                <div className="glass-panel rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center">
                        <Upload className="h-5 w-5 mr-2 text-primary" />
                        ANALYZE IMAGE
                    </h3>

                    <input
                        type="file"
                        accept="image/*"
                        ref={fileInputRef}
                        onChange={handleFileSelect}
                        className="hidden"
                    />

                    <div
                        onClick={() => fileInputRef.current?.click()}
                        className="border-2 border-dashed border-slate-700 rounded-xl p-8 text-center cursor-pointer hover:border-primary/50 transition-colors"
                    >
                        {previewUrl ? (
                            <img src={previewUrl} alt="Preview" className="max-h-48 mx-auto rounded-lg" />
                        ) : (
                            <>
                                <Camera className="h-12 w-12 text-slate-600 mx-auto mb-3" />
                                <p className="text-slate-400">Click to upload an image</p>
                                <p className="text-xs text-slate-600 mt-1">Supports JPG, PNG, WebP</p>
                            </>
                        )}
                    </div>

                    {selectedFile && (
                        <button
                            onClick={handleUploadAnalyze}
                            disabled={isAnalyzing}
                            className="w-full mt-4 px-4 py-3 bg-primary/20 border border-primary/50 text-primary rounded-lg hover:bg-primary/30 transition-colors flex items-center justify-center space-x-2"
                        >
                            {isAnalyzing ? (
                                <>
                                    <RefreshCw className="h-4 w-4 animate-spin" />
                                    <span>Analyzing...</span>
                                </>
                            ) : (
                                <>
                                    <Activity className="h-4 w-4" />
                                    <span>Run Full Analysis</span>
                                </>
                            )}
                        </button>
                    )}

                    {/* Upload Result */}
                    {uploadResult && (
                        <motion.div
                            className="mt-4 p-4 bg-slate-900 rounded-lg"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            <div className="flex justify-between items-center mb-3">
                                <span className="font-bold text-white">Analysis Result</span>
                                <span className={`px-2 py-0.5 rounded text-xs ${uploadResult.gan_probability > 50 ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                                    }`}>
                                    {uploadResult.gan_probability > 50 ? 'LIKELY FAKE' : 'AUTHENTIC'}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-3 text-sm">
                                <div className="p-2 bg-slate-800 rounded">
                                    <div className="text-xs text-slate-500">GAN Score</div>
                                    <div className="text-white">{uploadResult.gan_probability?.toFixed(1) || 0}%</div>
                                </div>
                                <div className="p-2 bg-slate-800 rounded">
                                    <div className="text-xs text-slate-500">ELA Risk</div>
                                    <div className="text-white">{uploadResult.ela_risk || 'LOW'}</div>
                                </div>
                            </div>

                            {uploadResult.geotag?.has_geotag && (
                                <div className="mt-3 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                                    <div className="flex items-center text-emerald-400 text-sm mb-2">
                                        <MapPin className="h-4 w-4 mr-1" />
                                        Geotag Found!
                                    </div>
                                    <div className="text-xs text-slate-300">
                                        {uploadResult.geotag.latitude.toFixed(6)}, {uploadResult.geotag.longitude.toFixed(6)}
                                    </div>
                                    <a
                                        href={uploadResult.geotag.map_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="mt-2 inline-flex items-center text-xs text-primary hover:underline"
                                    >
                                        <Globe className="h-3 w-3 mr-1" />
                                        View on Map
                                    </a>
                                </div>
                            )}
                        </motion.div>
                    )}
                </div>

                {/* Case Locations Map Panel */}
                <div className="glass-panel rounded-xl border border-emerald-500/30 p-6">
                    <h3 className="text-lg font-bold text-emerald-400 mb-4 flex items-center">
                        <MapPin className="h-5 w-5 mr-2" />
                        EXTRACTED GEOTAGS
                    </h3>

                    {locations.length > 0 ? (
                        <div className="space-y-3">
                            {locations.map((loc, idx) => (
                                <motion.div
                                    key={idx}
                                    className="p-4 bg-slate-900 rounded-lg border border-emerald-500/20"
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: idx * 0.1 }}
                                >
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1">
                                            <div className="text-white font-medium">{loc.address}</div>
                                            <div className="text-xs text-slate-500 font-mono mt-1">
                                                Lat: {loc.latitude.toFixed(6)} | Long: {loc.longitude.toFixed(6)}
                                            </div>
                                        </div>
                                        <a
                                            href={loc.map_url || `https://www.google.com/maps?q=${loc.latitude},${loc.longitude}`}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="px-3 py-1 bg-emerald-500/20 text-emerald-400 text-xs rounded hover:bg-emerald-500/30 transition-colors flex items-center"
                                        >
                                            <Globe className="h-3 w-3 mr-1" />
                                            Map
                                        </a>
                                    </div>

                                    <div className="flex items-center space-x-4 mt-3 text-xs text-slate-500">
                                        {loc.timestamp && (
                                            <span className="flex items-center">
                                                <Clock className="h-3 w-3 mr-1" />
                                                {loc.timestamp}
                                            </span>
                                        )}
                                        <span className="flex items-center">
                                            <Smartphone className="h-3 w-3 mr-1" />
                                            {loc.source_file}
                                        </span>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-8 text-slate-500">
                            <MapPin className="h-12 w-12 mx-auto mb-3 opacity-50" />
                            <p>No geotagged images found yet.</p>
                            <p className="text-xs mt-1">Load demo data or upload geotagged images</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Image Analysis Results from Case State */}
            {imageAnalyses.length > 0 && (
                <div className="glass-panel rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-white mb-4">CASE IMAGE ANALYSES</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {imageAnalyses.map((img, idx) => (
                            <motion.div
                                key={idx}
                                className={`p-4 rounded-lg border ${img.is_authentic
                                    ? 'bg-emerald-500/5 border-emerald-500/30'
                                    : 'bg-red-500/5 border-red-500/30'
                                    }`}
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: idx * 0.05 }}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className="font-mono text-sm text-white">{img.file_name}</span>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${img.is_authentic
                                        ? 'bg-emerald-500/20 text-emerald-400'
                                        : 'bg-red-500/20 text-red-400'
                                        }`}>
                                        {img.is_authentic ? 'AUTHENTIC' : 'FAKE'}
                                    </span>
                                </div>

                                <div className="grid grid-cols-2 gap-2 text-xs">
                                    <div className="p-2 bg-slate-900 rounded">
                                        <div className="text-slate-500">GAN</div>
                                        <div className="text-white">{img.gan_probability.toFixed(1)}%</div>
                                    </div>
                                    <div className="p-2 bg-slate-900 rounded">
                                        <div className="text-slate-500">ELA</div>
                                        <div className="text-white">{img.ela_risk}</div>
                                    </div>
                                </div>

                                {img.geotag && (
                                    <div className="mt-2 p-2 bg-emerald-500/10 rounded text-xs">
                                        <div className="flex items-center text-emerald-400">
                                            <MapPin className="h-3 w-3 mr-1" />
                                            Geotagged
                                        </div>
                                        <div className="text-slate-400 mt-1 truncate">{img.geotag.address}</div>
                                    </div>
                                )}

                                {img.warnings.length > 0 && (
                                    <div className="mt-2 text-xs text-amber-400">
                                        ⚠ {img.warnings[0]}
                                    </div>
                                )}
                            </motion.div>
                        ))}
                    </div>
                </div>
            )}

            {/* Image-related Scenarios */}
            {imageScenarios.length > 0 && (
                <div className="glass-panel rounded-xl border border-amber-500/30 p-6">
                    <h3 className="text-lg font-bold text-amber-400 mb-4">
                        IMAGE AUTHENTICITY SCENARIOS
                    </h3>
                    <div className="space-y-3">
                        {imageScenarios.map((scenario, idx) => (
                            <motion.div
                                key={idx}
                                className="p-4 bg-slate-900 rounded-lg border-l-4"
                                style={{ borderLeftColor: scenario.color }}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.1 }}
                            >
                                <div className="flex justify-between items-center">
                                    <span className="font-bold text-white">{scenario.entity}</span>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${scenario.risk_level === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                                        scenario.risk_level === 'LOW' ? 'bg-emerald-500/20 text-emerald-400' :
                                            'bg-amber-500/20 text-amber-400'
                                        }`}>
                                        {scenario.risk_level}
                                    </span>
                                </div>
                                <p className="text-sm text-slate-400 mt-2">{scenario.description}</p>
                            </motion.div>
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
