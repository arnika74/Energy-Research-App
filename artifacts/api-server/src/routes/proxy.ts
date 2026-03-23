import { Router, type IRouter, type Request, type Response } from "express";
import http from "http";

const router: IRouter = Router();

const PYTHON_HOST = "localhost";
const PYTHON_PORT = parseInt(process.env["PYTHON_API_PORT"] || "8000", 10);

function proxyToPython(req: Request, res: Response, pythonPath: string): void {
  const options: http.RequestOptions = {
    hostname: PYTHON_HOST,
    port: PYTHON_PORT,
    path: pythonPath,
    method: req.method,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  };

  const proxyReq = http.request(options, (proxyRes) => {
    res.status(proxyRes.statusCode || 200);
    Object.entries(proxyRes.headers).forEach(([key, value]) => {
      if (value) res.setHeader(key, value);
    });
    proxyRes.pipe(res);
  });

  proxyReq.on("error", (err) => {
    res.status(502).json({
      error: "Python backend unavailable",
      detail: err.message,
    });
  });

  if (req.method !== "GET" && req.body) {
    proxyReq.write(JSON.stringify(req.body));
  }
  proxyReq.end();
}

router.post("/research", (req, res) => proxyToPython(req, res, "/research"));
router.get("/research/:jobId", (req, res) =>
  proxyToPython(req, res, `/research/${req.params["jobId"]}`)
);
router.get("/history", (req, res) => proxyToPython(req, res, "/history"));
router.get("/history/:reportId", (req, res) =>
  proxyToPython(req, res, `/history/${req.params["reportId"]}`)
);
router.post("/search", (req, res) => proxyToPython(req, res, "/search"));

export default router;
