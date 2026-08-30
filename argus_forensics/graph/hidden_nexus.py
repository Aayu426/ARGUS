
import networkx as nx
from ..core.telemetry import Telemetry
import json
import os

logger = Telemetry.get_logger("HiddenNexus")

class HiddenNexus:
    """
    Unveils indirect connections between users using Graph Analysis.
    Intended to use PyTorch Geometric (GraphSAGE) for embeddings.
    For this implementation, uses NetworkX for community detection and pathfinding.
    """
    
    def __init__(self):
        self.graph = nx.Graph()

    def add_interaction(self, user1: str, user2: str, weight: float = 1.0):
        self.graph.add_edge(user1, user2, weight=weight)

    def find_communities(self) -> dict:
        """
        Detects communities using Louvain or Greedy Modularity.
        """
        try:
            communities = list(nx.community.greedy_modularity_communities(self.graph))
            # Convert frozensets to lists
            return {f"community_{i}": list(c) for i, c in enumerate(communities)}
        except Exception as e:
            logger.error(f"Community detection failed: {e}")
            return {}

    def find_hidden_paths(self, suspect_a: str, suspect_b: str) -> list:
        """
        Finds indirect paths between two suspects.
        """
        try:
            return list(nx.all_simple_paths(self.graph, suspect_a, suspect_b, cutoff=3))
        except nx.NetworkXNoPath:
            return []
        except Exception as e:
            return []


