import { useEffect, useState } from "react";
import { Mail, Search } from "lucide-react";
import { API, Business } from "../lib/api";
import { Button } from "../components/ui";

export default function OutreachGenerator() {
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [outreach, setOutreach] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    API.listBusinesses({ limit: 100 }).then((r) => setBusinesses(r.data.filter((b: any) => b.website)));
  }, []);

  const generate = async () => {
    if (!selected) return;
    setLoading(true);
    try {
      const r = await API.generateOutreach(selected);
      setOutreach(r.data);
    } catch (e) {
      alert("Failed to generate outreach");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-navy-900">Outreach Generator</h1>
        <p className="text-gray-600">Generate WhatsApp, email, proposal, and follow-up messages for a lead. Messages are not sent automatically.</p>
      </div>

      <div className="card">
        <div className="space-y-4">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-gray-500 uppercase block">Select Business</label>
            <select className="select" value={selected ?? ""} onChange={(e) => setSelected(Number(e.target.value))}>
              <option value="">— Choose a business with a website —</option>
              {businesses.map((b) => <option key={b.id} value={b.id}>{b.business_name}</option>)}
            </select>
          </div>
          <Button onClick={generate} loading={loading} disabled={!selected}>
            <Mail size={18} className="mr-2" /> Generate Outreach
          </Button>
        </div>
      </div>

      {outreach && (
        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-4">Generated Messages</h2>
          <div className="space-y-4">
            <div className="p-4 rounded bg-blue-50 border border-blue-200">
              <p className="text-xs font-semibold text-blue-800 uppercase mb-2">WhatsApp</p>
              <p className="text-sm text-gray-900 whitespace-pre-wrap">{outreach.whatsapp_message}</p>
            </div>
            <div className="p-4 rounded bg-blue-50 border border-blue-200">
              <p className="text-xs font-semibold text-blue-800 uppercase mb-2">Email</p>
              <p className="text-sm font-medium text-gray-900">{outreach.email_subject}</p>
              <p className="text-sm text-gray-700 whitespace-pre-wrap mt-2">{outreach.email_body}</p>
            </div>
            <div className="p-4 rounded bg-green-50 border border-green-200">
              <p className="text-xs font-semibold text-green-800 uppercase mb-2">Proposal</p>
              <p className="text-sm text-gray-800 whitespace-pre-wrap">{outreach.proposal}</p>
            </div>
            <div className="p-4 rounded bg-orange-50 border border-orange-200">
              <p className="text-xs font-semibold text-orange-800 uppercase mb-2">Follow-up</p>
              <p className="text-sm text-gray-800 whitespace-pre-wrap">{outreach.followup_message}</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">These messages use only publicly listed business contact information. Copy and send manually—this app never sends automatically.</p>
        </div>
      )}
    </div>
  );
}
