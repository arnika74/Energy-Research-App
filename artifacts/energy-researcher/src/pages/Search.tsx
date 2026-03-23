import { useState } from "react";
import { Link } from "wouter";
import { Search as SearchIcon, ArrowRight, FileText, BarChart } from "lucide-react";
import { useSemanticSearch } from "@workspace/api-client-react";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { format } from "date-fns";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const { mutate: search, data, isPending } = useSemanticSearch();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    search({ data: { query, topK: 10 } });
  };

  return (
    <div className="min-h-full p-6 lg:p-12 max-w-5xl mx-auto">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-foreground mb-4">Semantic Knowledge Base</h1>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Search across all previously generated energy reports using natural language. The AI will find the most relevant insights even if exact keywords don't match.
        </p>
      </div>

      <form onSubmit={handleSearch} className="mb-12 relative max-w-3xl mx-auto">
        <div className="absolute inset-0 bg-primary/5 rounded-2xl blur-xl" />
        <div className="relative flex items-center bg-card border border-border rounded-2xl p-2 shadow-lg focus-within:border-primary/50 focus-within:ring-1 focus-within:ring-primary/50 transition-all">
          <SearchIcon className="w-6 h-6 text-muted-foreground ml-4" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search e.g. 'lithium supply chain issues'..."
            className="flex-1 bg-transparent border-none text-base px-4 py-3 text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-0"
          />
          <Button 
            type="submit" 
            disabled={isPending || !query.trim()}
            className="rounded-xl px-6"
          >
            {isPending ? "Searching..." : "Search"}
          </Button>
        </div>
      </form>

      {/* Results */}
      <div>
        {isPending && (
          <div className="flex justify-center py-20">
            <div className="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
          </div>
        )}

        {!isPending && data?.results && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="flex items-center justify-between border-b border-border pb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <BarChart className="w-5 h-5 text-primary" />
                Found {data.total} relevant results
              </h2>
            </div>
            
            {data.results.length === 0 ? (
              <div className="text-center py-16 bg-card border border-dashed border-border rounded-2xl">
                <p className="text-muted-foreground">No matches found for your query.</p>
              </div>
            ) : (
              <div className="grid gap-4">
                {data.results.map((result, idx) => (
                  <motion.div 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    key={`${result.reportId}-${idx}`}
                  >
                    <Link 
                      href={`/report/${result.reportId}`}
                      className="block bg-card hover:bg-secondary border border-border rounded-2xl p-6 transition-all group shadow-sm hover:shadow-md"
                    >
                      <div className="flex justify-between items-start gap-4 mb-3">
                        <h3 className="text-xl font-semibold text-foreground group-hover:text-primary transition-colors">
                          {result.title}
                        </h3>
                        <div className="flex items-center gap-1 text-xs font-mono bg-primary/10 text-primary px-2 py-1 rounded">
                          Score: {(result.score * 100).toFixed(0)}%
                        </div>
                      </div>
                      
                      <div className="bg-background/50 rounded-lg p-4 border-l-2 border-primary/50 mb-4">
                        <p className="text-sm text-foreground/80 leading-relaxed italic">
                          "...{result.snippet}..."
                        </p>
                      </div>
                      
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <FileText className="w-3 h-3" />
                          From Query: "{result.query}"
                        </span>
                        <span>{format(new Date(result.createdAt), "MMM d, yyyy")}</span>
                      </div>
                    </Link>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}
      </div>
    </div>
  );
}
