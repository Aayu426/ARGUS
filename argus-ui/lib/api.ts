
const API_BASE = "http://localhost:8000/api";

export const ArgusAPI = {
    async createCase() {
        try {
            const res = await fetch(`${API_BASE}/case/new`, { method: "POST" });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    async uploadEvidence(caseId: string, file: File) {
        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch(`${API_BASE}/evidence/upload/${caseId}`, {
                method: "POST",
                body: formData
            });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    async analyzeText(text: string) {
        try {
            const caseRes = await this.createCase();
            if (!caseRes) return null;

            const res = await fetch(`${API_BASE}/nlp/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ case_id: caseRes.case_id, text })
            });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    async analyzeImage(caseId: string, file: File) {
        try {
            const uploadRes = await this.uploadEvidence(caseId, file);
            if (!uploadRes || uploadRes.status !== "uploaded") return null;

            const res = await fetch(`${API_BASE}/vision/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    case_id: caseId,
                    file_path: uploadRes.file_path
                })
            });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    // === GRAPH API ===
    async buildGraph(interactions: any[]) {
        try {
            const res = await fetch(`${API_BASE}/graph/build`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ interactions })
            });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    async analyzeGraph() {
        try {
            const res = await fetch(`${API_BASE}/graph/analyze`);
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    // === GEOTAG API ===
    async extractGeotag(file: File) {
        try {
            const formData = new FormData();
            formData.append("file", file);

            const res = await fetch(`${API_BASE}/vision/geotag/upload`, {
                method: "POST",
                body: formData
            });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    // === FULL VISION ANALYSIS ===
    async fullVisionAnalysis(filePath: string) {
        try {
            const res = await fetch(`${API_BASE}/vision/full-analysis`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ file_path: filePath })
            });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    // === CONFIDENCE SCORE ===
    async calculateConfidence(data: any) {
        try {
            const res = await fetch(`${API_BASE}/confidence-score`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    // === INTEGRITY ===
    async verifyIntegrity() {
        try {
            const res = await fetch(`${API_BASE}/integrity/verify`);
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    // === DASHBOARD ===
    async getDashboardSummary() {
        try {
            const res = await fetch(`${API_BASE}/dashboard/summary`);
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    // === FORENSICS / FILE RECOVERY ===
    async scanEvidence() {
        try {
            const res = await fetch(`${API_BASE}/forensics/scan-evidence`, { method: "POST" });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    },

    // === REPORT GENERATION ===
    async generateReport(caseId: string, analysisResults: any) {
        try {
            const res = await fetch(`${API_BASE}/report/enhanced`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ case_id: caseId, analysis_results: analysisResults })
            });
            return await res.json();
        } catch (e) {
            console.error("API Error", e);
            return null;
        }
    }
};
