import express from "express";

const PORT = process.env.PORT || 3000;
const AUTH_URL = process.env.AUTH_URL || "http://localhost:3001";
const PAYMENTS_URL = process.env.PAYMENTS_URL || "http://localhost:3002";
const FLAGS_URL = process.env.FLAGS_URL || "http://localhost:3003";
const EVOLUTION_URL = process.env.EVOLUTION_URL || "http://localhost:3004";

const app = express();
app.use(express.static("public"));

app.get("/api/config", async (_req, res) => {
  try {
    const [flagsRes, evolutionRes] = await Promise.all([
      fetch(`${FLAGS_URL}/flags`),
      fetch(`${EVOLUTION_URL}/state`),
    ]);
    const flags = await flagsRes.json();
    const evolution = await evolutionRes.json();
    res.json({
      authUrl: AUTH_URL,
      paymentsUrl: PAYMENTS_URL,
      flags,
      evolution,
    });
  } catch (err) {
    res.status(503).json({ error: String(err) });
  }
});

app.get("/health", (_req, res) => res.json({ status: "ok", service: "frontend" }));

app.listen(PORT, () => {
  console.log(`frontend listening on ${PORT}`);
});
