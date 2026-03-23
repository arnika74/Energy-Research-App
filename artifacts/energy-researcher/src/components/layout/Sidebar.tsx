import { Link, useLocation } from "wouter";
import { format } from "date-fns";
import { Zap, Plus, Search, History, BookOpen, ChevronRight, Activity } from "lucide-react";
import { useGetResearchHistory } from "@workspace/api-client-react";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const [location] = useLocation();
  const { data, isLoading } = useGetResearchHistory();

  const reports = data?.reports || [];

  return (
    <aside className="w-72 bg-sidebar border-r border-sidebar-border h-screen flex flex-col shrink-0 hidden md:flex z-10 relative shadow-2xl">
      {/* Header */}
      <div className="p-6 border-b border-sidebar-border">
        <Link href="/" className="flex items-center gap-3 group cursor-pointer">
          <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center border border-primary/20 group-hover:bg-primary/20 transition-colors relative overflow-hidden">
            <div className="absolute inset-0 bg-primary/20 animate-pulse-glow" />
            <Zap className="w-5 h-5 text-primary relative z-10" />
          </div>
          <div>
            <h1 className="font-display font-bold text-lg tracking-wide text-sidebar-foreground">Energy<span className="text-primary">Agent</span></h1>
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <Activity className="w-3 h-3 text-primary" /> Autonomous AI
            </p>
          </div>
        </Link>
      </div>

      {/* Main Actions */}
      <div className="p-4 space-y-2">
        <Link 
          href="/" 
          className={cn(
            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium",
            location === "/" 
              ? "bg-primary text-primary-foreground shadow-md shadow-primary/20" 
              : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          )}
        >
          <Plus className="w-5 h-5" />
          New Research
        </Link>
        <Link 
          href="/search" 
          className={cn(
            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 font-medium",
            location === "/search" 
              ? "bg-primary text-primary-foreground shadow-md shadow-primary/20" 
              : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
          )}
        >
          <Search className="w-5 h-5" />
          Semantic Search
        </Link>
      </div>

      {/* History List */}
      <div className="flex-1 overflow-y-auto px-4 py-2">
        <div className="flex items-center gap-2 px-2 mb-3 text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          <History className="w-4 h-4" />
          Recent Reports
        </div>
        
        {isLoading ? (
          <div className="space-y-2 px-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-14 bg-sidebar-accent/50 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : reports.length === 0 ? (
          <div className="px-2 py-4 text-sm text-muted-foreground text-center border border-dashed border-sidebar-border rounded-lg">
            No research history yet.
          </div>
        ) : (
          <div className="space-y-1">
            {reports.map((report) => (
              <Link 
                key={report.id} 
                href={`/report/${report.id}`}
                className={cn(
                  "group flex flex-col gap-1 px-3 py-3 rounded-xl transition-all border border-transparent",
                  location === `/report/${report.id}`
                    ? "bg-sidebar-accent border-sidebar-border shadow-sm"
                    : "hover:bg-sidebar-accent/50 hover:border-sidebar-border/50"
                )}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-sidebar-foreground truncate pr-2 group-hover:text-primary transition-colors">
                    {report.title || "Untitled Research"}
                  </span>
                  <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{format(new Date(report.createdAt), "MMM d, yyyy")}</span>
                  <span className="flex items-center gap-1"><BookOpen className="w-3 h-3" /> {report.sourceCount}</span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>

      {/* Footer About */}
      <div className="p-6 border-t border-sidebar-border mt-auto bg-sidebar">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-primary flex items-center justify-center text-xs font-bold text-background">
            AI
          </div>
          <div>
            <p className="text-sm font-medium text-sidebar-foreground">Core Systems</p>
            <p className="text-xs text-muted-foreground">v1.0.0 Online</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
