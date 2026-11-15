import { useState, useEffect } from "react";
import { Activity, Play, RefreshCw, ShieldAlert, Clock, Layers, Laptop, Code, Wifi } from "lucide-react";
import { API } from "../lib/api";
import { Button } from "../components/ui";

const Issue = ({ text }: { text: string }) => (
  <li className="flex items-start gap-2 text-sm text-gray-700">
    <span className="text-red-500 shrink-0 mt-0.5">·</span>
    <span>{text}</span>
  </li>
);

export default function WebsiteAudits() {
  const [url, setUrl] = useState("");
  const [maxPages, setMaxPages] = useState(10);
  const [includePagespeed, setIncludePagespeed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const u = params.get("url");
    if (u) setUrl(u);
  }, []);

  const handleAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await API.audit(url, maxPages, includePagespeed);
      setResult(r.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "Audit failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-900">Website Audits</h1>
        <p className="text-gray-600">Audit a public website for verified technical issues. Checks include SSL, broken links, mobile viewport, metadata, tech stack, and Core Web Vitals.</p>
      </div>

      <div className="card">
        <form onSubmit={handleAudit} className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-500 uppercase block">Website URL</label>
            <input
              className="input"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase block">Max pages to crawl</label>
              <select className="select" value={String(maxPages)} onChange={(e) => setMaxPages(Number(e.target.value))}>
                {[1, 3, 5, 10, 20].map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
              <p className="text-xs text-gray-400">Limited to protect target sites.</p>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-semibold text-gray-500 uppercase block">PageSpeed Insights</label>
              <select className="select" value={String(includePagespeed)} onChange={(e) => setIncludePagespeed(e.target.value === "true")}>
                <option value="false">Disabled</option>
                <option value="true">Enable (needs API key)</option>
              </select>
            </div>
          </div>
          <Button type="submit" loading={loading}>
            <Play size={18} className="mr-2" /> Run Audit
          </Button>
        </form>
      </div>

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {error}
        </div>
      )}

      {result && (
        <div className="card">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6 border-b border-gray-200 pb-4">
            <div>
              <h2 className="font-bold text-navy-900">{result.website}</h2>
              <p className="text-sm text-gray-600">
                HTTP {result.http_status} &middot; Reachable: {result.reachable ? "Yes" : "No"} &middot;
                SSL: {result.ssl_status?.valid ? "Valid" : result.ssl_status?.valid === false ? "Invalid" : "N/A"}
              </p>
            </div>
            <div className="flex gap-3">
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${result.score >= 70 ? "bg-red-100 text-red-700" : result.score >= 40 ? "bg-orange-100 text-orange-700" : "bg-green-100 text-green-700"}`}>
                Score: {result.score}/100
              </span>
              <span className="text-xs font-medium text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
                {result.audit_confidence} confidence
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 rounded-lg bg-gray-50">
              <div className="text-xs font-semibold text-gray-500 uppercase">Response Time</div>
              <div className="text-lg font-mono text-navy-900">{result.response_time}</div>
            </div>
            <div className="p-4 rounded-lg bg-gray-50">
              <div className="text-xs font-semibold text-gray-500 uppercase">HTML Size</div>
              <div className="text-lg font-mono text-navy-900">{result.performance_metrics?.html_size_bytes ?? 0} bytes</div>
            </div>
            <div className="p-4 rounded-lg bg-gray-50">
              <div className="text-xs font-semibold text-gray-500 uppercase">Images</div>
              <div className="text-lg font-mono text-navy-900">{result.performance_metrics?.image_count ?? 0}</div>
            </div>
          </div>

          {result.pagespeed_metrics && (
            <div className="mb-6">
              <h3 className="font-semibold text-navy-900 mb-3 flex items-center gap-2">
                <Laptop size={16} className="text-indigo-600" /> PageSpeed Insights ({result.pagespeed_metrics.strategy})
              </h3>
              <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                <div><div className="text-xs text-gray-500 uppercase">Performance</div><div className="text-lg font-mono font-bold">{result.pagespeed_metrics.performance_score ?? "—"}/100</div></div>
                <div><div className="text-xs text-gray-500 uppercase">SEO</div><div className="text-lg font-mono font-bold">{result.pagespeed_metrics.seo_score ?? "—"}/100</div></div>
                <div><div className="text-xs text-gray-500 uppercase">LCP</div><div className="text-lg font-mono font-bold">{result.core_web_vitals?.LCP ?? "—"} ms</div></div>
                <div><div className="text-xs text-gray-500 uppercase">CLS</div><div className="text-lg font-mono font-bold">{result.core_web_vitals?.CLS ?? "—"}</div></div>
                <div><div className="text-xs text-gray-500 uppercase">TBT</div><div className="text-lg font-mono font-bold">{result.core_web_vitals?.TBT ?? "—"} ms</div></div>
                <div><div className="text-xs text-gray-500 uppercase">FCP</div><div className="text-lg font-mono font-bold">{result.core_web_vitals?.FCP ?? "—"} ms</div></div>
              </div>
            </div>
          )}

          {result.tech_stack && (
            <div className="mb-6">
              <h3 className="font-semibold text-navy-900 mb-3 flex items-center gap-2">
                <Code size={16} className="text-purple-600" /> Technology Stack
              </h3>
              <div className="flex gap-2 flex-wrap">
                {result.tech_stack.cms && <span className="px-3 py-1 rounded bg-blue-50 text-blue-700 text-xs font-medium border border-blue-200">CMS: {result.tech_stack.cms}</span>}
                {result.tech_stack.ecommerce && <span className="px-3 py-1 rounded bg-green-50 text-green-700 text-xs font-medium border border-green-200">E-comm: {result.tech_stack.ecommerce}</span>}
                {result.tech_stack.frontend && <span className="px-3 py-1 rounded bg-purple-50 text-purple-700 text-xs font-medium border border-purple-200">Frontend: {result.tech_stack.frontend}</span>}
                {result.tech_stack.indicators?.slice(0, 3).map((ind: string, i: number) => (
                  <span key={i} className="px-3 py-1 rounded bg-gray-100 text-gray-700 text-xs border border-gray-200">{ind}</span>
                ))}
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-navy-900 mb-3 flex items-center gap-2">
                <ShieldAlert size={16} className="text-red-600" /> Verified Issues
              </h3>
              {result.verified_issues?.length ? (
                <ul className="space-y-2">{result.verified_issues.map((t: string, i: number) => <Issue key={i} text={t} />)}</ul>
              ) : (
                <p className="text-sm text-green-600">No verified issues detected.</p>
              )}
            </div>
            <div>
              <h3 className="font-semibold text-navy-900 mb-3 flex items-center gap-2">
                <Layers size={16} className="text-gray-600" /> Details
              </h3>
              <div className="text-xs text-gray-600 space-y-1 bg-gray-50 p-3 rounded">
                <div><span className="font-medium">Pages crawled:</span> {result.details?.crawled_pages}</div>
                <div><span className="font-medium">Internal links found:</span> {result.details?.internal_links_found}</div>
                <div><span className="font-medium">External links found:</span> {result.details?.external_links_found}</div>
                <div><span className="font-medium">Title:</span> {result.details?.title || "—"}</div>
                <div><span className="font-medium">SSL expiry:</span> {result.ssl_expiry_date || "—"}</div>
                <div><span className="font-medium">Confidence:</span> {result.audit_confidence}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
