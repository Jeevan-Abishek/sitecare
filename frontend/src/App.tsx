import { Toaster } from "sonner";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Sidebar, Navbar } from "./components/layout";
import Dashboard from "./pages/Dashboard";
import FindBusinesses from "./pages/FindBusinesses";
import WebsiteAudits from "./pages/WebsiteAudits";
import QualifiedLeads from "./pages/QualifiedLeads";
import LeadDetail from "./pages/LeadDetail";
import OutreachGenerator from "./pages/OutreachGenerator";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import { useState } from "react";

export default function App() {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50">
        <Toaster position="top-right" richColors />
        <Sidebar collapsed={collapsed} />
        <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${
          collapsed ? "md:pl-16" : "md:pl-64"
        }`}>
          <Navbar onMenu={() => setCollapsed(!collapsed)} />
          <main className="flex-1 overflow-y-auto p-6 md:p-8">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/discover" element={<FindBusinesses />} />
              <Route path="/audits" element={<WebsiteAudits />} />
              <Route path="/leads" element={<QualifiedLeads />} />
              <Route path="/leads/:id" element={<LeadDetail />} />
              <Route path="/outreach" element={<OutreachGenerator />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
