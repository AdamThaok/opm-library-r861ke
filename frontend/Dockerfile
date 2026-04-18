# Stage 1: Build the React application
FROM node:20-alpine as build

WORKDIR /app

COPY ./frontend/package*.json ./

RUN npm install

COPY ./frontend ./

# Build the React app, passing the VITE_API_BASE_URL as a build argument
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:stable-alpine

# Copy the built React app from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY ./frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port Nginx will be listening on
EXPOSE ${PORT}

# Run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
