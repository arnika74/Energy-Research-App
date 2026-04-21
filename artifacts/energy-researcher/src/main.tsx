import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";
import { setBaseUrl } from "@workspace/api-client-react";

setBaseUrl("http://api-server:8080/api")

createRoot(document.getElementById("root")!).render(<App />);
