# Directory containing the Flutter app
APP_DIR=docker_scanner
# Docker image name
IMAGE_NAME=docker-scanner-frontend
# Docker container port
PORT=58632

.PHONY: help install dev build docker-build docker-run clean

help:
	@echo "Available targets:"
	@echo "  install       Install Flutter dependencies (pub get)"
	@echo "  dev           Run Flutter in development mode (Chrome)"
	@echo "  build         Build Flutter web release"
	@echo "  docker-build  Build the Docker image for the frontend"
	@echo "  docker-run    Run the Docker container for the frontend"
	@echo "  clean         Clean Flutter build artifacts"

install:
	cd $(APP_DIR) && flutter pub get

dev:
	cd $(APP_DIR) && flutter run -d chrome

build:
	cd $(APP_DIR) && flutter build web --release

docker-build: build
	docker build -t $(IMAGE_NAME) .

docker-run:
	docker run --rm -p $(PORT):$(PORT) $(IMAGE_NAME)

clean:
	cd $(APP_DIR) && flutter clean
