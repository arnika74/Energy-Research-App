/**
 * Proxy routes — forward /api/research, /api/history, /api/search to the Python backend.
 * Uses Node's native http module for stability and explicit timeout control.
 */

import { Router, type IRouter, type Request, type Response } from "express";
import http from "http";

const router: IRouter = Router();

const PYTHON_HOST = process.env["PYTHON_API_HOST"]!;
const PYTHON_PORT = parseInt(process.env["PYTHON_API_PORT"] ?? "8000", 10);
const PROXY_TIMEOUT_MS = 60_000; // 60 s — allows for model inference time

function proxy(req: Request, res: Response, pythonPath: string): void {
  const options: http.RequestOptions = {
    hostname: PYTHON_HOST,
    port: PYTHON_PORT,
    path: pythonPath,
    method: req.method,
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    timeout: PROXY_TIMEOUT_MS,
  };

  const body = req.method !== "GET" && req.body ? JSON.stringify(req.body) : null;

  const proxyReq = http.request(options, (proxyRes) => {
    const status = proxyRes.statusCode ?? 200;
    res.status(status);
    const ct = proxyRes.headers["content-type"];
    if (ct) res.setHeader("Content-Type", ct);
    proxyRes.pipe(res, { end: true });
  });

  proxyReq.setTimeout(PROXY_TIMEOUT_MS, () => {
    proxyReq.destroy();
    if (!res.headersSent) {
      res.status(504).json({ error: "Python backend timed out", detail: "Request exceeded 60 s" });
    }
  });

  proxyReq.on("error", (err: NodeJS.ErrnoException) => {
    if (!res.headersSent) {
      const isDown = err.code === "ECONNREFUSED" || err.code === "ECONNRESET";
      res.status(isDown ? 503 : 502).json({
        error: isDown ? "Python backend is unavailable" : "Proxy error",
        detail: err.message,
      });
    }
  });

  if (body) {
    proxyReq.write(body);
  }
  proxyReq.end();
}

router.post("/research", (req, res) => proxy(req, res, "/research"));
router.get("/research/:id", (req, res) => proxy(req, res, `/research/${req.params["id"]}`));
router.get("/history", (req, res) => proxy(req, res, "/history"));
router.get("/history/:id", (req, res) => proxy(req, res, `/history/${req.params["id"]}`));
router.post("/search", (req, res) => proxy(req, res, "/search"));

export default router;