class EnhancedGraphAnalyzer:
    """
    PRD-compliant enhanced graph analyzer with centrality, broker detection,
    anomaly scoring, and visual graph export capabilities.
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.node_metadata = {}  # Store additional node attributes
    
    def add_node(self, node_id: str, metadata: dict = None):
        """Add a node with optional metadata."""
        self.graph.add_node(node_id)
        if metadata:
            self.node_metadata[node_id] = metadata
    
    def add_interaction(self, user1: str, user2: str, interaction_type: str = "unknown", weight: float = 1.0):
        """Add an interaction (edge) between two users."""
        self.graph.add_edge(user1, user2, weight=weight, type=interaction_type)
    
    def bulk_add_interactions(self, interactions: list):
        """Add multiple interactions at once. Each item: {from, to, type, weight}"""
        for i in interactions:
            self.add_interaction(
                i.get("from", ""),
                i.get("to", ""),
                i.get("type", "interaction"),
                i.get("weight", 1.0)
            )
    
    def compute_centrality_metrics(self) -> dict:
        """
        Compute all centrality metrics for each node.
        Returns dict of node_id -> {degree, betweenness, closeness, pagerank}
        """
        if self.graph.number_of_nodes() == 0:
            return {}
        
        try:
            degree = dict(self.graph.degree())
            betweenness = nx.betweenness_centrality(self.graph)
            closeness = nx.closeness_centrality(self.graph)
            pagerank = nx.pagerank(self.graph) if self.graph.number_of_edges() > 0 else {n: 0 for n in self.graph.nodes()}
        except Exception as e:
            logger.error(f"Centrality computation failed: {e}")
            return {}
        
        metrics = {}
        for node in self.graph.nodes():
            metrics[node] = {
                "degree": degree.get(node, 0),
                "betweenness": round(betweenness.get(node, 0), 4),
                "closeness": round(closeness.get(node, 0), 4),
                "pagerank": round(pagerank.get(node, 0), 4),
            }
        
        return metrics
    
    def identify_brokers(self, top_n: int = 5) -> list:
        """
        Identify broker/influencer nodes based on high betweenness centrality.
        Brokers bridge different communities and control information flow.
        """
        if self.graph.number_of_nodes() == 0:
            return []
        
        betweenness = nx.betweenness_centrality(self.graph)
        sorted_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
        
        brokers = []
        for node, score in sorted_nodes[:top_n]:
            brokers.append({
                "node_id": node,
                "betweenness_score": round(score, 4),
                "role": "BROKER" if score > 0.1 else "INFLUENCER" if score > 0.05 else "CONNECTOR",
                "explanation": self._explain_node(node, "broker")
            })
        
        return brokers
    
    def identify_high_centrality_nodes(self, top_n: int = 5) -> list:
        """
        Identify nodes with highest overall centrality (PageRank + Degree).
        """
        if self.graph.number_of_nodes() == 0:
            return []
        
        pagerank = nx.pagerank(self.graph) if self.graph.number_of_edges() > 0 else {}
        degree = dict(self.graph.degree())
        max_degree = max(degree.values()) if degree else 1
        
        # Combined score: normalized degree + pagerank
        combined = {}
        for node in self.graph.nodes():
            norm_degree = degree.get(node, 0) / max_degree
            pr = pagerank.get(node, 0)
            combined[node] = norm_degree * 0.5 + pr * 0.5
        
        sorted_nodes = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "node_id": node,
                "centrality_score": round(score * 100, 1),
                "degree": degree.get(node, 0),
                "pagerank": round(pagerank.get(node, 0), 4),
                "explanation": self._explain_node(node, "centrality")
            }
            for node, score in sorted_nodes[:top_n]
        ]
    
    def detect_suspicious_clusters(self) -> list:
        """
        Detect clusters with bot-like behavior patterns:
        - High interconnectivity
        - Similar posting times (simulated)
        - Low diversity of connections
        """
        if self.graph.number_of_nodes() < 3:
            return []
        
        communities = list(nx.community.greedy_modularity_communities(self.graph))
        
        suspicious_clusters = []
        for i, community in enumerate(communities):
            if len(community) < 2:
                continue
            
            # Analyze cluster density
            subgraph = self.graph.subgraph(community)
            density = nx.density(subgraph)
            
            # Bot-like indicators
            avg_degree = sum(dict(subgraph.degree()).values()) / len(community)
            
            suspicion_score = 0
            reasons = []
            
            if density > 0.7:
                suspicion_score += 40
                reasons.append("Unusually high interconnection")
            if avg_degree > 5:
                suspicion_score += 30
                reasons.append("High average connections")
            if len(community) > 3 and density > 0.5:
                suspicion_score += 30
                reasons.append("Tight-knit coordinated group")
            
            if suspicion_score > 30:
                suspicious_clusters.append({
                    "cluster_id": f"cluster_{i}",
                    "members": list(community),
                    "size": len(community),
                    "density": round(density, 3),
                    "suspicion_score": min(suspicion_score, 100),
                    "verdict": "HIGH_RISK" if suspicion_score > 60 else "MEDIUM_RISK",
                    "reasons": reasons
                })
        
        return sorted(suspicious_clusters, key=lambda x: x["suspicion_score"], reverse=True)
    
    def _explain_node(self, node_id: str, context: str) -> str:
        """Generate human-readable explanation for why a node matters."""
        degree = self.graph.degree(node_id)
        neighbors = list(self.graph.neighbors(node_id))
        
        if context == "broker":
            return f"This account bridges {degree} connections and may control information flow between {len(neighbors)} different accounts."
        elif context == "centrality":
            return f"High-influence node with {degree} direct connections. Likely a key player in the network."
        else:
            return f"Connected to {degree} accounts in the network."
    
    def get_node_explanation(self, node_id: str) -> dict:
        """
        Get detailed explanation for why a specific node matters.
        PRD requirement: "Clear explanation of why this node matters"
        """
        if node_id not in self.graph:
            return {"error": "Node not found"}
        
        metrics = self.compute_centrality_metrics().get(node_id, {})
        neighbors = list(self.graph.neighbors(node_id))
        
        # Determine node type
        node_type = "REGULAR"
        if metrics.get("betweenness", 0) > 0.1:
            node_type = "BROKER"
        elif metrics.get("pagerank", 0) > 0.1:
            node_type = "INFLUENCER"
        elif metrics.get("degree", 0) > 10:
            node_type = "HUB"
        
        return {
            "node_id": node_id,
            "node_type": node_type,
            "metrics": metrics,
            "connections": len(neighbors),
            "connected_to": neighbors[:10],  # First 10
            "explanation": self._explain_node(node_id, "centrality"),
            "metadata": self.node_metadata.get(node_id, {})
        }
    
    def export_visual_graph(self, output_path: str = "graph_visualization.html") -> str:
        """
        Export interactive visual graph using pyvis.
        Falls back to JSON export if pyvis not available.
        """
        try:
            from pyvis.network import Network
            
            net = Network(height="600px", width="100%", bgcolor="#1a1a2e", font_color="white")
            net.barnes_hut()
            
            # Compute metrics for coloring
            metrics = self.compute_centrality_metrics()
            
            # Add nodes with colors based on centrality
            for node in self.graph.nodes():
                m = metrics.get(node, {})
                pagerank = m.get("pagerank", 0)
                
                # Color based on importance
                if pagerank > 0.1:
                    color = "#ff6b6b"  # Red for high importance
                elif pagerank > 0.05:
                    color = "#feca57"  # Yellow for medium
                else:
                    color = "#48dbfb"  # Blue for regular
                
                size = 10 + m.get("degree", 1) * 3
                
                net.add_node(node, label=node, color=color, size=min(size, 50), 
                           title=f"Degree: {m.get('degree', 0)}, PageRank: {m.get('pagerank', 0):.4f}")
            
            # Add edges
            for u, v, data in self.graph.edges(data=True):
                net.add_edge(u, v, title=data.get("type", "interaction"))
            
            # Save to file
            net.save_graph(output_path)
            logger.info(f"Graph visualization saved to {output_path}")
            return output_path
            
        except ImportError:
            # Fallback: export as JSON for frontend rendering
            logger.warning("pyvis not installed, exporting as JSON")
            return self._export_graph_json(output_path.replace(".html", ".json"))
    
    def _export_graph_json(self, output_path: str) -> str:
        """Export graph as JSON for frontend visualization."""
        nodes = []
        metrics = self.compute_centrality_metrics()
        
        for node in self.graph.nodes():
            m = metrics.get(node, {})
            nodes.append({
                "id": node,
                "label": node,
                "metrics": m,
                "size": 10 + m.get("degree", 1) * 2
            })
        
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "from": u,
                "to": v,
                "type": data.get("type", "interaction")
            })
        
        data = {"nodes": nodes, "edges": edges}
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return output_path
    
    def get_graph_summary(self) -> dict:
        """Get overall graph statistics."""
        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "density": round(nx.density(self.graph), 4) if self.graph.number_of_nodes() > 0 else 0,
            "is_connected": nx.is_connected(self.graph) if self.graph.number_of_nodes() > 0 else False,
            "avg_clustering": round(nx.average_clustering(self.graph), 4) if self.graph.number_of_nodes() > 0 else 0
        }

