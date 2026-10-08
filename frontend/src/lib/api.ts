const API = "";

export async function fetchDashboard() {
  const res = await fetch(`${API}/api/dashboard`, { cache: "no-store" });
  return res.json();
}

export async function fetchAlerts(severity?: string, status?: string) {
  const params = new URLSearchParams();
  if (severity) params.set("severity", severity);
  if (status) params.set("status", status);
  const res = await fetch(`${API}/api/alerts?${params}`, { cache: "no-store" });
  return res.json();
}

export async function fetchAlert(id: string) {
  const res = await fetch(`${API}/api/alerts/${id}`, { cache: "no-store" });
  return res.json();
}

export async function triageAlert(id: string) {
  const res = await fetch(`${API}/api/alerts/${id}/triage`, { method: "POST" });
  return res.json();
}

export async function investigateAlert(id: string) {
  const res = await fetch(`${API}/api/alerts/${id}/investigate`, { method: "POST" });
  return res.json();
}

export async function fetchInvestigations() {
  const res = await fetch(`${API}/api/investigations`, { cache: "no-store" });
  return res.json();
}

export async function fetchInvestigation(id: string) {
  const res = await fetch(`${API}/api/investigations/${id}`, { cache: "no-store" });
  return res.json();
}

export async function updateAlertStatus(id: string, status: string) {
  const res = await fetch(`${API}/api/alerts/${id}/status?status=${status}`, { method: "PATCH" });
  return res.json();
}
