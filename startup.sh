#!/bin/bash

docker-compose up -d

echo -e "\nAll services are healthy! Opening browser..."
case "$(uname -s)" in
    Linux*)     xdg-open http://localhost:58632 ;;
    Darwin*)    open http://localhost:58632 ;;
    CYGWIN*|MINGW*|MSYS*) start http://localhost:58632 ;;
    *)          echo "Please open http://localhost:58632 in your browser" ;;
esac

docker-compose logs -f
