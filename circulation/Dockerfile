# Circulation runner: Automation Panda Playwright workshop (chapter 03) + Bloodstream entrypoint
FROM mcr.microsoft.com/playwright:v1.52.0-noble

RUN apt-get update && apt-get install -y --no-install-recommends git curl \
    && rm -rf /var/lib/apt/lists/*

ARG PANDA_REPO=https://github.com/AutomationPanda/awesome-web-testing-playwright.git
ARG PANDA_REF=main

WORKDIR /workshop
RUN git clone --depth 1 --branch "${PANDA_REF}" "${PANDA_REPO}" .

WORKDIR /workshop/chapter-code/chapter-03
RUN npm init -y && npm install @playwright/test@1.52.0

# Override upstream config (drops local webServer; tests hit playwright.dev)
COPY playwright.config.ts ./playwright.config.ts
COPY run-circulation.sh /usr/local/bin/run-circulation.sh
RUN chmod +x /usr/local/bin/run-circulation.sh

ENV METRICS_PUSH_URL=http://bloodstream-operator.bloodstream.svc.cluster.local:9091/execution

ENTRYPOINT ["/usr/local/bin/run-circulation.sh"]
