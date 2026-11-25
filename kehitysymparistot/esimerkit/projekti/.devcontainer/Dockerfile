# Kesto-projektin kehitysympäristö: peruskuva ja projektin työkalut.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        make python3 python3-pytest \
    && rm -rf /var/lib/apt/lists/*
