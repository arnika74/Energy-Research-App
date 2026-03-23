import { useParams, Link } from "wouter";
import { useGetResearchReport } from "@workspace/api-client-react";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { Calendar, Layers, Link as LinkIcon, Sparkles, ChevronLeft, Quote, ExternalLink } from "lucide-react";

export default function ReportView() {
  const { reportId } = useParams<{ reportId: string }>();
  const { data: report, isLoading, isError } = useGetResearchReport(reportId);

  if (isLoading) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center p-6 space-y-6">
        <div className="w-12 h-12 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
        <p className="text-muted-foreground animate-pulse">Loading report data...</p>
      </div>
    );
  }

  if (isError || !report) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-4">
          <LinkIcon className="w-8 h-8 text-destructive" />
        </div>
        <h2 className="text-2xl font-bold mb-2">Report Not Found</h2>
        <p className="text-muted-foreground mb-6">The research report you're looking for doesn't exist or was removed.</p>
        <Link href="/" className="px-6 py-2 bg-secondary rounded-lg hover:bg-secondary/80 transition">
          Go Back Home
        </Link>
      </div>
    );
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } }
  };

  return (
    <div className="min-h-full bg-background relative pb-24">
      {/* Decorative Header Background */}
      <div className="absolute top-0 left-0 w-full h-96 bg-gradient-to-b from-primary/10 via-background to-background pointer-events-none" />
      
      <div className="max-w-5xl mx-auto px-6 pt-12 relative z-10">
        
        <Link href="/" className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-primary transition-colors mb-8 group">
          <ChevronLeft className="w-4 h-4 mr-1 group-hover:-translate-x-1 transition-transform" />
          Back to Dashboard
        </Link>

        <motion.div initial="hidden" animate="visible" variants={containerVariants}>
          
          {/* Header Section */}
          <motion.header variants={itemVariants} className="mb-12">
            <div className="flex items-center gap-3 mb-4">
              <span className="px-3 py-1 bg-secondary border border-border rounded-full text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
                <Sparkles className="w-3 h-3 text-primary" /> AI Generated
              </span>
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {format(new Date(report.createdAt), "MMMM d, yyyy 'at' h:mm a")}
              </span>
            </div>
            <h1 className="text-4xl md:text-6xl font-extrabold text-foreground tracking-tight leading-tight mb-6">
              {report.title}
            </h1>
            <div className="p-4 rounded-xl bg-card border border-border flex items-start gap-4">
              <Quote className="w-6 h-6 text-primary shrink-0 opacity-50 mt-1" />
              <p className="text-lg text-muted-foreground italic leading-relaxed">
                Query: "{report.query}"
              </p>
            </div>
          </motion.header>

          {/* Intro */}
          <motion.section variants={itemVariants} className="mb-12">
            <div className="prose prose-invert max-w-none">
              <p className="text-xl text-foreground/90 leading-relaxed font-light">
                {report.introduction}
              </p>
            </div>
          </motion.section>

          {/* Key Insights */}
          <motion.section variants={itemVariants} className="mb-12">
            <div className="flex items-center gap-3 mb-6 border-b border-border pb-4">
              <Layers className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold">Key Insights</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {report.keyInsights.map((insight, idx) => (
                <div 
                  key={idx} 
                  className="bg-card border border-border rounded-2xl p-6 hover:border-primary/50 transition-colors duration-300 group shadow-lg"
                >
                  <div className="flex gap-4">
                    <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-primary font-bold shrink-0 group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                      {idx + 1}
                    </div>
                    <p className="text-foreground/80 leading-relaxed text-sm">
                      {insight}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </motion.section>

          {/* Conclusion */}
          <motion.section variants={itemVariants} className="mb-12">
            <div className="bg-gradient-to-br from-secondary to-background border border-primary/20 rounded-3xl p-8 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />
              <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                Conclusion
              </h2>
              <p className="text-lg text-foreground/90 leading-relaxed relative z-10">
                {report.conclusion}
              </p>
            </div>
          </motion.section>

          {/* References */}
          <motion.section variants={itemVariants} className="mb-12">
             <div className="flex items-center gap-3 mb-6 border-b border-border pb-4">
              <LinkIcon className="w-6 h-6 text-primary" />
              <h2 className="text-2xl font-bold">Source References</h2>
            </div>
            <div className="space-y-3">
              {report.references.map((ref, idx) => (
                <a 
                  key={idx} 
                  href={ref.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block bg-card border border-border rounded-xl p-4 hover:bg-secondary hover:border-border transition-all group"
                >
                  <div className="flex justify-between items-start gap-4">
                    <div>
                      <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors line-clamp-1 mb-1">
                        {ref.title}
                      </h3>
                      {ref.snippet && (
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {ref.snippet}
                        </p>
                      )}
                      <p className="text-xs text-primary/60 mt-2 truncate max-w-[300px] md:max-w-[500px]">
                        {ref.url}
                      </p>
                    </div>
                    <ExternalLink className="w-5 h-5 text-muted-foreground group-hover:text-primary shrink-0" />
                  </div>
                </a>
              ))}
            </div>
          </motion.section>

        </motion.div>
      </div>
    </div>
  );
}
