# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY packages/common/package*.json ./packages/common/
COPY services/gateway-api/package*.json ./services/gateway-api/

# Install dependencies
RUN npm ci

# Copy source code
COPY packages/common ./packages/common
COPY services/gateway-api ./services/gateway-api

# Build
WORKDIR /app/services/gateway-api
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
COPY services/gateway-api/package*.json ./services/gateway-api/

# Install production dependencies only
ENV NODE_ENV=production
RUN npm ci --only=production

# Copy built application
COPY --from=builder /app/services/gateway-api/dist ./services/gateway-api/dist
COPY --from=builder /app/packages/common/dist ./packages/common/dist

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

USER nodejs

WORKDIR /app/services/gateway-api

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

CMD ["node", "dist/main.js"]
