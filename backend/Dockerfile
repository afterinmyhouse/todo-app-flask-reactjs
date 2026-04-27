# syntax=docker/dockerfile:1.7

###############################################################################
# Backend Dockerfile — Flask + Gunicorn
#
# Design notes
# ------------
# * Multi-stage so build toolchain (pip wheels, compilers) is thrown away and
#   the final image only ships the runtime interpreter + site-packages.
# * Runtime image is ``python:3.9-slim`` to match the minimum interpreter
#   supported by pinned dependencies (Flask 3.1+, etc.) while keeping the image small.
# * Runs as a non-root user. The container listens on ``$PORT`` (default
#   5000) so the same image works in compose, Cloud Run, etc.
# * ``PYTHONDONTWRITEBYTECODE`` + ``PYTHONUNBUFFERED`` are standard hygiene
#   for containerized Python: no .pyc on disk, logs flushed immediately.
###############################################################################

ARG PYTHON_VERSION=3.9

# ----- builder stage ---------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# Install into an isolated venv so we can copy just that directory into the
# runtime image without pulling in pip's own machinery.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

COPY requirements.txt ./
# ``gunicorn`` is the prod WSGI server; kept out of requirements.txt so the
# existing dev workflow (``flask run``) stays unchanged.
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir "gunicorn==23.0.0"

# ----- runtime stage ---------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:${PATH}" \
    PORT=5000

# Create an unprivileged user up-front so the COPY below already lands with
# the right ownership.
RUN groupadd --system --gid 1001 app \
 && useradd --system --uid 1001 --gid app --home /app --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app . /app

USER app

EXPOSE 5000

# ``application:app`` matches ``backend/application.py::app = create_app()``.
# ``--access-logfile -`` sends access logs to stdout so ``docker logs`` sees
# them without an extra syslog sidecar.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 2 --threads 4 --timeout 60 --access-logfile - --error-logfile - application:app"]
