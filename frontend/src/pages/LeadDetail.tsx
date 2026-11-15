import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Activity, Mail, FileText, ArrowLeft, Edit2, Save, Phone, MapPin, AtSign, Download, Link, Monitor, Smartphone } from "lucide-react";
import { API, Lead } from "../lib/api";
import { STATUS_COLOR, STATUS_LABELS } from "../lib/constants";
import { Button } from "../components/ui";

export default function LeadDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [lead, setLead] = useState<Lead | null>(null);
  const [loading, setLoading] = useState(true);
  const [notes, setNotes] = useState("");
  const [outreach, setOutreach] = useState<any>(null);
  const [report, setReport] = useState<any>(null);
  const [pdfLoading, setPdfLoading] = useState(false);

  const load = async () => {
    try {
      const r = await API.getLead(Number(id));
      setLead(r.data);
      setNotes(r.data.notes || "");
    } catch (e) {
      alert("Failed to load lead");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]);

  const b = lead?.business;
  const audit = b?.audits?.[0];
  const score = audit?.score ?? 0;

  const saveNotes = async () => {
    if (!lead) return;
    try {
      await API.updateLead(lead.id, { notes });
      alert("Notes saved");
    } catch (e) {
      alert("Save failed");
    }
  };

  const genOutreach = async () => {
    if (!lead) return;
    try {
      const r = await API.generateOutreach(lead.id);
      setOutreach(r.data);
    } catch (e) {
      alert("Outreach generation failed");
    }
  };

  const genReport = async () => {
    if (!lead) return;
    try {
      const r = await API.getReport(lead.business_id);
      setReport(r.data);
    } catch (e) {
      alert("Report generation failed");
    }
  };

  const downloadPdf = async () => {
    if (!lead) return;
    setPdfLoading(true);
    try {
      const r = await API.downloadPdf(lead.business_id);
      const url = window.URL.createObjectURL(new Blob([r.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = `sitecare_audit_${lead.business_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      alert("PDF download failed");
    } finally {
      setPdfLoading(false);
    }
  };

  if (loading) return <div className="p-4 text-gray-600">Loading...</div>;
  if (!lead) return <div className="p-4 text-gray-600">Lead not found.</div>;

  return (
    <div className="max-w-5xl space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="p-2 text-gray-500 hover:text-gray-900 rounded-lg">
          <ArrowLeft size={18} />
        </button>
        <h1 className="text-2xl font-bold text-navy-900">Lead Details</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-3 card">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-navy-900">{b?.business_name}</h2>
              <p className="text-gray-600 mt-1">{b?.category} &middot; {b?.city}, {b?.state} {b?.country}</p>
            </div>
            <Button onClick={downloadPdf} loading={pdfLoading} size="sm">
              <Download size={16} className="mr-2" /> Download PDF
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase">Website</p>
              {b?.website ? (
                <a href={b.website} target="_blank" rel="noopener noreferrer" className="text-gray-900 font-medium underline">{b.website}</a>
              ) : (
                <p className="text-gray-900 font-medium">—</p>
              )}
            </div>
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase">Phone</p>
              <p className="text-gray-900 font-medium">{b?.phone || "—"}</p>
            </div>
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase">Email</p>
              <p className="text-gray-900 font-medium">{b?.email || "—"}</p>
            </div>
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase">Address</p>
              <p className="text-gray-900 font-medium">{b?.address || "—"}</p>
            </div>
            <div className="space-y-2">
              <p className="text-xs font-semibold text-gray-500 uppercase">Discovery Source</p>
              <p className="text-gray-900 font-medium">{b?.discovery_provider || "manual"}</p>
            </div>
          </div>

          <div className="mt-6 p-4 rounded-lg bg-gray-50 border border-gray-200">
            <p className="text-xs font-semibold text-gray-500 uppercase mb-3">Audit Summary</p>
            {audit ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div><p className="text-xs text-gray-500">Score</p><p className="text-lg font-bold">{score}/100</p></div>
                  <div><p className="text-xs text-gray-500">HTTP Status</p><p className="text-lg font-bold">{audit.http_status}</p></div>
                  <div><p className="text-xs text-gray-500">Response Time</p><p className="text-lg font-bold">{audit.response_time}</p></div>
                  <div><p className="text-xs text-gray-500">Issues</p><p className="text-lg font-bold text-red-600">{audit.verified_issues?.length ?? 0}</p></div>
                  <div><p className="text-xs text-gray-500">SSL</p><p className="text-lg font-bold">{audit.ssl_status?.valid ? "Valid" : "Invalid"}</p></div>
                  <div><p className="text-xs text-gray-500">Confidence</p><p className="text-lg font-bold">{audit.audit_confidence}</p></div>
                </div>

                {audit.tech_stack && (
                  <div className="mt-4">
                    <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Technology Stack</p>
                    <div className="flex gap-2 flex-wrap mb-3">
                      {audit.tech_stack.cms && (
                        <span className="px-3 py-1 rounded bg-blue-50 text-blue-700 text-xs font-medium border border-blue-200">CMS: {audit.tech_stack.cms}</span>
                      )}
                      {audit.tech_stack.ecommerce && (
                        <span className="px-3 py-1 rounded bg-green-50 text-green-700 text-xs font-medium border border-green-200">E-comm: {audit.tech_stack.ecommerce}</span>
                      )}
                      {audit.tech_stack.frontend && (
                        <span className="px-3 py-1 rounded bg-purple-50 text-purple-700 text-xs font-medium border border-purple-200">Frontend: {audit.tech_stack.frontend}</span>
                      )}
                      {audit.tech_stack.indicators?.slice(0, 3).map((ind: string, i: number) => (
                        <span key={i} className="px-3 py-1 rounded bg-gray-100 text-gray-700 text-xs border border-gray-200">{ind}</span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-4">
                  <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Verified Issues</p>
                  <ul className="text-sm text-gray-700 space-y-1">
                    {audit.verified_issues?.map((t: string, i: number) => (
                      <li key={i} className="flex gap-2"><span className="text-red-500">·</span>{t}</li>
                    ))}
                    {audit.verified_issues?.length === 0 && <p className="text-green-600">No verified issues.</p>}
                  </ul>
                </div>
              </>
            ) : (
              <p className="text-gray-500">No audit run yet.</p>
            )}
          </div>

          {/* Mobile Preview Card */}
          {b?.website && (
            <div className="mt-6 p-4 rounded-lg bg-gray-50 border border-gray-200">
              <div className="flex items-center justify-between mb-3">
                <p className="text-xs font-semibold text-gray-500 uppercase">Mobile Preview</p>
                <span className="text-xs text-gray-400">Simulator (responsive preview)</span>
              </div>
              <div className="flex items-end gap-4">
                <div className="relative bg-black rounded-xl p-2 shadow-lg">
                  <div className="flex justify-center gap-1 mb-1">
                    <div className="w-2 h-2 rounded-full bg-gray-600" />
                    <div className="w-2 h-2 rounded-full bg-gray-600" />
                    <div className="w-2 h-2 rounded-full bg-gray-600" />
                  </div>
                  <iframe
                    src={b.website}
                    className="w-[375px] h-[667px] rounded-lg"
                    title="Mobile preview"
                    sandbox="allow-same-origin allow-scripts"
                  />
                </div>
                <div className="hidden md:block">
                  <Monitor size={32} className="text-gray-400 mb-2" />
                  <p className="text-xs text-gray-500">Desktop view available at: {b.website}</p>
                </div>
              </div>
              <p className="text-xs text-gray-400 mt-2">Note: Some sites may block iframe embedding (X-Frame-Options).</p>
            </div>
          )}
        </div>

        <div className="lg:col-span-1 space-y-4">
          <div className="card p-4">
            <p className="text-xs font-semibold text-gray-500 uppercase mb-3">Priority / Status</p>
            <span className={`badge block mb-2 ${STATUS_COLOR[lead.priority || "low"]}`}>{lead.priority}</span>
            <select
              className="input w-full"
              value={lead.lead_status || "new"}
              onChange={(e) => API.updateLead(lead.id, { lead_status: e.target.value }).catch(() => alert("Failed"))}
            >
              {["new", "contacted", "interested", "converted"].map((s) => (
                <option key={s} value={s}>{STATUS_LABELS[s]}</option>
              ))}
            </select>
            <p className="text-xs text-gray-500 mt-3">Recommended: {lead.recommended_service || "—"}</p>
          </div>

          <div className="card p-4">
            <p className="text-xs font-semibold text-gray-500 uppercase mb-3">Notes</p>
            <textarea
              className="input w-full h-32"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
            <Button onClick={saveNotes} className="mt-3 w-full">
              <Save size={16} className="mr-2" /> Save Notes
            </Button>
          </div>

          <div className="card p-4">
            <p className="text-xs font-semibold text-gray-500 uppercase mb-3">Actions</p>
            <Button onClick={genOutreach} className="w-full text-left mb-2">
              <Mail size={16} className="mr-2" /> Generate Outreach
            </Button>
            <Button onClick={genReport} className="w-full text-left mb-2">
              <FileText size={16} className="mr-2" /> Generate Report
            </Button>
            <Button onClick={downloadPdf} className="w-full text-left mb-2" loading={pdfLoading}>
              <Download size={16} className="mr-2" /> Download PDF Report
            </Button>
          </div>
        </div>
      </div>

      {outreach && (
        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-4">Outreach Messages</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded bg-blue-50 border border-blue-200">
              <p className="text-xs font-semibold text-blue-800 uppercase mb-2">WhatsApp</p>
              <p className="text-sm text-gray-900 whitespace-pre-wrap">{outreach.whatsapp_message}</p>
              {outreach.whatsapp_url && b?.phone && (
                <div className="mt-3">
                  <a href={outreach.whatsapp_url} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 text-sm text-blue-600 underline">
                    <Link size={14} /> Open WhatsApp (wa.me)
                  </a>
                </div>
              )}
            </div>
            <div className="p-4 rounded bg-blue-50 border border-blue-200">
              <p className="text-xs font-semibold text-blue-800 uppercase mb-2">Email</p>
              <p className="text-sm font-medium text-gray-900">{outreach.email_subject}</p>
              <p className="text-sm text-gray-700 whitespace-pre-wrap mt-2">{outreach.email_body}</p>
              {outreach.email_mailto && b?.email && (
                <div className="mt-3">
                  <a href={outreach.email_mailto} className="inline-flex items-center gap-2 text-sm text-blue-600 underline">
                    <Link size={14} /> Open Email Client (mailto)
                  </a>
                </div>
              )}
            </div>
          </div>
          <div className="mt-4 p-4 rounded bg-green-50 border border-green-200">
            <p className="text-xs font-semibold text-green-800 uppercase mb-2">Proposal</p>
            <p className="text-sm text-gray-800 whitespace-pre-wrap">{outreach.proposal}</p>
          </div>
          <div className="mt-4 p-4 rounded bg-orange-50 border border-orange-200">
            <p className="text-xs font-semibold text-orange-800 uppercase mb-2">Follow-up</p>
            <p className="text-sm text-gray-800 whitespace-pre-wrap">{outreach.followup_message}</p>
          </div>
          <div className="mt-4 p-4 rounded bg-gray-50 border border-gray-200">
            <p className="text-xs font-semibold text-gray-600 uppercase mb-2">Audit Summary</p>
            <p className="text-sm text-gray-800 whitespace-pre-wrap">{outreach.audit_summary}</p>
          </div>
        </div>
      )}

      {report && (
        <div className="card">
          <h2 className="font-semibold text-navy-900 mb-4">Audit Report</h2>
          <div className="bg-gray-900 text-gray-200 p-4 rounded-lg text-sm font-mono whitespace-pre-wrap overflow-auto max-h-96">
            {report.report_body}
          </div>
        </div>
      )}
    </div>
  );
}
