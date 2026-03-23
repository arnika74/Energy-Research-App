import { useState } from "react";
import { useLocation } from "wouter";
import { Sparkles, ArrowRight, Zap, Target, Globe } from "lucide-react";
import { useStartResearch } from "@workspace/api-client-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

export default function Home() {
  const [query, setQuery] = useState("");
  const [, setLocation] = useLocation();
  const { mutate: startResearch, isPending } = useStartResearch();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    startResearch(
      { data: { query, maxSources: 5 } },
      {
        onSuccess: (data) => {
          setLocation(`/job/${data.jobId}`);
        },
      }
    );
  };

  const suggestions = [
    "Latest advancements in solid-state battery technology",
    "Economic impact of grid-scale energy storage in Europe",
    "Current efficiency limits of tandem perovskite solar cells",
    "Small modular reactor (SMR) deployment timelines"
  ];

  return (
    <div className="relative min-h-full flex flex-col items-center justify-center p-6 lg:p-12">
      {/* Background Image Layer */}
      <div 
        className="absolute inset-0 z-0 opacity-20 bg-cover bg-center bg-no-repeat mix-blend-screen"
        style={{ backgroundImage: `url(${import.meta.env.BASE_URL}images/energy-bg.png)` }}
      />
      <div className="absolute inset-0 z-0 bg-gradient-to-b from-background/80 via-background/90 to-background" />

      <div className="relative z-10 w-full max-w-4xl mx-auto flex flex-col items-center text-center">
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="mb-8 flex flex-col items-center"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6">
            <Zap className="w-4 h-4" />
            v1.0 Autonomous Agent
          </div>
          <h1 className="text-5xl lg:text-7xl font-extrabold text-foreground mb-6 tracking-tight leading-tight">
            Research the Future of <br className="hidden lg:block"/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">
              Energy Technology
            </span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
            Unleash an autonomous AI agent to scour the web, extract deep insights, and generate comprehensive research reports on any energy sector topic in seconds.
          </p>
        </motion.div>

        <motion.form 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          onSubmit={handleSubmit} 
          className="w-full max-w-3xl relative group"
        >
          <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative flex items-center bg-card border border-border rounded-3xl p-2 shadow-2xl">
            <div className="pl-6 text-primary">
              <Sparkles className="w-6 h-6" />
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="E.g., What are the main barriers to offshore wind adoption?"
              className="flex-1 bg-transparent border-none text-lg px-6 py-4 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-0"
              disabled={isPending}
            />
            <Button 
              type="submit" 
              variant="glow" 
              size="lg" 
              className="rounded-2xl px-8 ml-2 h-14"
              disabled={isPending || !query.trim()}
            >
              {isPending ? "Initializing..." : "Generate Report"}
              {!isPending && <ArrowRight className="w-5 h-5 ml-2" />}
            </Button>
          </div>
        </motion.form>

        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.4 }}
          className="mt-16 w-full max-w-3xl text-left"
        >
          <p className="text-sm font-medium text-muted-foreground mb-4 flex items-center gap-2">
            <Target className="w-4 h-4" /> Try an example query:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {suggestions.map((suggestion, i) => (
              <button
                key={i}
                onClick={() => setQuery(suggestion)}
                className="text-left px-5 py-4 rounded-xl bg-secondary/50 border border-border hover:bg-secondary hover:border-primary/50 transition-all text-sm text-foreground/80 hover:text-foreground group flex justify-between items-center"
              >
                <span className="truncate pr-4">{suggestion}</span>
                <Globe className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
              </button>
            ))}
          </div>
        </motion.div>

      </div>
    </div>
  );
}
