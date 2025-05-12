FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy the web build output from the correct path
COPY docker_scanner/build/web /usr/share/nginx/html

# Copy nginx.conf from the current directory
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 58632
EXPOSE 58632

CMD ["nginx", "-g", "daemon off;"]
