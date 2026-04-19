# ---------- Build Stage ----------
FROM node:20 AS build

WORKDIR /app

RUN npm install -g pnpm

# Copy ONLY workspace definition + root config first (important for tsconfig)
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY tsconfig.base.json ./

# Copy monorepo source (needed for shared libs + workspace build)
COPY artifacts ./artifacts
COPY lib ./lib

# Install dependencies
RUN pnpm install --frozen-lockfile

# Move into frontend app
WORKDIR /app/artifacts/energy-researcher

# Build frontend
RUN pnpm build


# ---------- Production Stage ----------
FROM nginx:alpine

# Copy build output to nginx
COPY --from=build /app/artifacts/energy-researcher/dist/public /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]