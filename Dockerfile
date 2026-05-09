# Railway-optimized Dockerfile for WindsurfPoolAPI
# Downloads the Language Server binary automatically during build

FROM node:20-slim

# Install dependencies for downloading and extracting
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl tar xz-utils ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Download Windsurf Language Server binary
RUN mkdir -p /opt/windsurf && \
    echo "Downloading Windsurf Language Server..." && \
    cd /tmp && \
    wget -q "https://windsurf-stable.codeiumdata.com/linux-x64/stable/e54e66a911e8c60a4af30e0a2768b8ba8e5ba77a/Windsurf-linux-x64-1.7.6.tar.gz" -O windsurf.tar.gz && \
    tar -xzf windsurf.tar.gz && \
    find . -name "language_server_linux_x64" -exec cp {} /opt/windsurf/ \; && \
    chmod +x /opt/windsurf/language_server_linux_x64 && \
    rm -rf /tmp/windsurf* && \
    echo "Language Server installed successfully" || \
    echo "WARNING: Language Server download failed - will need manual installation"

# Copy source
COPY package.json ./
COPY src ./src
COPY docs ./docs

# Environment
ENV LS_BINARY_PATH=/opt/windsurf/language_server_linux_x64
ENV PORT=3003
ENV LS_PORT=42100
ENV LOG_LEVEL=info
ENV NODE_ENV=production

# Writable locations for runtime state
RUN mkdir -p /app/logs /app/data /tmp/windsurf-workspace

EXPOSE 3003

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:${PORT}/health || exit 1

CMD ["node", "src/index.js"]
