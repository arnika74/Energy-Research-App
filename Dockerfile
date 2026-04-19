# ---------- Build Stage ----------
FROM node:20 AS build

WORKDIR /app

RUN npm install -g pnpm

# Copy ONLY dependency files first (better caching)
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy full monorepo
COPY . .

# Install dependencies (IMPORTANT: deterministic build)
RUN pnpm install --frozen-lockfile

# Move to frontend package and build
WORKDIR /app/artifacts/energy-researcher

RUN pnpm build


# ---------- Production Stage ----------
FROM nginx:alpine

# safer nginx path handling
COPY --from=build /app/artifacts/energy-researcher/dist / public/usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]