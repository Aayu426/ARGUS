"use client";

import { useMemo } from 'react';
import { Share2, Target, Users, AlertTriangle, RefreshCw, Bot, User, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { useCaseContext } from '@/lib/case-context';

export default function NetworkGraph() {
    const {
        caseState,
        isLoading,
        getGraphData,
        getScenarios,
        getAttribution,
        refreshCaseState
    } = useCaseContext();

    const { nodes, edges, metrics } = getGraphData();
    const scenarios = getScenarios();
    const attribution = getAttribution();

    // Calculate node positions for visualization
    const nodePositions = useMemo(() => {
        const positions: Record<string, { x: number, y: number }> = {};
        const centerX = 400;
        const centerY = 300;

        // Group nodes by type
        const suspects = nodes.filter(n => n.type === 'SUSPECT' || n.risk === 'HIGH');
        const fakes = nodes.filter(n => n.type === 'FAKE');
        const victims = nodes.filter(n => n.type === 'VICTIM' || n.risk === 'LOW');
        const bots = nodes.filter(n => n.type === 'BOT');

        // Position suspect in center
        suspects.forEach((node, i) => {
            positions[node.id] = { x: centerX, y: centerY };
        });

        // Position fakes around suspect
        fakes.forEach((node, i) => {
            const angle = (i * 2 * Math.PI) / Math.max(fakes.length, 1);
            positions[node.id] = {
                x: centerX + Math.cos(angle) * 120,
                y: centerY + Math.sin(angle) * 120
            };
        });

        // Position victims on outer ring
        victims.forEach((node, i) => {
            const angle = ((i + 0.5) * 2 * Math.PI) / Math.max(victims.length, 1);
            positions[node.id] = {
                x: centerX + Math.cos(angle) * 220,
                y: centerY + Math.sin(angle) * 220
            };
        });

        // Position bots on separate area
        bots.forEach((node, i) => {
            positions[node.id] = {
                x: 100 + i * 60,
                y: 100
            };
        });

        return positions;
    }, [nodes]);

    const getNodeColor = (type: string, risk: string) => {
        if (type === 'SUSPECT' || risk === 'HIGH') return '#ef4444';
        if (type === 'FAKE') return '#f97316';
        if (type === 'BOT') return '#eab308';
        if (type === 'VICTIM' || risk === 'LOW') return '#22c55e';
        return '#6b7280';
    };

    const getNodeIcon = (type: string) => {
        if (type === 'SUSPECT') return <Target className="h-4 w-4" />;
        if (type === 'FAKE') return <AlertTriangle className="h-4 w-4" />;
        if (type === 'BOT') return <Bot className="h-4 w-4" />;
        if (type === 'VICTIM') return <User className="h-4 w-4" />;
        return <Users className="h-4 w-4" />;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-black text-white tracking-tight">NETWORK GRAPH</h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Entity relationships, influence mapping, and cluster detection
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
                    icon={<Users />}
                    label="Nodes"
                    value={nodes.length}
                    color="sky"
                />
                <StatCard
                    icon={<Share2 />}
                    label="Connections"
                    value={edges.length}
                    color="purple"
                />
                <StatCard
                    icon={<Target />}
                    label="Top Brokers"
                    value={metrics?.top_brokers?.length || 1}
                    color="red"
                />
                <StatCard
                    icon={<Zap />}
                    label="Clusters"
                    value={metrics?.clusters?.length || 3}
                    color="emerald"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Graph Visualization */}
                <div className="lg:col-span-2 glass-panel rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-white mb-4">NETWORK VISUALIZATION</h3>

                    {nodes.length > 0 ? (
                        <div className="relative bg-slate-900 rounded-lg" style={{ height: '500px' }}>
                            <svg width="100%" height="100%" viewBox="0 0 800 600">
                                {/* Draw edges */}
                                {edges.map((edge, idx) => {
                                    const from = nodePositions[edge.from];
                                    const to = nodePositions[edge.to];
                                    if (!from || !to) return null;

                                    const color = edge.type === 'attacked' ? '#ef4444' :
                                        edge.type === 'controls' ? '#f97316' : '#6b7280';

                                    return (
                                        <motion.line
                                            key={idx}
                                            x1={from.x}
                                            y1={from.y}
                                            x2={to.x}
                                            y2={to.y}
                                            stroke={color}
                                            strokeWidth={edge.weight * 2}
                                            strokeOpacity={0.5}
                                            initial={{ pathLength: 0 }}
                                            animate={{ pathLength: 1 }}
                                            transition={{ duration: 0.5, delay: idx * 0.05 }}
                                        />
                                    );
                                })}

                                {/* Draw nodes */}
                                {nodes.map((node, idx) => {
                                    const pos = nodePositions[node.id];
                                    if (!pos) return null;

                                    const color = getNodeColor(node.type, node.risk);
                                    const radius = node.type === 'SUSPECT' ? 30 : 20;

                                    return (
                                        <motion.g
                                            key={node.id}
                                            initial={{ opacity: 0, scale: 0 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            transition={{ duration: 0.3, delay: idx * 0.05 }}
                                        >
                                            <circle
                                                cx={pos.x}
                                                cy={pos.y}
                                                r={radius}
                                                fill={color}
                                                fillOpacity={0.2}
                                                stroke={color}
                                                strokeWidth={2}
                                            />
                                            <text
                                                x={pos.x}
                                                y={pos.y + radius + 15}
                                                textAnchor="middle"
                                                fill="#94a3b8"
                                                fontSize="10"
                                            >
                                                {node.label.length > 12 ? node.label.substring(0, 12) + '...' : node.label}
                                            </text>
                                        </motion.g>
                                    );
                                })}
                            </svg>

                            {/* Legend */}
                            <div className="absolute bottom-4 left-4 bg-slate-900/90 p-3 rounded border border-slate-800 text-xs">
                                <div className="font-bold text-slate-400 mb-2">LEGEND</div>
                                <div className="space-y-1">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 rounded-full bg-red-500"></div>
                                        <span className="text-slate-300">Suspect</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                                        <span className="text-slate-300">Fake Profile</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                                        <span className="text-slate-300">Bot</span>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                                        <span className="text-slate-300">Victim</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-16 text-slate-500">
                            <Share2 className="h-16 w-16 mx-auto mb-4 opacity-50" />
                            <p>No graph data yet.</p>
                            <p className="text-xs mt-1">Load demo data or process evidence to build the network.</p>
                        </div>
                    )}
                </div>

                {/* Right Panel - Metrics & Clusters */}
                <div className="space-y-4">
                    {/* Top Broker */}
                    {attribution && (
                        <div className="glass-panel rounded-xl border border-red-500/30 p-4">
                            <h3 className="text-sm font-bold text-red-400 mb-3 flex items-center">
                                <Target className="h-4 w-4 mr-2" />
                                TOP BROKER
                            </h3>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-white">{attribution.suspect}</div>
                                <div className="text-xs text-slate-500 mt-1">{attribution.role}</div>
                                <div className="mt-3 text-3xl font-black text-red-500">
                                    {attribution.confidence_score}%
                                </div>
                                <div className="text-xs text-slate-500">Confidence Score</div>
                            </div>
                        </div>
                    )}

                    {/* Clusters */}
                    {metrics?.clusters && metrics.clusters.length > 0 && (
                        <div className="glass-panel rounded-xl border border-slate-700 p-4">
                            <h3 className="text-sm font-bold text-slate-400 mb-3">DETECTED CLUSTERS</h3>
                            <div className="space-y-3">
                                {metrics.clusters.map((cluster: any, idx: number) => (
                                    <motion.div
                                        key={idx}
                                        className="p-3 bg-slate-900 rounded-lg"
                                        initial={{ opacity: 0, x: 10 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.1 }}
                                    >
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-xs text-slate-500">Cluster {cluster.id}</span>
                                            <span className="text-xs bg-slate-800 px-2 py-0.5 rounded text-slate-400">
                                                {cluster.members?.length || 0} members
                                            </span>
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                            {cluster.members?.slice(0, 5).map((member: string, mIdx: number) => (
                                                <span
                                                    key={mIdx}
                                                    className="text-[10px] px-1.5 py-0.5 bg-slate-800 rounded text-slate-300"
                                                >
                                                    {member}
                                                </span>
                                            ))}
                                            {cluster.members?.length > 5 && (
                                                <span className="text-[10px] px-1.5 py-0.5 text-slate-500">
                                                    +{cluster.members.length - 5} more
                                                </span>
                                            )}
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Node List */}
                    {nodes.length > 0 && (
                        <div className="glass-panel rounded-xl border border-slate-700 p-4 max-h-80 overflow-y-auto">
                            <h3 className="text-sm font-bold text-slate-400 mb-3">ALL NODES</h3>
                            <div className="space-y-2">
                                {nodes.map((node, idx) => (
                                    <motion.div
                                        key={node.id}
                                        className="flex items-center justify-between p-2 bg-slate-900 rounded"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: idx * 0.02 }}
                                    >
                                        <div className="flex items-center space-x-2">
                                            <div style={{ color: getNodeColor(node.type, node.risk) }}>
                                                {getNodeIcon(node.type)}
                                            </div>
                                            <span className="text-sm text-white truncate max-w-[120px]">
                                                {node.label}
                                            </span>
                                        </div>
                                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${node.risk === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                                                node.risk === 'LOW' ? 'bg-emerald-500/20 text-emerald-400' :
                                                    'bg-amber-500/20 text-amber-400'
                                            }`}>
                                            {node.risk}
                                        </span>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Connection Details */}
            {edges.length > 0 && (
                <div className="glass-panel rounded-xl border border-slate-700 p-6">
                    <h3 className="text-lg font-bold text-white mb-4">CONNECTION DETAILS</h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead className="text-xs text-slate-500 uppercase">
                                <tr>
                                    <th className="text-left py-2">From</th>
                                    <th className="text-left py-2">To</th>
                                    <th className="text-left py-2">Type</th>
                                    <th className="text-right py-2">Weight</th>
                                </tr>
                            </thead>
                            <tbody className="text-slate-300">
                                {edges.map((edge, idx) => (
                                    <tr key={idx} className="border-t border-slate-800">
                                        <td className="py-2 font-mono">{edge.from}</td>
                                        <td className="py-2 font-mono">{edge.to}</td>
                                        <td className="py-2">
                                            <span className={`px-2 py-0.5 rounded text-xs ${edge.type === 'attacked' ? 'bg-red-500/20 text-red-400' :
                                                    edge.type === 'controls' ? 'bg-orange-500/20 text-orange-400' :
                                                        'bg-slate-700 text-slate-400'
                                                }`}>
                                                {edge.type}
                                            </span>
                                        </td>
                                        <td className="py-2 text-right">{edge.weight.toFixed(1)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
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
