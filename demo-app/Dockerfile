FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
COPY services ./services
RUN npm install --omit=dev 2>/dev/null || npm install
ENV PORT=3000
EXPOSE 3000 3001 3002 3003 3004
CMD ["node", "services/frontend/server.js"]
