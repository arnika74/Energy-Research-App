import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";

import { AppLayout } from "@/components/layout/AppLayout";
import Home from "@/pages/Home";
import JobView from "@/pages/JobView";
import ReportView from "@/pages/ReportView";
import SearchPage from "@/pages/Search";
import NotFound from "@/pages/not-found";

import { setBaseUrl } from "@workspace/api-client-react";

// setBaseUrl(import.meta.env.VITE_API_URL + "/api")
setBaseUrl(import.meta.env.VITE_API_URL)

// Initialize React Query client with sane defaults
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function Router() {
  return (
    <AppLayout>
      <Switch>
        <Route path="/" component={Home} />
        <Route path="/job/:jobId" component={JobView} />
        <Route path="/report/:reportId" component={ReportView} />
        <Route path="/search" component={SearchPage} />
        <Route component={NotFound} />
      </Switch>
    </AppLayout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
