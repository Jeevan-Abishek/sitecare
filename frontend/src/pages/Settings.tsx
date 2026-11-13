import { Settings, ShieldCheck, Database } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-900">Settings</h1>
        <p className="text-gray-600">Configure SiteCare AI.</p>
      </div>

      <div className="card">
        <h2 className="font-semibold text-navy-900 mb-4">Security & Privacy</h2>
        <ul className="space-y-3 text-sm text-gray-600">
          <li className="flex items-start gap-3"><ShieldCheck size={16} className="mt-0.5 shrink-0" /> Crawl targets are validated; localhost and private IPs are blocked (SSRF protection).</li>
          <li className="flex items-start gap-3"><Database size={16} className="mt-0.5 shrink-0" /> All data stored locally in SQLite; no personal data beyond public business listings is retained.</li>
          <li className="flex items-start gap-3"><Settings size={16} className="mt-0.5 shrink-0" /> AI reporting uses a free rules-based generator by default. External LLM integration is optional.</li>
          <li className="flex items-start gap-3"><Settings size={16} className="mt-0.5 shrink-0" /> Outreach messages are generated locally and never sent automatically.</li>
        </ul>
      </div>

      <div className="card">
        <h2 className="font-semibold text-navy-900 mb-4">Limits</h2>
        <ul className="space-y-3 text-sm text-gray-600">
          <li>Max pages crawled per domain: configurable (default 10)</li>
          <li>Request timeout: 15 seconds</li>
          <li>Concurrent requests: 4</li>
          <li>Discovery: OpenStreetMap Overpass API (free)</li>
          <li>Database: SQLite (local file)</li>
        </ul>
      </div>
    </div>
  );
}
