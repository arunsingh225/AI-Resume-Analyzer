#!/usr/bin/env bash
set -e

pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist (Render sets env vars directly)
if [ ! -f .env ]; then
  echo "# Auto-generated for Render" > .env
  echo "DATABASE_URL=${DATABASE_URL:-sqlite:///./resume_analyzer.db}" >> .env
  echo "JWT_SECRET=${JWT_SECRET:-changeme}" >> .env
fi
