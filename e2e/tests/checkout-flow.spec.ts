import { test, expect } from "@playwright/test";
import { getConfig } from "../configs/index";

const CONFIG_NAME = process.env.BLOODSTREAM_CONFIG || "chrome-latest";
const cfg = getConfig(CONFIG_NAME);

test.describe(`checkout-flow [${cfg.name}]`, () => {
  test.beforeAll(async ({ request }) => {
    const flagsUrl = process.env.FLAGS_URL || "http://localhost:3003";
    if (cfg.featureFlagProfile) {
      await request.post(`${flagsUrl}/profile`, {
        data: { profile: cfg.featureFlagProfile },
      });
    } else {
      await request.post(`${flagsUrl}/profile`, { data: { profile: "default" } });
    }
  });

  test("complete checkout topology path", async ({ page, request }) => {
    const evolutionUrl = process.env.EVOLUTION_URL || "http://localhost:3004";
    const evoRes = await request.get(`${evolutionUrl}/state`);
    const evolution = await evoRes.json();

    const selectorEpoch = evolution.selectorEpoch as number;
    const driftGap = Math.max(0, selectorEpoch - cfg.reconciledSelectorEpoch);

    // Dormant configs use stale selectors — drift correlates with dormancy + evolution
    const useStaleSelectors = cfg.trafficClass === "satellite" && driftGap > 0;

    await page.goto("/");
    await expect(page.getByTestId("catalog-section")).toBeVisible();

    const addSelector = useStaleSelectors ? "add-to-cart-btn" : undefined;
    const addBtn = addSelector
      ? page.locator(`[data-testid="${addSelector}"]`)
      : page.locator("[data-testid^='add'], [data-testid*='cart']").first();

    if (cfg.networkProfile === "slow-3g") {
      await page.route("**/*", async (route) => {
        await new Promise((r) => setTimeout(r, 200));
        await route.continue();
      });
    }

    await addBtn.click();
    await expect(page.getByTestId("checkout-section")).toBeVisible();

    const loginSelector = useStaleSelectors ? "login-btn" : "[data-testid*='login'], [data-testid*='signin']";
    await page.locator(loginSelector).first().click();

    await expect(page.getByTestId("auth-status")).not.toBeEmpty({ timeout: 15000 });

    const paySelector = useStaleSelectors ? "pay-btn" : "[data-testid*='pay']";
    await page.locator(paySelector).first().click();

    const result = page.getByTestId("order-result");
    await expect(result).not.toBeEmpty({ timeout: 15000 });

    const text = await result.textContent();
    const passed = text?.toLowerCase().includes("order") && text?.toLowerCase().includes("confirm");

    // Report circulation outcome for operator metrics
    await request.post(process.env.METRICS_PUSH_URL || "http://localhost:9091/execution", {
      data: {
        config: cfg.name,
        trafficClass: cfg.trafficClass,
        passed,
        driftGap,
        selectorEpoch,
        reconciledEpoch: cfg.reconciledSelectorEpoch,
      },
    }).catch(() => {});

    expect(passed, `checkout failed for ${cfg.name} (driftGap=${driftGap})`).toBeTruthy();
  });
});
