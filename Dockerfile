FROM alpine:latest

# Create the data directory
RUN mkdir -p /data

# Write some test data and performance data
CMD sh -c '\
    echo "Creating test files in data directory..." && \
    echo "Test file 1" > /data/test1.txt && \
    echo "Test file 2" > /data/test2.txt && \
    echo "{\"perf\":0.69}" > /data/perf.json && \
    echo "\nData directory contents:" && \
    ls -la /data && \
    echo "\nFile contents:" && \
    cat /data/test1.txt && \
    cat /data/test2.txt && \
    cat /data/perf.json'
