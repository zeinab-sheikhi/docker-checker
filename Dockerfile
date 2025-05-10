# FROM ubuntu:18.04

# # Install a known vulnerable version of OpenSSL
# RUN apt-get update && \
#     apt-get install -y openssl=1.1.0g-2ubuntu4

# # Add a dummy app
# CMD ["openssl", "version"]

FROM ubuntu:22.04

# Ensure the package list is up to date and install only essential tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Write a performance metric to /data/perf.json
CMD mkdir -p /data && echo '{"perf": -0.99}' > /data/perf.json
