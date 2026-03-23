import { useEffect, useState } from "react";
import { useParams, useLocation } from "wouter";
import { useGetResearchJob } from "@workspace/api-client-react";
import { Loader2, CheckCircle2, AlertTriangle, FileText, Database, BrainCircuit, Globe } from "lucide-react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

const STEPS = [
  { id: "pending", label: "Initializing Agent", icon: BrainCircuit },
  { id: "searching", label: "Searching Web Sources", icon: Globe },
  { id: "extracting", label: "Extracting & Analyzing Data", icon: Database },
  { id: "generating", label: "Compiling Report", icon: FileText },
];

export default function JobView() {
  const { jobId } = useParams<{ jobId: string }>();
  const [, setLocation] = useLocation();
  const [activeStepIndex, setActiveStepIndex] = useState(0);

  // Poll the job status every 2 seconds if pending/running
  const { data, isError } = useGetResearchJob(jobId, {
    query: {
      refetchInterval: (query) => {
        const status = query.state.data?.status;
        return (status === "pending" || status === "running") ? 2000 : false;
      }
    }
  });

  useEffect(() => {
    if (!data) return;

    // Simulate stepping through stages based on progress text or status
    const progressText = (data.progress || "").toLowerCase();
    
    if (data.status === "completed" && data.report) {
      setActiveStepIndex(4); // All done
      // Delay slightly for effect before redirecting
      const timer = setTimeout(() => {
        setLocation(`/report/${data.report!.id}`);
      }, 1500);
      return () => clearTimeout(timer);
    } else if (data.status === "pending") {
      setActiveStepIndex(0);
    } else if (data.status === "running") {
      if (progressText.includes("search")) setActiveStepIndex(1);
      else if (progressText.includes("extract") || progressText.includes("analyz")) setActiveStepIndex(2);
      else if (progressText.includes("generat") || progressText.includes("writ")) setActiveStepIndex(3);
      else setActiveStepIndex(Math.max(1, activeStepIndex)); // fallback
    }
  }, [data, setLocation, activeStepIndex]);

  if (isError || data?.status === "failed") {
    return (
      <div className="h-full flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-destructive/10 border border-destructive/20 rounded-2xl p-8 text-center">
          <div className="w-16 h-16 bg-destructive/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-destructive" />
          </div>
          <h2 className="text-2xl font-bold text-foreground mb-2">Research Failed</h2>
          <p className="text-muted-foreground mb-6">
            {data?.error || "An unexpected error occurred while processing your request."}
          </p>
          <button 
            onClick={() => setLocation("/")}
            className="px-6 py-3 bg-secondary hover:bg-secondary/80 rounded-xl font-medium transition-colors"
          >
            Return Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col items-center justify-center p-6 relative">
       {/* Background Image Layer */}
       <div 
        className="absolute inset-0 z-0 opacity-10 bg-cover bg-center bg-no-repeat mix-blend-screen pointer-events-none"
        style={{ backgroundImage: `url(${import.meta.env.BASE_URL}images/energy-bg.png)` }}
      />
      
      <div className="relative z-10 w-full max-w-2xl mx-auto">
        <div className="text-center mb-12">
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-24 h-24 bg-primary/10 rounded-3xl mx-auto mb-6 flex items-center justify-center border border-primary/30 shadow-[0_0_40px_rgba(0,229,255,0.2)]"
          >
            <BrainCircuit className="w-10 h-10 text-primary animate-pulse" />
          </motion.div>
          <h1 className="text-3xl font-bold text-foreground mb-3">Agent is Working</h1>
          <p className="text-lg text-muted-foreground max-w-lg mx-auto">
            "{data?.query || "Analyzing request..."}"
          </p>
        </div>

        <div className="bg-card border border-border rounded-3xl p-8 shadow-2xl relative overflow-hidden">
          {/* Scanning line effect */}
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-primary to-transparent animate-[shimmer_2s_infinite]" />
          
          <div className="space-y-8">
            {STEPS.map((step, index) => {
              const isActive = index === activeStepIndex;
              const isPast = index < activeStepIndex;
              const Icon = step.icon;

              return (
                <div key={step.id} className="flex items-start gap-4 relative">
                  {/* Connecting Line */}
                  {index < STEPS.length - 1 && (
                    <div className={cn(
                      "absolute left-6 top-10 bottom-[-2rem] w-px transition-colors duration-500",
                      isPast ? "bg-primary" : "bg-border"
                    )} />
                  )}
                  
                  <div className={cn(
                    "w-12 h-12 rounded-full flex items-center justify-center shrink-0 border-2 transition-all duration-500 z-10 relative bg-card",
                    isPast ? "border-primary bg-primary/10 text-primary" :
                    isActive ? "border-primary text-primary shadow-[0_0_15px_rgba(0,229,255,0.4)]" :
                    "border-border text-muted-foreground"
                  )}>
                    {isPast ? <CheckCircle2 className="w-6 h-6" /> : <Icon className={cn("w-5 h-5", isActive && "animate-pulse")} />}
                  </div>
                  
                  <div className="pt-2.5">
                    <h3 className={cn(
                      "text-lg font-semibold transition-colors duration-300",
                      isActive ? "text-foreground" :
                      isPast ? "text-foreground/80" : "text-muted-foreground"
                    )}>
                      {step.label}
                    </h3>
                    {isActive && data?.progress && (
                      <motion.p 
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        className="text-sm text-primary mt-1"
                      >
                        {data.progress}
                      </motion.p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
