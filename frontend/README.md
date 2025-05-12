# Docker Scanner Frontend (Flutter Web)

## Prerequisites
- [Flutter SDK](https://docs.flutter.dev/get-started/install) (ensure it's added to your PATH)
- [Docker](https://docs.docker.com/get-docker/)

## 1. Install Dependencies
Navigate to the Flutter app directory and install the required packages:

```bash
cd docker_scanner
flutter pub get
```

## 2. Run in Development Mode
You can run the Flutter web app in development mode using Chrome:

```bash
flutter run -d chrome
```

Or, to use the built-in web server (useful for testing on other browsers):

```bash
flutter run -d web-server
```

## 3. Build for Web Release
To generate a production-ready build:

```bash
flutter build web --release
```

The output will be in `docker_scanner/build/web`.

## 4. Build and Run with Docker
After building the web release, you can serve it using Docker and Nginx:

### Build the Docker image

```bash
docker build -t docker-scanner-frontend .
```

### Run the Docker container

```bash
docker run --rm -p 58632:58632 docker-scanner-frontend
```

The app will be available at [http://localhost:58632](http://localhost:58632).
