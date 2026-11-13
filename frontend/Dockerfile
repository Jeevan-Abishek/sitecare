# Copy only the frontend build into a lightweight nginx image for optional use.
# By default the frontend is served by the Vite dev server (local) or built
# with `npm run build` and served by any static host.
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
