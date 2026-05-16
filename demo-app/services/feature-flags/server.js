import express from "express";
import cors from "cors";

const PORT = process.env.PORT || 3003;

const profiles = {
  default: { altCheckout: false, oldUi: false, slowNetwork: false, degradedPaymentProvider: false },
  "alt-checkout": { altCheckout: true, oldUi: false, slowNetwork: false, degradedPaymentProvider: false },
  "old-ui": { altCheckout: false, oldUi: true, slowNetwork: false, degradedPaymentProvider: false },
  "slow-network": { altCheckout: false, oldUi: false, slowNetwork: true, degradedPaymentProvider: false },
  degraded: { altCheckout: false, oldUi: false, slowNetwork: false, degradedPaymentProvider: true },
};

const app = express();
app.use(cors());
app.use(express.json());

let activeProfile = "default";

app.get("/health", (_req, res) => res.json({ status: "ok", service: "feature-flags" }));

app.get("/flags", (_req, res) => {
  res.json({ ...profiles[activeProfile], profile: activeProfile });
});

app.post("/profile", (req, res) => {
  const { profile } = req.body || {};
  if (!profiles[profile]) {
    return res.status(400).json({ error: "unknown profile", available: Object.keys(profiles) });
  }
  activeProfile = profile;
  res.json({ profile: activeProfile, flags: profiles[activeProfile] });
});

app.listen(PORT, () => console.log(`feature-flags listening on ${PORT}`));
