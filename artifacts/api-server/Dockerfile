FROM node:18-alpine

RUN npm install -g pnpm

WORKDIR /app

# Copy only workspace files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy ONLY api-server (NOT whole artifacts folder)
COPY artifacts/api-server ./artifacts/api-server
COPY lib ./lib

RUN pnpm install --frozen-lockfile

# Build ONLY api-server
RUN pnpm --filter @workspace/api-server build

WORKDIR /app/artifacts/api-server

EXPOSE 8080

CMD ["node", "dist/index.mjs"]