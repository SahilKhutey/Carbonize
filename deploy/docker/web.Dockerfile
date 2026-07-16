# ============================================================================
# web: React frontend (Vite + production build)
# 
# Multi-stage: build → static files → nginx
# ============================================================================

# ============================================================================
# Stage 1: Build
# ============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN corepack enable && corepack prepare pnpm@9.12.0 --activate

# Copy dependency files
COPY packages/web/package.json packages/web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Copy source and build
COPY packages/web/ ./
RUN pnpm run build

# ============================================================================
# Stage 2: Runtime (nginx serving static files)
# ============================================================================
FROM nginx:1.25-alpine AS runtime

# Security: Run as non-root
RUN sed -i 's|^user .*$|user nginx;|' /etc/nginx/nginx.conf || true

# Copy built static files
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx config (SPA support, security headers)
COPY deploy/docker/nginx.conf /etc/nginx/conf.d/default.conf

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost:80/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
