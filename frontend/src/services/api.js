const API_BASE = "http://127.0.0.1:8000";

export const api = {
  // System Health
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error("Backend offline");
    return res.json();
  },

  // Cases
  async getCases(limit = 100) {
    const res = await fetch(`${API_BASE}/api/cases?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to load cases");
    return res.json();
  },

  async getCaseDossier(caseId) {
    const res = await fetch(`${API_BASE}/api/cases/${caseId}`);
    if (!res.ok) throw new Error(`Case ${caseId} not found`);
    return res.json();
  },

  // Predictions & Intelligence
  async getPrediction(caseId, tCutoff = null) {
    const url = tCutoff 
      ? `${API_BASE}/api/predictions/${caseId}?t_cutoff=${encodeURIComponent(tCutoff)}`
      : `${API_BASE}/api/predictions/${caseId}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error("Inference failed");
    return res.json();
  },

  async getExplanation(caseId, rank = 1) {
    const res = await fetch(`${API_BASE}/api/predictions/${caseId}/explain?rank=${rank}`);
    if (!res.ok) throw new Error("Explainability attribution failed");
    return res.json();
  },

  // Locations
  async getLocations() {
    const res = await fetch(`${API_BASE}/api/predictions/locations`);
    if (!res.ok) throw new Error("Failed to load locations");
    return res.json();
  },

  // Real-time Transaction Simulation
  async injectTransaction(payload) {
    const res = await fetch(`${API_BASE}/api/transactions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Failed to ingest transaction stream");
    return res.json();
  },

  // Surveillance Alerts
  async getAlerts() {
    const res = await fetch(`${API_BASE}/api/alerts?limit=20`);
    if (!res.ok) throw new Error("Failed to load alerts");
    return res.json();
  },

  async acknowledgeAlert(alertId) {
    const res = await fetch(`${API_BASE}/api/alerts/${alertId}/status`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "ACKNOWLEDGED", notes: "Field patrol dispatched" })
    });
    if (!res.ok) throw new Error("Failed to update alert");
    return res.json();
  },

  // Authentication
  async login(username, password) {
    const res = await fetch(`${API_BASE}/api/auth/login/json`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) throw new Error("Authentication failed");
    return res.json();
  }
};
