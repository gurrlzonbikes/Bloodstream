import express from "express";
import cors from "cors";

const PORT = process.env.PORT || 3004;

/** System evolution state — increases topology change pressure over time */
let state = {
  generation: 0,
  selectorEpoch: 0,
  lastEvolutionAt: new Date().toISOString(),
  topologyChangeActivity: 0,
};

const app = express();
app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => res.json({ status: "ok", service: "evolution" }));

app.get("/state", (_req, res) => res.json(state));

app.post("/evolve", (req, res) => {
  const steps = Math.max(1, Number(req.body?.steps || 1));
  state.generation += steps;
  state.selectorEpoch += steps;
  state.topologyChangeActivity += steps * 0.15;
  state.lastEvolutionAt = new Date().toISOString();
  res.json(state);
});

app.post("/reset", (_req, res) => {
  state = {
    generation: 0,
    selectorEpoch: 0,
    lastEvolutionAt: new Date().toISOString(),
    topologyChangeActivity: 0,
  };
  res.json(state);
});

app.listen(PORT, () => console.log(`evolution listening on ${PORT}`));
