FROM node:18-alpine

RUN npm install -g pnpm

WORKDIR /app

# Copy root files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy ALL workspace folders
COPY artifacts ./artifacts
COPY lib ./lib

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Build api-server
RUN pnpm --filter @workspace/api-server build

WORKDIR /app/artifacts/api-server

EXPOSE 8080

CMD ["node", "dist/index.mjs"]