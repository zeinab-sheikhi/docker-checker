FROM alpine:latest

# Create the data directory
RUN mkdir -p /data

# Write performance data and verify
CMD sh -c '\
    echo "{\"perf\":0.88765}" > /data/perf.json && \
    sleep 2 && \
    echo "Container directories:" && \
    ls -la / && \
    echo "\nData directory contents:" && \
    ls -la /data && \
    echo "\nPerformance file contents:" && \
    cat /data/perf.json'
