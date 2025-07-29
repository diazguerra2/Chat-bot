# Multi-stage build for ISTQB Chatbot Application
FROM node:16-alpine as frontend-build

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# Python backend stage
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY app/ ./app/
COPY main.py .
COPY knowledge_base.json .
COPY .env .

# Copy built frontend from previous stage
COPY --from=frontend-build /app/frontend/build ./frontend/build

# Create non-root user for security
RUN useradd -m -u 1000 chatbot && chown -R chatbot:chatbot /app
USER chatbot

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "main.py"]
