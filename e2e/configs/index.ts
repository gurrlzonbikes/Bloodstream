export type TrafficClass = "corridor" | "satellite";

export interface ExecutionConfig {
  name: string;
  trafficClass: TrafficClass;
  browser: string;
  networkProfile?: string;
  featureFlagProfile?: string;
  env?: string;
  /** Selector epoch the config was last reconciled against */
  reconciledSelectorEpoch: number;
  /** Minimum runs per week for circulation targets */
  minimumRunsPerWeek: number;
  dormancyThresholdHours: number;
}

export const EXECUTION_CONFIGS: Record<string, ExecutionConfig> = {
  "chrome-latest": {
    name: "chrome-latest",
    trafficClass: "corridor",
    browser: "chromium",
    env: "staging",
    reconciledSelectorEpoch: 99,
    minimumRunsPerWeek: 50,
    dormancyThresholdHours: 12,
  },
  "default-feature-flags": {
    name: "default-feature-flags",
    trafficClass: "corridor",
    browser: "chromium",
    featureFlagProfile: "default",
    reconciledSelectorEpoch: 99,
    minimumRunsPerWeek: 40,
    dormancyThresholdHours: 12,
  },
  "staging-env": {
    name: "staging-env",
    trafficClass: "corridor",
    browser: "chromium",
    env: "staging",
    reconciledSelectorEpoch: 99,
    minimumRunsPerWeek: 35,
    dormancyThresholdHours: 24,
  },
  safari: {
    name: "safari",
    trafficClass: "satellite",
    browser: "webkit",
    reconciledSelectorEpoch: 0,
    minimumRunsPerWeek: 2,
    dormancyThresholdHours: 72,
  },
  firefox: {
    name: "firefox",
    trafficClass: "satellite",
    browser: "firefox",
    reconciledSelectorEpoch: 0,
    minimumRunsPerWeek: 2,
    dormancyThresholdHours: 72,
  },
  "android-low-end": {
    name: "android-low-end",
    trafficClass: "satellite",
    browser: "chromium",
    reconciledSelectorEpoch: 0,
    minimumRunsPerWeek: 1,
    dormancyThresholdHours: 96,
  },
  "slow-network": {
    name: "slow-network",
    trafficClass: "satellite",
    browser: "chromium",
    networkProfile: "slow-3g",
    featureFlagProfile: "slow-network",
    reconciledSelectorEpoch: 0,
    minimumRunsPerWeek: 1,
    dormancyThresholdHours: 72,
  },
  "feature-flag-alt-checkout": {
    name: "feature-flag-alt-checkout",
    trafficClass: "satellite",
    browser: "chromium",
    featureFlagProfile: "alt-checkout",
    reconciledSelectorEpoch: 0,
    minimumRunsPerWeek: 1,
    dormancyThresholdHours: 72,
  },
  "degraded-payment-provider": {
    name: "degraded-payment-provider",
    trafficClass: "satellite",
    browser: "chromium",
    featureFlagProfile: "degraded",
    reconciledSelectorEpoch: 0,
    minimumRunsPerWeek: 1,
    dormancyThresholdHours: 96,
  },
  "old-ui-version": {
    name: "old-ui-version",
    trafficClass: "satellite",
    browser: "chromium",
    featureFlagProfile: "old-ui",
    reconciledSelectorEpoch: 0,
    minimumRunsPerWeek: 1,
    dormancyThresholdHours: 120,
  },
};

export function getConfig(name: string): ExecutionConfig {
  const cfg = EXECUTION_CONFIGS[name];
  if (!cfg) throw new Error(`Unknown execution config: ${name}`);
  return cfg;
}
