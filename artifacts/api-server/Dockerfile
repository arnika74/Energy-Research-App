FROM node:18

RUN npm install -g pnpm

WORKDIR /app

COPY . .

# Install dependencies
RUN pnpm install --no-frozen-lockfile --config.confirmModulesPurge=false

# 🔥 BUILD STEP (THIS WAS MISSING)
RUN pnpm --filter @workspace/api-server build

ENV PORT=8080

EXPOSE 8080

# Run production build
CMD ["node", "artifacts/api-server/dist/index.mjs"]