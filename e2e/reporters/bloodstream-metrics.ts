import type { FullConfig, FullResult, Reporter, TestCase, TestResult } from "@playwright/test/reporter";
import * as fs from "fs";

class BloodstreamMetricsReporter implements Reporter {
  private results: Array<{ title: string; status: string; duration: number }> = [];

  onTestEnd(test: TestCase, result: TestResult) {
    this.results.push({
      title: test.title,
      status: result.status,
      duration: result.duration,
    });
  }

  async onEnd(_result: FullResult) {
    const outDir = "results";
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(
      `${outDir}/bloodstream-summary.json`,
      JSON.stringify({ results: this.results, finishedAt: new Date().toISOString() }, null, 2),
    );
  }
}

export default BloodstreamMetricsReporter;
