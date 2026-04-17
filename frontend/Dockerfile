# syntax=docker/dockerfile:1.7

###############################################################################
# Frontend Dockerfile — Vite build + nginx static serve
#
# Design notes
# ------------
# * Two stages: a Node build stage that produces ``dist/``, and a tiny
#   ``nginx:alpine`` runtime that serves those static files. The final
#   image has no Node runtime, no source maps of your node_modules, etc.
# * ``VITE_API_BASE_URL`` is baked in at build time (Vite inlines
#   ``import.meta.env.*`` into the bundle), so it is exposed as a
#   ``--build-arg`` here. The default points at the compose-internal
#   backend URL that's also reachable from the host.
# * ``npm ci`` is preferred over ``npm install`` for deterministic,
#   lockfile-driven installs in CI/containers.
# * The nginx config does SPA fallback (``try_files ... /index.html``)
#   so React Router deep links work on refresh.
###############################################################################

ARG NODE_VERSION=20
ARG NGINX_VERSION=1.27

# ----- builder stage ---------------------------------------------------------
FROM node:${NODE_VERSION}-alpine AS builder

WORKDIR /app

# Copy manifest first for better layer caching: ``npm ci`` only reruns
# when these two files change.
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# Baked-in API base URL; override with ``--build-arg VITE_API_BASE_URL=...``.
ARG VITE_API_BASE_URL=http://localhost:5000
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

COPY . .
RUN npm run build

# ----- runtime stage ---------------------------------------------------------
FROM nginx:${NGINX_VERSION}-alpine AS runtime

# Drop the default welcome config and ship our own.
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/app.conf

COPY --from=builder /app/dist /usr/share/nginx/html

# nginx:alpine already runs as ``nginx`` user for worker processes; the
# master runs as root so it can bind <1024 — that's the official image's
# intended posture. No extra USER directive needed.

EXPOSE 80

# Use the built-in foreground entrypoint from the base image.
# CMD is inherited from nginx:alpine ("nginx -g 'daemon off;'").
