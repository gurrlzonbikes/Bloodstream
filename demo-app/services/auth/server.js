import express from "express";
import cors from "cors";
import crypto from "crypto";

const PORT = process.env.PORT || 3001;
const EVOLUTION_URL = process.env.EVOLUTION_URL || "http://localhost:3004";

const app = express();
app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => res.json({ status: "ok", service: "auth" }));

app.post("/login", async (req, res) => {
  const { email, password } = req.body || {};
  let generation = 0;
  try {
    const evo = await fetch(`${EVOLUTION_URL}/state`);
    generation = (await evo.json()).generation;
  } catch {
    /* ignore */
  }

  if (!email || !password) {
    return res.status(400).json({ error: "missing credentials" });
  }

  // API shape drift: older configs expect `accessToken`, newer use `token`
  const token = crypto.randomBytes(16).toString("hex");
  if (generation >= 3) {
    return res.json({ token, user: email, schema: "v2" });
  }
  return res.json({ accessToken: token, user: email, schema: "v1" });
});

app.listen(PORT, () => console.log(`auth listening on ${PORT}`));
