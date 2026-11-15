import axios, { AxiosInstance } from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

export const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

export type Business = {
  id: number;
  business_name: string;
  category: string;
  city: string | null;
  state: string | null;
  country: string | null;
  website: string | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  source_url: string | null;
  source: string;
  discovery_provider: string | null;
  google_place_id: string | null;
  domain: string | null;
  is_discovered: boolean;
  created_at: string;
};

export type Audit = {
  id: number;
  business_id: number;
  audit_date: string;
  http_status: number | null;
  response_time: string | null;
  ssl_status: any;
  ssl_expiry_date: string | null;
  performance_metrics: any;
  pagespeed_metrics: any;
  core_web_vitals: any;
  tech_stack: any;
  verified_issues: string[];
  score: number | null;
  audit_confidence: string | null;
  details: any;
};

export type Lead = {
  id: number;
  business_id: number;
  priority: string | null;
  lead_status: string | null;
  recommended_service: string | null;
  notes: string | null;
  created_at: string;
  business: Business;
};

export type DashboardStats = {
  total_businesses: number;
  websites_found: number;
  websites_audited: number;
  websites_with_issues: number;
  high_priority_leads: number;
  potential_monthly_revenue: number;
  sites_down: number;
  ssl_expiring_soon: number;
};

export type DiscoveryFilters = {
  country: string;
  state: string;
  city?: string;
  category: string;
  industry?: string;
  website_available: boolean;
  limit: number;
  provider?: string;
};

export type DiscoveryResult = {
  total: number;
  businesses: any[];
  provider: string;
  coverage_note: string;
  filters: DiscoveryFilters;
};

export type AuditResult = {
  business_id: number | null;
  website: string;
  http_status: number | null;
  reachable: boolean;
  response_time: string;
  ssl_status: any;
  ssl_expiry_date: string | null;
  performance_metrics: any;
  pagespeed_metrics: any;
  core_web_vitals: any;
  tech_stack: any;
  verified_issues: string[];
  score: number;
  audit_confidence: string;
  details: any;
};

export type OutreachResult = {
  business_id: number;
  whatsapp_message: string | null;
  whatsapp_url: string | null;
  email_subject: string | null;
  email_body: string | null;
  email_mailto: string | null;
  proposal: string | null;
  followup_message: string | null;
  audit_summary: string | null;
};

export type ReportOut = {
  business_id: number;
  report_title: string;
  report_body: string;
  generated_at: string;
  provider: string;
  pdf_url: string | null;
};

export type CsvImportResult = {
  imported: number;
  skipped: number;
  errors: string[];
};

export type MonitorOut = {
  id: number;
  business_id: number;
  last_check: string | null;
  uptime_status: string | null;
  response_time_ms: number | null;
  ssl_days_until_expiry: number | null;
  ssl_expiring_soon: boolean;
  site_down: boolean;
  alert_sent: boolean;
};

export const API = {
  discover: (filters: DiscoveryFilters) => api.post<DiscoveryResult>("/discover", filters),
  audit: (website: string, max_pages?: number, include_pagespeed = false) =>
    api.post<AuditResult>("/audit", { website, max_pages, include_pagespeed }),
  auditBulk: (urls: string[], max_pages?: number) =>
    api.post<AuditResult[]>("/audit/bulk", { website_urls: urls, max_pages }),
  listBusinesses: (params?: any) => api.get<Business[]>("/businesses", { params }),
  createBusiness: (data: any) => api.post<Business>("/businesses", data),
  importCsv: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post<CsvImportResult>("/import/csv", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  listLeads: (params?: any) => api.get<Lead[]>("/leads", { params }),
  getLead: (id: number) => api.get<Lead>(`/leads/${id}`),
  updateLead: (id: number, data: any) => api.patch<Lead>(`/leads/${id}`, data),
  deleteLead: (id: number) => api.delete<void>(`/leads/${id}`),
  exportCsv: () => api.get("/export/csv", { responseType: "blob" }),
  generateOutreach: (business_id: number) =>
    api.post<OutreachResult>("/outreach/generate", { business_id }),
  listReports: () => api.get<ReportOut[]>("/reports"),
  getReport: (business_id: number, provider = "rules") =>
    api.get<ReportOut>(`/reports/${business_id}`, { params: { provider } }),
  downloadPdf: (business_id: number) =>
    api.get(`/reports/${business_id}/pdf`, { responseType: "blob" }),
  runMonitorCheck: () => api.post("/monitor/check"),
  monitorStatus: () => api.get<MonitorOut[]>("/monitor/status"),
  monitorDashboard: () => api.get<{ sites_down: number; ssl_expiring_soon: number; total_monitored: number }>("/monitor/dashboard"),
};
