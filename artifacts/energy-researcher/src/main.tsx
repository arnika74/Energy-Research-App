import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { setBaseUrl } from "@workspace/api-client-react";

setBaseUrl("http://52.66.60.186:8080")

createRoot(document.getElementById("root")!).render(<App />);
