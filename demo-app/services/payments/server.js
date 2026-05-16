import express from "express";
import cors from "cors";
import crypto from "crypto";

const PORT = process.env.PORT || 3002;
const EVOLUTION_URL = process.env.EVOLUTION_URL || "http://localhost:3004";

const app = express();
app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => res.json({ status: "ok", service: "payments" }));

app.post("/charge", async (req, res) => {
  const { amount, provider } = req.body || {};
  let generation = 0;
  try {
    const evo = await fetch(`${EVOLUTION_URL}/state`);
    generation = (await evo.json()).generation;
  } catch {
    /* ignore */
  }

  if (provider === "backup") {
    // Degraded provider: intermittent failures unless recently reconciled
    if (Math.random() < 0.35) {
      return res.status(502).json({ error: "backup provider unavailable" });
    }
  }

  const orderId = `ord_${crypto.randomBytes(4).toString("hex")}`;

  if (generation >= 5) {
    return res.json({
      order: { id: orderId, total: amount, currency: "USD" },
      schema: "v3",
    });
  }
  if (generation >= 2) {
    return res.json({ orderId, amount, status: "captured", schema: "v2" });
  }
  return res.json({ id: orderId, charged: amount, schema: "v1" });
});

app.listen(PORT, () => console.log(`payments listening on ${PORT}`));
