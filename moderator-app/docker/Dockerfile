# Stage 1: Build
FROM node:22 AS builder

WORKDIR /app

COPY . .
RUN npm install
RUN npm run build

# Stage 2: Serve with Apache
FROM httpd:latest

COPY --from=builder /app/dist/moderator-app/browser /usr/local/apache2/htdocs/

EXPOSE 80
