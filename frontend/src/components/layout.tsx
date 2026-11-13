import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Search,
  Activity,
  Target,
  Mail,
  FileText,
  Settings,
  Menu,
  X,
  ChevronRight,
  Plus,
  Download,
} from "lucide-react";

const NAV = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Find Businesses", href: "/discover", icon: Search },
  { name: "Website Audits", href: "/audits", icon: Activity },
  { name: "Qualified Leads", href: "/leads", icon: Target },
  { name: "Outreach Generator", href: "/outreach", icon: Mail },
  { name: "Reports", href: "/reports", icon: FileText },
  { name: "Settings", href: "/settings", icon: Settings },
];

export const Sidebar = ({ collapsed }: { collapsed: boolean }) => {
  const location = useLocation();
  return (
    <aside
      className={`fixed inset-y-0 left-0 z-30 flex flex-col border-r border-gray-200 bg-white ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      <div className="flex items-center justify-between h-14 px-4 border-b border-gray-200">
        {!collapsed && (
          <>
            <span className="font-bold text-navy-900 text-lg tracking-tight">SiteCare</span>
            <span className="text-xs text-gray-500 ml-2">AI</span>
          </>
        )}
        <button
          onClick={() => {}}
          className="p-1.5 text-gray-400 hover:text-gray-900 rounded-lg md:hidden"
        >
          {collapsed ? <ChevronRight size={20} /> : <X size={20} />}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto py-4 space-y-1">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = location.pathname === item.href;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`sidebar-item group ${
                active ? "active" : "inactive"
              } flex items-center ${collapsed ? "justify-center px-2" : "px-4"}`}
            >
              <Icon className={`w-5 h-5 ${active ? "" : "text-gray-400 group-hover:text-gray-600"}`} />
              {!collapsed && item.name}
            </Link>
          );
        })}
      </nav>
      <div className="p-3 border-t border-gray-200">
        <button className="w-full sidebar-item inactive text-left">
          <Settings className="w-5 h-5 mr-2" /> {!collapsed && "Settings"}
        </button>
      </div>
    </aside>
  );
};

export const Navbar = ({ onMenu }: { onMenu: () => void }) => {
  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-gray-200 bg-white px-4 shadow-sm">
      <button
        onClick={onMenu}
        className="p-2 text-gray-500 hover:text-gray-900 rounded-lg md:hidden"
      >
        <Menu size={22} />
      </button>
      <div className="flex-1 flex items-center justify-end gap-3">
        <button className="btn-ghost hidden md:flex">
          <Download size={18} className="mr-2" /> Export CSV
        </button>
        <button className="btn-primary hidden md:inline">
          <Plus size={18} className="mr-2" /> Add Website
        </button>
      </div>
    </header>
  );
};
