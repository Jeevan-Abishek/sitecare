import { useState, useEffect } from "react";
import { Search, Trash2, Phone, Mail, Edit3, ArrowRight, ChevronLeft, ChevronRight as ChevronRightIcon } from "lucide-react";
import { API, Lead } from "../lib/api";
import { STATUS_COLOR, STATUS_LABELS, SCORE_LABEL } from "../lib/constants";
import { Button } from "../components/ui";

export default function QualifiedLeads() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [city, setCity] = useState("");
  const [priority, setPriority] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState("score");
  const [dir, setDir] = useState("desc");
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState<number | null>(null);

  const fetch = async () => {
    setLoading(true);
    try {
      const r = await API.listLeads({
        skip: (page - 1) * pageSize,
        limit: pageSize,
        search: search || undefined,
        category: category || undefined,
        city: city || undefined,
        priority: priority || undefined,
        status: status || undefined,
      });
      // API returns a list without total; approximate total from length for pagination UI
      setLeads(r.data);
      setTotal(Math.max(r.data.length, (page - 1) * pageSize + r.data.length));
    } catch (e) {
      alert("Failed to load leads");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetch(); }, [page, pageSize, search, category, city, priority, status, sort, dir]);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this lead?")) return;
    setDeleting(id);
    try {
      await API.deleteLead(id);
      setLeads(leads.filter((l) => l.id !== id));
    } catch (e) {
      alert("Delete failed");
    } finally {
      setDeleting(null);
    }
  };

  const handleStatus = (id: number, value: string) => {
    const lead = leads.find((l) => l.id === id);
    API.updateLead(id, { lead_status: value }).then(() => {
      if (lead) lead.lead_status = value;
    }).catch(() => alert("Update failed"));
  };

  const pages = Math.ceil(total / pageSize) || 1;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-navy-900">Qualified Leads</h1>
          <p className="text-gray-600">Manage and score leads discovered from audited websites.</p>
        </div>
        <Button asChild={false} onClick={() => window.location.assign("/discover")}>
          <ArrowRight size={16} className="mr-2" /> Find Businesses
        </Button>
      </div>

      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
            <input
              className="input pl-10"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search business or city..."
            />
          </div>
          <select className="select" value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}>
            <option value="">All Categories</option>
          </select>
          <select className="select" value={priority} onChange={(e) => { setPriority(e.target.value); setPage(1); }}>
            <option value="">All Priorities</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
          </select>
          <select className="select" value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}>
            <option value="">All Statuses</option><option value="new">New</option><option value="contacted">Contacted</option><option value="interested">Interested</option><option value="converted">Converted</option>
          </select>
        </div>

        <div className="overflow-hidden rounded-lg border border-gray-200">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase border-b border-gray-200">
                  <th className="px-4 py-3 cursor-pointer hover:bg-gray-100" onClick={() => { setSort("business_name"); setDir(dir === "asc" ? "desc" : "asc"); }}>
                    Business <span className="ml-1 text-gray-400">{sort === "business_name" ? (dir === "asc" ? "▲" : "▼") : ""}</span>
                  </th>
                  <th className="px-4 py-3">City</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Website</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Phone</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead) => {
                  const b = lead.business;
                  const score = lead.business.audits?.[0]?.score ?? 0;
                  const issues = lead.business.audits?.[0]?.verified_issues?.length ?? 0;
                  return (
                    <tr key={lead.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-900 font-medium">{b.business_name}</td>
                      <td className="px-4 py-3 text-gray-600">{b.city || "—"}</td>
                      <td className="px-4 py-3 text-gray-600">{b.category}</td>
                      <td className="px-4 py-3 text-gray-600 truncate max-w-[30px]">{b.website || "—"}</td>
                      <td className="px-4 py-3">
                        <span className={`badge ${score >= 70 ? "bg-red-100 text-red-700 border-red-200" : score >= 40 ? "bg-orange-100 text-orange-700 border-orange-200" : "bg-green-100 text-green-700 border-green-200"}`}>
                          {score}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-600">{b.phone || "—"}</td>
                      <td className="px-4 py-3 text-gray-600 truncate max-w-[28px]">{b.email || "—"}</td>
                      <td className="px-4 py-3">
                        <span className={`badge ${STATUS_COLOR[lead.lead_status || "new"]}`}>
                          {STATUS_LABELS[lead.lead_status || "new"]}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            className="p-2 text-gray-400 hover:text-blue-600"
                            onClick={() => window.location.assign(`/leads/${lead.id}`)}
                            title="View details"
                          >
                            <ArrowRight size={16} />
                          </button>
                          <select
                            className="text-xs border border-gray-300 rounded px-1.5 py-1 bg-white"
                            value={lead.lead_status || "new"}
                            onChange={(e) => handleStatus(lead.id, e.target.value)}
                            >
                            {["new", "contacted", "interested", "converted"].map((s) => (
                              <option key={s} value={s}>{STATUS_LABELS[s]}</option>
                            ))}
                          </select>
                          <button
                            className="p-2 text-gray-400 hover:text-red-600"
                            onClick={() => handleDelete(lead.id)}
                            disabled={deleting === lead.id}
                          >
                            {deleting === lead.id ? (
                              <span className="flex h-4 w-4 items-center justify-center">
                                <span className="animate-spin block h-3 w-3 border-2 border-current rounded-full border-t-transparent" />
                              </span>
                            ) : (
                              <Trash2 size={16} />
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {leads.length === 0 && (
                  <tr><td colSpan={10} className="px-4 py-12 text-center text-gray-500">No leads found. Start by discovering and auditing businesses.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="flex items-center justify-between gap-4 mt-4 text-sm">
          <div className="text-gray-600">Showing {leads.length} lead(s)</div>
          <div className="flex items-center gap-2 text-gray-600">
            <button
              disabled={page === 1 || loading}
              onClick={() => setPage(page - 1)}
              className="px-3 py-1 rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronLeft size={16} />
            </button>
            <span className="px-2 font-medium">{page} / {pages}</span>
            <button
              disabled={page >= pages || loading}
              onClick={() => setPage(page + 1)}
              className="px-3 py-1 rounded border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronRightIcon size={16} />
            </button>
          </div>
            <select className="select w-auto" value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}>
              {[10, 25, 50].map((n) => (
                <option key={n} value={n}>{n} per page</option>
              ))}
            </select>
        </div>
      </div>
    </div>
  );
}
