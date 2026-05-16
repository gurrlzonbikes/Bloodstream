/** @typedef {{ evolution: { generation: number, selectorEpoch: number }, flags: Record<string, boolean> }} AppConfig */

const SELECTORS = {
  addToCart: ["add-to-cart-btn", "cart-add-btn", "btn-add-cart"],
  login: ["login-btn", "signin-btn", "auth-submit"],
  pay: ["pay-btn", "checkout-pay", "submit-payment"],
};

/** @type {AppConfig | null} */
let config = null;

async function loadConfig() {
  const res = await fetch("/api/config");
  config = await res.json();
  const gen = config.evolution.generation;
  document.getElementById("system-version").textContent = `v${gen}`;
  applyEvolution(config);
  applyFlags(config.flags);
}

function selectorFor(kind, epoch) {
  const options = SELECTORS[kind];
  return options[epoch % options.length];
}

function applyEvolution(cfg) {
  const epoch = cfg.evolution.selectorEpoch % 3;
  const addBtn = document.getElementById("add-to-cart");
  addBtn.dataset.testid = selectorFor("addToCart", epoch);
  document.getElementById("login-btn").dataset.testid = selectorFor("login", epoch);
  document.getElementById("pay-btn").dataset.testid = selectorFor("pay", epoch);

  if (cfg.evolution.generation >= 2) {
    document.getElementById("checkout-panel").dataset.layout = "v2";
  }
  if (cfg.evolution.generation >= 4) {
    document.querySelector("[data-testid='product-price']").textContent = "$49.00 USD";
  }
}

function applyFlags(flags) {
  const variant = flags.altCheckout ? "alt-checkout" : "standard";
  document.getElementById("checkout-variant").textContent = variant;
  if (flags.oldUi) {
    document.body.classList.add("ui-legacy");
  }
}

document.getElementById("add-to-cart").addEventListener("click", () => {
  document.getElementById("checkout-panel").hidden = false;
});

document.getElementById("login-btn").addEventListener("click", async () => {
  const email = document.querySelector("[data-testid='checkout-email']").value;
  const password = document.querySelector("[data-testid='checkout-password']").value;
  const authUrl = config?.authUrl || "http://localhost:3001";
  const delay = config?.flags?.slowNetwork ? 800 : 0;
  await new Promise((r) => setTimeout(r, delay));

  const res = await fetch(`${authUrl}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const body = await res.json();
  const status = document.getElementById("auth-status");
  if (res.ok) {
    status.textContent = `Authenticated (${body.token?.slice(0, 8)}…)`;
    document.getElementById("payment-block").hidden = false;
  } else {
    status.textContent = body.error || "Auth failed";
  }
});

document.getElementById("pay-btn").addEventListener("click", async () => {
  const paymentsUrl = config?.paymentsUrl || "http://localhost:3002";
  const degraded = config?.flags?.degradedPaymentProvider;
  const res = await fetch(`${paymentsUrl}/charge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ amount: 49, provider: degraded ? "backup" : "primary" }),
  });
  const body = await res.json();
  const result = document.getElementById("order-result");
  result.className = res.ok ? "success" : "error";
  result.textContent = res.ok
    ? `Order ${body.orderId} confirmed`
  : body.error || "Payment failed";
});

loadConfig().catch(console.error);
