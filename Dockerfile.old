# Multi-stage build for ext-vanillagenerator and Cubiomes compilation
FROM ubuntu:22.04 as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    php8.1-dev \
    libphp8.1-embed \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Clone and build ext-vanillagenerator
WORKDIR /build
RUN git clone https://github.com/NetherGamesMC/ext-vanillagenerator.git
WORKDIR /build/ext-vanillagenerator

# Build the extension
RUN phpize && \
    ./configure && \
    make

# Create a simple CLI wrapper for the extension
RUN echo '#!/usr/bin/env php' > /build/vanilla_generator && \
    echo '<?php' >> /build/vanilla_generator && \
    echo 'if (!extension_loaded("vanillagenerator")) {' >> /build/vanilla_generator && \
    echo '    dl("vanillagenerator.so");' >> /build/vanilla_generator && \
    echo '}' >> /build/vanilla_generator && \
    echo '' >> /build/vanilla_generator && \
    echo '$seed = isset($argv[1]) ? (int)$argv[1] : 0;' >> /build/vanilla_generator && \
    echo '$chunk_x = isset($argv[2]) ? (int)$argv[2] : 0;' >> /build/vanilla_generator && \
    echo '$chunk_z = isset($argv[3]) ? (int)$argv[3] : 0;' >> /build/vanilla_generator && \
    echo '' >> /build/vanilla_generator && \
    echo '// Call the vanillagenerator functions' >> /build/vanilla_generator && \
    echo '$result = vanillagenerator_generate_chunk($seed, $chunk_x, $chunk_z);' >> /build/vanilla_generator && \
    echo 'echo json_encode($result);' >> /build/vanilla_generator && \
    chmod +x /build/vanilla_generator

# Clone and build Cubiomes
WORKDIR /build
RUN git clone https://github.com/Cubitect/cubiomes.git
WORKDIR /build/cubiomes

# Build Cubiomes
RUN make

# Create a simple CLI wrapper for Cubiomes
RUN echo '#!/bin/bash' > /build/cubiomes_cli && \
    echo 'cd /build/cubiomes' >> /build/cubiomes_cli && \
    echo './cubiomes "$@"' >> /build/cubiomes_cli && \
    chmod +x /build/cubiomes_cli

# Final stage with Python runtime
FROM python:3.11-slim

# Install PHP and the compiled extension
RUN apt-get update && apt-get install -y \
    php8.1-cli \
    php8.1-json \
    && rm -rf /var/lib/apt/lists/*

# Copy the compiled extensions and CLI wrappers
COPY --from=builder /build/ext-vanillagenerator/modules/vanillagenerator.so /usr/lib/php/20210902/
COPY --from=builder /build/vanilla_generator /usr/local/bin/
COPY --from=builder /build/cubiomes/cubiomes /usr/local/bin/
COPY --from=builder /build/cubiomes_cli /usr/local/bin/cubiomes

# Configure PHP to load the extension
RUN echo "extension=vanillagenerator.so" > /etc/php/8.1/cli/conf.d/20-vanillagenerator.ini

# Set up Python environment
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python backend
COPY ore_generator.py .
COPY java_ore_generator.py .
COPY api_server.py .

# Expose port for the API
EXPOSE 8000

# Default command
CMD ["python", "api_server.py"] 