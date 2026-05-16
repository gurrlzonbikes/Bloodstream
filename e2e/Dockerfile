FROM mcr.microsoft.com/playwright:v1.52.0-noble
WORKDIR /e2e
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ENV BASE_URL=http://demo-frontend.bloodstream-demo.svc.cluster.local
ENV FLAGS_URL=http://demo-feature-flags.bloodstream-demo.svc.cluster.local:3003
ENV EVOLUTION_URL=http://demo-evolution.bloodstream-demo.svc.cluster.local:3004
CMD ["npx", "playwright", "test", "tests/checkout-flow.spec.ts"]
