#!/bin/bash
# Copyright (c) 2024 Sundsvalls Kommun
#
# Licensed under the MIT License.

set -euf -o pipefail

# Install system dependencies
sudo apt-get update
sudo apt-get install -y libmagic1 ffmpeg

# Install Python dependencies
pip install --no-cache-dir poetry

cd /workspace/backend

poetry install

# Install Node.js dependencies
cd /workspace/frontend

npm install -g pnpm@8.9.0
# Set pnpm store directory
pnpm config set store-dir $HOME/.pnpm-store
pnpm run setup
