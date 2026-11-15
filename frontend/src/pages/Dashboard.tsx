import { useEffect, useState } from "react";
import {
  LayoutDashboard, Building, Activity, Target, DollarSign, TrendingUp, AlertCircle,
  ShieldAlert, Globe, RefreshCw,
} from "lucide-react";
import { API, DashboardStats } from "../lib/api";
import { Button } from "../components/ui";

const Stat = ({ icon: Icon, label, value, delta, color }: any) => (
  <div className="card">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-500">{label}</p>
        <p className="mt-1 text-2xl font-bold text-navy-900">{value}</p>
        {delta && <p className="text-xs text-green-600 mt-1">{delta}</p>}
      </div>
      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${color}`}>
        <Icon size={20} />
      </div>
    </div>
  </div>
);

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    total_businesses: 0, websites_found: 0, websites_audited: 0,
    websites_with_issues: 0, high_priority_leads: 0, potential_monthly_revenue: 0,
    sites_down: 0, ssl_expiring_soon: 0,
  });
  const [recent, setRecent] = useState<any[]>([]);
  const [monitorLoading, setMonitorLoading] = useState(false);

  useEffect(() => {
    API.listBusinesses({ limit: 6 }).then((r) => setRecent(r.data));
    API.monitorDashboard().then((r) => setStats((s) => ({ ...s, sites_down: r.data.sites_down, ssl_expiring_soon: r.data.ssl_expiring_soon }))).catch(() => {});
  }, []);

  const runMonitor = async () => {
    setMonitorLoading(true);
    try {
      await API.runMonitorCheck();
      const d = await API.monitorDashboard();
      setStats((s) => ({ ...s, sites_down: d.data.sites_down, ssl_expiring_soon: d.data.ssl_expiring_soon }));
    } catch (e) {
      alert("Monitor check failed");
    } finally {
      setMonitorLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Track your website maintenance leads and audits.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Stat icon={Building} label="Businesses Discovered" value={stats.total_businesses} color="bg-blue-50 text-blue-600" />
        <Stat icon={Activity} label="Websites Found" value={stats.websites_found} delta="+new" color="bg-indigo-50 text-indigo-600" />
        <Stat icon={Activity} label="Websites Audited" value={stats.websites_audited} color="bg-purple-50 text-purple-600" />
        <Stat icon={AlertCircle} label="With Verified Issues" value={stats.websites_with_issues} color="bg-red-50 text-red-600" />
        <Stat icon={Target} label="High-Priority Leads" value={stats.high_priority_leads} color="bg-orange-50 text-orange-600" />
        <Stat icon={DollarSign} label="Potential Monthly Revenue" value={`₹${stats.potential_monthly_revenue}`} color="bg-green-50 text-green-600" />
        <Stat icon={Globe} label="Sites Down" value={stats.sites_down} color={stats.sites_down > 0 ? "bg-red-50 text-red-600" : "bg-green-50 text-green-600"} />
        <Stat icon={ShieldAlert} label="SSL Expiring Soon" value={stats.ssl_expiring_soon} color={stats.ssl_expiring_soon > 0 ? "bg-orange-50 text-orange-600" : "bg-green-50 text-green-600"} />
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-navy-900">Uptime & SSL Monitor</h2>
          <Button onClick={runMonitor} loading={monitorLoading} size="sm">
            <RefreshCw size={16} className="mr-2" /> Run Check Now
          </Button>
        </div>
        <p className="text-sm text-gray-600 mb-3">
          Automated monitoring checks saved websites for uptime and SSL expiry.
          Sites down or SSL expiring within {30} days are flagged for retainer pitches.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card lg:col-span-2">
          <h2 className="font-semibold text-navy-900 mb-4">Recent Leads</h2>
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase border-b border-gray-200">
                  <th className="px-4 py-3">Business</th>
                  <th className="px-4 py-3">City</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((b) => {
                  const audit = b.audits?.[0];
                  const score = audit?.score ?? 0;
                  return (
                    <tr key={b.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-3 text-gray-900 font-medium">{b.business_name}</td>
                      <td className="px-4 py-3 text-gray-600">{b.city || "—"}</td>
                      <td className="px-4 py-3 text-gray-600">{b.category}</td>
                      <td className="px-4 py-3">
                        <span className={`badge ${score >= 70 ? "bg-red-50 text-red-600 border-red-200" : score >= 40 ? "bg-orange-50 text-orange-600 border-orange-200" : "bg-green-50 text-green-600 border-green-200"}`}>
                          {score}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-gray-600">{b.city ? "Active" : "New"}</td>
                    </tr>
                  );
                })}
                {recent.length === 0 && (
                  <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-500">No leads yet. Find businesses to get started.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-4">Quick Start</h2>
          <ul className="space-y-3 text-sm text-gray-600">
            <li className="flex items-center gap-2"><TrendingUp size={16} /> Discover businesses via OpenStreetMap or Google Places</li>
            <li className="flex items-center gap-2"><Activity size={16} /> Audit websites with PageSpeed & tech stack detection</li>
            <li className="flex items-center gap-2"><Target size={16} /> Review qualified leads and generate outreach</li>
            <li className="flex items-center gap-2"><ShieldAlert size={16} /> Monitor uptime & SSL expiry for retainer pitches</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
