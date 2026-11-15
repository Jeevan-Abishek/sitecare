import { useState } from "react";
import { Search, Plus } from "lucide-react";
import { API } from "../lib/api";
import { CATEGORIES, DEFAULT_FILTERS } from "../lib/constants";
import { Button } from "../components/ui";

export default function FindBusinesses() {
  const [filters, setFilters] = useState({ ...DEFAULT_FILTERS });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<any>(null);

  const handleDiscover = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const r = await API.discover(filters);
      setResult(r.data);
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.message || "Discovery failed");
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const r = await API.importCsv(file);
      setImportResult(r.data);
      e.target.value = "";
    } catch (err: any) {
      alert(err.response?.data?.detail || "Import failed");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-900">Find Businesses</h1>
        <p className="text-gray-600">Discover local businesses that may need website maintenance. Default location: Tamil Nadu, India.</p>
      </div>

      <div className="card">
        <form onSubmit={handleDiscover} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase">Country</label>
              <select className="select" value={filters.country} onChange={(e) => setFilters({ ...filters, country: e.target.value })}>
                <option>India</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase">State</label>
              <select className="select" value={filters.state} onChange={(e) => setFilters({ ...filters, state: e.target.value })}>
                <option>Tamil Nadu</option><option>Kerala</option><option>Karnataka</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase">City</label>
              <input className="input" value={filters.city} onChange={(e) => setFilters({ ...filters, city: e.target.value })} placeholder="e.g. Chennai" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase">Category</label>
              <select className="select" value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
                {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase">Limit</label>
              <select className="select" value={String(filters.limit)} onChange={(e) => setFilters({ ...filters, limit: Number(e.target.value) })}>
                {[10, 25, 50, 100].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase">Website required</label>
              <select className="select" value={String(filters.website_available)} onChange={(e) => setFilters({ ...filters, website_available: e.target.value === "true" })}>
                <option value="true">Yes</option><option value="false">No</option>
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase">Provider</label>
              <select className="select" value={filters.provider || "osm"} onChange={(e) => setFilters({ ...filters, provider: e.target.value })}>
                <option value="osm">OpenStreetMap (Free)</option>
                <option value="google_places">Google Places (API Key)</option>
              </select>
              {filters.provider === "google_places" && (
                <p className="text-xs text-gray-500 mt-1">Requires GOOGLE_PLACES_API_KEY in .env</p>
              )}
            </div>
          </div>
          <div className="pt-4">
            <Button loading={loading} type="submit">
              <Search size={18} className="mr-2" /> Discover Businesses
            </Button>
          </div>
        </form>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          Discovery provider unavailable ({error}).<br />
          <span className="mt-1 block text-red-600">Fallback: import a CSV or add websites manually below.</span>
        </div>
      )}

      {result && (
        <div className="card">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
            <div>
              <h2 className="font-semibold text-navy-900">Discovery Results</h2>
              <p className="text-sm text-gray-600">{result.total} businesses found via <span className="font-mono text-xs">{result.provider}</span></p>
              <p className="text-xs text-gray-500 mt-1">{result.coverage_note}</p>
            </div>
          </div>
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase border-b border-gray-200">
                  <th className="px-4 py-3">Business</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">City</th>
                  <th className="px-4 py-3">Website</th>
                  <th className="px-4 py-3">Phone</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {result.businesses.map((b: any, i: number) => (
                  <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900 font-medium">{b.business_name}</td>
                    <td className="px-4 py-3 text-gray-600">{b.category}</td>
                    <td className="px-4 py-3 text-gray-600">{b.city || "—"}</td>
                    <td className="px-4 py-3 text-gray-600">{b.website || <span className="text-gray-400">none</span>}</td>
                    <td className="px-4 py-3 text-gray-600">{b.phone || "—"}</td>
                    <td className="px-4 py-3 text-right">
                      <button className="text-sm text-blue-600 hover:underline" onClick={() => {}}>Audit</button>
                    </td>
                  </tr>
                ))}
                {result.businesses.length === 0 && (
                  <tr><td colSpan={6} className="px-4 py-8 text-center text-gray-500">No businesses found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-4">Import CSV</h2>
          <p className="text-sm text-gray-600 mb-3">Import business leads from a CSV file (columns: business_name, category, city, website, phone, email, address, source_url).</p>
          <input type="file" accept=".csv" onChange={handleImport} className="block w-full text-sm text-gray-600 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100" />
          {importResult && (
            <div className="mt-3 p-3 rounded bg-green-50 text-green-800 text-xs">
              Imported {importResult.imported} business(es){importResult.skipped ? `, skipped ${importResult.skipped}` : ""}.
            </div>
          )}
        </div>

        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-4">Add Website Manually</h2>
          <p className="text-sm text-gray-600 mb-3">Run an audit directly on any public website URL.</p>
          <div className="space-y-3">
            <input className="input" id="manualUrl" placeholder="https://example.com" />
            <Button onClick={() => {
              const url = (document.getElementById("manualUrl") as HTMLInputElement).value;
              if (!url) return alert("Enter a URL");
              window.location.href = `/audits?url=${encodeURIComponent(url)}`;
            }}>
              <Plus size={18} className="mr-2" /> Audit Website
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
