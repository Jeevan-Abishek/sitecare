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
  performance_metrics: any;
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
};

export type DiscoveryFilters = {
  country: string;
  state: string;
  city?: string;
  category: string;
  industry?: string;
  website_available: boolean;
  limit: number;
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
  performance_metrics: any;
  verified_issues: string[];
  score: number;
  audit_confidence: string;
  details: any;
};

export type OutreachResult = {
  business_id: number;
  whatsapp_message: string | null;
  email_subject: string | null;
  email_body: string | null;
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
};

export type CsvImportResult = {
  imported: number;
  skipped: number;
  errors: string[];
};

export const API = {
  discover: (filters: DiscoveryFilters) => api.post<DiscoveryResult>("/discover", filters),
  audit: (website: string, max_pages?: number) =>
    api.post<AuditResult>("/audit", { website, max_pages }),
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
};
