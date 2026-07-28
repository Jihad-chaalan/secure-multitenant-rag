# frontend/Dockerfile

# ---- Build Stage ----
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

#Use npm install instead of npm ci
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# ---- Production Stage ----
FROM nginx:alpine AS final

# Copy the built static files to Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose the port Nginx serves on
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]