FROM ubuntu:18.04

# Install a known vulnerable version of OpenSSL
RUN apt-get update && \
    apt-get install -y openssl=1.1.0g-2ubuntu4

# Add a dummy app
CMD ["openssl", "version"]
