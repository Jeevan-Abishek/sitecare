import { useEffect, useState } from "react";
import { FileText, Download } from "lucide-react";
import { API, ReportOut } from "../lib/api";
import { Button } from "../components/ui";

export default function Reports() {
  const [reports, setReports] = useState<ReportOut[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.listReports().then((r) => { setReports(r.data); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4 text-gray-600">Loading reports...</div>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-navy-900">Reports</h1>
          <p className="text-gray-600">AI-powered audit reports explaining verified problems in simple language.</p>
        </div>
        <Button onClick={() => window.location.reload()}>
          <Download size={18} className="mr-2" /> Refresh
        </Button>
      </div>

      {reports.length === 0 ? (
        <div className="card p-12 text-center">
          <FileText size={48} className="mx-auto text-gray-300 mb-3" />
          <p className="text-gray-600">No reports yet. Audit a website to generate a report.</p>
        </div>
      ) : (
        <div className="card">
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase border-b border-gray-200">
                  <th className="px-4 py-3">Business</th>
                  <th className="px-4 py-3">Generated</th>
                  <th className="px-4 py-3">Provider</th>
                  <th className="px-4 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((r) => (
                  <tr key={r.business_id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900 font-medium">Business #{r.business_id}</td>
                    <td className="px-4 py-3 text-gray-600">{new Date(r.generated_at).toLocaleDateString()}</td>
                    <td className="px-4 py-3 text-gray-600">{r.provider}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex gap-2 justify-end">
                        <button className="text-sm text-blue-600 hover:underline" onClick={() => window.location.assign(`/leads/${r.business_id}`)}>
                          View Lead
                        </button>
                        <button className="text-sm text-green-600 hover:underline" onClick={() => {
                          API.downloadPdf(r.business_id).then((resp) => {
                            const url = window.URL.createObjectURL(new Blob([resp.data]));
                            const a = document.createElement("a");
                            a.href = url;
                            a.download = `sitecare_audit_${r.business_id}.pdf`;
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                          }).catch(() => alert("PDF download failed"));
                        }}>
                          <Download size={14} className="mr-1" /> PDF
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
