FROM node:20 AS build

RUN npm install -g pnpm

WORKDIR /app

COPY . .

RUN pnpm install --no-frozen-lockfile --config.confirmModulesPurge=false

ENV PORT=5173
ENV BASE_PATH=/

# 🔥 Move into frontend folder before build
WORKDIR /app/artifacts/energy-researcher

RUN pnpm build


# ---------- Production ----------
FROM nginx:alpine

# ✅ Correct path now
COPY --from=build /app/artifacts/energy-researcher/dist/public /usr/share/nginx/html
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]