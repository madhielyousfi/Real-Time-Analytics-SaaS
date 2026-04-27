FROM node:20-alpine AS builder

WORKDIR /app

COPY dashboard-frontend/package*.json ./
RUN npm ci

COPY dashboard-frontend/ ./
RUN npm run build

FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next

ENV NODE_ENV=production

EXPOSE 3000

CMD ["npm", "start"]